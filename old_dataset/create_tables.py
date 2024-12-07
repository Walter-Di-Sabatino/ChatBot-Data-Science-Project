import pymysql

db_config = {
    'host': 'localhost',
    'user': 'root',        # Cambia con il tuo username
    'password': 'password', # Cambia con la tua password
    'database': 'games_data',  # Assicurati che il database esista
    'charset': 'utf8mb4'
}

# Funzione per eseguire file SQL
def execute_sql_file(file_path, connection):
    with open(file_path, 'r', encoding='utf-8') as f:
        sql = f.read()
        with connection.cursor() as cursor:
            cursor.execute(sql)
            connection.commit()

# Connessione al database
connection = pymysql.connect(**db_config)

# Esegui il file SQL per creare le tabelle
execute_sql_file('create_tables.sql', connection)

# Chiudi la connessione dopo la creazione delle tabelle
connection.close()
