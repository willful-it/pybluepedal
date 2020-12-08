import logging
import os

from dotenv import find_dotenv, load_dotenv

from pybluepedal.device import BLEDevice

load_dotenv(find_dotenv())

logger = logging.getLogger("Collector")

BLE_CONNECT_MAX_TRIES = os.getenv("BLE_CONNECT_MAX_TRIES", 3)

BLE_SERVER_KEYS = os.getenv("BLE_SERVER_KEYS", []).split(" ")

BLE_DEVICES = []
for server in BLE_SERVER_KEYS:
    BLE_DEVICES.append(
        BLEDevice(
            os.getenv(f"{server.upper()}_NAME"),
            os.getenv(f"{server.upper()}_ADDRESS"),
            os.getenv(f"{server.upper()}_COLLECTOR_FUNCTIONS").split(" "),
            BLE_CONNECT_MAX_TRIES
        )
    )
