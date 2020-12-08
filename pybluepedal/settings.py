import logging
import os

from dotenv import find_dotenv, load_dotenv

from pybluepedal.device import BLEDevice

logger = logging.getLogger("Collector")


class Settings:

    def __init__(self):
        load_dotenv(find_dotenv())

        self.BLE_CONNECT_MAX_TRIES = int(os.getenv("BLE_CONNECT_MAX_TRIES", 3))
        self.BLE_SERVER_KEYS = os.getenv("BLE_SERVER_KEYS", "").split(" ")

        self.BLE_DEVICES = []
        for server in self.BLE_SERVER_KEYS:
            functions = os.getenv(f"{server.upper()}_COLLECTOR_FUNCTIONS", "")
            self.BLE_DEVICES.append(
                BLEDevice(
                    os.getenv(f"{server.upper()}_NAME"),
                    os.getenv(f"{server.upper()}_ADDRESS"),
                    functions.split(" "),
                    self.BLE_CONNECT_MAX_TRIES
                )
            )
