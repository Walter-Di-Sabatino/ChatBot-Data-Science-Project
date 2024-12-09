import csv
from typing import Any, Text, Dict, List
from dotenv import load_dotenv
import os
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from models import *
from rasa_sdk.events import SlotSet
from rapidfuzz import process 

from sqlalchemy import func
import math

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

def fuzzy_find_in_list(item, items_list):
    lowercase_item_list = [s.lower() for s in items_list]

    similar_item_index = process.extractOne(
                item.lower(),
                lowercase_item_list)

    similar_item = items_list[similar_item_index]

    return similar_item

# Calcola il punteggio finale
def get_game_score(game):
    # Gestione del caso di zero recensioni
    if game.positive + game.negative == 0:
        return 0
    else:
        percentuale_pos = game.positive / (game.positive + game.negative)
        # Calcoliamo il punteggio finale
        return percentuale_pos * math.log(game.positive + game.negative + 1)

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

            session.close()
            return [{"game_name": None, "release_date": None, "price": None}]

        # Se il gioco non è trovato nel database
        dispatcher.utter_message(text=f"Sorry, I couldn't retrieve details for the game '{game_name}'. Please check the name and try again.")
        session.close()
        return [{"game_name": None, "release_date": None, "price": None}]

class ActionProvideGenreRecommendationo(Action):
    def name(self) -> Text:
        return "action_provide_recommendation"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Recupera il nome del gioco dallo slot
        genre_tag_name = tracker.get_slot("genre_name")

        game_ids = []

        if genre_tag_name:
            session = get_session()

            # Trova il genere e il tag corrispondenti
            genre = session.query(Genre).filter(Genre.name.ilike(genre_tag_name)).first()
            tag = session.query(Tag).filter(Tag.name.ilike(genre_tag_name)).first()

            if genre and tag:
                # Unisci le tabelle GameGenre e GameTag utilizzando un JOIN sui rispettivi ID
                game_ids = session.query(GameGenre.app_id) \
                    .join(GameTag, GameTag.app_id == GameGenre.app_id) \
                    .filter(GameGenre.genre_id == genre.genre_id, GameTag.tag_id == tag.tag_id) \
                    .distinct() \
                    .all()
            elif genre:  # Se solo il genere è stato trovato
                game_ids = session.query(GameGenre.app_id) \
                    .filter(GameGenre.genre_id == genre.genre_id) \
                    .distinct() \
                    .all()
            elif tag:  # Se solo il tag è stato trovato
                game_ids = session.query(GameTag.app_id) \
                    .filter(GameTag.tag_id == tag.tag_id) \
                    .distinct() \
                    .all()

            if len(game_ids) == 0:
                dispatcher.utter_message(text=f"Sorry, I couldn't retrieve details for the genre '{genre_tag_name}'. Please check the name and try again.")
                session.close()
                return []
            
            # Estrai gli app_id dalla lista di tuple
            unique_game_ids = [game_id[0] for game_id in game_ids]

            # Recupera i giochi con gli app_id trovati
            games = session.query(Game).filter(Game.app_id.in_(unique_game_ids)).all()

            # Calcoliamo il punteggio per ogni gioco
            games_with_scores = [(game, get_game_score(game)) for game in games]

            # Ordina i giochi in base al punteggio finale, in ordine decrescente
            top_games = sorted(games_with_scores, key=lambda x: x[1], reverse=True)

            num_games = 5

            # Prendi i primi 10 giochi o meno se la lista è più breve
            top_games = top_games[:min(len(top_games), num_games)]

            # Se vuoi solo i giochi, estrae i giochi dai tuple
            top_games_only = [game for game, score in top_games]

            top_games_with_developers = []

            for game in top_games_only:
                developer_names = session.query(Developer.name) \
                .join(GameDeveloper, GameDeveloper.developer_id == Developer.developer_id) \
                .join(Game, Game.app_id == GameDeveloper.app_id) \
                .filter(Game.app_id == game.app_id) \
                .distinct() \
                .all()

                top_games_with_developers.append([game,developer_names])

            response = f"Sure! Here are some suggestions for the {genre_tag_name} genre:"

            # Stampa i giochi e i loro punteggi
            for game in top_games_with_developers:
                response += f"\n{game[0].name} developed by: "
                response += ", ".join(str(developer[0]) for developer in game[1])
            
            dispatcher.utter_message(text=response)
            return [SlotSet("genre_name", None)]

        else:
            # inserire caso in cui non ha inserito generi l'utente
            print()

        return [SlotSet("genre_name", None)]
    

