"""Test Configuration for the tests."""

import os
import pytest

from aiohttp.test_utils import TestClient
from aiohttp.web import Application, Request, Response
from collections.abc import Callable, Coroutine
from unittest.mock import patch

from homeassistant.core import HomeAssistant
from homeassistant.components.http.forwarded import async_setup_forwarded

from custom_components.leakbot.api import (
    API_LOGIN,
    API_ACCOUNT_MYREAD,
    API_ADDRESS_MYREAD,
    API_DEVICE_LIST,
    API_DEVICE_MYVIEW,
    API_TENANT_MYVIEW,
    API_DEVICE_MYMSG,
    API_DEVICE_WATERUSAGE,
    API_DEVICE_MYSIMPLEMSG,
)

VALID_LOGIN = {
    "username": "value_user@address.com",
    "password": "realpassword",
}


# This fixture is used to enable custom integration for testing.
@pytest.fixture(autouse=True)
def auto_enable_custom_integration(
    enable_custom_integrations,
):  # pylint: disable=unused-argument
    """Auto Enable Custom Integrations."""
    yield


# This fixture is used to prevent HomeAssistant from attempting to create and dismiss persistent
# notifications. These calls would fail without this fixture since the persistent_notification
# integration is never loaded during a test.
@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    with (
        patch("homeassistant.components.persistent_notification.async_create"),
        patch("homeassistant.components.persistent_notification.async_dismiss"),
    ):
        yield


def load_fixture(filename: str) -> str | None:
    """Load a JSON fixture for testing."""
    try:
        path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
        with open(path, encoding="utf-8") as fptr:
            return fptr.read()
    except OSError:
        return None


# ============================================================
# Mock API Functions and Class to mimic the Leakbot API.
ClientSessionGenerator = Callable[..., Coroutine[any, any, TestClient]]


@pytest.fixture(autouse=True)
def api_leakbot_rul():
    """Patch the URL Base for the leakbot api."""
    with patch("custom_components.leakbot.api.API_URL", ""):
        yield


@pytest.fixture
def aiohttp_client(aiohttp_client, socket_enabled) -> ClientSessionGenerator:  # pylint: disable=unused-argument, redefined-outer-name
    """Return aiohttp_client and allow opening sockets."""
    return aiohttp_client


@pytest.fixture
async def leakbot_api(hass: HomeAssistant) -> Application:
    """Mock the Leakbot API."""
    app = Application()
    app["hass"] = hass

    api = LeakbotAPIMock()
    app.router.add_route("POST", API_LOGIN, api.account_mylogin)
    app.router.add_route("POST", API_DEVICE_LIST, api.device_mydevicelist)
    app.router.add_route("POST", API_ACCOUNT_MYREAD, api.account_myread)
    app.router.add_route("POST", API_ADDRESS_MYREAD, api.address_myread)
    app.router.add_route("POST", API_TENANT_MYVIEW, api.tenant_myview)
    app.router.add_route("POST", API_DEVICE_MYVIEW, api.device_myview)
    app.router.add_route("POST", API_DEVICE_MYMSG, api.device_messages)
    app.router.add_route("POST", API_DEVICE_WATERUSAGE, api.device_waterusage)
    app.router.add_route("POST", API_DEVICE_MYSIMPLEMSG, api.device_simpleeventlist)

    async_setup_forwarded(app, True, [])
    return app


