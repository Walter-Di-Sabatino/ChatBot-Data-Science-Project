from typing import Any, Text, Dict, List
from dotenv import load_dotenv
import os
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from database.models import Game, Developer, Publisher, Genre, Package
from rasa_sdk.events import SlotSet

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

class ActionProvideGameInfo(Action):
    def name(self) -> Text:
        return "action_provide_game_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Recupera i dati dagli slot
        game_name = tracker.get_slot("game_name")

        # Se manca il nome del gioco, invia un messaggio di errore
        if not game_name:
            dispatcher.utter_message(text="I need the name of the game to provide details.")
            return []

        # Connessione al database e recupero del gioco
        session = get_session()
        game = session.query(Game).filter(Game.name.ilike(game_name)).first()
        session.close()

        print(game)

        # Se il gioco non è trovato
        if not game:
            dispatcher.utter_message(text=f"No details found for the game '{game_name}'.")
            return []

        # Se il gioco è trovato, aggiorna gli slot con i dettagli
        game_name = game.name
        release_date = game.release_date
        price = game.price

        # Ritorna gli SlotSet con i nuovi valori
        return [
            SlotSet("game_name", game_name),
            SlotSet("release_date", release_date),
            SlotSet("price", price)
        ]


class ActionProvideDeveloperInfo(Action):
    def name(self) -> Text:
        return "action_provide_developer_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_name = tracker.get_slot("game_name")
        game = get_game_by_name(game_name)

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
        game = get_game_by_name(game_name)

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
        game = get_game_by_name(game_name)

        if game:
            # You can extend this logic for specific system requirements retrieval
            support_windows = tracker.get_slot("supportWindows")
            support_mac = tracker.get_slot("supportMac")
            support_linux = tracker.get_slot("supportLinux")
            dispatcher.utter_message(
                text=f"{game_name} supports the following platforms: Windows - {support_windows}, Mac - {support_mac}, Linux - {support_linux}."
            )
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
        game = get_game_by_name(game_name)

        if game:
            price = tracker.get_slot("price")
            dispatcher.utter_message(text=f"The price for '{game_name}' is {price} USD.")
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
        game = get_game_by_name(game_name)

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
        game = get_game_by_name(game_name)

        if game:
            metacritic_score = tracker.get_slot("metacriticScore")
            user_score = tracker.get_slot("userScore")
            dispatcher.utter_message(
                text=f"Reviews for '{game_name}': Metacritic Score - {metacritic_score}, User Score - {user_score}"
            )
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
        game = get_game_by_name(game_name)

        if game:
            achievements = tracker.get_slot("achievements")
            dispatcher.utter_message(text=f"Achievements for '{game_name}': {achievements}")
        else:
            dispatcher.utter_message(text=f"No achievements information found for '{game_name}'.")

        return []
