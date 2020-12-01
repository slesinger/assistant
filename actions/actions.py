from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionRozsvitit(Action):

    def name(self) -> Text:
        return "action_rozsvit"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        mistnost = tracker.get_slot('mistnost')
        print("HASS call service light.enable", mistnost)
        dispatcher.utter_message(text="jo jo")

        return []
