"""Test the API Client."""

import pytest

from aiohttp import ClientSession

from custom_components.leakbot.api import (
    LeakbotApiClient,
    LeakbotApiClientAuthenticationError,
    LeakbotApiClientTokenError,
)


async def test_setup(leakbot_api_client: LeakbotApiClient):
    """Test the API Setup."""
    assert leakbot_api_client is not None


async def test_login_fail(leakbot_session: ClientSession):
    """Test the API Login Failure."""
    api = LeakbotApiClient("wrong", "creds", leakbot_session)
    with pytest.raises(LeakbotApiClientAuthenticationError):
        await api.login()


async def test_login_pass(leakbot_api_client: LeakbotApiClient):
    """Test API Login Success."""
    result = await leakbot_api_client.login()

    assert leakbot_api_client.is_connected
    assert result["token"]
    assert result["tenant_id"]


async def test_token_error(leakbot_api_client: LeakbotApiClient):
    """Test the API Token Error."""
    result = await leakbot_api_client.login()
    assert leakbot_api_client.is_connected
    assert result["token"]
    assert result["tenant_id"]

    leakbot_api_client._token = "INVALID"
    with pytest.raises(LeakbotApiClientTokenError):
        await leakbot_api_client.get_device_list()


async def test_device_list(leakbot_api_client: LeakbotApiClient):
    """Test getting the device list."""
    await leakbot_api_client.login()
    assert leakbot_api_client.is_connected

    device_list = await leakbot_api_client.get_device_list()
    assert device_list


async def test_account_myread(leakbot_api_client: LeakbotApiClient):
    """Test getting the account data."""
    await leakbot_api_client.login()
    assert leakbot_api_client.is_connected

    account_myread = await leakbot_api_client.get_account_myread()
    assert account_myread


async def test_address_myread(leakbot_api_client: LeakbotApiClient):
    """Test getting the account data."""
    await leakbot_api_client.login()
    assert leakbot_api_client.is_connected

    address_myread = await leakbot_api_client.get_address_myread()
    assert address_myread


async def test_tenant_myview(leakbot_api_client: LeakbotApiClient):
    """Test getting the account data."""
    await leakbot_api_client.login()
    assert leakbot_api_client.is_connected

    tenant = await leakbot_api_client.get_tenant_myview()
    assert tenant


async def test_device_myview(leakbot_api_client: LeakbotApiClient):
    """Test getting the device data."""
    await leakbot_api_client.login()
    assert leakbot_api_client.is_connected

    devices = await leakbot_api_client.get_device_list()
    assert devices

    for device in devices["IDs"]:
        device_data = await leakbot_api_client.get_device_data(device["id"])
        assert device_data


async def test_device_messages(leakbot_api_client: LeakbotApiClient):
    """Test getting the device mesages list."""
    await leakbot_api_client.login()
    assert leakbot_api_client.is_connected

    devices = await leakbot_api_client.get_device_list()
    assert devices

    for device in devices["IDs"]:
        device_data = await leakbot_api_client.get_device_messages(device["id"])
        assert device_data


async def test_device_simpleeventlist(leakbot_api_client: LeakbotApiClient):
    """Test getting the device simple event list."""
    await leakbot_api_client.login()
    assert leakbot_api_client.is_connected

    devices = await leakbot_api_client.get_device_list()
    assert devices

    for device in devices["IDs"]:
        device_data = await leakbot_api_client.get_device_messages(device["id"])
        assert device_data

        alert_msg = False
        for event in device_data["list"]["record"]:
            if event["msg_type"] == "9" and event["event_type"] == "2":
                alert_msg = True
                break

        if alert_msg:
            starting_date = "2025-04-11 08:00:00"
            event_data = await leakbot_api_client.get_device_simple_event_list(
                device["id"], starting_date
            )
            assert event_data


async def test_device_waterusage(leakbot_api_client: LeakbotApiClient):
    """Test getting the device water usage."""
    await leakbot_api_client.login()
    assert leakbot_api_client.is_connected

    devices = await leakbot_api_client.get_device_list()
    assert devices

    for device in devices["IDs"]:
        device_data = await leakbot_api_client.get_device_water_usage(device["id"], 0)
        assert device_data
