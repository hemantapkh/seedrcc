from typing import Any, Dict

import httpx

from . import _constants


def get_device_code(client: httpx.Client) -> Dict[str, Any]:
    """
    Fetches a device and user code for the device auth flow.
    """
    params = {"client_id": _constants.DEVICE_CLIENT_ID}
    response = client.get(_constants.DEVICE_CODE_URL, params=params)
    response.raise_for_status()
    return response.json()


def authorize_device(client: httpx.Client, device_code: str) -> Dict[str, Any]:
    """
    Exchanges a device code for access and refresh tokens.
    """
    params = {"client_id": _constants.DEVICE_CLIENT_ID, "device_code": device_code}
    response = client.get(_constants.DEVICE_AUTHORIZE_URL, params=params)
    response.raise_for_status()
    return response.json()


def authorize_password(client: httpx.Client, username: str, password: str) -> Dict[str, Any]:
    """
    Exchanges a username and password for access and refresh tokens.
    """
    data = {
        "grant_type": "password",
        "client_id": _constants.PSWRD_CLIENT_ID,
        "type": "login",
        "username": username,
        "password": password,
    }
    response = client.post(_constants.TOKEN_URL, data=data)
    response.raise_for_status()
    return response.json()


def refresh_token(client: httpx.Client, refresh_token: str) -> Dict[str, Any]:
    """
    Exchanges a refresh token for a new access token.
    """
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": _constants.PSWRD_CLIENT_ID,
    }
    response = client.post(_constants.TOKEN_URL, data=data)
    response.raise_for_status()
    return response.json()
