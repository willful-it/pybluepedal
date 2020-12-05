import logging
import queue
import threading
import time

from bluepy.btle import ADDR_TYPE_RANDOM, Peripheral

from pybluepedal.services.cycling_speed_cadence import CSCDelegate, CSCService
from pybluepedal.services.heart_rate import HeartRateDelegate, HeartRateService

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


def hrm_listener(
        producer_queue: queue.Queue,
        stop_queue: queue.Queue):

    device_address = "C4:DB:A6:DC:51:5A"
    logger.info(f"connecting to heart rate monitor: {device_address}")
    hrm_device = Peripheral(device_address, addrType=ADDR_TYPE_RANDOM)
    hrm_service = HeartRateService(hrm_device)
    hrm_service.start_notifications(HeartRateDelegate(producer_queue))

    device_address = "F1:80:A8:A8:3A:0F"

    while stop_queue.empty():
        hrm_device.waitForNotifications(1.0)

    hrm_device.disconnect()
    logger.info("heart rate monitor device disconnected")


def trainer_listener(
        producer_queue: queue.Queue,
        stop_queue: queue.Queue):

    device_address = "F1:80:A8:A8:3A:0F"
    logger.info(f"connecting to smart trainer: {device_address}")
    csc_device = Peripheral(device_address, addrType=ADDR_TYPE_RANDOM)
    csc_service = CSCService(csc_device)
    csc_service.start_notifications(CSCDelegate(producer_queue))

    while stop_queue.empty():
        csc_device.waitForNotifications(1.0)

    csc_device.disconnect()
    logger.info("smart trainer disconnected")


def run():
    producer_queue = queue.Queue()
    stop_queue = queue.Queue()

    threads = []
    thread = threading.Thread(
        target=dispacher,
        args=(producer_queue, stop_queue,))
    thread.start()
    threads.append(thread)

    thread = threading.Thread(
        target=trainer_listener,
        args=(producer_queue, stop_queue,))
    thread.start()
    threads.append(thread)

    thread = threading.Thread(
        target=hrm_listener,
        args=(producer_queue, stop_queue,))
    thread.start()
    threads.append(thread)

    input("press any key to stop...")
    stop_queue.put("stop")

    logger.info("waiting threads to finish...")
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    run()
