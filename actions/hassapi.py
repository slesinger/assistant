# Interface based on https://github.com/AppDaemon/appdaemon/tree/3e141b15b28de9c60fe6e9481581d2748e620cae/appdaemon/plugins/hass

import configparser
from requests import get, post
import logging
logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)

class Hass():

    def __init__(self):
        print("Connecting to Home Assistant")
        config = configparser.ConfigParser()
        config.read('hass.conf')
        self.url = config['api']['base_url']
        self.headers = {
            "Authorization": "Bearer " + config['api']['bearer'],
            "content-type": "application/json",
        }
        print(self.headers)
    
    def call_service(self, service, **kwargs):
        entity_id = kwargs.get('entity_id', False)
        logger.info("Hass service {} entity_id={}".format(service, entity_id))
        r = post(self.url + "/api/services/" + service.replace('.', '/', 1), headers=self.headers, json={ "entity_id": entity_id })
        if r.status_code != 200:
            logger.error("Hass call status code {}".format(r.status_code))