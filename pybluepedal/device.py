import logging
import queue

from bluepy.btle import ADDR_TYPE_RANDOM, BTLEDisconnectError, Peripheral

import pybluepedal.settings as settings

logger = logging.getLogger("Collector")


class PedalDevice:

    def __init__(self,
                 device_address: str,
                 device_name: str,
                 address_type: str = ADDR_TYPE_RANDOM):

        self.__device_address = device_address
        self.__device_name = device_name
        self.__address_type = address_type

    @property
    def name(self) -> str:
        return self.__device_name

    def connect(self, attempt: int = 1):

        logger.info(f"connecting to {self.__device_address} "
                    f"(attempt {attempt})")
        try:
            self.__peripheral = Peripheral(self.__device_address,
                                           addrType=self.__address_type)
            return self.__peripheral

        except BTLEDisconnectError as error:
            logger.error("error connecting to "
                         f"{self.__device_address}: {error}")

            if attempt == settings.BLE_CONNECT_MAX_TRIES:
                logger.error("max connect attempts reach for device "
                             f"{self.__device_address}")
                return None

            logger.info(f"trying to connect again to {self.__device_address}")
            self.connect(self.__device_address,
                         self.__address_type,
                         attempt + 1)

    def run_collector(
            self,
            service_cls,
            delegate_cls,
            producer_queue: queue.Queue,
            stop_queue: queue.Queue):

        logger.info(f"connecting to {self.__device_name}: "
                    f"{self.__device_address}")

        service = service_cls(self.__peripheral)
        delegate = delegate_cls(producer_queue)
        service.start_notifications(delegate)

        while stop_queue.empty():
            try:

                self.__peripheral.waitForNotifications(1.0)

            except BTLEDisconnectError as error:
                logger.error(
                    f"device {self.__device_address} disconneted "
                    f"unexpectedly: {error}")
                logger.info(
                    "trying to recover from disconnect "
                    f"from {self.__device_address}")

                device = self.connect()
                if not device:
                    logger.info(
                        f"could recover device {self.__device_address} "
                        "connection - quitting")
                    return

    def disconnect(self):
        self.__peripheral.disconnect()
