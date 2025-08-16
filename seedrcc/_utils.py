from datetime import datetime
from typing import Any, Dict, Optional

from . import _constants


def parse_datetime(dt_str: Optional[Any]) -> Optional[datetime]:
    """
    A centralized helper to parse datetime strings or timestamps from the API.
    Returns None if the input is invalid or None.
    """
    if not dt_str:
        return None
    try:
        if isinstance(dt_str, (int, float)):
            return datetime.fromtimestamp(dt_str)
        return datetime.strptime(str(dt_str), "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return None


def prepare_password_payload(username: str, password: str) -> Dict[str, str]:
    """Prepares the data payload for password-based authentication."""
    return {
        "grant_type": "password",
        "client_id": _constants.PSWRD_CLIENT_ID,
        "type": "login",
        "username": username,
        "password": password,
    }


def prepare_refresh_token_payload(refresh_token: str) -> Dict[str, str]:
    """Prepares the data payload for refreshing an access token."""
    return {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": _constants.PSWRD_CLIENT_ID,
    }


def prepare_device_code_params(device_code: str) -> Dict[str, str]:
    """Prepares the URL parameters for device code authorization."""
    return {
        "client_id": _constants.DEVICE_CLIENT_ID,
        "device_code": device_code,
    }


def prepare_add_torrent_payload(
    magnet_link: Optional[str],
    wishlist_id: Optional[str],
    folder_id: str,
) -> Dict[str, Any]:
    """Prepares the data payload for adding a new torrent."""
    return {
        "torrent_magnet": magnet_link,
        "wishlist_id": wishlist_id,
        "folder_id": folder_id,
    }


def read_file_bytes(path: str) -> bytes:
    """Reads a local file and returns its content as bytes."""
    with open(path, "rb") as f:
        return f.read()
