from dataclasses import asdict, dataclass
from typing import Any, Dict, Literal, Optional

from . import _constants


@dataclass
class BaseModel:
    """Base model for request payloads and parameters."""

    def to_dict(self) -> Dict[str, Any]:
        """Converts the dataclass instance to a dictionary."""
        return asdict(self)


@dataclass
class PasswordLoginPayload(BaseModel):
    """Payload for password-based authentication."""

    username: str
    password: str
    grant_type: str = "password"
    client_id: str = _constants.PSWRD_CLIENT_ID
    type: str = "login"


@dataclass
class RefreshTokenPayload(BaseModel):
    """Payload for refreshing an access token."""

    refresh_token: str
    grant_type: str = "refresh_token"
    client_id: str = _constants.PSWRD_CLIENT_ID


@dataclass
class GetDeviceCodeParams(BaseModel):
    """Parameters for fetching device code for device code authentication."""

    client_id: str = _constants.DEVICE_CLIENT_ID


@dataclass
class DeviceCodeAuthParams(BaseModel):
    """Parameters for device code authorization."""

    device_code: str
    client_id: str = _constants.DEVICE_CLIENT_ID


@dataclass
class AddTorrentPayload(BaseModel):
    """Payload for adding a new torrent."""

    folder_id: str = "-1"
    torrent_magnet: Optional[str] = None
    wishlist_id: Optional[str] = None


@dataclass
class ScanPagePayload(BaseModel):
    """Payload for scanning a page."""

    url: str


@dataclass
class CreateArchivePayload(BaseModel):
    """Payload for creating an archive from a folder."""

    folder_id: str

    def to_dict(self) -> Dict[str, Any]:
        """Overrides base to_dict to format the archive_arr correctly."""
        return {"archive_arr": f'[{{"type":"folder","id":{self.folder_id}}}]'}


@dataclass
class FetchFilePayload(BaseModel):
    """Payload for fetching a file's details."""

    folder_file_id: str


@dataclass
class ListContentsPayload(BaseModel):
    """Payload for listing contents of a folder."""

    content_type: str = "folder"
    content_id: str = "0"


@dataclass
class RenameFilePayload(BaseModel):
    """Payload for renaming a file."""

    rename_to: str
    file_id: str


@dataclass
class RenameFolderPayload(BaseModel):
    """Payload for renaming a folder."""

    rename_to: str
    folder_id: str


@dataclass
class DeleteItemPayload(BaseModel):
    """Payload for deleting an item (file, folder, or torrent)."""

    item_type: Literal["file", "folder", "torrent"]
    item_id: str

    def to_dict(self) -> Dict[str, Any]:
        """Overrides base to_dict to format the delete_arr correctly."""
        return {"delete_arr": f'[{{"type":"{self.item_type}","id":{self.item_id}}}]'}


@dataclass
class RemoveWishlistPayload(BaseModel):
    """Payload for removing a wishlist item."""

    id: str


@dataclass
class AddFolderPayload(BaseModel):
    """Payload for adding a new folder."""

    name: str


@dataclass
class SearchFilesPayload(BaseModel):
    """Payload for searching files."""

    search_query: str


@dataclass
class ChangeNamePayload(BaseModel):
    """Payload for changing the account name."""

    fullname: str
    password: str
    setting: str = "fullname"


@dataclass
class ChangePasswordPayload(BaseModel):
    """Payload for changing the account password."""

    password: str
    new_password: str
    new_password_repeat: str
    setting: str = "password"
