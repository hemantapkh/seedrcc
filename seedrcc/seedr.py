from typing import Any, Callable, Dict, List, Optional, Type

import httpx

from . import _constants, _login, models
from ._token import Token
from .exceptions import APIError, AuthenticationError, NetworkError, ServerError


class Seedr:
    """
    The main synchronous client for interacting with the Seedr API.
    It is recommended to use one of the factory methods to create an instance.
    e.g., `Seedr.from_password(...)`
    """

    _token: Token
    _on_token_refresh: Optional[Callable[[Token], None]]
    _client: httpx.Client

    def __init__(
        self,
        token: Token,
        on_token_refresh: Optional[Callable[[Token], None]] = None,
        httpx_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initializes the client with a Token object.

        Args:
            token (Token): A Token object containing the necessary authentication details.
            on_token_refresh (Callable, optional): A callback function that is called
                with the new Token object when the session is refreshed.
            httpx_kwargs (Dict, optional): A dictionary of keyword arguments to pass to the
                underlying `httpx.Client`. This is useful for setting timeouts,
                proxies, custom headers, etc.
        """
        self._token = token
        self._on_token_refresh = on_token_refresh
        self._client = httpx.Client(**(httpx_kwargs or {}))

    @property
    def token(self) -> Token:
        """The current authentication token used by the client."""
        return self._token

    @staticmethod
    def get_device_code() -> models.DeviceCode:
        """
        Step 1 of the device flow.
        Gets the device and user codes required for authorization.

        Example:
            >>> codes = Seedr.get_device_code()
            >>> print(f"Go to {codes.verification_url} and enter {codes.user_code}")
        """
        with httpx.Client() as client:
            response_data = _login.get_device_code(client)
        return models.DeviceCode.from_dict(response_data)

    @classmethod
    def from_device_code(
        cls: Type["Seedr"],
        device_code: str,
        on_token_refresh: Optional[Callable[[Token], None]] = None,
        **httpx_kwargs: Any,
    ) -> "Seedr":
        """
        Creates a new client by authorizing with a device code obtained from `get_device_code`.

        Args:
            device_code (str): The device code to authorize.
            on_token_refresh (Callable, optional): A callback function that is called
                with the new Token object when the session is refreshed.
            **httpx_kwargs: Keyword arguments to pass to the underlying `httpx.Client`.
        """
        try:
            with httpx.Client(**httpx_kwargs) as client:
                response = _login.authorize_device(client, device_code)
        except httpx.HTTPStatusError as e:
            if 500 <= e.response.status_code < 600:
                message = (
                    f"Server error during device authorization: {e.response.status_code} {e.response.reason_phrase}"
                )
                raise ServerError(message, response=e.response) from e
            # For 4xx errors
            raise AuthenticationError("Failed to authorize device", response=e.response) from e
        except httpx.RequestError as e:
            raise NetworkError(str(e)) from e

        token = Token(
            access_token=response["access_token"],
            refresh_token=response.get("refresh_token"),
            device_code=device_code,
        )
        return cls(token, on_token_refresh=on_token_refresh, httpx_kwargs=httpx_kwargs)

    @classmethod
    def from_password(
        cls: Type["Seedr"],
        username: str,
        password: str,
        on_token_refresh: Optional[Callable[[Token], None]] = None,
        **httpx_kwargs: Any,
    ) -> "Seedr":
        """
        Creates a new client by authenticating with a username and password.

        Args:
            username (str): The user's Seedr username (email).
            password (str): The user's Seedr password.
            on_token_refresh (Callable, optional): A callback function that is called
                with the new Token object when the session is refreshed.
            **httpx_kwargs: Keyword arguments to pass to the underlying `httpx.Client`.
        """
        try:
            with httpx.Client(**httpx_kwargs) as client:
                response = _login.authorize_password(client, username, password)
        except httpx.HTTPStatusError as e:
            if 500 <= e.response.status_code < 600:
                message = f"Server error during authentication: {e.response.status_code} {e.response.reason_phrase}"
                raise ServerError(message, response=e.response) from e
            # For 4xx errors
            raise AuthenticationError("Authentication failed", response=e.response) from e
        except httpx.RequestError as e:
            raise NetworkError(str(e)) from e

        token = Token(access_token=response["access_token"], refresh_token=response.get("refresh_token"))
        return cls(token, on_token_refresh=on_token_refresh, httpx_kwargs=httpx_kwargs)

    @classmethod
    def from_refresh_token(
        cls: Type["Seedr"],
        refresh_token: str,
        on_token_refresh: Optional[Callable[[Token], None]] = None,
        **httpx_kwargs: Any,
    ) -> "Seedr":
        """
        Creates a new client by refreshing an existing refresh token.

        Args:
            refresh_token (str): A valid refresh token.
            on_token_refresh (Callable, optional): A callback function that is called
                with the new Token object when the session is refreshed.
            **httpx_kwargs: Keyword arguments to pass to the underlying `httpx.Client`.
        """
        try:
            with httpx.Client(**httpx_kwargs) as client:
                response = _login.refresh_token(client, refresh_token)
        except httpx.HTTPStatusError as e:
            if 500 <= e.response.status_code < 600:
                message = f"Server error while refreshing token: {e.response.status_code} {e.response.reason_phrase}"
                raise ServerError(message, response=e.response) from e
            # For 4xx errors
            raise AuthenticationError("Failed to refresh token", response=e.response) from e
        except httpx.RequestError as e:
            raise NetworkError(str(e)) from e

        token = Token(access_token=response["access_token"], refresh_token=refresh_token)
        return cls(token, on_token_refresh=on_token_refresh, httpx_kwargs=httpx_kwargs)

    def _request(self, http_method: str, func: str, **kwargs: Any) -> Dict[str, Any]:
        """
        A centralized method for making API requests.
        Handles token refresh automatically and raises APIError for API-level errors.
        """
        params = kwargs.pop("params", {})
        params["access_token"] = self._token.access_token
        params["func"] = func

        try:
            response = self._client.request(http_method, _constants.RESOURCE_URL, params=params, **kwargs)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as e:
            if 500 <= e.response.status_code < 600:
                message = f"Server error: {e.response.status_code} {e.response.reason_phrase}"
                raise ServerError(message, response=e.response) from e
            # For 4xx errors
            raise APIError(f"API returned client error: {e.response.status_code}", response=e.response) from e
        except httpx.RequestError as e:
            raise NetworkError(str(e)) from e

        # Handle token expiration
        if isinstance(data, dict) and data.get("error") == "expired_token":
            self._perform_token_refresh()
            # Retry the request with the new token
            params["access_token"] = self._token.access_token
            response = self._client.request(http_method, _constants.RESOURCE_URL, params=params, **kwargs)
            response.raise_for_status()
            data = response.json()

        # Handle other API-level errors reported in the response body.
        # This checks for cases where the 'result' is not explicitly `True`.
        if isinstance(data, dict) and "result" in data and data["result"] is not True:
            error_message = data.get("error", "Unknown API error")
            raise APIError(error_message, response=response)

        return data

    def _perform_token_refresh(self) -> None:
        """Helper method to refresh the token."""
        try:
            if self._token.refresh_token:
                response = _login.refresh_token(self._client, self._token.refresh_token)
            elif self._token.device_code:
                response = _login.authorize_device(self._client, self._token.device_code)
            else:
                raise AuthenticationError("Session expired. No refresh token or device code available.")
        except httpx.HTTPStatusError as e:
            if 500 <= e.response.status_code < 600:
                message = f"Server error while refreshing token: {e.response.status_code} {e.response.reason_phrase}"
                raise ServerError(message, response=e.response) from e
            # For 4xx errors, let AuthenticationError parse the detailed error
            raise AuthenticationError("Failed to refresh token", response=e.response) from e
        except httpx.RequestError as e:
            raise NetworkError(str(e)) from e

        if "access_token" not in response:
            raise AuthenticationError("Token refresh failed. The response did not contain a new access token.")

        self._token.access_token = response["access_token"]

        if self._on_token_refresh:
            self._on_token_refresh(self._token)

    def refresh_token(self) -> None:
        """
        Manually refreshes the access token.

        This is useful if you want to proactively manage the token's lifecycle
        instead of waiting for an automatic refresh on an API call.

        Example:
            >>> try:
            ...     client.refresh_token()
            ...     print("Token successfully refreshed.")
            ... except AuthenticationError as e:
            ...     print(f"Failed to refresh token: {e}")

        Raises:
            AuthenticationError: If the refresh process fails.
        """
        self._perform_token_refresh()

    def get_settings(self) -> models.UserSettings:
        """
        Get the user settings.

        Example:
            >>> settings = client.get_settings()
            >>> print(settings.account.username)
        """
        response_data = self._request("get", "get_settings")
        return models.UserSettings.from_dict(response_data)

    def get_memory_bandwidth(self) -> models.MemoryBandwidth:
        """
        Get the memory and bandwidth usage.

        Example:
            >>> usage = client.get_memory_bandwidth()
            >>> print(f"Space used: {usage.space_used}/{usage.space_max}")
        """
        response_data = self._request("get", "get_memory_bandwidth")
        return models.MemoryBandwidth.from_dict(response_data)

    def add_torrent(
        self,
        magnet_link: Optional[str] = None,
        torrent_file: Optional[str] = None,
        wishlist_id: Optional[str] = None,
        folder_id: str = "-1",
    ) -> models.AddTorrentResult:
        """
        Add a torrent to the seedr account for downloading.

        Args:
            magnet_link (str, optional): The magnet link of the torrent.
            torrent_file (str, optional): Remote or local path of the torrent file.
            wishlist_id (str, optional): The ID of a wishlist item to add.
            folder_id (str, optional): The folder ID to add the torrent to. Defaults to root ('-1').

        Example:
            >>> result = client.add_torrent(magnet_link='magnet:?xt=...')
            >>> print(f"Added torrent: {result.title}")
        """
        data = {
            "torrent_magnet": magnet_link,
            "wishlist_id": wishlist_id,
            "folder_id": folder_id,
        }
        files = {}
        if torrent_file:
            # Handle remote URLs
            if torrent_file.startswith(("http://", "https://")):
                file_content = httpx.get(torrent_file).content
                files = {"torrent_file": file_content}
            # Handle local files more efficiently
            else:
                with open(torrent_file, "rb") as f:
                    files = {"torrent_file": f}
                    # The request is made outside the `with` block, but the file handle is passed.
                    # httpx will handle reading the file.
                    response_data = self._request("post", "add_torrent", data=data, files=files)
                    return models.AddTorrentResult.from_dict(response_data)

        response_data = self._request("post", "add_torrent", data=data, files=files)
        return models.AddTorrentResult.from_dict(response_data)

    def scan_page(self, url: str) -> List[models.Torrent]:
        """
        Scan a page and return a list of torrents. For example,
        you can pass the torrent link of 1337x.to and it will fetch
        the magnet link from that page.

        Args:
            url (str): The url of the page to scan.

        Example:
            >>> torrents = client.scan_page(url='https://1337x.to/torrent/1010994')
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
            file_id (string): The file id to fetch.

        Example:
            >>> result = client.fetch_file(file_id='12345')
            >>> print(f"Download URL: {result.url}")
        """
        response_data = self._request("post", "fetch_file", data={"folder_file_id": file_id})
        return models.FetchFileResult.from_dict(response_data)

    def list_contents(self, folder_id: str = "0", content_type: str = "folder") -> models.Folder:
        """
        List the contents of a folder.

        Args:
            folder_id (str, optional): The folder id to list the contents of. Defaults to root folder.
            content_type (str, optional): The type of content to list. Defaults to 'folder'.

        Example:
            >>> response = client.list_contents()
            >>> print(response)
        """
        data = {"content_type": content_type, "content_id": folder_id}
        response_data = self._request("post", "list_contents", data=data)
        return models.Folder.from_dict(response_data)

    def rename_file(self, file_id: str, rename_to: str) -> models.APIResult:
        """
        Rename a file.

        Args:
            file_id (str): The file id to rename.
            rename_to (str): The new name of the file.

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

        Example:
            >>> result = client.rename_folder(folder_id='12345', rename_to='newName')
            >>> if result.result:
            ...     print("Folder renamed successfully.")
        """
        data = {"rename_to": rename_to, "folder_id": folder_id}
        response_data = self._request("post", "rename", data=data)
        return models.APIResult.from_dict(response_data)

    def _delete_item(self, item_type: str, item_id: str) -> models.APIResult:
        """Helper to delete a file, folder, or torrent."""
        data = {"delete_arr": f'[{{"type":"{item_type}","id":{item_id}}}]'}
        response_data = self._request("post", "delete", data=data)
        return models.APIResult.from_dict(response_data)

    def delete_file(self, file_id: str) -> models.APIResult:
        """
        Delete a file.

        Args:
            file_id (str): The file id to delete.

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

        Example:
            >>> devices = client.get_devices()
            >>> for device in devices:
            ...     print(device.client_name)
        """
        response_data = self._request("get", "get_devices")
        devices_data = response_data.get("devices", [])
        return [models.Device.from_dict(d) for d in devices_data]

    def close(self) -> None:
        """Closes the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> "Seedr":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()
