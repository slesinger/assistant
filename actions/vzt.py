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

def lookupMode(rezim):
    modes = {
        'noc': 'Circulation',
        'cirkulace': 'Circulation',
        'vetrani': 'Ventilation'
    }
    return modes.get(rezim, None)

class ActionZapniVzduchotechniku(Action, Hass):

    def name(self) -> Text:
        return "action_zapni_vzduchotechniku"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        rezim = next(tracker.get_latest_entity_values("rezim_vzt"), None)
        if rezim == None:
            logger.error("VOSEFOVAT")
            dispatcher.utter_message(text = "tohle se musí dodělat. schází tu režim")
            return []
    
        procenta = next(tracker.get_latest_entity_values("procenta"), None)
        pct = 0
        if procenta == None:
            if rezim == "cirkulace" or rezim == "krb":
                pct = 90
            if rezim == "vetrani" or rezim == "noc":
                pct = 70
        else:
            pct = int(procenta)
        logger.info("Zapinam VZT rezim {}, {}%".format(rezim, pct))
        self.call_service("climate.set_preset_mode", entity_id="climate.atrea", preset_mode=lookupMode(rezim))
        self.call_service("climate.set_fan_mode", entity_id="climate.atrea", fan_mode=str(pct)+"%")
        dispatcher.utter_message(template = "utter_potvrzeni")

        return []


class ActionVypniVzduchotechniku(Action, Hass):

    def name(self) -> Text:
        return "action_vypni_vzduchotechniku"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        rezim = next(tracker.get_latest_entity_values("rezim_vzt"), None)
        procenta = next(tracker.get_latest_entity_values("procenta"), None)
        logger.info("Vypinam VZT rezim {}, {}[%]".format(rezim, procenta))
        self.call_service("climate.set_preset_mode", entity_id="climate.atrea", preset_mode="Off")
        dispatcher.utter_message(template = "utter_potvrzeni")

        return []
