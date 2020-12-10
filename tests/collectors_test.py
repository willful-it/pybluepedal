"""Tests for the collectors module"""

import queue

import pytest
from pybluepedal.collectors import csc_collector, hrm_collector, load_collector
from pybluepedal.device import BLEDevice
from pybluepedal.services.cycling_speed_cadence import CSCDelegate, CSCService
from pybluepedal.services.heart_rate import HeartRateDelegate, HeartRateService


def test_should_be_able_to_load_collector():
    # arrange
    collector_func = "pybluepedal.collectors.hrm_collector"

    # act
    collector_module, collector_func_name = load_collector(collector_func)

    # assert
    assert collector_module.__name__ == "pybluepedal.collectors"
    assert collector_func_name == "hrm_collector"


def test_should_raise_error_if_collector_name_is_invalid():
    # arrange
    collector_func = "hrm_collector"

    # act & assert
    with pytest.raises(ValueError):
        load_collector(collector_func)


def test_should_run_hrm_collector_with_the_right_parameters(mocker):
    # arrange
    event_queue = queue.Queue()
    stop_queue = queue.Queue()

    mocker.patch.object(BLEDevice, "run_collector")
    device = BLEDevice("dummy_name", "dummy_address", [])

    # act
    hrm_collector(device, event_queue, stop_queue)

    # assert
    BLEDevice.run_collector.assert_called_once_with(
        HeartRateService,
        HeartRateDelegate,
        event_queue,
        stop_queue
    )


def test_should_run_csc_collector_with_the_right_parameters(mocker):
    # arrange
    event_queue = queue.Queue()
    stop_queue = queue.Queue()

    mocker.patch.object(BLEDevice, "run_collector")
    device = BLEDevice("dummy_name", "dummy_address", [])

    # act
    csc_collector(device, event_queue, stop_queue)

    # assert
    BLEDevice.run_collector.assert_called_once_with(
        CSCService,
        CSCDelegate,
        event_queue,
        stop_queue
    )
