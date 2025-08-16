from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

from . import models
from .token import Token


class BaseClient(ABC):
    """
    Base client containing all the core API logic.
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

    @staticmethod
    @abstractmethod
    def get_device_code() -> models.DeviceCode:
        """
        Get the device and user code required for authorization.
        """
        pass

    @property
    def token(self) -> Token:
        """
        Get the current authentication token used by the client.

        Returns:
            The Token object for the current session.
        """
        return self._token

    @abstractmethod
    def _request(
        self, http_method: str, func: str, files: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Helper to send request.
        """
        pass

    @abstractmethod
    def _perform_token_refresh(self) -> models.RefreshTokenResult:
        """
        Refresh the access token.
        """
        pass

    def refresh_token(self) -> models.RefreshTokenResult:
        """
        Manually refresh the access token.

        This is useful if you want to proactively manage the token's lifecycle
        instead of waiting for an automatic refresh on an API call.

        Returns:
            The result of the token refresh operation.

        Example:
            >>> try:
            ...     result = client.refresh_token()
            ...     print(f"Token successfully refreshed. New token expires in {result.expires_in} seconds.")
            ... except AuthenticationError as e:
            ...     print(f"Failed to refresh token: {e}")
        """
        return self._perform_token_refresh()

    def get_settings(self) -> models.UserSettings:
        """
        Get the user settings.

        Returns:
            An object containing the user's account settings.

        Example:
            >>> settings = client.get_settings()
            >>> print(settings.account.username)
        """
        response_data = self._request("get", "get_settings")
        return models.UserSettings.from_dict(response_data)

    def get_memory_bandwidth(self) -> models.MemoryBandwidth:
        """
        Get the memory and bandwidth usage.

        Returns:
            An object containing memory and bandwidth details.

        Example:
            >>> usage = client.get_memory_bandwidth()
            >>> print(f"Space used: {usage.space_used}/{usage.space_max}")
        """
        response_data = self._request("get", "get_memory_bandwidth")
        return models.MemoryBandwidth.from_dict(response_data)

    def scan_page(self, url: str) -> List[models.Torrent]:
        """
        Scan a page for torrents and magnet links.

        Args:
            url (str): The URL of the page to scan.

        Returns:
            A list of torrents found on the page.

        Example:
            >>> torrents = client.scan_page(url='some_torrent_page_url')
            >>> for torrent in torrents:
            ...     print(torrent.name)
        """
        response_data = self._request("post", "scan_page", data={"url": url})
        torrents_data = response_data.get("torrents", [])
        return [models.Torrent.from_dict(t) for t in torrents_data]

    def create_archive(self, folder_id: str) -> models.CreateArchiveResult:
        """
        Create an archive link of a folder.

        Args:
            folder_id (str): The folder id to create the archive of.

        Returns:
            An object containing the result of the archive creation.

        Example:
            >>> result = client.create_archive(folder_id='12345')
            >>> print(f"Archive URL: {result.archive_url}")
        """
        data = {"archive_arr": f'[{{"type":"folder","id":{folder_id}}}]'}
        response_data = self._request("post", "create_empty_archive", data=data)
        return models.CreateArchiveResult.from_dict(response_data)

    def fetch_file(self, file_id: str) -> models.FetchFileResult:
        """
        Create a link of a file.

        Args:
            file_id (str): The file id to fetch.

        Returns:
            An object containing the file details and download URL.

        Example:
            >>> result = client.fetch_file(file_id='12345')
            >>> print(f"Download URL: {result.url}")
        """
        response_data = self._request("post", "fetch_file", data={"folder_file_id": file_id})
        return models.FetchFileResult.from_dict(response_data)

    def list_contents(self, folder_id: str = "0") -> models.ListContentsResult:
        """
        List the contents of a folder.

        Args:
            folder_id (str, optional): The folder id to list the contents of. Defaults to root folder.

        Returns:
            An object containing the contents of the folder.

        Example:
            >>> response = client.list_contents()
            >>> print(response)
        """
        data = {"content_type": "folder", "content_id": folder_id}
        response_data = self._request("post", "list_contents", data=data)
        return models.ListContentsResult.from_dict(response_data)

    def rename_file(self, file_id: str, rename_to: str) -> models.APIResult:
        """
        Rename a file.

        Args:
            file_id (str): The file id to rename.
            rename_to (str): The new name of the file.

        Returns:
            An object indicating the result of the operation.

        Example:
            >>> result = client.rename_file(file_id='12345', rename_to='newName')
            >>> if result.result:
            ...     print("File renamed successfully.")
        """
        data = {"rename_to": rename_to, "file_id": file_id}
        response_data = self._request("post", "rename", data=data)
        return models.APIResult.from_dict(response_data)

    def rename_folder(self, folder_id: str, rename_to: str) -> models.APIResult:
        """
        Rename a folder.

        Args:
            folder_id (str): The folder id to rename.
            rename_to (str): The new name of the folder.

        Returns:
            An object indicating the result of the operation.

        Example:
            >>> result = client.rename_folder(folder_id='12345', rename_to='newName')
            >>> if result.result:
            ...     print("Folder renamed successfully.")
        """
        data = {"rename_to": rename_to, "folder_id": folder_id}
        response_data = self._request("post", "rename", data=data)
        return models.APIResult.from_dict(response_data)

    def _delete_item(self, item_type: str, item_id: str) -> models.APIResult:
        """
        Helper to delete a file, folder, or torrent.
        """
        data = {"delete_arr": f'[{{"type":"{item_type}","id":{item_id}}}]'}
        response_data = self._request("post", "delete", data=data)
        return models.APIResult.from_dict(response_data)

    def delete_file(self, file_id: str) -> models.APIResult:
        """
        Delete a file.

        Args:
            file_id (str): The file id to delete.

        Returns:
            An object indicating the result of the operation.

        Example:
            >>> response = client.delete_file(file_id='12345')
            >>> print(response)
        """
        return self._delete_item("file", file_id)

    def delete_folder(self, folder_id: str) -> models.APIResult:
        """
        Delete a folder.

        Args:
            folder_id (str): The folder id to delete.

        Returns:
            An object indicating the result of the operation.

        Example:
            >>> response = client.delete_folder(folder_id='12345')
            >>> print(response)
        """
        return self._delete_item("folder", folder_id)

    def delete_wishlist(self, wishlist_id: str) -> models.APIResult:
        """
        Delete an item from the wishlist.

        Args:
            wishlist_id (str): The wishlistId of item to delete.

        Returns:
            An object indicating the result of the operation.

        Example:
            >>> result = client.delete_wishlist(wishlist_id='12345')
        """
        response_data = self._request("post", "remove_wishlist", data={"id": wishlist_id})
        return models.APIResult.from_dict(response_data)

    def delete_torrent(self, torrent_id: str) -> models.APIResult:
        """
        Delete an active downloading torrent.

        Args:
            torrent_id (str): The torrent id to delete.

        Returns:
            An object indicating the result of the operation.

        Example:
            >>> response = client.delete_torrent(torrent_id='12345')
            >>> print(response)
        """
        return self._delete_item("torrent", torrent_id)

    def add_folder(self, name: str) -> models.APIResult:
        """
        Add a folder.

        Args:
            name (str): Folder name to add.

        Returns:
            An object indicating the result of the operation.

        Example:
            >>> result = client.add_folder(name='New Folder')
            >>> if result.result:
            ...     print("Folder created successfully.")
        """
        response_data = self._request("post", "add_folder", data={"name": name})
        return models.APIResult.from_dict(response_data)

    def search_files(self, query: str) -> models.Folder:
        """
        Search for files.

        Args:
            query (str): The query to search for.

        Returns:
            An object containing the search results.

        Example:
            >>> results = client.search_files(query='harry potter')
            >>> for f in results.folders:
            ...     print(f"Found folder: {f.name}")
        """
        response_data = self._request("post", "search_files", data={"search_query": query})
        return models.Folder.from_dict(response_data)

    def change_name(self, name: str, password: str) -> models.APIResult:
        """
        Change the name of the account.

        Args:
            name (str): The new name of the account.
            password (str): The password of the account.

        Returns:
            An object indicating the result of the operation.

        Example:
            >>> result = client.change_name(name='New Name', password='password')
        """
        data = {"setting": "fullname", "password": password, "fullname": name}
        response_data = self._request("post", "user_account_modify", data=data)
        return models.APIResult.from_dict(response_data)

    def change_password(self, old_password: str, new_password: str) -> models.APIResult:
        """
        Change the password of the account.

        Args:
            old_password (str): The old password of the account.
            new_password (str): The new password of the account.

        Returns:
            An object indicating the result of the operation.

        Example:
            >>> result = client.change_password(old_password='old', new_password='new')
        """
        data = {
            "setting": "password",
            "password": old_password,
            "new_password": new_password,
            "new_password_repeat": new_password,
        }
        response_data = self._request("post", "user_account_modify", data=data)
        return models.APIResult.from_dict(response_data)

    def get_devices(self) -> List[models.Device]:
        """
        Get the devices connected to the seedr account.

        Returns:
            A list of devices connected to the account.

        Example:
            >>> devices = client.get_devices()
            >>> for device in devices:
            ...     print(device.client_name)
        """
        response_data = self._request("get", "get_devices")
        devices_data = response_data.get("devices", [])
        return [models.Device.from_dict(d) for d in devices_data]

    @abstractmethod
    def add_torrent(
        self,
        magnet_link: Optional[str] = None,
        torrent_file: Optional[str] = None,
        wishlist_id: Optional[str] = None,
        folder_id: str = "-1",
    ) -> models.AddTorrentResult:
        """
        Add a torrent to the seedr account for downloading.
        """
        pass
