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

def format_names_list(names):

    all_names = ", ".join([name for name in names])

    if ", " in all_names:
        all_names = all_names.rsplit(", ", 1)
        all_names = " or ".join(all_names)

    return all_names

def format_plural(word, count):
    """Return the plural form of a word if count is greater than 1."""
    return f"{word}s" if count > 1 else word

def format_plural_verb(count):
    """Return the plural form of a word if count is greater than 1."""
    return "are" if count > 1 else "is"

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
        
        original_publisher = tracker.get_slot("publishers")[0]

        if not original_publisher:
            dispatcher.utter_message(text="❓ I need the name of the publishers to provide details.")
            return [SlotSet("publishers", None)]
        
        session = get_session()

        games = get_top_games_filtered(session, publisher_names = [original_publisher])

        verb = format_plural_verb(len(games))

        if not games:
            dispatcher.utter_message(text=f"🚫 Sorry, I couldn't find any games for the publisher {original_publisher}.")
        else:
            dispatcher.utter_message(text=f"💡 Here {verb} {len(games)} of our recommendations based on the publisher {original_publisher}:")

            for game in games:
                game_info_response_dispatched(dispatcher, game)
        
        session.close()
        return [SlotSet("publishers", None)]

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
            message += f"🔹 {i}. {genre.name} - {game_count} games in this genres\n"

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

        # Ottieni i top publishers con il conteggio dei giochi
        publishers = get_top_publishers(session)
        
        # Crea il messaggio da inviare
        message = f"🏢 I have {len(publishers)} publishers available. These are the 10 who have produced the most games:\n\n"

        # Aggiungi i dettagli dei primi 10 publishers in una lista numerata
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

        genres = tracker.get_slot("genres")
        publishers = tracker.get_slot("publishers")
        genres_filter = tracker.get_slot("genres_filter")
        publishers_filter = tracker.get_slot("publishers_filter")

        if genres == ["NO"]: genres = False
        else: genre_label = format_plural("genre", len(genres))

        if publishers == ["NO"]: publishers = False
        else: publisher_label = format_plural("publisher", len(publishers))

        logger.info(f"Tracker: yolo")

        session = get_session()

        negative_response = ""
        positive_response = ""

        games = None

        if not genres and not publishers and not genres_filter and not publishers_filter:
            games = get_top_games(session, limit=1000)

            if len(games) >= 5:
                games = random.sample(games, 5)
            else:
                games = games

            positive_response = "🎮 Here are 5 games across all genres and publishers."
            negative_response = "🚫 Sorry, I couldn't retrieve the top games right now."

        elif genres and publishers and genres_filter and publishers_filter:
            games = get_top_games_filtered(session, publishers, genres, limit = 100)

            if len(games) >= 5:
                games = random.sample(games, 5)
            else:
                games = games

            verb = format_plural_verb(len(games))

            positive_response = f"💡 Here {verb} {len(games)} of our recommendations based on the {format_names_list(genres)} {genre_label} and {format_names_list(publishers)} {publisher_label}:"
            negative_response = f"🚫 Sorry, I couldn't find any games for the {format_names_list(genres)} {genre_label} and {format_names_list(publishers)} {publisher_label} combination."

        elif not genres and publishers and not genres_filter and publishers_filter:
            games = get_top_games_filtered(session, publisher_names=publishers, limit=100)

            if len(games) >= 5:
                games = random.sample(games, 5)
            else:
                games = games
            
            verb = format_plural_verb(len(games))

            positive_response = f"📝 Here {verb} {len(games)} games published by {format_names_list(publishers)}:"
            negative_response = f"🚫 Sorry, I couldn't find any games published by {format_names_list(publishers)}."

        elif genres and not publishers and genres_filter and not publishers_filter:
            games = get_top_games_filtered(session, tag_names= genres, limit= 500)

            if len(games) >= 5:
                games = random.sample(games, 5)
            else:
                games = games
            
            verb = format_plural_verb(len(games))
            
            positive_response = f"🎮 Here {verb} {len(games)} games of the {format_names_list(genres)} {genre_label}:"
            negative_response = f"🚫 Sorry, I couldn't find any games of the {format_names_list(genres)} {genre_label}."

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

    def validate_genres_filter(
        self,
        value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> Dict[Text, Any]:

        slot_value = tracker.get_slot('genres_filter')
        
        logger.info(f"Tracker: yolo1")

        if slot_value == False:
            dispatcher.utter_message(text="🎮 Ok, I won't filter by genres. 👍")
            return {"genres_filter": False, "genres": ["NO"]}
        elif slot_value == True:
            return {"genres_filter": True}
        
        return {"genres_filter": None}

    def validate_genres(
        self,
        value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> Dict[Text, Any]:

        logger.info(f"Tracker: yolo2")

        if not tracker.get_slot('genres_filter')  and tracker.get_slot('genres') == ["NO"]:
            return {"genres": ["NO"]}

        session = get_session()
        genres = get_all_tag_names(session)
        genres = [genre[0].lower() for genre in genres]

        slot_value = tracker.get_slot('genres')

        logger.info(f"Tracker: {slot_value}")

        if slot_value:
            slot_value = list(set(slot_value))
            # Creiamo una lista per i generi validi
            valid_genres = []
            
            for value in slot_value:
                # Convertiamo e verifichiamo ogni valore
                normalized_value = value.strip().lower()
                if normalized_value in genres:
                    logger.info(f"Tracker: {value.strip()}")
                    valid_genres.append(value.strip())
            
            # Se abbiamo trovato generi validi, ritorniamo il risultato
            if valid_genres:
                return {'genres': valid_genres, "genres_filter": True}
        # Se il valore non è valido, inviamo un messaggio di errore
        dispatcher.utter_message(text="🚫 Sorry, that's not a valid genres. Please try again.")
        return {'genres': None}

    def validate_publishers_filter(
        self,
        value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> Dict[Text, Any]:

        slot_value = tracker.get_slot('publishers_filter')

        logger.info(f"Tracker: yolo3")
        
        if not slot_value:
            dispatcher.utter_message(text="🏢 Ok, I won't filter by publishers. 👍")
            return {"publishers_filter": False, "publishers": ["NO"]}
        elif slot_value:
            return {"publishers_filter": True}
        
        return {"publishers_filter": None}
        
    def validate_publishers(
        self,
        value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> Dict[Text, Any]:

        logger.info(f"Tracker: yolo4")

        if not tracker.get_slot('publishers_filter') and tracker.get_slot('publishers') == ["NO"]:
            return {"publishers": ["NO"]}

        session = get_session()
        publishers = get_all_publisher_names(session)
        publishers = [publisher[0].lower() for publisher in publishers]

        slot_value = tracker.get_slot('publishers')

        if slot_value:
            # Creiamo una lista per i publishers validi
            valid_publishers = []
            slot_value = list(set(slot_value))
            
            for value in slot_value:
                # Convertiamo e verifichiamo ogni valore
                normalized_value = value.strip().lower()
                if normalized_value in publishers:
                    logger.info(f"Tracker: {value.strip()}")
                    valid_publishers.append(value.strip())
            
            # Se abbiamo trovato publishers validi, ritorniamo il risultato
            if valid_publishers:
                return {'publishers': valid_publishers, "publishers_filter": True}

        # Se il valore non è valido, inviamo un messaggio di errore
        dispatcher.utter_message(text="🚫 Sorry, that's not a valid publishers. Please try again.")
        return {'publishers': None}

class ActionResetSlots(Action):
    def name(self) -> Text:
        return "action_reset_slots"
    
    def run(self,
            #slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [AllSlotsReset()]