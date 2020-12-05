
import logging
import queue

from bluepy.btle import Peripheral
from pybluepedal.common.base import BaseDelegate, BaseService
from pybluepedal.common.byte_ops import byte_array_to_int

logger = logging.getLogger("CSCService")


class CSCService(BaseService):
    UUID = "00001816"
    CHARACTERISTIC_MEASUREMENT = "00002a5b"
    CHARACTERISTIC_FEATURE = "00002a5c"
    CHARACTERISTIC_SENSOR_LOCATION = "00002a5d"

    ENABLE_NOTIFICATION_VALUE = (0x01, 0x00)

    FEATURE_CRANK_DATA = "FEATURE_CRANK_DATA"
    FEATURE_WHEEL_DATA = "FEATURE_CRANK_DATA"
    FEATURE_MULTIPLE_SENSOR_LOCATIONS = "FEATURE_MULTIPLE_SENSOR_LOCATIONS"

    CSC_FEATURES_MASK = {
        0b00000001: FEATURE_CRANK_DATA,
        0b00000010: FEATURE_WHEEL_DATA,
        0b00000100: FEATURE_MULTIPLE_SENSOR_LOCATIONS,
    }

    CSC_FEATURES = {v: k for k, v in CSC_FEATURES_MASK.items()}

    def __init__(self, peripheral: Peripheral):
        super().__init__(peripheral, CSCService.UUID)

    def supports_feature(self, name: str) -> bool:
        """Returns true if the feature is supported"""

        characteristics = self._service.getCharacteristics(
            forUUID=CSCService.CHARACTERISTIC_FEATURE)

        if len(characteristics) < 1:
            return False

        characteristic = characteristics[0]
        val = byte_array_to_int(characteristic.read())

        return CSCService.CSC_FEATURES[name] & val > 0

    def supports_crank_revolution(self) -> bool:
        """True if the CSCService.FEATURE_CRANK_REVOLUTION_DATA is supported"""

        return self.supports_feature(CSCService.FEATURE_CRANK_DATA)

    def supports_wheel_revolution(self) -> bool:
        """True if the CSCService.FEATURE_WHEEL_REVOLUTION_DATA is supported"""

        return self.supports_feature(CSCService.FEATURE_WHEEL_DATA)

    def supports_multiple_sensor_locations(self) -> bool:
        """
        True if the CSCService.FEATURE_MULTIPLE_SENSOR_LOCATIONS
        is supported
        """

        return self.supports_feature(
            CSCService.FEATURE_MULTIPLE_SENSOR_LOCATIONS)

    def start_notifications(self, delegate: BaseDelegate):
        """Starts the notifications for the characteristic measurement"""

        self._peripheral.setDelegate(delegate)

        characteristics = self._service.getCharacteristics(
            forUUID=CSCService.CHARACTERISTIC_MEASUREMENT)

        characteristic = characteristics[0]

        resp = self._peripheral.writeCharacteristic(
            characteristic.getHandle() + 1, b"\x01\x00", True)

        logger.debug(f"notification started: {resp}")


class CSCDelegate(BaseDelegate):
    def __init__(self, producer_queue: queue.Queue):
        super().__init__(self, producer_queue)

        self._producer_queue = producer_queue

    def handleNotification(self, cHandle, data):
        logger.debug(f"handing notification {cHandle} {data}")

        values = bytearray(data)

        cumulative_wheel_revolutions = byte_array_to_int(bytes(values[1:5]))
        last_wheel_event_time = byte_array_to_int(bytes(values[5:7]))
        cumulative_crank_revolutions = byte_array_to_int(bytes(values[7:9]))
        last_crank_event_time = byte_array_to_int(bytes(values[9:]))

        data = {
            "type": "CSC",
            "handle": cHandle,
            "cumulative_wheel_revolutions": cumulative_wheel_revolutions,
            "last_wheel_event_time": last_wheel_event_time,
            "cumulative_crank_revolutions": cumulative_crank_revolutions,
            "last_crank_event_time": last_crank_event_time,
        }

        self._producer_queue.put(data)
        logger.debug(f"added to queue {data}")
