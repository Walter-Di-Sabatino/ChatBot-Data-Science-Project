# 1. Inizializzare il progetto Alembic
# Questo comando crea la struttura di directory necessaria, come alembic.ini e la cartella versions/
alembic init alembic

# 2. Generare uno script di migrazione
# Genera un nuovo script di migrazione basato sui cambiamenti del modello SQLAlchemy
alembic revision --autogenerate -m "descrizione della migrazione"

# 3. Applicare le migrazioni
# Esegue tutte le migrazioni fino all'ultima versione
alembic upgrade head

# 4. Annullare una migrazione
# Torna a una versione precedente del database (puoi specificare una versione esatta o usare -1 per tornare all'ultima migrazione)
alembic downgrade <versione>       # Es. alembic downgrade -1
alembic downgrade base            # Torna alla versione iniziale del database

# 5. Controllare lo stato delle migrazioni
# Mostra la versione attuale del database rispetto alle migrazioni
alembic current

# 6. Visualizzare la lista delle migrazioni
# Mostra tutte le migrazioni e il loro stato
alembic history --verbose

# 7. Visualizzare l'ultimo "head" (migrazione più recente)
# Mostra l'ultimo "head", cioè l'ultima versione della migrazione
alembic heads

# 8. Esportare una migrazione manualmente
# Crea un nuovo script di migrazione manuale (senza autogenerazione)
alembic revision -m "descrizione della migrazione"

# 9. Mostrare la configurazione di Alembic
# Visualizza la configurazione corrente di Alembic
alembic config

# 10. Eseguire tutte le migrazioni
# Esegue tutte le migrazioni in ordine, fino alla versione finale
alembic upgrade head

# 11. Mostrare il log delle migrazioni
# Mostra i dettagli delle revisioni di migrazione applicate al database
alembic show <versione>           # Mostra il dettaglio di una specifica versione


nlu:
  - lookup: game_names
    file: "lookup_files/game_names.csv"
    entity: game_name

  - lookup: tags_names
    file: "lookup_files/tags_names.csv"
    entity: genre_name



  - rule: Ask recommendations
    steps:
      - intent: ask_recommendation
      - action: utter_ask_interest
      - intent: get_recommendation
      - action: action_provide_recommendation

  - rule: Provide genre recommendations
    steps:
      - intent: get_recommendation
      - action: action_provide_recommendation



- story: Provide recommendation
    steps:
      - intent: ask_recommendation
      - action: utter_ask_interest
      - intent: get_recommendation
        entities:
          - genre_name: "action"
      - action: action_provide_recommendation


- Recommend me some games.
- I'm open to any fun and engaging games.
- Maybe some popular or highly recommended games.
- I'm looking for some enjoyable games to pass the time.
- I want to try a different kind of game.
- I'm up for any good game to play.
- I don't have a specific type of game in mind.
- I’m just looking for a new game to dive into.
- I'm flexible; suggest an exciting game.