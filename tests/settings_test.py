import os

from pybluepedal.settings import Settings


def test_should_load_connect_max_retries():

    # arrange
    value = "42"
    os.environ["BLE_CONNECT_MAX_TRIES"] = value

    # act
    settings = Settings()

    # assert
    assert settings.BLE_CONNECT_MAX_TRIES == int(value)


def test_should_load_ble_server_keys():

    # arrange
    value = "HRM SMART_TRAINER"
    os.environ["BLE_SERVER_KEYS"] = value

    # act
    settings = Settings()

    # assert
    assert " ".join(settings.BLE_SERVER_KEYS) == value


def test_should_load_ble_devices():

    # arrange
    devices = "DEV1 DEV2"
    os.environ["BLE_SERVER_KEYS"] = devices

    os.environ["DEV1_NAME"] = "ZCycle Pro Trainer"
    os.environ["DEV1_ADDRESS"] = "F1:80:A8:A8:3A:0F"
    os.environ["DEV1_COLLECTOR_FUNCTIONS"] = "collectors.csc_collector"

    os.environ["DEV2_NAME"] = "ZCycle Pro Trainer 2"
    os.environ["DEV2_ADDRESS"] = "F1:80:A8:A8:3A:0F 2"
    os.environ["DEV2_COLLECTOR_FUNCTIONS"] = "collectors.csc_collector_2"

    # act
    settings = Settings()

    # assert
    assert len(settings.BLE_DEVICES) == 2

    ble_dev1 = settings.BLE_DEVICES[0]
    assert ble_dev1.name == os.environ["DEV1_NAME"]
    assert ble_dev1.address == os.environ["DEV1_ADDRESS"]
    assert ble_dev1.functions[0] == os.environ["DEV1_COLLECTOR_FUNCTIONS"]

    ble_dev2 = settings.BLE_DEVICES[1]
    assert ble_dev2.name == os.environ["DEV2_NAME"]
    assert ble_dev2.address == os.environ["DEV2_ADDRESS"]
    assert ble_dev2.functions[0] == os.environ["DEV2_COLLECTOR_FUNCTIONS"]
