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


def prepare_scan_page_payload(url: str) -> Dict[str, str]:
    """Prepares the data payload for scanning a page."""
    return {"url": url}


def prepare_create_archive_payload(folder_id: str) -> Dict[str, str]:
    """Prepares the data payload for creating an archive."""
    return {"archive_arr": f'[{{"type":"folder","id":{folder_id}}}]'}


def prepare_fetch_file_payload(file_id: str) -> Dict[str, str]:
    """Prepares the data payload for fetching a file."""
    return {"folder_file_id": file_id}


def prepare_list_contents_payload(folder_id: str) -> Dict[str, str]:
    """Prepares the data payload for listing contents."""
    return {"content_type": "folder", "content_id": folder_id}


def prepare_rename_payload(
    rename_to: str, file_id: Optional[str] = None, folder_id: Optional[str] = None
) -> Dict[str, str]:
    """Prepares the data payload for renaming a file or folder."""
    payload = {"rename_to": rename_to}
    if file_id:
        payload["file_id"] = file_id
    if folder_id:
        payload["folder_id"] = folder_id
    return payload


def prepare_delete_item_payload(item_type: str, item_id: str) -> Dict[str, str]:
    """Prepares the data payload for deleting an item."""
    return {"delete_arr": f'[{{"type":"{item_type}","id":{item_id}}}]'}


def prepare_remove_wishlist_payload(wishlist_id: str) -> Dict[str, str]:
    """Prepares the data payload for removing a wishlist item."""
    return {"id": wishlist_id}


def prepare_add_folder_payload(name: str) -> Dict[str, str]:
    """Prepares the data payload for adding a folder."""
    return {"name": name}


def prepare_search_files_payload(query: str) -> Dict[str, str]:
    """Prepares the data payload for searching files."""
    return {"search_query": query}


def prepare_change_name_payload(name: str, password: str) -> Dict[str, str]:
    """Prepares the data payload for changing the account name."""
    return {"setting": "fullname", "password": password, "fullname": name}


def prepare_change_password_payload(old_password: str, new_password: str) -> Dict[str, str]:
    """Prepares the data payload for changing the account password."""
    return {
        "setting": "password",
        "password": old_password,
        "new_password": new_password,
        "new_password_repeat": new_password,
    }

