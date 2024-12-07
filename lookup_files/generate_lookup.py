import json
import random
import csv
import re

def is_valid_game_name(name):
    """Verifica che il nome del gioco contenga solo caratteri latini, numeri e punteggiatura."""
    if name is None:
        return False
    # Regex che permette solo caratteri latini, numeri, spazi e simboli di punteggiatura comuni
    return bool(re.match(r'^[A-Za-z0-9\s\.,;\'"!&\(\)\[\]\{\}\-–_+?\/]*$', name))

def extract_and_save_names(json_file, csv_file, num_names=5000):
    # Carica il file JSON con l'encoding 'utf-8'
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Estrai i videogiochi che supportano l'inglese e hanno un nome valido
    names = [game['name'] for game in data.values() if 'English' in game.get('supported_languages', []) and is_valid_game_name(game.get('name'))]

    # Seleziona un numero casuale di nomi
    random_names = random.sample(names, min(num_names, len(names)))  # Assicurati di non selezionare più nomi di quelli disponibili

    # Salva i nomi estratti in un file CSV
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['game_name'])  # Header del CSV
        for name in random_names:
            writer.writerow([name])

    print(f"{len(random_names)} names have been saved to {csv_file}")

# Chiamata alla funzione
extract_and_save_names('database/dataset/games.json', 'lookup_files/game_name.csv')
