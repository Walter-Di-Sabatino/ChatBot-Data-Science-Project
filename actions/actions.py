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

# Carica le variabili di ambiente dal file .env
load_dotenv()

# Recupera gli elementi dell'URL del database
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Jawalter2020-")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "steam_library")
DB_DRIVER = os.getenv("DB_DRIVER", "mysql+pymysql")

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
        
        game_name = tracker.get_slot("game_name")
        if not game_name:
            dispatcher.utter_message(text="I need the name of the game to provide details.")
            return []
        
        session = get_session()
        game = get_game_by_name(session, game_name)

        if game:
            release_date = game.release_date.strftime("%Y-%m-%d") if game.release_date else None
            price = game.price
            dispatcher.utter_message(
                response="utter_game_info",
                game_name=game.name,
                release_date=release_date,
                price=price
            )
        else:
            dispatcher.utter_message(text=f"Sorry, I couldn't retrieve details for the game '{game_name}'.")
        
        session.close()
        return [SlotSet("game_name", None)]

class ActionProvideGenreRecommendation(Action):
    def name(self) -> Text:
        return "action_provide_recommendation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        genre_name = tracker.get_slot("genre_name")
        if genre_name:
        
            session = get_session()
            tag = get_tag_by_name(session, genre_name)

            if tag:
                games = get_top_games_by_tag_and_score(session, tag.tag_id, 5)
            else:
                dispatcher.utter_message(text=f"Sorry, I couldn't find any games for the genre'{genre_name}'.")
                session.close()
                return [SlotSet("genre_name", None)]
            
            if not games:
                dispatcher.utter_message(text=f"No games found for the genre '{genre_name}'.")
                session.close()
                return [SlotSet("genre_name", None)]

            response = f"Here are some recommendations for the {genre_name} genre:\n"
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
            return [SlotSet("genre_name", None)]
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
            return [SlotSet("genre_name", None)]
