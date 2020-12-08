import logging
import queue

from bluepy.btle import ADDR_TYPE_RANDOM, BTLEDisconnectError, Peripheral

logger = logging.getLogger("Collector")


class BLEDevice:

    def __init__(self,
                 name: str,
                 address: str,
                 functions: list,
                 max_connect_retries: int = 3):

        self.name = name
        self.address = address
        self.functions = functions
        self.address_type = ADDR_TYPE_RANDOM
        self.max_connect_retries = max_connect_retries

    def connect(self, attempt: int = 1):

        logger.info(f"connecting to {self.address} "
                    f"(attempt {attempt})")
        try:
            self.__peripheral = Peripheral(self.address,
                                           addrType=self.address_type)
            return self.__peripheral

        except BTLEDisconnectError as error:
            logger.error("error connecting to "
                         f"{self.address}: {error}")

            if attempt == self.max_connect_retries:
                logger.error("max connect attempts reach for device "
                             f"{self.address}")
                return None

            logger.info(f"trying to connect again to {self.address}")
            self.connect(self.address,
                         self.address_type,
                         attempt + 1)

    def run_collector(
            self,
            service_cls,
            delegate_cls,
            event_queue: queue.Queue,
            stop_queue: queue.Queue):

        logger.info(f"running collector for {self.name}: "
                    f"{self.address}")

        service = service_cls(self.__peripheral)
        delegate = delegate_cls(event_queue)
        service.start_notifications(delegate)

        while stop_queue.empty():
            try:

                self.__peripheral.waitForNotifications(1.0)

            except BTLEDisconnectError as error:
                logger.error(
                    f"device {self.address} disconneted "
                    f"unexpectedly: {error}")

                logger.info(
                    "trying to recover disconnect "
                    f"from {self.address}")

                device = self.connect()
                if not device:
                    logger.info(
                        f"could recover device {self.address} "
                        "connection - quitting")
                    return

    def disconnect(self):
        self.__peripheral.disconnect()
