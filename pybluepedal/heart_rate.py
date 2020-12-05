import logging
import queue

from bluepy.btle import DefaultDelegate, Peripheral

from pybluepedal.base import BaseService
from pybluepedal.byte_ops import check_bit_l2r

logger = logging.getLogger("HeartRateService")


class HeartRateService(BaseService):
    UUID = "0000180d"
    CHARACTERISTIC_MEASUREMENT = "00002a37"

    def __init__(self, peripheral: Peripheral):
        super().__init__(peripheral, HeartRateService.UUID)

    def start_notifications(self, delegate: DefaultDelegate):
        """Starts the notifications for the characteristic measurement"""

        logger.debug("starting notification")

        self._peripheral.setDelegate(delegate)

        characteristics = self.__service.getCharacteristics(
            forUUID=HeartRateService.CHARACTERISTIC_MEASUREMENT)

        characteristic = characteristics[0]

        resp = self._peripheral.writeCharacteristic(
            characteristic.getHandle() + 1, b"\x01\x00", True)

        logger.debug(f"notification started: {resp}")


class HeartRateDelegate(DefaultDelegate):
    def __init__(self, producer_queue: queue.Queue):
        DefaultDelegate.__init__(self)

        self.__producer_queue = producer_queue

    def handleNotification(self, cHandle, data):
        logger.debug(f"handing notification {cHandle} {data}")

        values = list(bytearray(data))
        flag_field = values[0]
        logger.debug(f"flag field {bin(flag_field)}")

        if not check_bit_l2r(flag_field, 0):
            data = {
                "type": "HeartRate",
                "handle": cHandle,
                "value": values[1]
            }
        else:
            data = {
                "type": "HeartRate",
                "handle": cHandle,
                "value": values[1:]
            }

        self.__producer_queue.put(data)
        logger.debug(f"added to queue {data}")
