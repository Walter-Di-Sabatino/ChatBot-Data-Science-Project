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
from rapidfuzz import process
from sqlalchemy import func
import math
from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

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

class ActionProvideGameInfo(Action):
    def name(self) -> Text:
        return "action_provide_game_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        game = tracker.get_slot("game")
        if not game:
            dispatcher.utter_message(text="I need the name of the game to provide details.")
            return []
        
        session = get_session()
        game = get_game_by_name(session, game)

        if game:
            release_date = game.release_date.strftime("%Y-%m-%d") if game.release_date else None
            price = game.price
            dispatcher.utter_message(
                f"{game.name} was released on {release_date}. It has a cost of {game.price} USD."
            )
        else:
            dispatcher.utter_message(text=f"Sorry, I couldn't retrieve details for the game '{game}'.")
        
        session.close()
        return [SlotSet("game", None)]

"""class ActionProvideGenreRecommendation(Action):
    def name(self) -> Text:
        return "action_provide_recommendation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        genre = tracker.get_slot("genre")
        if genre:
        
            session = get_session()
            tag = get_tag_by_name(session, genre)

            if tag:
                games = get_top_games_by_tag_and_score(session, tag.tag_id, 5)
            else:
                dispatcher.utter_message(text=f"Sorry, I couldn't find any games for the genre'{genre}'.")
                session.close()
                return [SlotSet("genre", None)]
            
            if not games:
                dispatcher.utter_message(text=f"No games found for the genre '{genre}'.")
                session.close()
                return [SlotSet("genre", None)]

            response = f"Here are some recommendations for the {genre} genre:\n"
            dispatcher.utter_message(text=response)

            for game in games:
                response = ""
                developers = get_developers_by_game(session, game.app_id)
                dev_names = ", ".join([dev.name for dev in developers])

                if ", " in dev_names:
                    dev_names = dev_names.rsplit(", ", 1)
                    dev_names = " and ".join(dev_names)

                response += f"{game.name} released on {game.release_date} by {dev_names}.\n\n"
                response += game.short_description
                dispatcher.utter_message(image = game.header_image, text=response)
            
            session.close()
            return [SlotSet("genre", None)]
        else:

            session = get_session()

            tags = get_top_tags(session)

            response = f"Here are 5 recommendations:\n"
            dispatcher.utter_message(text=response)

            for tag in tags:
                top_games = get_top_games_by_tag_and_score(session, tag[0].tag_id, 100)
                random_game = random.choice(top_games)
                game = random_game
                tag = tag[0]
                response = f"Here's a reccomendation for the {tag.name} genre:\n"
                developers = get_developers_by_game(session, game.app_id)
                dev_names = ", ".join([dev.name for dev in developers])

                if ", " in dev_names:
                    dev_names = dev_names.rsplit(", ", 1)
                    dev_names = " and ".join(dev_names)

                response += f"{game.name} released on {game.release_date} by {dev_names}.\n\n"
                response += game.short_description
                dispatcher.utter_message(image = game.header_image, text=response)                

            session.close()
            return [SlotSet("genre", None)]"""

class ActionProvideGenreRecommendation(Action):
    def name(self) -> Text:
        return "action_provide_recommendation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        genre = tracker.get_slot("genre")
        publisher = tracker.get_slot("publisher")

        session = get_session()

        games = get_top_games_by_publisher_and_tag(session, publisher, genre )

        if not games:
            dispatcher.utter_message(text=f"Sorry, I couldn't find any games for the {genre} and {publisher} combination.")
        else:
            for game in games:
                response = ""
                response += f"{game.name} released on {game.release_date} by {publisher}.\n\n"
                response += game.short_description
                dispatcher.utter_message(image=game.header_image, text=response)

        return [SlotSet("genre", None), SlotSet("publisher", None)]


'''class ValidateDetailedRecommendationForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_detailed_recommendation_form"

    @staticmethod
    def cuisine_db() -> List[Text]:
        """Database of supported cuisines"""

        return ["caribbean", "chinese", "french"]

    def validate_cuisine(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate cuisine value."""

        if slot_value.lower() in self.cuisine_db():
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"cuisine": slot_value}
        else:
            # validation failed, set this slot to None so that the
            # user will be asked for the slot again
            return {"cuisine": None}'''
