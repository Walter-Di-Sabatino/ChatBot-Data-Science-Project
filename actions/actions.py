import csv
from typing import Any, Text, Dict, List
from dotenv import load_dotenv
import os
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from database.models import Game, Developer, Publisher, Genre, Package
from rasa_sdk.events import SlotSet
from rapidfuzz import process 

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

# Create an engine and sessionmaker
engine = create_engine(DATABASE_URL)
SessionFactory = sessionmaker(bind=engine)

# Helper function to get the session
def get_session() -> Session:
    return SessionFactory()

# Utility function to get game details
def get_game_by_name(game_name: str) -> Game:
    session = get_session()
    game = session.query(Game).filter(Game.name.ilike(game_name)).first()
    session.close()
    return game

def fuzzy_find_in_list(item, items_list):
    lowercase_item_list = [s.lower() for s in items_list]

    similar_item_index = process.extractOne(
                item.lower(),
                lowercase_item_list)

    similar_item = items_list[similar_item_index]

    return similar_item

class ActionProvideGameInfo(Action):
    def name(self) -> Text:
        return "action_provide_game_info"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Recupera il nome del gioco dallo slot
        game_name = tracker.get_slot("game_name")
        
        # Controlla se è stato fornito un nome di gioco
        if not game_name:
            dispatcher.utter_message(text="I need the name of the game to provide details.")
            return []

        # Connessione al database e recupero delle informazioni sul gioco
        session = get_session() 
        game = session.query(Game).filter(Game.name.ilike(game_name)).first()

        if game:
            # Ottieni i dettagli del gioco
            release_date = game.release_date.strftime("%Y-%m-%d") if game.release_date else None
            price = game.price

            # Invia i dettagli del gioco all'utente
            dispatcher.utter_message(
                response="utter_game_info",
                game_name=game.name,
                release_date=release_date,
                price=price
            )

            # Restituisci gli slot con le informazioni del gioco
            session.close()
            return [{"game_name": game.name, "release_date": release_date, "price": price}]

        # Se il gioco non è trovato nel database
        dispatcher.utter_message(text=f"Sorry, I couldn't retrieve details for the game '{game_name}'. Please check the name and try again.")
        session.close()
        return []

class ActionProvideGenreReccomendationo(Action):
    def name(self) -> Text:
        return "action_provide_reccomendation"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return []

