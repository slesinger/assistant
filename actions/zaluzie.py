from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import logging
logger = logging.getLogger(__name__)
from actions.hassapi import Hass

from rasa_sdk.events import (
    SlotSet,
    UserUtteranceReverted,
    ConversationPaused,
    EventType,
    FollowupAction,
)

from actions.hassapi import Hass

def lookupEntity(room):
    entities = {
        'kuchyn': 'input_boolean.noc_jidelna',
        'kuba': 'input_boolean.noc_kuba',
        'loznice': 'input_boolean.noc_loznice',
        'maja': 'input_boolean.noc_maja',
        'obyvak': 'input_boolean.noc_obyvak'
    }
    return entities.get(room, None)

class ActionZapniNoc(Action, Hass):

    def name(self) -> Text:
        return "action_zapni_noc"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entity_id = next(tracker.get_latest_entity_values("mistnost"), None)
        logger.info("Zapinam noc v {}".format(entity_id))
        if entity_id == None:
            self.call_service("script.turn_on", entity_id="script.1581627254312") # Enable night in all rooms
        else:
            self.call_service("input_boolean.turn_on", entity_id=lookupEntity(entity_id))
        dispatcher.utter_message(template = "utter_potvrzeni")

        return []

class ActionVypniNoc(Action, Hass):

    def name(self) -> Text:
        return "action_vypni_noc"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entity_id = next(tracker.get_latest_entity_values("mistnost"), None)
        logger.info("Vypinam noc v {}".format(entity_id))
        if entity_id == None:
            self.call_service("script.turn_on", entity_id="script.1581626781665") # Disable night in all rooms
        else:
            self.call_service("input_boolean.turn_off", entity_id=lookupEntity(entity_id))
        dispatcher.utter_message(template = "utter_potvrzeni")

        return []

