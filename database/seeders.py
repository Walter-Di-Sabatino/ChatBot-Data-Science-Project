import json
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dateutil import parser
from dotenv import load_dotenv

import sys

# Ottieni la directory principale del progetto
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_dir)
from models import *
from sqlalchemy.exc import IntegrityError
import re

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

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def load_json_data(filepath):
    """Carica i dati dal file JSON."""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            print(f"Errore nel parsing del file JSON: {e}")
        except Exception as e:
            print(f"Errore nell'aprire il file: {e}")
    else:
        print(f"Il file {filepath} non esiste.")
    return None

def safe_get(value):
    """Restituisce None o NaN per valori mancanti o vuoti."""
    if isinstance(value, str) and value.strip() == '':
        return None  # Sostituisce stringhe vuote con None
    elif isinstance(value, (int, float)) and (value is None or value == ''):
        return float('nan')  # Sostituisce i valori numerici mancanti con NaN
    return value

def is_valid_game_name(name):
    """Verifica che il nome del gioco contenga solo caratteri latini, numeri e spazi."""
    if name is None:
        return False
    # Regex che permette solo caratteri latini, numeri e spazi
    return bool(re.match(r"^[a-zA-Z0-9\s!\"#$%&'()*+,\-./:;<=>?@[\\\]^_`{|}~®™]*$", name))

def seed_game_data(game):
    """Aggiungi i dati di un gioco nel database solo se supporta l'inglese e il nome è valido."""
    
    # Controlla se l'inglese è nelle lingue supportate
    supported_languages = game.get('supported_languages', [])
    if 'English' not in supported_languages:
        return None  # Salta il gioco se non supporta l'inglese
    
    detailed_description = game.get('detailed_description')
    if len(detailed_description.encode('utf-8')) > 65535:
        return None
    
    # Verifica che il nome del gioco contenga solo caratteri validi
    game_name = safe_get(game.get('name'))
    if not is_valid_game_name(game_name):
        print(f"Nome del gioco '{game_name}' non valido (contenuto non latino). Salto il gioco.")
        return None  # Salta il gioco se il nome non è valido
    
    print(game_name)

    game_name = re.sub(r"[®™]", "", game_name)

    # Recupero e conversione della data
    release_date = safe_get(game.get('release_date'))

    if release_date:
        release_date = release_date.replace(',', '')  # Rimuove la virgola
        
        try:
            # Tenta di fare il parsing con il formato specifico
            release_date = datetime.strptime(release_date, "%b %d %Y")
        except ValueError:
            # Se fallisce, usa il parser di dateutil
            release_date = parser.parse(release_date)

    new_game = Game(
        name=game_name,
        release_date=release_date,
        estimated_owners=safe_get(game.get('estimated_owners')),
        peak_ccu=safe_get(game.get('peak_ccu')),
        required_age=safe_get(game.get('required_age')),
        price=safe_get(game.get('price')),
        dlc_count=safe_get(game.get('dlc_count')),
        detailed_description=safe_get(game.get('detailed_description')),
        short_description=safe_get(game.get('short_description')),
        reviews=safe_get(game.get('reviews')),
        header_image=safe_get(game.get('header_image')),
        website=safe_get(game.get('website')),
        support_url=safe_get(game.get('support_url')),
        support_email=safe_get(game.get('support_email')),
        support_windows=safe_get(game.get('windows')),
        support_mac=safe_get(game.get('mac')),
        support_linux=safe_get(game.get('linux')),
        metacritic_score=safe_get(game.get('metacritic_score')),
        metacritic_url=safe_get(game.get('metacritic_url')),
        user_score=safe_get(game.get('user_score')),
        positive=safe_get(game.get('positive')),
        negative=safe_get(game.get('negative')),
        score_rank=safe_get(game.get('score_rank')),
        achievements=safe_get(game.get('achievements')),
        recommendations=safe_get(game.get('recommendations')),
        notes=safe_get(game.get('notes')),
        average_playtime=safe_get(game.get('average_playtime_forever')),
        average_playtime_2weeks=safe_get(game.get('average_playtime_2weeks')),
        median_playtime=safe_get(game.get('median_playtime_forever')),
        median_playtime_2weeks=safe_get(game.get('median_playtime_2weeks'))
    )
    session.add(new_game)
    return new_game

def seed_package_data(game, new_game):
    """Aggiungi i pacchetti e subpacchetti di un gioco nel database."""
    for package in game.get('packages', []):
        new_package = Package(
            app_id=new_game.app_id,
            title=safe_get(package.get('title')),
            description=safe_get(package.get('description'))
        )
        session.add(new_package)

        for subpackage in package.get('subpackages', []):
            new_subpackage = Subpackage(
                package_id=new_package.package_id,
                title=safe_get(subpackage.get('title')),
                description=safe_get(subpackage.get('description')),
                price=safe_get(subpackage.get('price'))
            )
            session.add(new_subpackage)

def seed_developers(game):
    """Aggiungi sviluppatori di un gioco nel database."""
    developers = []
    for dev in game.get('developers', []):
        existing_dev = session.query(Developer).filter_by(name=dev).first()
        if not existing_dev:
            new_dev = Developer(name=dev)
            session.add(new_dev)
            session.flush()
            developers.append(new_dev)
        else:
            developers.append(existing_dev)
    return developers

