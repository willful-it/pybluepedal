import logging
import queue
import threading
import time

from bluepy.btle import ADDR_TYPE_RANDOM, Peripheral

from heart_rate import HeartRateDelegate, HeartRateService

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s")

logger = logging.getLogger("PeripheralManager")


def consumer(producer_queue: queue.Queue, stop_queue: queue.Queue):
    logger.info("starting consumer")

    while stop_queue.empty():
        while not producer_queue.empty():
            item = producer_queue.get()
            logger.debug(f"processing {item}")

        logger.debug("waiting for data...")
        time.sleep(5)

    logger.info("finish consumer")


def peripheral_handling(producer_queue: queue.Queue, stop_queue: queue.Queue):

    device_address = "C4:DB:A6:DC:51:5A"

    logger.info(f"connecting to {device_address}")
    peripheral = Peripheral(device_address, addrType=ADDR_TYPE_RANDOM)
    service = HeartRateService(peripheral)
    service.start_notifications(HeartRateDelegate(producer_queue))

    while stop_queue.empty():
        peripheral.waitForNotifications(1.0)

    peripheral.disconnect()
    logger.info("finish peripheral")


producer_queue = queue.Queue()
stop_queue = queue.Queue()

threads = []
thread = threading.Thread(target=consumer,
                          args=(producer_queue, stop_queue,))
thread.start()
threads.append(thread)

thread = threading.Thread(target=peripheral_handling,
                          args=(producer_queue, stop_queue,))
thread.start()
threads.append(thread)

input("press any key to stop...")
stop_queue.put("stop")

logger.info("waiting threads to finish...")
for thread in threads:
    thread.join()
