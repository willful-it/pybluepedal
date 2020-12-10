import logging
import queue
import threading
import time

logger = logging.getLogger("Dispatcher")


class Dispatcher():
    """Dispatcher to write events to logs"""

    def __init__(self, event_queue: queue.Queue, stop_queue: queue.Queue):
        self.__event_queue = event_queue
        self.__stop_queue = stop_queue

    def run(self, sleep_time: int = 1) -> None:
        """Runs the dispatcher

        Args:
            sleep_time (int, optional):
                Sleep time in seconds to check the
                event queue for data. Defaults to 1.
        """
        logger.info("starting dispatcher")

        while True:
            while not self.__event_queue.empty():
                item = self.__event_queue.get()
                logger.debug(f"processing {item}")

            if not self.__stop_queue.empty():
                logger.debug("stopping...")
                break

            logger.debug("waiting for data...")
            time.sleep(sleep_time)

        logger.info("finish dispacher")

    def run_in_thread(self, sleep_time: int = 1) -> threading.Thread:
        """Runs the dispatcher in a thread

        Returns:
            threading.Thread: The started thread
        """
        thread = threading.Thread(target=self.run, args=(sleep_time, ))
        thread.start()

        return thread