def seed_genres(game):
    """Aggiungi generi di un gioco nel database."""
    genres = []
    for genre in game.get('genres', []):
        existing_genre = session.query(Genre).filter_by(name=genre).first()
        if not existing_genre:
            new_genre = Genre(name=genre)
            session.add(new_genre)
            session.flush()
            genres.append(new_genre)
        else:
            genres.append(existing_genre)
    return genres

def seed_categories(game):
    """Aggiungi generi di un gioco nel database."""
    categories = []
    for category in game.get('categories', []):
        existing_genre = session.query(Category).filter_by(name=category).first()
        if not existing_genre:
            new_genre = Category(name=category)
            session.add(new_genre)
            session.flush()
            categories.append(new_genre)
        else:
            categories.append(existing_genre)
    return categories

def seed_movies_and_screenshots(game, new_game):
    """Aggiungi film e screenshot di un gioco nel database."""
    movies = [Movie(app_id=new_game.app_id, url=safe_get(movie)) for movie in game.get('movies', [])]
    screenshots = [Screenshot(app_id=new_game.app_id, url=safe_get(screenshot)) for screenshot in game.get('screenshots', [])]
    session.bulk_save_objects(movies)
    session.bulk_save_objects(screenshots)

def seed_publishers_and_tags(game):
    """Aggiungi publisher e tag di un gioco nel database."""
    publishers = []
    tags = []
    for publisher in game.get('publishers', []):
        existing_pub = session.query(Publisher).filter_by(name=publisher).first()
        if not existing_pub:
            new_pub = Publisher(name=publisher)
            session.add(new_pub)
            session.flush()
            publishers.append(new_pub)
        else:
            publishers.append(existing_pub)

    if isinstance(game.get('tags'), dict):
        for tag, tag_value in game.get('tags', {}).items():
            existing_tag = session.query(Tag).filter_by(name=tag).first()
            if not existing_tag:
                new_tag = Tag(name=str(tag))
                session.add(new_tag)
                session.flush() 
                tags.append([new_tag, tag_value, tag])
            else:
                tags.append([existing_tag, tag_value, tag])

    return publishers, tags

def link_game_to_developers_genres_categories_publishers_tags(new_game, developers, genres, categories, publishers, tags):
    """Collega il gioco agli sviluppatori, generi, editori e tag (many-to-many)."""
    
    app_id = new_game.app_id
    game_developers = [GameDeveloper(app_id=app_id, developer_id=developer.developer_id) for developer in developers]
    game_categories = [GameCategory(app_id=app_id, category_id=category.category_id) for category in categories]
    game_genres = [GameGenre(app_id=app_id, genre_id=genre.genre_id) for genre in genres]
    game_publishers = [GamePublisher(app_id=app_id, publisher_id=publisher.publisher_id) for publisher in publishers]
    game_tags = [GameTag(app_id=app_id, tag_id=tag[0].tag_id, tag_value=tag[1]) for tag in tags]

    # Usa bulk_save_objects per inserire tutte le voci in un'unica operazione
    session.bulk_save_objects(game_developers + game_genres + game_publishers + game_tags + game_categories)


def seed_languages(game, new_game):
    """Aggiungi lingue supportate e lingue audio complete."""
    supported_languages = []
    for lang in game.get('supported_languages', []):
        existing_language = session.query(Language).filter_by(name=lang).first()
        if not existing_language:
            new_language = Language(name=lang)
            session.add(new_language)
            session.flush() 
            supported_languages.append(new_language)
        else:
            supported_languages.append(existing_language)

    full_audio_languages = []
    for lang in game.get('full_audio_languages', []):
        existing_language = session.query(Language).filter_by(name=lang).first()
        if not existing_language:
            new_language = Language(name=lang)
            session.add(new_language)
            session.flush() 
            full_audio_languages.append(new_language)
        else:
            full_audio_languages.append(existing_language)

    app_id = new_game.app_id
    supported_languages_list = [GameSupportedLanguage(app_id=app_id, language_id=language.language_id) for language in supported_languages]
    full_audio_languages_list = [GameFullAudioLanguage(app_id=app_id, language_id=language.language_id) for language in full_audio_languages]

    # Usa bulk_save_objects per inserire tutte le lingue in un'unica operazione
    session.bulk_save_objects(supported_languages_list + full_audio_languages_list)

def seed_data(dataset):
    """Esegui il seeding dei dati nel database."""
    
    for game in dataset.values():
        try:
            new_game = seed_game_data(game)
            if new_game is None:
                continue 
            seed_package_data(game, new_game)
            developers = seed_developers(game)
            categories = seed_categories(game)
            genres = seed_genres(game)
            seed_movies_and_screenshots(game, new_game)
            publishers, tags = seed_publishers_and_tags(game)
            link_game_to_developers_genres_categories_publishers_tags(new_game, developers, genres, categories, publishers, tags)
            seed_languages(game, new_game)
        except IntegrityError:
            session.rollback()
        
        session.commit()

    # Commit finale
    session.commit()

def run_seeding():
    """Esegui il seeding."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(script_dir, 'dataset', 'games.json')

    print(f"Percorso completo del file JSON: {json_file_path}")
    dataset = load_json_data(json_file_path)
    if dataset:
        seed_data(dataset)

# Esegui il seeding
if __name__ == "__main__":
    run_seeding()
