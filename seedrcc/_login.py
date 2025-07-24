from typing import Any, Dict

import httpx

from . import _constants


class _Login:
    _client: httpx.Client

    """
    Handles the direct authentication flows with the Seedr API.

    This is a stateless, internal helper class that performs the raw HTTP
    transactions for different authentication grant types. It is not
    intended for public use.
    """

    def __init__(self) -> None:
        self._client = httpx.Client()

    def get_device_code(self) -> Dict[str, Any]:
        """
        Fetches a device and user code for the device auth flow.

        Returns:
            Dict[str, Any]: The API response containing user_code, device_code, etc.
        """
        params = {"client_id": _constants.DEVICE_CLIENT_ID}
        response = self._client.get(_constants.DEVICE_CODE_URL, params=params)
        response.raise_for_status()
        return response.json()

    def authorize_device(self, device_code: str) -> Dict[str, Any]:
        """
        Exchanges a device code for access and refresh tokens.

        Args:
            device_code (str): The device code to authorize.

        Returns:
            Dict[str, Any]: The API response containing the tokens.
        """
        params = {"client_id": _constants.DEVICE_CLIENT_ID, "device_code": device_code}
        response = self._client.get(_constants.DEVICE_AUTHORIZE_URL, params=params)
        response.raise_for_status()
        return response.json()

    def authorize_password(self, username: str, password: str) -> Dict[str, Any]:
        """
        Exchanges a username and password for access and refresh tokens.

        Args:
            username (str): The user's Seedr username (email).
            password (str): The user's Seedr password.

        Returns:
            Dict[str, Any]: The API response containing the tokens.
        """
        data = {
            "grant_type": "password",
            "client_id": _constants.PASSWORD_CLIENT_ID,
            "type": "login",
            "username": username,
            "password": password,
        }
        response = self._client.post(_constants.TOKEN_URL, data=data)
        response.raise_for_status()
        return response.json()

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Exchanges a refresh token for a new access token.

        Args:
            refresh_token (str): The refresh token to use.

        Returns:
            Dict[str, Any]: The API response containing the new access token.
        """
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": _constants.PASSWORD_CLIENT_ID,
        }
        response = self._client.post(_constants.TOKEN_URL, data=data)
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        """Closes the underlying httpx client."""
        self._client.close()

    def __enter__(self) -> "_Login":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()
