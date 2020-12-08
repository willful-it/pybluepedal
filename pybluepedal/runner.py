import logging
import queue

import pybluepedal.settings as settings
from pybluepedal.collectors import run_collector_in_thread
from pybluepedal.dispacher import Dispatcher

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s")

logger = logging.getLogger("Runner")


def run():
    event_queue = queue.Queue()  # queue to write/read events
    stop_queue = queue.Queue()  # queue to signal threads to stop

    threads = []

    logger.info("starting the event dispatcher...")
    dispacher = Dispatcher(event_queue, stop_queue)
    dispacher_thread = dispacher.run_in_thread()
    threads.append(dispacher_thread)

    logger.info("starting collector threads...")
    devices = []
    for device in settings.BLE_DEVICES:
        device.connect()
        devices.append(device)

        for collector_function in device.functions:
            collector_thread = run_collector_in_thread(
                collector_function,
                device,
                event_queue,
                stop_queue)
            threads.append(collector_thread)

    logger.info("waiting threads to finish...")
    for thread in threads:
        thread.join()

    logger.info("disconnecting devices...")
    for device in devices:
        device.disconnect()


if __name__ == "__main__":
    run()
