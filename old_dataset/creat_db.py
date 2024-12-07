import pymysql

# Configurazione MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',        # Cambia con il tuo username
    'password': 'password', # Cambia con la tua password
    'database': 'games_data',  # Assicurati che il database esista
    'charset': 'utf8mb4'
}

# Funzione per creare il database se non esiste
def create_database(connection):
    with connection.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS games_data;")
        connection.commit()

# Connessione al database
connection = pymysql.connect(**db_config)

# Crea il database se non esiste
create_database(connection)

# Chiudi la connessione (fino a questo punto)
connection.close()
