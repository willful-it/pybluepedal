import logging
import queue

from pybluepedal.device import PedalDevice
from pybluepedal.services.cycling_speed_cadence import CSCDelegate, CSCService
from pybluepedal.services.heart_rate import HeartRateDelegate, HeartRateService

logger = logging.getLogger("Collector")


def hrm_collector(
        device: PedalDevice,
        producer_queue: queue.Queue,
        stop_queue: queue.Queue):

    device.run_collector(
        HeartRateService,
        HeartRateDelegate,
        producer_queue,
        stop_queue)


def csc_collector(
        device: PedalDevice,
        producer_queue: queue.Queue,
        stop_queue: queue.Queue):

    device.run_collector(
        CSCService,
        CSCDelegate,
        producer_queue,
        stop_queue)
