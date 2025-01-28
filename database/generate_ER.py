from sqlalchemy.orm import configure_mappers
from sqlalchemy_schemadisplay import create_schema_graph
from sqlalchemy import MetaData, create_engine
from models import Base 
import os

# Ottieni le variabili dal .env
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
db_driver = os.getenv("DB_DRIVER")

# Costruisci l'URL del database
database_url = f"{db_driver}://{db_user}:{db_password}@{db_host}/{db_name}"

# Crea l'engine con il collegamento al database
engine = create_engine(database_url)

metadata = Base.metadata
# Configura i modelli per la mappatura
configure_mappers()

# Filtra le tabelle da includere nel grafo
filtered_tables = [table for table in metadata.tables.values() if table.name != "alembic_version"]

# Crea il grafo dello schema usando Base.metadata
graph = create_schema_graph(
    engine=engine,
    metadata=metadata,
    tables=filtered_tables,  # Passa solo le tabelle filtrate
    show_datatypes=True,
    show_indexes=True,
    rankdir='TB',
    concentrate=False,
)


# Percorso del file di output
output_path = os.path.join(os.getcwd(), 'database/schema.png')

# Salva il grafo come file PNG
graph.write_png(output_path)
print(f"Schema generato: {output_path}")
