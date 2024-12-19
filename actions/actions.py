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

def game_info_response(game, publishers_developers):
    pub_names = format_names(publishers_developers[game.app_id]["publishers"])
    dev_names = format_names(publishers_developers[game.app_id]["developers"])

    release_date = game.release_date.strftime("%B %d, %Y") if game.release_date else None
    response = f"{game.name} was released on {release_date} by {pub_names}. It costs {game.price} USD and was developed by {dev_names}."
    return response

def fuzzy_finding(check_name, names, threshold=50):
    # Inizializza variabili per tenere traccia del miglior punteggio e del miglior gioco
    best_name = None
    highest_score = 0

    # Applica fuzzywuzzy per trovare la corrispondenza più simile
    for name in names:
        # Usa fuzz.ratio per un confronto più completo
        score = fuzz.ratio(name.name.lower(), check_name.lower())  # Confronto case-insensitive
        
        # Se il punteggio è maggiore del punteggio più alto trovato finora e supera la soglia
        if score > highest_score and score >= threshold:
            highest_score = score
            best_name = name

    return best_name


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

        # all_games = get_all_games(session)
        # best_game = fuzzy_finding(original_game, all_games)
        # game = get_game_by_name(session, best_game.name)

        game = get_game_by_name(session, original_game)

        if game:
            publishers_developers = get_developers_and_publishers_by_games(session , game.app_id)

            response = game_info_response(game, publishers_developers)
            
            dispatcher.utter_message(response)

            dispatcher.utter_message(image=game.header_image, text=game.short_description)
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
            games_ids = [game.app_id for game in games]
            publishers_developers = get_developers_and_publishers_by_games(session , games_ids)
            for game in games:
                response = ""
                response += game_info_response(game, publishers_developers)
                response += game.short_description
                dispatcher.utter_message(image=game.header_image, text=response)
        
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
            publishers_developers = get_developers_and_publishers_by_games(session , games_ids)
            for game in games:

                response = ""
                response += game_info_response(game, publishers_developers)
                response += game.short_description
                dispatcher.utter_message(image=game.header_image, text=response)

        session.close()
        return [SlotSet("genre", None), SlotSet("publisher", None)]
    
class ActionResumeForm(Action):
    def name(self):
        return "action_resume_form"

    def run(self, dispatcher, tracker, domain):
        # Riattiva il ciclo della form senza resettare gli slot
        dispatcher.utter_message(text="Alright, let's pick up where we left off!")
        return [ActiveLoop("detailed_recommendation_form")]
    
class ActionResetSlots(Action):
    def name(self) -> Text:
        return "action_reset_slots"
    
    def run(self,
            #slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [AllSlotsReset()]