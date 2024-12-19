import csv
from typing import Any, Text, Dict, List
from dotenv import load_dotenv
import os
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from database.db_queries import *
from database.models import *
from rasa_sdk.events import SlotSet
import random
from sqlalchemy import func
import math
from fuzzywuzzy import fuzz
from typing import Text, List, Any, Dict
from rasa_sdk.events import SlotSet, AllSlotsReset
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import ActiveLoop

import logging
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
    short_description = game.short_description if game.short_description else "No short description available."
    average_playtime = game.average_playtime if game.average_playtime else "Not available"
    reviews = game.reviews if game.reviews else "No reviews available."
    metacritic_score = f"Metacritic score: {game.metacritic_score}" if game.metacritic_score else "No Metacritic score available."
    supported_languages = ', '.join([language.name for language in game.supported_languages]) if game.supported_languages else "No supported languages listed."
    
    # Formattazione della risposta con informazioni aggiuntive
    response = (
        f"{game.name} was released on {release_date} by {pub_names}. "
        f"It costs {price} and was developed by {dev_names}. "
        f"Description: {short_description}\n"
        f"Average playtime: {average_playtime} minutes.\n"
        f"Reviews: {reviews}\n"
        f"{metacritic_score}\n"
        f"Languages supported: {supported_languages}"
    )
    
    return response


class ActionProvideGameInfo(Action):
    def name(self) -> Text:
        return "action_provide_game_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        original_game = tracker.get_slot("game")
        if not original_game:
            dispatcher.utter_message(text="I need the name of the game to provide details.")
            return [SlotSet("publisher", None)]
        
        session = get_session()

        game = get_game_by_name(session, original_game)

        if game:
            response = game_info_response(game)
            dispatcher.utter_message(image=game.header_image, text = response)
        else:
            dispatcher.utter_message(text=f"Sorry, I couldn't retrieve details for the game '{original_game}'.")
        
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
            dispatcher.utter_message(text="I need the name of the publisher to provide details.")
            return [SlotSet("publisher", None)]
        
        session = get_session()

        games = get_top_games_by_publisher(session, original_publisher)

        if not games:
            dispatcher.utter_message(text=f"Sorry, I couldn't find any games for the publisher {original_publisher}.")
        else:
            dispatcher.utter_message(text=f"Here are 5 of our reccomendations based on the publisher {original_publisher}:")

            for game in games:
                response = game_info_response(game)
                dispatcher.utter_message(image=game.header_image, text = response)
        
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
        message = f"I have a total of {len(genres)} genres and subgenres available. These are the 10 most popular:\n\n"
        
        for i, (genre, game_count) in enumerate(genres[:10], 1):  # Prendi solo i primi 10
            message += f"{i}. {genre.name} - {game_count} games in this genre\n"
        
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
        message = f"I have {len(publishers)} publishers available. These are the 10 who have produced the most games:\n\n"
        
        # Aggiungi i dettagli dei primi 10 publisher in una lista numerata
        for i, (publisher, game_count) in enumerate(publishers[:10], 1):  # Prendi solo i primi 10
            message += f"{i}. {publisher.name} - Games produced: {game_count}\n"
        
        # Manda il messaggio
        dispatcher.utter_message(message)
        
        session.close()
        return []

class ActionProvideGenreRecommendation(Action):
    def name(self) -> Text:
        return "action_provide_recommendation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        genre = tracker.get_slot("genre")
        publisher = tracker.get_slot("publisher")

        if not genre or not publisher:
            dispatcher.utter_message(text="Please provide both a genre and a publisher for the recommendation.")
            return [SlotSet("genre", None), SlotSet("publisher", None)]
        
        session = get_session()

        games = get_top_games_by_publisher_and_tag(session, publisher, genre )

        if not games:
            dispatcher.utter_message(text=f"Sorry, I couldn't find any games for the {genre} and {publisher} combination.")
        else:
            dispatcher.utter_message(text=f"Here are 5 of our reccomendations based on the {genre} and {publisher} combination:")

            games_ids = [game.app_id for game in games]
            for game in games:

                response = game_info_response(game)
                dispatcher.utter_message(image=game.header_image, text = response)

        session.close()
        return [SlotSet("genre", None), SlotSet("publisher", None)]
    
class ActionResumeForm(Action):
    def name(self):
        return "action_resume_form"

    def run(self, dispatcher, tracker, domain):
        # Riattiva il ciclo della form senza resettare gli slot
        dispatcher.utter_message(text="Alright, let's pick up where we left off!")
        return [ActiveLoop("detailed_recommendation_form")]

class ValidateDetailedRecommendationForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_detailed_recommendation_form"


    async def validate_genre(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ):
        session = get_session()
        genres = get_all_tag_names(session)
        genres = [genre[0].lower() for genre in genres]

        slot_value = tracker.get_slot('genre')

        logger.info(f"Tracker: {slot_value}")

        if slot_value:
            # Convertiamo e verifichiamo se il valore è valido
            normalized_value = slot_value.strip().lower()
            if normalized_value in genres:
                return {'genre': slot_value.strip()}
        # Se il valore non è valido, inviamo un messaggio di errore
        dispatcher.utter_message(template="utter_unclear_input")
        return {'genre': None}
        
    async def validate_publisher(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ):
        session = get_session()
        publishers = get_all_publisher_names(session)
        publishers = [publisher[0].lower() for publisher in publishers]

        slot_value = tracker.get_slot('publisher')
        
        if slot_value:
            # Convertiamo e verifichiamo se il valore è valido
            normalized_value = slot_value.strip().lower()
            if normalized_value in publishers:
                return {'publisher': slot_value.strip()}
        # Se il valore non è valido, inviamo un messaggio di errore
        dispatcher.utter_message(template="utter_unclear_input")
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