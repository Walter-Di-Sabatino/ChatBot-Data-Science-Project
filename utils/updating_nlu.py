import os
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import sys
import os

project_root = r"C:\Users\dswal\Desktop\ChatBot-Data-Science-Project"
sys.path.append(project_root)

from database.models import *

load_dotenv()
# Recupera gli elementi dell'URL del database
DB_USER = os.getenv("DB_USER")  # Usa "root" come valore predefinito
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_DRIVER = os.getenv("DB_DRIVER")

# Costruisci l'URL del database
DATABASE_URL = f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

column = "language"

elements_list = session.query(Language.name).distinct().all()

elements_list = [str(genre[0]) for genre in elements_list]

# Formatta gli esempi in stile YAML
formatted_examples = "\n    - ".join(elements_list)

# Prepara la struttura finale in formato testo simile a YAML
lookup_table = f"- lookup: {column}\n  examples: |\n    - {formatted_examples}"

# Carica il file nlu.yml
nlu_file = 'C:/Users\dswal\Desktop/ChatBot-Data-Science-Project/data/nlu.yml'  # Sostituisci con il percorso del tuo file YAML

# Leggi il contenuto del file YAML
with open(nlu_file, 'r') as file:
    nlu_data = file.readlines()

# Aggiungi la lookup table al contenuto del file YAML
nlu_data.append(lookup_table + "\n")

# Scrivi nuovamente nel file nlu.yml
with open(nlu_file, 'w', encoding='utf-8') as file:
    file.writelines(nlu_data)

print("Lookup table aggiunta con successo al file nlu.yml!")
