
# 🎮 Videogame Suggestions Chatbot

Un chatbot intelligente sviluppato con **Rasa** che fornisce **consigli sui videogiochi** basati sulle preferenze dell’utente.
Il bot sfrutta un database derivato dallo **Steam Games Dataset** per rispondere a domande su generi, publisher e titoli, generando raccomandazioni personalizzate.
È stato inoltre integrato con **Telegram** per un’esperienza di utilizzo semplice e accessibile da mobile.

---

## 🚀 Funzionalità

* 🔎 **Visualizzazione dei generi disponibili** – Elenco dei generi principali ordinati per popolarità.
* 🏢 **Visualizzazione dei publisher disponibili** – Elenco dei publisher con più titoli pubblicati.
* 🎲 **Informazioni su un videogioco specifico** – Nome, data di rilascio, prezzo, recensioni, piattaforme supportate, ecc.
* 📚 **Elenco dei videogiochi di un publisher** – I giochi più giocati e meglio recensiti pubblicati da un editore.
* 🤖 **Raccomandazioni personalizzate** – Suggerimenti basati su filtri di genere e/o publisher selezionati dall’utente.

---

## 🛠️ Tecnologie utilizzate

* **[Rasa](https://rasa.com/)** – Framework open source per chatbot NLP.
* **Python 3.9+**
* **SQLAlchemy** – ORM per la gestione del database.
* **SQLite / SQL** – Per l’archiviazione dei dati.
* **Ngrok** – Per esporre il bot in locale e collegarlo a Telegram.
* **Telegram Bot API** – Per interazione con gli utenti.

---

## 📂 Struttura del progetto

* `actions.py` – Azioni custom del bot collegate al DB.
* `nlu.yml` – Intent ed entità per l’addestramento del modello NLP.
* `rules.yml` – Regole di gestione del dialogo.
* `stories.yml` – Esempi di conversazioni reali.
* `config.yml` – Configurazione del modello di machine learning.
* `domain.yml` – Definizione di intent, slot, utterances, azioni e form.
* `database/` – Script SQLAlchemy per il DB (`seeders.py`, `db_queries.py`).

---

## 📊 Dataset

Il chatbot utilizza il **[Steam Games Dataset](https://www.kaggle.com/datasets/fronkongames/steam-games-dataset?select=games.json)**, contenente circa **97.000 videogiochi**.
Dal dataset sono stati caricati **5.000 titoli selezionati** (con più recensioni e valutazioni positive) per ottimizzare le prestazioni.

---

## ✅ Testing

Sono stati effettuati test per:

* Avvio e connessione del bot
* Visualizzazione generi e publisher
* Richiesta info su singoli videogiochi
* Raccomandazioni con e senza filtri
* Gestione input errati

---

## 👥 Autori

* **Agnese Bruglia**
* **Alessandra D’Anna**
* **Walter Di Sabatino**

Relazione svolta per il corso di **Data Science** presso l’**Università Politecnica delle Marche**.
