import logging
import queue
import threading
import time

import pybluepedal.collectors as collectors
import pybluepedal.settings as settings
from pybluepedal.device import PedalDevice

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s")

logger = logging.getLogger("Dispatcher")


def _dispacher(producer_queue: queue.Queue,
               stop_queue: queue.Queue,
               sleep_time: int = 1):

    logger.info("starting consumer")

    while stop_queue.empty():
        while not producer_queue.empty():
            item = producer_queue.get()
            logger.debug(f"processing {item}")

        logger.debug("waiting for data...")
        time.sleep(sleep_time)

    logger.info("finish consumer")


def _call_collector(
        collector_func,
        device: PedalDevice,
        producer_queue: queue.Queue,
        stop_queue: queue.Queue):

    method_to_call = getattr(collectors, str(collector_func))
    method_to_call(device, producer_queue, stop_queue)


def run():
    producer_queue = queue.Queue()
    stop_queue = queue.Queue()

    threads = []

    thread = threading.Thread(_dispacher, (producer_queue, stop_queue,))
    thread.start()
    threads.append(thread)

    pedal_devices = []
    for ble_server in settings.BLE_SERVERS:
        pedal_device = PedalDevice(ble_server.address, ble_server.name)
        pedal_device.connect()

        pedal_devices.append(pedal_device)

        for func in ble_server.functions:
            thread = threading.Thread(
                target=_call_collector,
                args=(func, pedal_device, producer_queue, stop_queue,))
            thread.start()
            threads.append(thread)

    logger.info("waiting threads to finish...")
    for thread in threads:
        thread.join()

    for device in pedal_devices:
        device.disconnect()


if __name__ == "__main__":
    run()
