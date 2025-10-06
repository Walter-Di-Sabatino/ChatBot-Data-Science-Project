
# 🎮 Videogame Suggestions Chatbot

An intelligent chatbot developed with **Rasa** that provides **videogame recommendations** based on user preferences.
The bot uses a database derived from the **Steam Games Dataset** to answer questions about genres, publishers, and titles, generating personalized suggestions.
It has also been integrated with **Telegram** for a simple and mobile-friendly user experience.

---

## 🚀 Features

* 🔎 **View available genres** – List of main genres sorted by popularity.
* 🏢 **View available publishers** – List of publishers with the highest number of released titles.
* 🎲 **Information about a specific videogame** – Name, release date, price, reviews, supported platforms, and more.
* 📚 **List of a publisher’s videogames** – Most played and top-rated games released by a publisher.
* 🤖 **Personalized recommendations** – Suggestions based on genre and/or publisher filters selected by the user.

---

## 🛠️ Technologies Used

* **[Rasa](https://rasa.com/)** – Open-source NLP chatbot framework.
* **Python 3.9+**
* **SQLAlchemy** – ORM for database management.
* **SQLite / SQL** – For data storage.
* **Ngrok** – To expose the bot locally and connect it to Telegram.
* **Telegram Bot API** – For user interaction.

---

## 📂 Project Structure

* `actions.py` – Custom bot actions connected to the database.
* `nlu.yml` – Intents and entities for NLP model training.
* `rules.yml` – Dialogue management rules.
* `stories.yml` – Examples of real conversations.
* `config.yml` – Machine learning model configuration.
* `domain.yml` – Definition of intents, slots, utterances, actions, and forms.
* `database/` – SQLAlchemy scripts for the DB (`seeders.py`, `db_queries.py`).

---

## 📊 Dataset

The chatbot uses the **[Steam Games Dataset](https://www.kaggle.com/datasets/fronkongames/steam-games-dataset?select=games.json)**, containing about **97,000 videogames**.
From this dataset, **5,000 selected titles** (with the most reviews and positive ratings) were loaded to optimize performance.

---

## ✅ Testing

Tests were performed for:

* Bot startup and connection
* Genre and publisher display
* Requests for specific videogame details
* Recommendations with and without filters
* Handling of incorrect inputs

---

## 👥 Authors

* **Agnese Bruglia**
* **Alessandra D’Anna**
* **Walter Di Sabatino**

Project completed for the **Data Science** course at the **Polytechnic University of Marche**.
