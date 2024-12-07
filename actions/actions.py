from typing import Any, Text, Dict, List
from dotenv import load_dotenv
import os
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database.models import Game, Developer, Publisher, Genre, Review, Package  

# Carica le variabili di ambiente dal file .env
load_dotenv()

# Recupera gli elementi dell'URL del database
DB_USER = os.getenv("DB_USER", "root")  # Usa "root" come valore predefinito
DB_PASSWORD = os.getenv("DB_PASSWORD", "Jawalter2020-")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "steam_library")
DB_DRIVER = os.getenv("DB_DRIVER", "mysql+pymysql")

# Costruisci l'URL del database
DATABASE_URL = f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Create an engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

class ActionProvideGameInfo(Action):
    def name(self) -> Text:
        return "action_provide_game_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_name = tracker.get_slot("game_name")
        # Query the Game model to get details
        game = session.query(Game).filter(Game.name.ilike(game_name)).first()
        
        if game:
            details = f"Game: {game.name}\nRelease Date: {game.release_date}\nPrice: {game.price}\nDescription: {game.short_description}"
            dispatcher.utter_message(text=details)
        else:
            dispatcher.utter_message(text=f"No details found for the game '{game_name}'.")

        return []

class ActionProvideDeveloperInfo(Action):
    def name(self) -> Text:
        return "action_provide_developer_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_name = tracker.get_slot("game_name")
        game = session.query(Game).filter(Game.name.ilike(game_name)).first()

        if game:
            developers = [developer.name for developer in game.developers]
            dispatcher.utter_message(text=f"Developers for '{game_name}': {', '.join(developers)}")
        else:
            dispatcher.utter_message(text=f"No developer information found for '{game_name}'.")

        return []

class ActionProvidePublisherInfo(Action):
    def name(self) -> Text:
        return "action_provide_publisher_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_name = tracker.get_slot("game_name")
        game = session.query(Game).filter(Game.name.ilike(game_name)).first()

        if game:
            publishers = [publisher.name for publisher in game.publishers]
            dispatcher.utter_message(text=f"Publishers for '{game_name}': {', '.join(publishers)}")
        else:
            dispatcher.utter_message(text=f"No publisher information found for '{game_name}'.")

        return []

class ActionProvideSystemRequirements(Action):
    def name(self) -> Text:
        return "action_provide_system_requirements"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_name = tracker.get_slot("game_name")
        # Add system requirements query if available in the database schema
        game = session.query(Game).filter(Game.name.ilike(game_name)).first()

        if game:
            # Placeholder, adjust as needed
            dispatcher.utter_message(text=f"System requirements for '{game_name}' will be fetched.")
        else:
            dispatcher.utter_message(text=f"No system requirements found for '{game_name}'.")

        return []

class ActionProvidePriceInfo(Action):
    def name(self) -> Text:
        return "action_provide_price_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_name = tracker.get_slot("game_name")
        game = session.query(Game).filter(Game.name.ilike(game_name)).first()

        if game:
            dispatcher.utter_message(text=f"The price for '{game_name}' is {game.price}.")
        else:
            dispatcher.utter_message(text=f"No price information found for '{game_name}'.")

        return []

class ActionProvideGenreInfo(Action):
    def name(self) -> Text:
        return "action_provide_genre_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_name = tracker.get_slot("game_name")
        game = session.query(Game).filter(Game.name.ilike(game_name)).first()

        if game:
            genres = [genre.name for genre in game.genres]
            dispatcher.utter_message(text=f"Genres for '{game_name}': {', '.join(genres)}")
        else:
            dispatcher.utter_message(text=f"No genre information found for '{game_name}'.")

        return []

class ActionProvideReviewInfo(Action):
    def name(self) -> Text:
        return "action_provide_review_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_name = tracker.get_slot("game_name")
        game = session.query(Game).filter(Game.name.ilike(game_name)).first()

        if game:
            # Assuming reviews are stored as text or ratings in the game model
            dispatcher.utter_message(text=f"Reviews for '{game_name}': {game.reviews}")
        else:
            dispatcher.utter_message(text=f"No review information found for '{game_name}'.")

        return []

class ActionProvideAchievementsInfo(Action):
    def name(self) -> Text:
        return "action_provide_achievements_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_name = tracker.get_slot("game_name")
        game = session.query(Game).filter(Game.name.ilike(game_name)).first()

        if game:
            dispatcher.utter_message(text=f"Achievements for '{game_name}': {game.achievements}")
        else:
            dispatcher.utter_message(text=f"No achievements information found for '{game_name}'.")

        return []
