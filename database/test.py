import os
from dotenv import load_dotenv
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from models import *
from sqlalchemy import create_engine

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
Session = sessionmaker(bind=engine)

# Helper function to get the session

# Query per contare la distribuzione dei user_score, score_rank e reviews
with Session() as session:
    # Query per user_score
    score_counts = session.query(Game.user_score, func.count(Game.user_score)) \
        .group_by(Game.user_score) \
        .all()

    # Mostra i risultati per user_score
    print("Distribuzione dei User Scores:")
    for score, count in score_counts:
        print(f"User Score: {score}, Count: {count}")

    # Query per score_rank
    score_rank_counts = session.query(Game.score_rank, func.count(Game.score_rank)) \
        .group_by(Game.score_rank) \
        .all()

    # Mostra i risultati per score_rank
    print("\nDistribuzione degli Score Ranks:")
    for rank, count in score_rank_counts:
        print(f"Score Rank: {rank}, Count: {count}")

    # Query per reviews
    print("\nDistribuzione delle reviews:")
    empty_reviews_count = session.query(func.count(Game.reviews)) \
    .filter(Game.reviews == '') \
    .scalar()

    # Contare le reviews non vuote
    non_empty_reviews_count = session.query(func.count(Game.reviews)) \
        .filter(Game.reviews != '') \
        .scalar()

    # Mostra i risultati per le reviews
    print(f"Reviews Vuote: {empty_reviews_count}")
    print(f"Reviews Piene: {non_empty_reviews_count}")
