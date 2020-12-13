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


# Kde se nalezaji Asistenti, bere se ze sender_id
def lookupDefaultLight(sender_id):
    default_lights = {
        'loznice': ['loznice'],
        'jidelna': ['jidelna', 'kuchyne'],
        'obyvak': ['obyvak']
    }
    return default_lights.get(sender_id, ['light.pracovna'])

# Mapa entit na svetla
def lookupLight(sender_id):
    default_lights = {
        'dole': ['light.obyvak', 'light.jidelna', 'light.loznice'],
        'vsude': ['light.chodba', 'light.dvorek', 'light.hala', 'light.jidelna', 'light.koupelna', 'light.krb', 'light.kuba1', 'light.kuba2', 'switch.kuchyn_leva', 'switch.kuchyn_prava',
            'switch.kuchyn_okno', 'light.kuchyn', 'light.loznice', 'light.maja1', 'light.maja2', 'light.obyvak', 'light.pracovna', 'switch.zasuvka_lampicka', 'light.terasa', 'light.vchod'],
        'chodba': ['light.chodba'],
        'hala': ['light.hala'],
        'jidelna': ['light.jidelna'],
        'koupelna': ['light.koupelna'],
        'krb': ['light.krb'],
        'kuba': ['light.kuba1', 'light.kuba2'],
        'kuchyn': ['switch.kuchyn_leva', 'switch.kuchyn_prava', 'switch.kuchyn_okno', 'light.kuchyn'],
        'loznice': ['light.loznice'],
        'maja': ['light.maja1', 'light.maja2'],
        'obyvak': ['light.obyvak'],
        'pracovna': ['light.pracovna'],
        'lampicka': ['switch.zasuvka_lampicka'],
        'vchod': ['light.vchod']
    }
    return default_lights.get(sender_id, ['light.pracovna'])

class ActionRozsvitit(Action, Hass):

    def name(self) -> Text:
        return "action_rozsvit"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        sender_id = tracker.current_state()['sender_id']
        e = next(tracker.get_latest_entity_values("mistnost"), None)
        logger.debug("Sender {}, Entity {}".format(sender_id, e))
        lights = None
        if e == None:
            lights = lookupDefaultLight(sender_id)
        else:
            lights = lookupLight(e)
        for l in lights:
            domain = l.split('.')[0]
            self.call_service(domain + ".turn_on", entity_id=l)
        dispatcher.utter_message(template = "utter_potvrzeni")

        return [SlotSet("posledni_mistnost", e)]


class ActionZhasnout(Action, Hass):

    def name(self) -> Text:
        return "action_zhasni"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        sender_id = tracker.current_state()['sender_id']
        e = next(tracker.get_latest_entity_values("mistnost"), None)
        logger.debug("Sender {}, Entity {}".format(sender_id, e))
        lights = None
        if e == None:
            lights = lookupDefaultLight(sender_id)
        else:
            lights = lookupLight(e)
        for l in lights:
            domain = l.split('.')[0]
            self.call_service(domain + ".turn_off", entity_id=l)
        dispatcher.utter_message(template = "utter_potvrzeni")

        return [SlotSet("posledni_mistnost", e)]
