from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from datetime import datetime

class ActionTime(Action):

    def name(self) -> Text:
        return "action_time"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        now = datetime.now()
        dispatcher.utter_message(text = now.strftime("%I:%M"))
        return []