class LeakbotAPIMock:
    """Mock the Leakbox API class so we can test in isolation."""

    def __init__(self) -> None:
        """Initialize the Mock API."""
        self._token = "correcttoken"

    async def account_mylogin(self, request: Request) -> Response:
        """Mock API for logging in."""
        data = await request.json()

        if (
            data["username"] == VALID_LOGIN["username"]
            and data["password"] == VALID_LOGIN["password"]
        ):
            self._token = "correcttokenstring"
            response_text = load_fixture("account_mylogin.json")
        else:
            self._token = "wrongtokenstring"
            response_text = load_fixture("account_mylogin_failure.json")

        return Response(
            text=response_text,
            content_type="application/json",
        )

    async def device_mydevicelist(self, request: Request) -> Response:
        """Mock API to get devices."""
        data = await request.json()
        token = data["token"]
        lctoken = request.cookies.get("lctoken")

        if self._token == token and self._token == lctoken:
            response_text = load_fixture("device_mydevicelist.json")
        else:
            response_text = load_fixture("account_invalid_token.json")

        return Response(
            text=response_text,
            content_type="application/json",
        )

    async def account_myread(self, request: Request) -> Response:
        """Mock API to get Account Details."""
        data = await request.json()
        token = data["token"]
        lctoken = request.cookies.get("lctoken")

        if self._token == token and self._token == lctoken:
            response_text = load_fixture("account_myread.json")
        else:
            response_text = load_fixture("account_invalid_token.json")

        return Response(
            text=response_text,
            content_type="application/json",
        )

    async def address_myread(self, request: Request) -> Response:
        """Mock API to get Address Details."""
        data = await request.json()
        token = data["token"]
        lctoken = request.cookies.get("lctoken")

        if self._token == token and self._token == lctoken:
            response_text = load_fixture("address_myread.json")
        else:
            response_text = load_fixture("account_invalid_token.json")

        return Response(
            text=response_text,
            content_type="application/json",
        )

    async def tenant_myview(self, request: Request) -> Response:
        """Mock API to get Tentant Details."""
        data = await request.json()
        token = data["token"]
        lctoken = request.cookies.get("lctoken")

        if self._token == token and self._token == lctoken:
            response_text = load_fixture("tenant_myview.json")
        else:
            response_text = load_fixture("account_invalid_token.json")

        return Response(
            text=response_text,
            content_type="application/json",
        )

    async def device_myview(self, request: Request) -> Response:
        """Mock API to get Device Data."""
        data = await request.json()
        token = data["token"]
        lctoken = request.cookies.get("lctoken")

        if self._token == token and self._token == lctoken:
            device_id = data["LbDevice_ID"]
            response_text = load_fixture(f"device_myview_{device_id}.json")
        else:
            response_text = load_fixture("account_invalid_token.json")

        return Response(
            text=response_text,
            content_type="application/json",
        )

    async def device_messages(self, request: Request) -> Response:
        """Mock API to get Device Messages."""
        data = await request.json()
        token = data["token"]
        lctoken = request.cookies.get("lctoken")

        if self._token == token and self._token == lctoken:
            device_id = data["LbDevice_ID"]
            response_text = load_fixture(f"device_mylistmsg4device_{device_id}.json")
        else:
            response_text = load_fixture("account_invalid_token.json")

        return Response(
            text=response_text,
            content_type="application/json",
        )

    async def device_waterusage(self, request: Request) -> Response:
        """Mock API to get Device Water Usage."""
        data = await request.json()
        token = data["token"]
        lctoken = request.cookies.get("lctoken")

        if self._token == token and self._token == lctoken:
            device_id = data["LbDevice_ID"]
            offset = data["timeZoneOffset"]
            response_text = load_fixture(f"device_waterusage_{device_id}_{offset}.json")
        else:
            response_text = load_fixture("account_invalid_token.json")

        return Response(
            text=response_text,
            content_type="application/json",
        )

    async def device_simpleeventlist(self, request: Request) -> Response:
        """Mock API to get Device Simple Event List."""
        data = await request.json()
        token = data["token"]
        lctoken = request.cookies.get("lctoken")
        starting_date = data["starting_date"]

        if (
            self._token == token
            and self._token == lctoken
            and starting_date is not None
        ):
            device_id = data["LbDevice_ID"]
            response_text = load_fixture(f"device_mysimpleeventlist_{device_id}.json")
        else:
            response_text = load_fixture("account_invalid_token.json")

        return Response(
            text=response_text,
            content_type="application/json",
        )
