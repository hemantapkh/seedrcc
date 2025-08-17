from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

from . import models
from .token import Token


class BaseClient(ABC):
    """
    Abstract Base Client defining the contract for all API clients.
    """

    _on_token_refresh: Optional[Callable[[Token], None]]
    _token: Token

    def __init__(
        self,
        token: Token,
        on_token_refresh: Optional[Callable[[Token], None]] = None,
    ) -> None:
        self._token = token
        self._on_token_refresh = on_token_refresh

    @property
    def token(self) -> Token:
        """Get the current authentication token used by the client."""
        return self._token

    @staticmethod
    @abstractmethod
    def get_device_code() -> "models.DeviceCode":
        """Get the device and user code required for authorization."""
        pass

    @abstractmethod
    def refresh_token(self) -> "models.RefreshTokenResult":
        """Manually refresh the access token."""
        pass

    @abstractmethod
    def get_settings(self) -> "models.UserSettings":
        """Get the user settings."""
        pass

    @abstractmethod
    def get_memory_bandwidth(self) -> "models.MemoryBandwidth":
        """Get the memory and bandwidth usage."""
        pass

    @abstractmethod
    def list_contents(self, folder_id: str = "0") -> "models.ListContentsResult":
        """List the contents of a folder."""
        pass

    @abstractmethod
    def add_torrent(
        self,
        magnet_link: Optional[str] = None,
        torrent_file: Optional[str] = None,
        wishlist_id: Optional[str] = None,
        folder_id: str = "-1",
    ) -> "models.AddTorrentResult":
        """Add a torrent to the seedr account for downloading."""
        pass

    @abstractmethod
    def scan_page(self, url: str) -> "models.ScanPageResult":
        """Scan a page for torrents and magnet links."""
        pass

    @abstractmethod
    def fetch_file(self, file_id: str) -> "models.FetchFileResult":
        """Create a link of a file."""
        pass

    @abstractmethod
    def create_archive(self, folder_id: str) -> "models.CreateArchiveResult":
        """Create an archive link of a folder."""
        pass

    @abstractmethod
    def search_files(self, query: str) -> "models.Folder":
        """Search for files."""
        pass

    @abstractmethod
    def add_folder(self, name: str) -> "models.APIResult":
        """Add a folder."""
        pass

    @abstractmethod
    def rename_file(self, file_id: str, rename_to: str) -> "models.APIResult":
        """Rename a file."""
        pass

    @abstractmethod
    def rename_folder(self, folder_id: str, rename_to: str) -> "models.APIResult":
        """Rename a folder."""
        pass

    @abstractmethod
    def delete_file(self, file_id: str) -> "models.APIResult":
        """Delete a file."""
        pass

    @abstractmethod
    def delete_folder(self, folder_id: str) -> "models.APIResult":
        """Delete a folder."""
        pass

    @abstractmethod
    def delete_torrent(self, torrent_id: str) -> "models.APIResult":
        """Delete an active downloading torrent."""
        pass

    @abstractmethod
    def delete_wishlist(self, wishlist_id: str) -> "models.APIResult":
        """Delete an item from the wishlist."""
        pass

    @abstractmethod
    def get_devices(self) -> List["models.Device"]:
        """Get the devices connected to the seedr account."""
        pass

    @abstractmethod
    def change_name(self, name: str, password: str) -> "models.APIResult":
        """Change the name of the account."""
        pass

    @abstractmethod
    def change_password(self, old_password: str, new_password: str) -> "models.APIResult":
        """Change the password of the account."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the underlying HTTP client."""
        pass
