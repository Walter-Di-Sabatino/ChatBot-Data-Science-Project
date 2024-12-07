import json
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tables import Game, Developer, Genre, Movie, Package, Publisher, Screenshot, Subpackage, Tag

# Configura la connessione al database
DATABASE_URL = 'mysql+pymysql://root:Jawalter2020-@localhost/steam_library'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def load_json_data(filepath):
    """Carica i dati dal file JSON."""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError as e:
                print(f"Errore nel parsing del file JSON: {e}")
                return None
    else:
        print(f"Il file {filepath} non esiste.")
        return None

def seed_data(dataset):
    """Esegui il seeding dei dati nel database."""
    for app_id, game in dataset.items():
        # Aggiungi il gioco
        new_game = Game(
            app_id=app_id,
            name=game['name'],
            release_date=game['release_date'],
            estimated_owners=game['estimated_owners'],
            peak_ccu=game['peak_ccu'],
            required_age=game['required_age'],
            price=game['price'],
            dlc_count=game['dlc_count'],
            detailed_description=game['detailed_description'],
            short_description=game['short_description'],
            supported_languages=game['supported_languages'],
            full_audio_languages=game['full_audio_languages'],
            reviews=game['reviews'],
            header_image=game['header_image'],
            website=game['website'],
            support_url=game['support_url'],
            support_email=game['support_email'],
            support_windows=game['windows'],
            support_mac=game['mac'],
            support_linux=game['linux'],
            metacritic_score=game['metacritic_score'],
            metacritic_url=game['metacritic_url'],
            user_score=game['user_score'],
            positive=game['positive'],
            negative=game['negative'],
            score_rank=game['score_rank'],
            achievements=game['achievements'],
            recommendations=game['recommendations'],
            notes=game['notes'],
            average_playtime=game['average_playtime_forever'],
            average_playtime_2weeks=game['average_playtime_2weeks'],
            median_playtime=game['median_playtime_forever'],
            median_playtime_2weeks=game['median_playtime_2weeks']
        )
        session.add(new_game)

        # Aggiungi developers, genres, movies, ecc.
        developers = [Developer(app_id=app_id, name=dev) for dev in game['developers']]
        genres = [Genre(app_id=app_id, name=genre) for genre in game['genres']]
        movies = [Movie(app_id=app_id, url=movie) for movie in game['movies']]
        publishers = [Publisher(app_id=app_id, name=publisher) for publisher in game['publishers']]
        screenshots = [Screenshot(app_id=app_id, url=screenshot) for screenshot in game['scrennshots']]
        tags = [Tag(app_id=app_id, name=tag) for tag in game['tags']]

        session.bulk_save_objects(developers + genres + movies + publishers + screenshots + tags)

        # Gestione dei pacchetti e subpacchetti
        packages = []
        subpackages = []
        for package in game['packages']:
            new_package = Package(app_id=app_id, title=package['title'], description=package['description'])
            packages.append(new_package)

            for sub in package['subs']:
                new_subpackage = Subpackage(
                    package_id=new_package.package_id,
                    title=sub['text'],
                    description=sub['description'],
                    price=sub['price']
                )
                subpackages.append(new_subpackage)

        session.bulk_save_objects(packages + subpackages)

        # Commit ogni 1000 record (puoi regolare questo valore)
        if len(session.new) >= 1000:
            session.commit()

    # Commit finale
    session.commit()

def run_seeding():
    """Esegui il seeding."""
    dataset = load_json_data('raw/games.json')
    if dataset:
        seed_data(dataset)

# Esegui il seeding
if __name__ == "__main__":
    run_seeding()
