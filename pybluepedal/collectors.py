import logging
import queue

from bluepy.btle import ADDR_TYPE_RANDOM, BTLEDisconnectError, Peripheral

import pybluepedal.settings as settings
from pybluepedal.services.cycling_speed_cadence import CSCDelegate, CSCService
from pybluepedal.services.heart_rate import HeartRateDelegate, HeartRateService

logger = logging.getLogger("Collector")


def connect(device_address: str, address_type: str, attempt: int = 1):

    logger.info(f"connecting to {device_address} (attempt {attempt})")

    try:

        return Peripheral(device_address, addrType=address_type)

    except BTLEDisconnectError as error:
        logger.error(f"error connecting to {device_address}: {error}")
        if attempt == settings.BLE_CONNECT_MAX_TRIES:
            logger.error("max connect attempts reach for device "
                         f"{device_address}")
            return None

        logger.info(f"trying to connect again to {device_address}")
        connect(device_address, address_type, attempt + 1)


def collector(
        ble_server: settings.BLEServer,
        service_cls,
        delegate_cls,
        producer_queue: queue.Queue,
        stop_queue: queue.Queue):

    device_address = ble_server.address
    logger.info(f"connecting to {ble_server.name}: {device_address}")

    # connects to device
    device = connect(device_address, ADDR_TYPE_RANDOM)
    if not device:
        logger.info(f"could not connect to {device_address} - quitting")
        return

    service = service_cls(device)
    delegate = delegate_cls(producer_queue)
    service.start_notifications(delegate)

    while stop_queue.empty():
        try:

            device.waitForNotifications(1.0)

        except BTLEDisconnectError as error:
            logger.error(
                f"device {device_address} disconneted unexpectedly: {error}")
            logger.info(
                f"trying to recover from disconnect from {device_address}")

            device = connect(device_address, ADDR_TYPE_RANDOM)
            if not device:
                logger.info(
                    "could recover device "
                    f" {device_address} connection - quitting")
                return

    device.disconnect()
    logger.info("heart rate monitor device disconnected")


def hrm_collector(
        ble_server: settings.BLEServer,
        producer_queue: queue.Queue,
        stop_queue: queue.Queue):

    collector(ble_server,
              HeartRateService,
              HeartRateDelegate,
              producer_queue,
              stop_queue)


def trainer_collector(
        ble_server: settings.BLEServer,
        producer_queue: queue.Queue,
        stop_queue: queue.Queue):

    collector(ble_server,
              CSCService,
              CSCDelegate,
              producer_queue,
              stop_queue)
