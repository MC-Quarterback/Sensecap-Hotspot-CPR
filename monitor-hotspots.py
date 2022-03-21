import logging
import configparser
import threading
import time

from api import blockchain
from api import hotspot
from exceptions import CPRException

logging.basicConfig(
    format='%(asctime)s %(levelname)-1s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

LOGGER = logging.getLogger(__name__)

class Monitor():
    CONFIG_FILE = 'settings.ini'
    SYSTEM_CONFIG = 'System'

    # System setting fields
    CFG_REBOOT_AFTER = 'reboot_after_reset'
    CFG_REBOOT_BEFORE = 'reboot_before_reset'
    CFG_DELTA = 'max_delta'
    # Hotspot setting fields
    CFG_ADDRESS = 'address'
    CFG_TOKEN = 'token'
    CFG_IP = 'ip'

    WAIT_AFTER_REBOOT = 180 # Seconds = 3 minutes
    WAIT_AFTER_RESET = 2100 # Seconds = 35 minutes
    CHECK_INTERVAL = 420 # Seconds = 7 minutes

    config = None
    reboot_before_reset = False
    reboot_after_reset = False
    max_delta = 6

    cprs_in_progress = {}

    def __init__(self):
        self.read_config()

    def read_config(self):
        self.config = configparser.ConfigParser()
        self.config.read(Monitor.CONFIG_FILE)
        self.check_config()
        self.reboot_before_reset = self.config[Monitor.SYSTEM_CONFIG].getboolean(Monitor.CFG_REBOOT_BEFORE)
        self.reboot_after_reset = self.config[Monitor.SYSTEM_CONFIG].getboolean(Monitor.CFG_REBOOT_AFTER)
        self.max_delta = self.config[Monitor.SYSTEM_CONFIG].getint(Monitor.CFG_DELTA)
        LOGGER.info(f"Config: reboot_before_reset={self.reboot_before_reset} reboot_after_reset={self.reboot_after_reset} max_delta={self.max_delta}")

    def check_config(self):
        if len(self.config.sections())<2:
            raise CPRException("Please configure some hotspots")

        for section in self.config.sections():
            if section != Monitor.SYSTEM_CONFIG:
                if not self.config[section][Monitor.CFG_ADDRESS]:
                    raise CPRException(f"{Monitor.CFG_ADDRESS} not configured for hotspot {section}")
                if not self.config[section][Monitor.CFG_TOKEN]:
                    raise CPRException(f"{Monitor.CFG_TOKEN} not configured for hotspot {section}")
                if not self.config[section][Monitor.CFG_IP]:
                    raise CPRException(f"{Monitor.CFG_IP} not configured for hotspot {section}")

    def check_hotspot(self, hotspot_name):
        LOGGER.info(f"Checking {hotspot_name}...")
        address = self.config[hotspot_name][Monitor.CFG_ADDRESS]
        token = self.config[hotspot_name][Monitor.CFG_TOKEN]
        ip = self.config[hotspot_name][Monitor.CFG_IP]

        bc_height = blockchain.get_blockchain_height()
        hotspot_height = blockchain.get_hotspot_height(address)
        gap = bc_height - hotspot_height
        LOGGER.info(f"{hotspot_name}: blockchain_height={bc_height} hotspot_height={hotspot_height} gap={gap} status={'HEALTHY' if gap <= self.max_delta else 'STALLED'}")
        if gap > self.max_delta:
            self.perform_cpr(hotspot_name, token, ip)

    def perform_cpr(self, name, token, ip):
        if name in self.cprs_in_progress:
            LOGGER.info(f"ERROR - CPR already in progress for {name}")
            return
        self.cprs_in_progress[name] = name

        LOGGER.info(f"Blockchain gap is too great for hotspot {name}, performing CPR...")
        if self.reboot_before_reset:
            total_delay = Monitor.WAIT_AFTER_REBOOT + Monitor.WAIT_AFTER_RESET
            hotspot.reboot(name, token, ip)
            LOGGER.info(f"Will reset blocks on {name} after {Monitor.WAIT_AFTER_REBOOT / 60} minutes")
            self._delay_action(hotspot.resetblocks, name, token, ip, Monitor.WAIT_AFTER_REBOOT)
            if self.reboot_after_reset:
                LOGGER.info(f"Will reboot after reset blocks on {name} after {(Monitor.WAIT_AFTER_REBOOT + Monitor.WAIT_AFTER_RESET) / 60} minutes")
                self._delay_action(hotspot.reboot, name, token, ip, Monitor.WAIT_AFTER_REBOOT+Monitor.WAIT_AFTER_RESET)
                total_delay += Monitor.WAIT_AFTER_REBOOT
        else:
            total_delay = Monitor.WAIT_AFTER_RESET
            hotspot.resetblocks(name, token, ip)
            if self.reboot_after_reset:
                LOGGER.info(f"Will reboot after reset blocks on {name} after {Monitor.WAIT_AFTER_RESET / 60} minutes")
                self._delay_action(hotspot.reboot, name, token, ip, Monitor.WAIT_AFTER_RESET)
                total_delay += Monitor.WAIT_AFTER_REBOOT
            self._delay_action(self.cpr_complete, name, token, ip, Monitor.WAIT_AFTER_RESET)

    def cpr_complete(self, name, _token, _ip, _delay):
        LOGGER.info(f"CPR process finishe for {name}")
        try:
            del self.cprs_in_progress[name]
        except:
            pass
        return True

    def _delay_action(self, action, name, token, ip, delay):
        thread = threading.Thread(target=self._do_action, args=[action, name, token, ip, delay])
        thread.start()

    def _do_action(self, action, name, token, ip, delay):
        if delay and delay>0:
            time.sleep(delay)
        if not action(name, token, ip):
            LOGGER.error(f"There was a problem performing {action} on {name}")


    def perform_reset(self, sleep=0):
        time.sleep(sleep)

    def start(self):
        thread = threading.Thread(target=self._run_loop)
        thread.start()

    def _run_loop(self):
        while(True):
            self.check_hotspots()
            LOGGER.info(f"Will check hotspots again in another {Monitor.CHECK_INTERVAL / 60} minutes")
            time.sleep(Monitor.CHECK_INTERVAL)

    def check_hotspots(self):
        LOGGER.info("Checking hotspots...")
        hotspot_names = list(self.config.sections())
        hotspot_names.remove(Monitor.SYSTEM_CONFIG)
        for name in hotspot_names:
            if name not in self.cprs_in_progress:
                self.check_hotspot(name)
            else:
                LOGGER.info(f"Skipping check on {name} as CPR still in progress")

monitor = Monitor()
monitor.start()


