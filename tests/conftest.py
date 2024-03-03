"""Test Configuration for the tests."""

import os
import pytest

from aiohttp.test_utils import TestClient
from aiohttp.web import Application, Request, Response
from collections.abc import Callable, Coroutine
from unittest.mock import patch

from homeassistant.core import HomeAssistant
from homeassistant.components.http.forwarded import async_setup_forwarded

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
    with patch("homeassistant.components.persistent_notification.async_create"), patch(
        "homeassistant.components.persistent_notification.async_dismiss"
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
def aiohttp_client(
    event_loop, aiohttp_client, socket_enabled
) -> ClientSessionGenerator:  # pylint: disable=unused-argument, redefined-outer-name
    """Return aiohttp_client and allow opening sockets."""
    return aiohttp_client


@pytest.fixture
async def leakbot_api(hass: HomeAssistant) -> Application:
    """Mock the Leakbot API."""
    app = Application()
    app["hass"] = hass

    api = LeakbotAPIMock()
    app.router.add_route("POST", "/User/Account/MyLogin/", api.account_mylogin)

    async_setup_forwarded(app, True, [])
    return app


class LeakbotAPIMock:
    """Mock the Leakbox API class so we can test in isolation."""

    def __init__(self) -> None:
        """Initialize the Mock API."""
        self._logged_in = False
        self._token = ""

    async def account_mylogin(self, request: Request) -> Response:
        """Mock API for logging in."""
        data = await request.json()

        if (
            data["username"] == VALID_LOGIN["username"]
            and data["password"] == VALID_LOGIN["password"]
        ):
            self._logged_in = True
            response_text = load_fixture("account_mylogin.json")
        else:
            self._logged_in = False
            response_text = load_fixture("account_mylogin_failure.json")

        return Response(
            text=response_text,
            content_type="application/json",
        )
