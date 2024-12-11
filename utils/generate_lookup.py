import json
import random
import csv
import re

def is_valid_game_name(name):
    """Verifica che il nome del gioco contenga solo caratteri latini, numeri e punteggiatura."""
    if name is None:
        return False
    # Regex che permette solo caratteri latini, numeri, spazi e simboli di punteggiatura comuni
    return bool(re.match(r"^[a-zA-Z0-9\s!\"#$%&'()*+,\-./:;<=>?@[\\\]^_`{|}~®™]*$", name))

def extract_and_save_names(json_file, csv_file, num_names=20000):
    # Carica il file JSON con l'encoding 'utf-8'
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Estrai i videogiochi che supportano l'inglese e hanno un nome valido
    names = [game['name'] for game in data.values() if 'English' in game.get('supported_languages', []) and is_valid_game_name(game.get('name'))]

    # Seleziona un numero casuale di nomi
    random_names = random.sample(names, min(len(names), len(names)))  # Assicurati di non selezionare più nomi di quelli disponibili

    # Salva i nomi estratti in un file CSV
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['game_name'])  # Header del CSV
        for name in random_names:
            writer.writerow([re.sub(r"[®™]", "",name)])

    print(f"{len(random_names)} names have been saved to {csv_file}")


def extract_and_save_field(json_file, csv_file, field):
    """Estrai e salva valori unici da un campo specifico in un file CSV."""
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Estrai i valori unici dal campo specificato, facendo il confronto senza case-sensitive e senza spazi,
    # ma salvando il valore originale nel CSV
    seen_values = set()
    values_to_save = []

    for game in data.values():
        for value in game.get(field, []):
            normalized_value = value.replace(" ", "").lower()  # Normalizza (senza spazi e case-insensitive)
            if normalized_value not in seen_values:
                seen_values.add(normalized_value)
                values_to_save.append(value)  # Aggiungi il valore originale

    # Salva i valori unici in un file CSV
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([f'{field}_name'])  # Header del CSV
        for value in sorted(values_to_save):
            writer.writerow([value])

    print(f"{len(values_to_save)} unique {field}s have been saved to {csv_file}")

file = 'database/dataset/games.json'

# Esempi di utilizzo:
# Estrarre e salvare i nomi dei giochi
# extract_and_save_names(file, 'lookup_files/game_names.csv')

# Estrarre e salvare generi, categorie e tag
# extract_and_save_field(file, 'lookup_files/genres_names.csv', 'genres')
# extract_and_save_field(file, 'lookup_files/categories._names.csv', 'categories')
# extract_and_save_field(file, 'lookup_files/tags_names.csv', 'tags')
extract_and_save_field(file, 'lookup_files/developers_names.csv', 'developers')