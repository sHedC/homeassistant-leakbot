"""Test the API Client."""

import pytest

from aiohttp.web import Application

from custom_components.leakbot.api import (
    LeakbotApiClient,
    LeakbotApiClientAuthenticationError,
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
