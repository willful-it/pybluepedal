import logging
import queue
import threading
import time

import pybluepedal.collectors as collectors
import pybluepedal.settings as settings

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s")

logger = logging.getLogger("Dispatcher")


def dispacher(producer_queue: queue.Queue, stop_queue: queue.Queue):
    logger.info("starting consumer")

    while stop_queue.empty():
        while not producer_queue.empty():
            item = producer_queue.get()
            logger.debug(f"processing {item}")

        logger.debug("waiting for data...")
        time.sleep(5)

    logger.info("finish consumer")


def call_collector(
        ble_server: settings.BLEServer,
        producer_queue: queue.Queue,
        stop_queue: queue.Queue):

    method_to_call = getattr(collectors, str(ble_server.function))
    method_to_call(ble_server, producer_queue, stop_queue)


def run():
    producer_queue = queue.Queue()
    stop_queue = queue.Queue()

    threads = []

    logger.info("starting dispatcher thread")
    thread = threading.Thread(
        target=dispacher,
        args=(producer_queue, stop_queue,))
    thread.start()
    threads.append(thread)

    for ble_server in settings.BLE_SERVERS:
        logger.info(f"starting {ble_server.name}")
        thread = threading.Thread(
            target=call_collector,
            args=(ble_server, producer_queue, stop_queue,))
        thread.start()
        threads.append(thread)

    input("press any key to stop...")
    stop_queue.put("stop")

    logger.info("waiting threads to finish...")
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    run()
