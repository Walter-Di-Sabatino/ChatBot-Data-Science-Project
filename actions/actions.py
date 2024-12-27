# Standard Library Imports
import os
import random
import math
import logging

# Third-Party Libraries
import requests
import validators
from dotenv import load_dotenv
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from typing import Any, Text, Dict, List

# Rasa SDK Imports
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset, ActiveLoop

# Custom Modules
from database.db_queries import *
from database.models import *

logger = logging.getLogger(__name__)
logging.basicConfig(level="DEBUG")

# Carica le variabili di ambiente dal file .env
load_dotenv()

# Recupera gli elementi dell'URL del database
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_DRIVER = os.getenv("DB_DRIVER")

# Costruisci l'URL del database
DATABASE_URL = f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Create an engine and sessionmaker
engine = create_engine(DATABASE_URL)
SessionFactory = sessionmaker(bind=engine)

# Helper function to get the session
def get_session() -> Session:
    return SessionFactory()

def get_game_score(game):
    if game.positive + game.negative == 0:
        return 0
    return (game.positive / (game.positive + game.negative)) * math.log(game.positive + game.negative + 1)

def format_names(names):

    all_names = ", ".join([name.name for name in names])

    if ", " in all_names:
        all_names = all_names.rsplit(", ", 1)
        all_names = " and ".join(all_names)

    return all_names

def game_info_response(game):
    # Recupero dei nomi degli editori e degli sviluppatori
    pub_names = format_names(game.publishers)
    dev_names = format_names(game.developers)
    
    # Recupero della data di rilascio
    release_date = game.release_date.strftime("%B %d, %Y") if game.release_date else "N/A"
    
    # Recupero dei dettagli aggiuntivi
    price = f"${game.price:.2f}" if game.price else "Price not available"
    short_description = game.short_description if game.short_description else "No description available."
    required_age = game.required_age if game.required_age else "Not available"
    estimated_owners = game.estimated_owners if game.estimated_owners else "Not available"
    reviews = game.reviews if game.reviews else "No reviews available."
    metacritic_score = f"Metacritic score: {game.metacritic_score}" if game.metacritic_score else "No Metacritic score available."
    supported_languages = ', '.join([language.name for language in game.supported_languages]) if game.supported_languages else "No supported languages listed."
    
    # Recupero del supporto per i sistemi operativi
    os_support = []
    if game.support_windows:
        os_support.append("Windows")
    if game.support_mac:
        os_support.append("Mac")
    if game.support_linux:
        os_support.append("Linux")
    
    os_support_text = ', '.join(os_support) if os_support else "No operating system support listed."
    
    # Formattazione della risposta con informazioni aggiuntive
    response = (
        f"🎮 {game.name} was released on {release_date} by {pub_names}.\n"
        f"💰 It costs {price} and was developed by {dev_names}.\n"
        f"🔞 Required Age: {required_age}.\n"
        f"📝 Description: {short_description}\n"
        f"👥 Estimated owners: {estimated_owners}.\n"
        f"⭐ Reviews: {reviews}\n"
        f"🎯 {metacritic_score}\n"
        f"🌐 Languages supported: {supported_languages}\n"
        f"💻 Operating System Support: {os_support_text}"
    )
    
    return response

def game_info_response_dispatched(dispatcher, game):
    response = game_info_response(game)
    header_image = game.header_image
    
    # Controlla se l'URL è valido
    if validators.url(header_image):
        try:
            # Fai una richiesta HEAD per ottenere il tipo di contenuto, seguendo le redirezioni
            response = requests.head(header_image, allow_redirects=True, timeout=10)
            content_type = response.headers.get('Content-Type', '').lower()
            
            # Verifica se il Content-Type è di un'immagine
            if 'image' in content_type:
                dispatcher.utter_message(image=header_image, text=game_info_response(game))
            else:
                response = game_info_response(game) + "\n🚫 The URL does not point to an image"
                dispatcher.utter_message(text=response)
        except requests.exceptions.RequestException as e:
            # Gestisce eventuali errori durante la richiesta
            response = game_info_response(game) + "\n❌ Failed to retrieve image"
            dispatcher.utter_message(text=response)
    else:
        response = game_info_response(game) + "\n❓ No valid URL found"
        dispatcher.utter_message(text=response)


