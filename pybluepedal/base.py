

from bluepy.btle import Peripheral


class BaseService:
    def __init__(self, peripheral: Peripheral, service_uuid: str):
        self._peripheral = peripheral
        self._service = self._peripheral.getServiceByUUID(service_uuid)
