import collections as col

from bluepy import btle
from bluepy.btle import ADDR_TYPE_RANDOM, DefaultDelegate, Peripheral

from conversion import byte_array_to_int

OnOffNotification = col.namedtuple('EnableNotification', ['on', 'off'])

measurement_notification = OnOffNotification(b"\x01\x00", b"\x00\x00")


class CSCService:
    UUID = "00001816"
    CHARACTERISTIC_MEASUREMENT = "00002a5b"
    CHARACTERISTIC_FEATURE = "00002a5c"
    CHARACTERISTIC_SENSOR_LOCATION = "00002a5d"

    ENABLE_NOTIFICATION_VALUE = (0x01, 0x00)

    FEATURE_CRANK_REVOLUTION_DATA = "FEATURE_CRANK_REVOLUTION_DATA"
    FEATURE_WHEEL_REVOLUTION_DATA = "FEATURE_WHEEL_REVOLUTION_DATA"
    FEATURE_MULTIPLE_SENSOR_LOCATIONS = "FEATURE_MULTIPLE_SENSOR_LOCATIONS"

    CSC_FEATURES_MASK = {
        0b00000001: FEATURE_CRANK_REVOLUTION_DATA,
        0b00000010: FEATURE_WHEEL_REVOLUTION_DATA,
        0b00000100: FEATURE_MULTIPLE_SENSOR_LOCATIONS,
    }

    CSC_FEATURES = {v: k for k, v in CSC_FEATURES_MASK.items()}

    def __init__(self, peripheral: Peripheral):
        self.__peripheral = peripheral
        self.__service = self.__peripheral.getServiceByUUID(CSCService.UUID)

    def supports_feature(self, name: str) -> bool:
        """Returns true if the feature is supported"""

        characteristics = self.__service.getCharacteristics(
            forUUID=CSCService.CHARACTERISTIC_FEATURE)

        if len(characteristics) < 1:
            return False

        characteristic = characteristics[0]
        val = byte_array_to_int(characteristic.read())

        return CSCService.CSC_FEATURES[name] & val > 0

    def supports_crank_revolution(self) -> bool:
        """True if the CSCService.FEATURE_CRANK_REVOLUTION_DATA is supported"""

        return self.supports_feature(CSCService.FEATURE_CRANK_REVOLUTION_DATA)

    def supports_wheel_revolution(self) -> bool:
        """True if the CSCService.FEATURE_WHEEL_REVOLUTION_DATA is supported"""

        return self.supports_feature(CSCService.FEATURE_WHEEL_REVOLUTION_DATA)

    def supports_multiple_sensor_locations(self) -> bool:
        """True if the CSCService.FEATURE_MULTIPLE_SENSOR_LOCATIONS is supported"""

        return self.supports_feature(CSCService.FEATURE_MULTIPLE_SENSOR_LOCATIONS)

    def start_notifications(self, delegate: DefaultDelegate):
        """Starts the notifications for the characteristic measurement"""

        self.__peripheral.setDelegate(delegate)

        characteristics = self.__service.getCharacteristics(
            forUUID=CSCService.CHARACTERISTIC_MEASUREMENT)

        characteristic = characteristics[0]

        resp = self.__peripheral.writeCharacteristic(
            characteristic.getHandle() + 1, measurement_notification.on, True)

        print(f"notify resp = {resp}")


class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        values = bytearray(data)

        cumulative_wheel_revolutions = byte_array_to_int(bytes(values[1:5]))
        last_wheel_event_time = byte_array_to_int(bytes(values[5:7]))
        cumulative_crank_revolutions = byte_array_to_int(bytes(values[7:9]))
        last_crank_event_time = byte_array_to_int(bytes(values[9:]))

        print(f"{cHandle}")
        print(f"> wheel_revolutions: {cumulative_wheel_revolutions}")
        print(f"> last_wheel_event_time: {last_wheel_event_time}")
        print(f"> crank_revolutions: {cumulative_crank_revolutions}")
        print(f"> last_crank_event_time: {last_crank_event_time}")


device_address = "F1:80:A8:A8:3A:0F"

print("Connecting...")
dev = btle.Peripheral(device_address, addrType=ADDR_TYPE_RANDOM)

service = CSCService(dev)
print(service.supports_crank_revolution())
print(service.supports_wheel_revolution())
print(service.supports_multiple_sensor_locations())

service.start_notifications(MyDelegate())

while True:
    if dev.waitForNotifications(1.0):
        # handleNotification() was called
        continue

    print("Waiting...")

# print("Services...")
# for svc in dev.services:
#     print("---------------------------")
#     uuid = str(svc.uuid)
#     name = str(svc.uuid.getCommonName())
#     print(uuid, name)

#     print(f"Characteristics for {name}")
#     sensor = btle.UUID(uuid)

#     sensor_service = dev.getServiceByUUID(sensor)
#     for ch in sensor_service.getCharacteristics():
#         print(str(ch), str(ch.uuid), str(ch))
#         try:
#             val = ch.read()
#             print("   > Raw value", str(val), binascii.b2a_hex(val))
#         except Exception as e:
#             print("   > Error")
#             pass
#             # print(e)
