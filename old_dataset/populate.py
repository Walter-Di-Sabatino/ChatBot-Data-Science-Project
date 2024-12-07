import json
import pymysql

db_config = {
    'host': 'localhost',
    'user': 'root',        # Cambia con il tuo username
    'password': 'password', # Cambia con la tua password
    'database': 'games_data',  # Assicurati che il database esista
    'charset': 'utf8mb4'
}

# Funzione per caricare il JSON
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Funzione per popolare le tabelle
def populate_tables(data, connection):
    try:
        with connection.cursor() as cursor:
            # Inserisci i dati nella tabella 'games'
            for app_id, game in data.items():
                sql_game = """
                INSERT INTO games (
                    app_id, name, release_date, estimated_owners, peak_ccu, required_age, price, dlc_count, 
                    detailed_description, short_description, supported_languages, full_audio_languages, reviews, 
                    header_image, website, support_url, support_email, support_windows, support_mac, support_linux, 
                    metacritic_score, metacritic_url, user_score, positive, negative, score_rank, achievements, 
                    recommendations, notes, average_playtime, average_playtime_2weeks, median_playtime, 
                    median_playtime_2weeks
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """
                cursor.execute(sql_game, (
                    app_id, game['name'], game['release_date'], game['estimated_owners'], game['peak_ccu'], 
                    game['required_age'], game['price'], game['dlc_count'], game['detailed_description'], 
                    game['short_description'], ','.join(game['supported_languages']), 
                    ','.join(game['full_audio_languages']), game['reviews'], game['header_image'], 
                    game['website'], game['support_url'], game['support_email'], game['windows'], 
                    game['mac'], game['linux'], game['metacritic_score'], game['metacritic_url'], 
                    game['user_score'], game['positive'], game['negative'], game['score_rank'], 
                    game['achievements'], game['recommendations'], game['notes'], 
                    game['average_playtime_forever'], game['average_playtime_2weeks'], 
                    game['median_playtime_forever'], game['median_playtime_2weeks']
                ))

                # Inserisci i dati correlati nelle altre tabelle (packages, developers, ecc.)
                for dev in game.get('developers', []):
                    sql_dev = "INSERT INTO developers (app_id, name) VALUES (%s, %s)"
                    cursor.execute(sql_dev, (app_id, dev))

                for pub in game.get('publishers', []):
                    sql_pub = "INSERT INTO publishers (app_id, name) VALUES (%s, %s)"
                    cursor.execute(sql_pub, (app_id, pub))

                for cat in game.get('categories', []):
                    sql_cat = "INSERT INTO categories (app_id, name) VALUES (%s, %s)"
                    cursor.execute(sql_cat, (app_id, cat))

                for gen in game.get('genres', []):
                    sql_gen = "INSERT INTO genres (app_id, name) VALUES (%s, %s)"
                    cursor.execute(sql_gen, (app_id, gen))

                for tag_key, tag_value in game.get('tags', {}).items():
                    sql_tag = "INSERT INTO tags (app_id, name) VALUES (%s, %s)"
                    cursor.execute(sql_tag, (app_id, tag_key))

                for screenshot in game.get('screenshots', []):
                    sql_ss = "INSERT INTO screenshots (app_id, url) VALUES (%s, %s)"
                    cursor.execute(sql_ss, (app_id, screenshot))

                for movie in game.get('movies', []):
                    sql_movie = "INSERT INTO movies (app_id, url) VALUES (%s, %s)"
                    cursor.execute(sql_movie, (app_id, movie))

            # Commit dei cambiamenti
            connection.commit()
    except Exception as e:
        print(f"Errore durante l'inserimento dei dati: {e}")
        connection.rollback()

# Main
if __name__ == '__main__':
    # Percorso al file JSON
    file_path = 'data/raw/games.json'

    # Carica il dataset
    dataset = load_json(file_path)

    # Connessione al database
    connection = pymysql.connect(**db_config)

    # Popola le tabelle
    populate_tables(dataset, connection)

    # Chiudi la connessione
    connection.close()
