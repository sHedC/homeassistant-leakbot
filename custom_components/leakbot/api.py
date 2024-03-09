"""Leakbot API Client."""

from __future__ import annotations

import json

from aiohttp import ClientSession, ClientError
from json.decoder import JSONDecodeError
from urllib.parse import urljoin

from .const import LOGGER

API_URL = "https://api.leakbot.io"
API_LOGIN = "/v1.0/User/Account/MyLogin/"
API_DEVICE_LIST = "/v1.0/User/Device/MyDeviceList/"


class LeakbotApiClientError(Exception):
    """Exception to indicate a general API error."""

    def __init__(self, status, description) -> None:
        """Initialize the exception."""
        super().__init__(description)
        self.status = status
        self.description = description


class LeakbotApiClientCommunicationError(LeakbotApiClientError):
    """Exception to indicate a communication error."""


class LeakbotApiClientAuthenticationError(LeakbotApiClientError):
    """Exception to indicate an authentication error."""


class LeakbotApiClient:
    """Leakbot API Client Connector."""

    def __init__(self, username: str, password: str, session: ClientSession) -> None:
        """Initialize API Client."""
        self._session = session
        self._username = username
        self._password = password
        self._connected = False
        self._token = "randomtoken"
        self._token_expires = 0

    async def _post(self, url: str, params: dict[str, any]) -> dict[str, any]:
        """Perform post to the api."""
        try:
            response = await self._session.post(
                url,
                data=json.dumps(params),
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                cookies={"lctoken": self._token},
            )
            LOGGER.debug(
                "__post: response status: %s, content: %s",
                response.status,
                await response.text(),
            )
            response.raise_for_status()
            response_json = await response.json()
        except ClientError as ex:
            LOGGER.error("Client Error: %s", ex)
            raise LeakbotApiClientCommunicationError(
                response.status, "Error fetching information"
            ) from ex
        except JSONDecodeError as ex:
            response_text = await response.text()
            LOGGER.error("JSON Decode Error: %s:%s", response.status, response_text)
            raise LeakbotApiClientCommunicationError(
                response.status, response_text
            ) from ex

        return response_json

    def is_connected(self) -> bool:
        """Is the API Connected."""
        return self._connected

    async def login(self) -> dict[str, any]:
        """Attempt to login to the api server."""
        params = {
            "username": self._username,
            "password": self._password,
        }
        result_json = await self._post(urljoin(API_URL, API_LOGIN), params)

        if "error" in result_json:
            self._connected = False
            raise LeakbotApiClientAuthenticationError(
                result_json["error"], result_json["description"]
            )

        self._token = result_json["token"]
        self._connected = True
        return result_json

    async def get_device_list(self) -> dict[str, any]:
        """Retrieve the list of devices connected to the account."""
        params = {"token": self._token}
        result_json = await self._post(urljoin(API_URL, API_DEVICE_LIST), params)

        # TODO: Handle Error responses (invalid token)
        return result_json

    async def async_get_data(self) -> any:
        """Get data from the API."""
        return {}
