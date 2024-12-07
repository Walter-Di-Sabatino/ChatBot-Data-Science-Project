# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionProvideGameInfo(Action):
    def name(self) -> Text:
        return "action_provide_game_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Placeholder logic
        game_name = tracker.get_slot("game_name")
        # Logic to retrieve game info goes here
        dispatcher.utter_message(text=f"Details about the game '{game_name}' will be fetched.")
        return []

class ActionProvideDeveloperInfo(Action):
    def name(self) -> Text:
        return "action_provide_developer_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Placeholder logic
        game_name = tracker.get_slot("game_name")
        # Logic to retrieve developer info goes here
        dispatcher.utter_message(text=f"Developer information for '{game_name}' will be fetched.")
        return []

class ActionProvidePublisherInfo(Action):
    def name(self) -> Text:
        return "action_provide_publisher_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Placeholder logic
        game_name = tracker.get_slot("game_name")
        # Logic to retrieve publisher info goes here
        dispatcher.utter_message(text=f"Publisher information for '{game_name}' will be fetched.")
        return []

class ActionProvideSystemRequirements(Action):
    def name(self) -> Text:
        return "action_provide_system_requirements"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Placeholder logic
        game_name = tracker.get_slot("game_name")
        # Logic to retrieve system requirements goes here
        dispatcher.utter_message(text=f"System requirements for '{game_name}' will be fetched.")
        return []

class ActionProvidePriceInfo(Action):
    def name(self) -> Text:
        return "action_provide_price_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Placeholder logic
        game_name = tracker.get_slot("game_name")
        # Logic to retrieve price info goes here
        dispatcher.utter_message(text=f"Price information for '{game_name}' will be fetched.")
        return []

class ActionProvideGenreInfo(Action):
    def name(self) -> Text:
        return "action_provide_genre_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Placeholder logic
        game_name = tracker.get_slot("game_name")
        # Logic to retrieve genre info goes here
        dispatcher.utter_message(text=f"Genre information for '{game_name}' will be fetched.")
        return []

class ActionProvideReviewInfo(Action):
    def name(self) -> Text:
        return "action_provide_review_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Placeholder logic
        game_name = tracker.get_slot("game_name")
        # Logic to retrieve review info goes here
        dispatcher.utter_message(text=f"Review information for '{game_name}' will be fetched.")
        return []

class ActionProvideAchievementsInfo(Action):
    def name(self) -> Text:
        return "action_provide_achievements_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Placeholder logic
        game_name = tracker.get_slot("game_name")
        # Logic to retrieve achievements info goes here
        dispatcher.utter_message(text=f"Achievements for '{game_name}' will be fetched.")
        return []
