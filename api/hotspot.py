import requests
import logging

from exceptions import CPRException

LOGGER = logging.getLogger(__name__)

def reboot(name, token, ip):
    LOGGER.info(f"Rebooting {name} now")
    return _do_post('reboot', token, ip)

def resetblocks(name, token, ip):
    LOGGER.info(f"Resetting blocks on {name} now")
    return _do_post('resetblocks', token, ip)

def turbo_sync(name, token, ip):
    LOGGER.info(f"Turbosyncing {name} now")
    return _do_post('turbosync', token, ip)

def _do_post(command, token, ip):
    response = requests.post(f'http://{ip}/{command}', headers=_get_headers(token))
    if response.ok:
        return True
    else:
        raise CPRException(f'{response.status_code}: {response.reason}')

def _get_headers(token):
     return {'Authorization': 'Basic '+token}

