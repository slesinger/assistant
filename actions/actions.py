from actions.hassapi import Hass
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
    SlotSet,
    UserUtteranceReverted,
    ConversationPaused,
    EventType,
    FollowupAction,
)


class ActionRozsvitit(Action, Hass):

    def name(self) -> Text:
        return "action_rozsvit"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print("entiti", next(tracker.get_latest_entity_values("mistnost"), None))
        self.call_service("light.turn_on", entity_id="light.pracovna")
        dispatcher.utter_message(text="jo jo")

        return [SlotSet("mistnost", None)]
