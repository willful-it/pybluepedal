import importlib
import logging
import queue
import threading

from pybluepedal.device import BLEDevice
from pybluepedal.services.cycling_speed_cadence import CSCDelegate, CSCService
from pybluepedal.services.heart_rate import HeartRateDelegate, HeartRateService

logger = logging.getLogger("Collector")


def load_collector(collector_func: str) -> tuple:

    # collector is in the <module>.<function> format
    collector = collector_func.split(".")

    collector_module_name = importlib.import_module(collector[0])
    collector_func_name = collector[1]

    return collector_module_name, collector_func_name


def run_collector_in_thread(
        collector_func,
        device: BLEDevice,
        event_queue: queue.Queue,
        stop_queue: queue.Queue) -> threading.Thread:

    collector_module_name, collector_func_name = load_collector(collector_func)

    target = getattr(collector_module_name, str(collector_func_name))
    target_args = (device, event_queue, stop_queue,)

    thread = threading.Thread(target=target, args=target_args)
    thread.start()

    return thread


def hrm_collector(
        device: BLEDevice,
        event_queue: queue.Queue,
        stop_queue: queue.Queue):

    device.run_collector(
        HeartRateService,
        HeartRateDelegate,
        event_queue,
        stop_queue)


def csc_collector(
        device: BLEDevice,
        event_queue: queue.Queue,
        stop_queue: queue.Queue):

    device.run_collector(
        CSCService,
        CSCDelegate,
        event_queue,
        stop_queue)
