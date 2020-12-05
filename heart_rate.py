import collections as col

from bluepy.btle import ADDR_TYPE_RANDOM, DefaultDelegate, Peripheral

from conversion import byte_array_to_int

OnOffNotification = col.namedtuple('EnableNotification', ['on', 'off'])

measurement_notification = OnOffNotification(b"\x01\x00", b"\x00\x00")


class HRService:
    UUID = "0000180d"
    CHARACTERISTIC_MEASUREMENT = "00002a37"

    ENABLE_NOTIFICATION_VALUE = (0x01, 0x00)

    def __init__(self, peripheral: Peripheral):
        self.__peripheral = peripheral
        self.__service = self.__peripheral.getServiceByUUID(HRService.UUID)

    def start_notifications(self, delegate: DefaultDelegate):
        """Starts the notifications for the characteristic measurement"""

        self.__peripheral.setDelegate(delegate)

        characteristics = self.__service.getCharacteristics(
            forUUID=HRService.CHARACTERISTIC_MEASUREMENT)

        characteristic = characteristics[0]

        resp = self.__peripheral.writeCharacteristic(
            characteristic.getHandle() + 1, measurement_notification.on, True)

        print(f"notify resp = {resp}")


def check_bitL2R(byte, bit):
    return bool(byte & (0b10000 >> bit))


class MyDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        print("---->")
        print(f"{cHandle} {data}")

        values = list(bytearray(data))
        print(f"number of values: {len(values)}")
        print(f"values: {values}")

        flag_field = values[0]
        print(f"{bin(flag_field)}")

        print(f"check_bitL2R(flag_field, 0) = {check_bitL2R(flag_field, 0)}")
        if not check_bitL2R(flag_field, 0):
            print("uint8 value")
            print(f"> hr: {values[1]}")
        else:
            print("uint16 value")
            print(f"> hr: {byte_array_to_int(values[1:3])}")


device_address = "C4:DB:A6:DC:51:5A"

print("Connecting...")
dev = Peripheral(device_address, addrType=ADDR_TYPE_RANDOM)

service = HRService(dev)

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
