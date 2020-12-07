import collections as col
import logging
import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

logger = logging.getLogger("Collector")

BLEServer = col.namedtuple('BLEServer', "name address functions")

BLE_SERVER_KEYS = os.getenv("BLE_SERVER_KEYS", []).split(" ")

BLE_SERVERS = []
for server in BLE_SERVER_KEYS:
    BLE_SERVERS.append(
        BLEServer(
            os.getenv(f"{server.upper()}_NAME"),
            os.getenv(f"{server.upper()}_ADDRESS"),
            os.getenv(f"{server.upper()}_COLLECTOR_FUNCTIONS").split(" "),
        )
    )

BLE_CONNECT_MAX_TRIES = os.getenv("BLE_CONNECT_MAX_TRIES", 3)
