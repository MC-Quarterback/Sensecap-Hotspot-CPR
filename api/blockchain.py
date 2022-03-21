import logging
import requests

from exceptions import CPRException

LOGGER = logging.getLogger(__name__)

def get_hotspot_status(address):
    assert type(address) == str, "Address musst be given in string format"
    response = requests.get(f'https://api.helium.io/v1/hotspots/{address}')

    if response.ok:
        return response.json()["data"]
    else:
        raise CPRException(f'{response.status_code}: {response.reason}')

def get_hotspot_height(address):
    status = get_hotspot_status(address)
    return status["block"]

def get_blockchain_height():
    response = requests.get('https://api.helium.io/v1/blocks/height')

    if response.ok:
        return response.json()["data"]["height"]

    else:
        raise CPRException(f'{response.status_code}: {response.reason}')



