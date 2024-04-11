"""Test the API Client."""

import pytest

from aiohttp.web import Application

from custom_components.leakbot.api import (
    LeakbotApiClient,
    LeakbotApiClientAuthenticationError,
    LeakbotApiClientTokenError,
)

from .conftest import ClientSessionGenerator, VALID_LOGIN


async def test_setup(leakbot_api: Application, aiohttp_client: ClientSessionGenerator):
    """Test the API Setup."""
    session = await aiohttp_client(leakbot_api)
    api = LeakbotApiClient("none", "none", session)
    assert api is not None


async def test_login_fail(
    leakbot_api: Application, aiohttp_client: ClientSessionGenerator
):
    """Test the API Login Failure."""
    session = await aiohttp_client(leakbot_api)
    api = LeakbotApiClient("none", "none", session)

    with pytest.raises(LeakbotApiClientAuthenticationError):
        await api.login()


async def test_login_pass(
    leakbot_api: Application, aiohttp_client: ClientSessionGenerator
):
    """Test API Login Success."""
    session = await aiohttp_client(leakbot_api)
    api = LeakbotApiClient(VALID_LOGIN["username"], VALID_LOGIN["password"], session)

    result = await api.login()
    assert api.is_connected
    assert result["token"]
    assert result["tenant_id"]


async def test_token_error(
    leakbot_api: Application, aiohttp_client: ClientSessionGenerator
):
    """Test the API Token Error."""
    session = await aiohttp_client(leakbot_api)
    api = LeakbotApiClient(VALID_LOGIN["username"], VALID_LOGIN["password"], session)

    result = await api.login()
    assert api.is_connected
    assert result["token"]
    assert result["tenant_id"]

    api._token = "INVALID"
    with pytest.raises(LeakbotApiClientTokenError):
        await api.get_device_list()


async def test_device_list(
    leakbot_api: Application, aiohttp_client: ClientSessionGenerator
):
    """Test getting the device list."""
    session = await aiohttp_client(leakbot_api)
    api = LeakbotApiClient(VALID_LOGIN["username"], VALID_LOGIN["password"], session)

    await api.login()
    assert api.is_connected

    device_list = await api.get_device_list()
    assert device_list


async def test_account_myread(
    leakbot_api: Application, aiohttp_client: ClientSessionGenerator
):
    """Test getting the account data."""
    session = await aiohttp_client(leakbot_api)
    api = LeakbotApiClient(VALID_LOGIN["username"], VALID_LOGIN["password"], session)

    await api.login()
    assert api.is_connected

    account_myread = await api.get_account_myread()
    assert account_myread


async def test_address_myread(
    leakbot_api: Application, aiohttp_client: ClientSessionGenerator
):
    """Test getting the account data."""
    session = await aiohttp_client(leakbot_api)
    api = LeakbotApiClient(VALID_LOGIN["username"], VALID_LOGIN["password"], session)

    await api.login()
    assert api.is_connected

    address_myread = await api.get_address_myread()
    assert address_myread


async def test_tenant_myview(
    leakbot_api: Application, aiohttp_client: ClientSessionGenerator
):
    """Test getting the account data."""
    session = await aiohttp_client(leakbot_api)
    api = LeakbotApiClient(VALID_LOGIN["username"], VALID_LOGIN["password"], session)

    await api.login()
    assert api.is_connected

    tenant = await api.get_tenant_myview()
    assert tenant


async def test_device_myview(
    leakbot_api: Application, aiohttp_client: ClientSessionGenerator
):
    """Test getting the device data."""
    session = await aiohttp_client(leakbot_api)
    api = LeakbotApiClient(VALID_LOGIN["username"], VALID_LOGIN["password"], session)

    await api.login()
    assert api.is_connected

    devices = await api.get_device_list()
    assert devices

    for device in devices["IDs"]:
        device_data = await api.get_device_data(device["id"])
        assert device_data


async def test_device_messages(
    leakbot_api: Application, aiohttp_client: ClientSessionGenerator
):
    """Test getting the device mesages list."""
    session = await aiohttp_client(leakbot_api)
    api = LeakbotApiClient(VALID_LOGIN["username"], VALID_LOGIN["password"], session)

    await api.login()
    assert api.is_connected

    devices = await api.get_device_list()
    assert devices

    for device in devices["IDs"]:
        device_data = await api.get_device_messages(device["id"])
        assert device_data


async def test_device_waterusage(
    leakbot_api: Application, aiohttp_client: ClientSessionGenerator
):
    """Test getting the device water usage."""
    session = await aiohttp_client(leakbot_api)
    api = LeakbotApiClient(VALID_LOGIN["username"], VALID_LOGIN["password"], session)

    await api.login()
    assert api.is_connected

    devices = await api.get_device_list()
    assert devices

    for device in devices["IDs"]:
        device_data = await api.get_device_water_usage(device["id"])
        assert device_data