class ActionProvideGameInfo(Action):
    def name(self) -> Text:
        return "action_provide_game_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        original_game = tracker.get_slot("game")
        if not original_game:
            dispatcher.utter_message(text="❓ I need the name of the game to provide details.")
            return [SlotSet("game", None)]
        
        session = get_session()

        game = get_game_by_name(session, original_game)

        if game:
            game_info_response_dispatched(dispatcher, game)
        else:
            dispatcher.utter_message(text=f"🚫 Sorry, I couldn't retrieve details for the game '{original_game}'.")
        
        session.close()
        return [SlotSet("game", None)]
    
class ActionProvidePublisherGames(Action):
    def name(self) -> Text:
        return "action_provide_publisher_games"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        original_publisher = tracker.get_slot("publisher")
        if not original_publisher:
            dispatcher.utter_message(text="❓ I need the name of the publisher to provide details.")
            return [SlotSet("publisher", None)]
        
        session = get_session()

        games = get_top_games_by_publisher(session, original_publisher)

        if not games:
            dispatcher.utter_message(text=f"🚫 Sorry, I couldn't find any games for the publisher {original_publisher}.")
        else:
            dispatcher.utter_message(text=f"💡 Here are 5 of our recommendations based on the publisher {original_publisher}:")

            for game in games:
                game_info_response_dispatched(dispatcher, game)
        
        session.close()
        return [SlotSet("publisher", None)]

class ActionProvideGenres(Action):
    def name(self) -> Text:
        return "action_provide_genres"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        session = get_session()

        genres = get_top_tags(session)
        
        # Crea il messaggio da inviare
        message = f"🎮 I have a total of {len(genres)} genres and subgenres available. These are the 10 most popular:\n\n"

        for i, (genre, game_count) in enumerate(genres[:10], 1):  # Prendi solo i primi 10
            message += f"🔹 {i}. {genre.name} - {game_count} games in this genre\n"

        dispatcher.utter_message(message)
        
        session.close()
        return []
    
class ActionProvidePublishers(Action):
    def name(self) -> Text:
        return "action_provide_publishers"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        session = get_session()

        # Ottieni i top publisher con il conteggio dei giochi
        publishers = get_top_publishers(session)
        
        # Crea il messaggio da inviare
        message = f"🏢 I have {len(publishers)} publishers available. These are the 10 who have produced the most games:\n\n"

        # Aggiungi i dettagli dei primi 10 publisher in una lista numerata
        for i, (publisher, game_count) in enumerate(publishers[:10], 1):  # Prendi solo i primi 10
            message += f"🔸 {i}. {publisher.name} - Games produced: {game_count}\n"

        # Manda il messaggio
        dispatcher.utter_message(message)
        session.close()
        return []

class ActionProvideRecommendation(Action):
    def name(self) -> Text:
        return "action_provide_recommendation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        genre = tracker.get_slot("genre")
        publisher = tracker.get_slot("publisher")
        genre_filter = tracker.get_slot("genre_filter")
        publisher_filter = tracker.get_slot("publisher_filter")

        if genre == "NO": genre = False
        if publisher == "NO": publisher = False

        logger.info(f"Tracker: yolo")

        session = get_session()

        negative_response = ""
        positive_response = ""

        games = None

        if not genre and not publisher and not genre_filter and not publisher_filter:
            games = get_top_games(session, limit=1000)

            if len(games) >= 5:
                games = random.sample(games, 5)
            else:
                games = games

            positive_response = "🎮 Here are 5 games across all genres and publishers."
            negative_response = "🚫 Sorry, I couldn't retrieve the top games right now."

        elif genre and publisher and genre_filter and publisher_filter:
            games = get_top_games_by_publisher_and_tag(session, publisher, genre, limit = 100)

            if len(games) >= 5:
                games = random.sample(games, 5)
            else:
                games = games

            positive_response = f"💡 Here are {len(games)} of our recommendations based on the {genre} and {publisher} combination:"
            negative_response = f"🚫 Sorry, I couldn't find any games for the {genre} and {publisher} combination."

        elif not genre and publisher and not genre_filter and publisher_filter:
            games = get_top_games_by_publisher(session, publisher, limit=100)

            if len(games) >= 5:
                games = random.sample(games, 5)
            else:
                games = games

            positive_response = f"📝 Here are {len(games)} games published by {publisher}:"
            negative_response = f"🚫 Sorry, I couldn't find any games published by {publisher}."

        elif genre and not publisher and genre_filter and not publisher_filter:
            games = get_top_games_by_tag(session, genre, limit= 500)

            if len(games) >= 5:
                games = random.sample(games, 5)
            else:
                games = games

            positive_response = f"🎮 Here are {len(games)} games in the {genre} genre:"
            negative_response = f"🚫 Sorry, I couldn't find any games in the {genre} genre."

        else:
            negative_response = "🚫 Sorry, I couldn't process your request. Please try specifying different criteria or check your input."


        if not games:
            dispatcher.utter_message(text=negative_response)
        else:
            dispatcher.utter_message(text=positive_response)

            for game in games:
                game_info_response_dispatched(dispatcher, game)

        session.close()
        return [AllSlotsReset()]

    
