
import queue

from bluepy.btle import DefaultDelegate, Peripheral


class BaseService:
    def __init__(self, peripheral: Peripheral, service_uuid: str):
        self._peripheral = peripheral
        self._service = self._peripheral.getServiceByUUID(service_uuid)


class BaseDelegate(DefaultDelegate):
    def __init__(self, producer_queue: queue.Queue):
        super().__init__(self)

        self._producer_queue = producer_queue
