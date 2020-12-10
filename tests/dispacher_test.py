"""Tests for the dispacher module"""

import queue

from pybluepedal.dispacher import Dispatcher


def test_should_empty_queue_after_data_is_sent():
    event_queue = queue.Queue()
    for e in [1, 2, 3, 4]:
        event_queue.put(e)

    stop_queue = queue.Queue()
    stop_queue.put(1)

    dispacher = Dispatcher(event_queue, stop_queue)
    dispacher.run()

    assert event_queue


def test_should_run_in_thread():
    event_queue = queue.Queue()
    stop_queue = queue.Queue()

    dispacher = Dispatcher(event_queue, stop_queue)
    thread = dispacher.run_in_thread(0)

    assert thread
    assert thread.is_alive()

    stop_queue.put(1)
    thread.join(10)
    assert not thread.is_alive()