class ActionResumeForm(Action):
    def name(self):
        return "action_resume_form"

    def run(self, dispatcher, tracker, domain):
        # Riattiva il ciclo della form senza resettare gli slot
        dispatcher.utter_message(text="🔄 Alright, let's pick up where we left off! 😊")
        return [ActiveLoop("detailed_recommendation_form")]
    
class ValidateDetailedRecommendationForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_detailed_recommendation_form"

    def validate_genre_filter(
        self,
        value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> Dict[Text, Any]:

        slot_value = tracker.get_slot('genre_filter')
        
        logger.info(f"Tracker: yolo1")

        if slot_value == False:
            dispatcher.utter_message(text="🎮 Ok, I won't filter by genre. 👍")
            return {"genre_filter": False, "genre": "NO"}
        elif slot_value == True:
            return {"genre_filter": True}
        
        return {"genre_filter": None}

    def validate_genre(
        self,
        value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> Dict[Text, Any]:

        logger.info(f"Tracker: yolo2")

        if not tracker.get_slot('genre_filter')  and tracker.get_slot('genre') == "NO":
            return {"genre": "NO"}

        session = get_session()
        genres = get_all_tag_names(session)
        genres = [genre[0].lower() for genre in genres]

        slot_value = tracker.get_slot('genre')

        if slot_value:
            # Convertiamo e verifichiamo se il valore è valido
            normalized_value = slot_value.strip().lower()
            if normalized_value in genres:
                return {'genre': slot_value.strip(), "genre_filter": True}
        # Se il valore non è valido, inviamo un messaggio di errore
        dispatcher.utter_message(text="🚫 Sorry, that's not a valid genre. Please try again.")
        return {'genre': None}

    def validate_publisher_filter(
        self,
        value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> Dict[Text, Any]:

        slot_value = tracker.get_slot('publisher_filter')

        logger.info(f"Tracker: yolo3")
        
        if not slot_value:
            dispatcher.utter_message(text="🏢 Ok, I won't filter by publisher. 👍")
            return {"publisher_filter": False, "publisher": "NO"}
        elif slot_value:
            return {"publisher_filter": True}
        
        return {"publisher_filter": None}
        
    def validate_publisher(
        self,
        value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> Dict[Text, Any]:

        logger.info(f"Tracker: yolo4")

        if not tracker.get_slot('publisher_filter') and tracker.get_slot('publisher') == "NO":
            return {"publisher": "NO"}

        session = get_session()
        publishers = get_all_publisher_names(session)
        publishers = [publisher[0].lower() for publisher in publishers]

        slot_value = tracker.get_slot('publisher')

        if slot_value:
            # Convertiamo e verifichiamo se il valore è valido
            normalized_value = slot_value.strip().lower()
            if normalized_value in publishers:
                logger.info(f"Tracker: {slot_value.strip()}")
                return {'publisher': slot_value.strip(), "publisher_filter": True}
        # Se il valore non è valido, inviamo un messaggio di errore
        dispatcher.utter_message(text="🚫 Sorry, that's not a valid publisher. Please try again.")
        return {'publisher': None}

class ActionResetSlots(Action):
    def name(self) -> Text:
        return "action_reset_slots"
    
    def run(self,
            #slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [AllSlotsReset()]