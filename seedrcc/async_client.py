from typing import Any, Callable, Coroutine, Dict, List, Optional, Type

import anyio
import httpx

from . import _constants, _utils, models
from ._base import BaseClient
from .exceptions import APIError, AuthenticationError, NetworkError, ServerError
from .token import Token


class AsyncSeedr(BaseClient):
    """
    Asynchronous client for interacting with the Seedr API.

    This client provides access to all the API endpoints and handles authentication.
    You can use one of the factory class methods to create an instance:
    - `AsyncSeedr.from_password()`
    - `AsyncSeedr.from_device_code()`
    - `AsyncSeedr.from_refresh_token()`

    Initializing with an existing token:
        If you have a previously saved token, you can initialize the client directly.

        ```python
        from seedrcc import AsyncSeedr, Token

        # Load your token data (e.g., from a file or database)
        token_data = {"access_token": "...", "refresh_token": "..."}
        token = Token.from_dict(token_data)

        client = AsyncSeedr(token=token)
        # You can now make authenticated requests
        # settings = await client.get_settings()
        ```

    Using a custom `httpx.AsyncClient`:
        For advanced configuration (e.g., custom timeouts, proxies, headers),
        you can pass your own `httpx.AsyncClient` instance.

        ```python
        import httpx

        my_httpx_client = httpx.AsyncClient(timeout=30.0)
        # client = await AsyncSeedr.from_password("user", "pass", httpx_client=my_httpx_client)
        ```

    Using `httpx` keyword arguments:
        For simpler customizations, you can pass `httpx.AsyncClient` arguments directly
        to the factory methods.

        ```python
        # client = await AsyncSeedr.from_password("user", "pass", timeout=30.0)
        ```
    """

    _client: httpx.AsyncClient
    _manages_client_lifecycle: bool

    def __init__(
        self,
        token: Token,
        on_token_refresh: Optional[Callable[[Token], None]] = None,
        httpx_client: Optional[httpx.AsyncClient] = None,
        **httpx_kwargs: Any,
    ) -> None:
        super().__init__(token, on_token_refresh)
        if httpx_client is not None:
            self._client = httpx_client
            self._manages_client_lifecycle = False
        else:
            self._client = httpx.AsyncClient(**httpx_kwargs)
            self._manages_client_lifecycle = True

    # Public Properties
    @property
    def token(self) -> Token:
        return super().token

    # Public Class Methods (Factories)
    @staticmethod
    async def get_device_code() -> models.DeviceCode:
        """
        Gets the device and user codes required for authorization.

        This is the first step in the device authentication flow.

        Returns:
            A `DeviceCode` object containing the codes needed for the next step.

        Example:
            ```python
            from seedrcc import AsyncSeedr
            
            # codes = await AsyncSeedr.get_device_code()
            # print(f"Go to {codes.verification_url} and enter {codes.user_code}")
            ```
        """
        params = {"client_id": _constants.DEVICE_CLIENT_ID}
        async with httpx.AsyncClient() as client:
            response = await client.get(_constants.DEVICE_CODE_URL, params=params)
            response.raise_for_status()
            response_data = response.json()
        return models.DeviceCode.from_dict(response_data)

    @classmethod
    async def from_password(
        cls: Type["AsyncSeedr"],
        username: str,
        password: str,
        on_token_refresh: Optional[Callable[[Token], None]] = None,
        httpx_client: Optional[httpx.AsyncClient] = None,
        **httpx_kwargs: Any,
    ) -> "AsyncSeedr":
        """
        Creates a new client by authenticating with a username and password.

        Args:
            username: The user's Seedr username (email).
            password: The user's Seedr password.
            on_token_refresh: A callback function that is called with the new
                Token object when the session is refreshed.
            httpx_client: An optional, pre-configured `httpx.AsyncClient` instance.
            **httpx_kwargs: Optional keyword arguments to pass to the `httpx.AsyncClient` constructor.
                These are ignored if `httpx_client` is provided.

        Returns:
            An initialized `AsyncSeedr` client instance.

        Example:
            ```python
            # client = await AsyncSeedr.from_password("your_email@example.com", "your_password")
            ```
        """

        async def auth_callable(client: httpx.AsyncClient) -> Dict[str, Any]:
            data = _utils.prepare_password_payload(username, password)
            return await cls._perform_auth_request(
                client, "post", _constants.TOKEN_URL, "Authentication failed", data=data
            )

        return await cls._create_client_from_auth(
            auth_callable, lambda r: {}, on_token_refresh, httpx_client, **httpx_kwargs
        )

    @classmethod
    async def from_device_code(
        cls: Type["AsyncSeedr"],
        device_code: str,
        on_token_refresh: Optional[Callable[[Token], None]] = None,
        httpx_client: Optional[httpx.AsyncClient] = None,
        **httpx_kwargs: Any,
    ) -> "AsyncSeedr":
        """
        Creates a new client by authorizing with a device code.

        This is the second step in the device authentication flow, after getting the
        codes from `AsyncSeedr.get_device_code()`.

        Args:
            device_code: The device code obtained from `get_device_code()`.
            on_token_refresh: A callback function that is called with the new
                Token object when the session is refreshed.
            httpx_client: An optional, pre-configured `httpx.AsyncClient` instance.
            **httpx_kwargs: Optional keyword arguments to pass to the `httpx.AsyncClient` constructor.
                These are ignored if `httpx_client` is provided.

        Returns:
            An initialized `AsyncSeedr` client instance.
        
        Example:
            ```python
            # client = await AsyncSeedr.from_device_code("your_device_code")
            ```
        """

        async def auth_callable(client: httpx.AsyncClient) -> Dict[str, Any]:
            params = _utils.prepare_device_code_params(device_code)
            return await cls._perform_auth_request(
                client, "get", _constants.DEVICE_AUTHORIZE_URL, "Failed to authorize device", params=params
            )

        return await cls._create_client_from_auth(
            auth_callable,
            lambda r: {"device_code": device_code},
            on_token_refresh,
            httpx_client,
            **httpx_kwargs,
        )

    @classmethod
    async def from_refresh_token(
        cls: Type["AsyncSeedr"],
        refresh_token: str,
        on_token_refresh: Optional[Callable[[Token], None]] = None,
        httpx_client: Optional[httpx.AsyncClient] = None,
        **httpx_kwargs: Any,
    ) -> "AsyncSeedr":
        """
        Creates a new client by using an existing refresh token.

        Args:
            refresh_token: A valid refresh token.
            on_token_refresh: A callback function that is called with the new
                Token object when the session is refreshed.
            httpx_client: An optional, pre-configured `httpx.AsyncClient` instance.
            **httpx_kwargs: Optional keyword arguments to pass to the `httpx.AsyncClient` constructor.
                These are ignored if `httpx_client` is provided.

        Returns:
            An initialized `AsyncSeedr` client instance.

        Example:
            ```python
            # client = await AsyncSeedr.from_refresh_token("your_refresh_token")
            ```
        """

        async def auth_callable(client: httpx.AsyncClient) -> Dict[str, Any]:
            data = _utils.prepare_refresh_token_payload(refresh_token)
            return await cls._perform_auth_request(
                client, "post", _constants.TOKEN_URL, "Failed to refresh token", data=data
            )

        return await cls._create_client_from_auth(
            auth_callable,
            lambda r: {"refresh_token": refresh_token},
            on_token_refresh,
            httpx_client,
            **httpx_kwargs,
        )

    # Public Instance Methods (Core API Logic)
    async def refresh_token(self) -> models.RefreshTokenResult:
        """
        Manually refreshes the access token.

        This is useful if you want to proactively manage the token's lifecycle
        instead of waiting for an automatic refresh on an API call.

        Returns:
            The result of the token refresh operation.
        
        Example:
            ```python
            # try:
            #     result = await client.refresh_token()
            #     print(f"Token successfully refreshed. New token expires in {result.expires_in} seconds.")
            # except AuthenticationError as e:
            #     print(f"Failed to refresh token: {e}")
            ```
        """
        return await self._perform_token_refresh()

    async def get_settings(self) -> models.UserSettings:
        """
        Get the user settings.

        Returns:
            An object containing the user's account settings.

        Example:
            ```python
            # settings = await client.get_settings()
            # print(settings.account.username)
            ```
        """
        response_data = await self._request("get", "get_settings")
        return models.UserSettings.from_dict(response_data)

    async def get_memory_bandwidth(self) -> models.MemoryBandwidth:
        """
        Get the memory and bandwidth usage.

        Returns:
            An object containing memory and bandwidth details.

        Example:
            ```python
            # usage = await client.get_memory_bandwidth()
            # print(f"Space used: {usage.space_used}/{usage.space_max}")
            ```
        """
        response_data = await self._request("get", "get_memory_bandwidth")
        return models.MemoryBandwidth.from_dict(response_data)

    async def list_contents(self, folder_id: str = "0") -> models.ListContentsResult:
        """
        List the contents of a folder.

        Args:
            folder_id (str, optional): The folder id to list the contents of. Defaults to root folder.

        Returns:
            An object containing the contents of the folder.

        Example:
            ```python
            # response = await client.list_contents()
            # print(response)
            ```
        """
        data = _utils.prepare_list_contents_payload(folder_id)
        response_data = await self._request("post", "list_contents", data=data)
        return models.ListContentsResult.from_dict(response_data)

    async def add_torrent(
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

        Returns:
            An object containing the result of the add torrent operation.

        Example:
            ```python
            # Add by magnet link
            # result = await client.add_torrent(magnet_link="magnet:?xt=urn:btih:...")
            # print(result.title)
            
            # Add from a local .torrent file
            # result = await client.add_torrent(torrent_file="/path/to/your/file.torrent")
            # print(result.title)
            ```
        """
        data = _utils.prepare_add_torrent_payload(magnet_link, wishlist_id, folder_id)
        files = {}
        if torrent_file:
            files = await self._handle_torrent_file_async(torrent_file)

        response_data = await self._request("post", "add_torrent", data=data, files=files)
        return models.AddTorrentResult.from_dict(response_data)

    async def scan_page(self, url: str) -> List[models.Torrent]:
        """
        Scan a page for torrents and magnet links.

        Args:
            url (str): The URL of the page to scan.

        Returns:
            A list of torrents found on the page.

        Example:
            ```python
            # torrents = await client.scan_page(url='some_torrent_page_url')
            # for torrent in torrents:
            #     print(torrent.name)
            ```
        """
        data = _utils.prepare_scan_page_payload(url)
        response_data = await self._request("post", "scan_page", data=data)
        torrents_data = response_data.get("torrents", [])
        return [models.Torrent.from_dict(t) for t in torrents_data]

    async def fetch_file(self, file_id: str) -> models.FetchFileResult:
        """
        Create a link of a file.

        Args:
            file_id (str): The file id to fetch.

        Returns:
            An object containing the file details and download URL.

        Example:
            ```python
            # result = await client.fetch_file(file_id='12345')
            # print(f"Download URL: {result.url}")
            ```
        """
        data = _utils.prepare_fetch_file_payload(file_id)
        response_data = await self._request("post", "fetch_file", data=data)
        return models.FetchFileResult.from_dict(response_data)

    async def create_archive(self, folder_id: str) -> models.CreateArchiveResult:
        """
        Create an archive link of a folder.

        Args:
            folder_id (str): The folder id to create the archive of.

        Returns:
            An object containing the result of the archive creation.

        Example:
            ```python
            # result = await client.create_archive(folder_id='12345')
            # print(f"Archive URL: {result.archive_url}")
            ```
        """
        data = _utils.prepare_create_archive_payload(folder_id)
        response_data = await self._request("post", "create_empty_archive", data=data)
        return models.CreateArchiveResult.from_dict(response_data)

    async def search_files(self, query: str) -> models.Folder:
        """
        Search for files.

        Args:
            query (str): The query to search for.

        Returns:
            An object containing the search results.

        Example:
            ```python
            # results = await client.search_files(query='harry potter')
            # for f in results.folders:
            #     print(f"Found folder: {f.name}")
            ```
        """
        data = _utils.prepare_search_files_payload(query)
        response_data = await self._request("post", "search_files", data=data)
        return models.Folder.from_dict(response_data)

    async def add_folder(self, name: str) -> models.APIResult:
        """
        Add a folder.

        Args:
            name (str): Folder name to add.

        Returns:
            An object indicating the result of the operation.

        Example:
            ```python
            # result = await client.add_folder(name='New Folder')
            # if result.result:
            #     print("Folder created successfully.")
            ```
        """
        data = _utils.prepare_add_folder_payload(name)
        response_data = await self._request("post", "add_folder", data=data)
        return models.APIResult.from_dict(response_data)

    async def rename_file(self, file_id: str, rename_to: str) -> models.APIResult:
        """
        Rename a file.

        Args:
            file_id (str): The file id to rename.
            rename_to (str): The new name of the file.

        Returns:
            An object indicating the result of the operation.

        Example:
            ```python
            # result = await client.rename_file(file_id='12345', rename_to='newName')
            # if result.result:
            #     print("File renamed successfully.")
            ```
        """
        data = _utils.prepare_rename_payload(rename_to, file_id=file_id)
        response_data = await self._request("post", "rename", data=data)
        return models.APIResult.from_dict(response_data)

    async def rename_folder(self, folder_id: str, rename_to: str) -> models.APIResult:
        """
        Rename a folder.

        Args:
            folder_id (str): The folder id to rename.
            rename_to (str): The new name of the folder.

        Returns:
            An object indicating the result of the operation.

        Example:
            ```python
            # result = await client.rename_folder(folder_id='12345', rename_to='newName')
            # if result.result:
            #     print("Folder renamed successfully.")
            ```
        """
        data = _utils.prepare_rename_payload(rename_to, folder_id=folder_id)
        response_data = await self._request("post", "rename", data=data)
        return models.APIResult.from_dict(response_data)

    async def delete_file(self, file_id: str) -> models.APIResult:
        """
        Delete a file.

        Args:
            file_id (str): The file id to delete.

        Returns:
            An object indicating the result of the operation.

        Example:
            ```python
            # response = await client.delete_file(file_id='12345')
            # print(response)
            ```
        """
        return await self._delete_item("file", file_id)

    async def delete_folder(self, folder_id: str) -> models.APIResult:
        """
        Delete a folder.

        Args:
            folder_id (str): The folder id to delete.

        Returns:
            An object indicating the result of the operation.

        Example:
            ```python
            # response = await client.delete_folder(folder_id='12345')
            # print(response)
            ```
        """
        return await self._delete_item("folder", folder_id)

    async def delete_torrent(self, torrent_id: str) -> models.APIResult:
        """
        Delete an active downloading torrent.

        Args:
            torrent_id (str): The torrent id to delete.

        Returns:
            An object indicating the result of the operation.

        Example:
            ```python
            # response = await client.delete_torrent(torrent_id='12345')
            # print(response)
            ```
        """
        return await self._delete_item("torrent", torrent_id)

    async def delete_wishlist(self, wishlist_id: str) -> models.APIResult:
        """
        Delete an item from the wishlist.

        Args:
            wishlist_id (str): The wishlistId of item to delete.

        Returns:
            An object indicating the result of the operation.

        Example:
            ```python
            # result = await client.delete_wishlist(wishlist_id='12345')
            ```
        """
        data = _utils.prepare_remove_wishlist_payload(wishlist_id)
        response_data = await self._request("post", "remove_wishlist", data=data)
        return models.APIResult.from_dict(response_data)

    async def get_devices(self) -> List[models.Device]:
        """
        Get the devices connected to the seedr account.

        Returns:
            A list of devices connected to the account.

        Example:
            ```python
            # devices = await client.get_devices()
            # for device in devices:
            #     print(device.client_name)
            ```
        """
        response_data = await self._request("get", "get_devices")
        devices_data = response_data.get("devices", [])
        return [models.Device.from_dict(d) for d in devices_data]

    async def change_name(self, name: str, password: str) -> models.APIResult:
        """
        Change the name of the account.

        Args:
            name (str): The new name of the account.
            password (str): The password of the account.

        Returns:
            An object indicating the result of the operation.

        Example:
            ```python
            # result = await client.change_name(name='New Name', password='password')
            ```
        """
        data = _utils.prepare_change_name_payload(name, password)
        response_data = await self._request("post", "user_account_modify", data=data)
        return models.APIResult.from_dict(response_data)

    async def change_password(self, old_password: str, new_password: str) -> models.APIResult:
        """
        Change the password of the account.

        Args:
            old_password (str): The old password of the account.
            new_password (str): The new password of the account.

        Returns:
            An object indicating the result of the operation.

        Example:
            ```python
            # result = await client.change_password(old_password='old', new_password='new')
            ```
        """
        data = _utils.prepare_change_password_payload(old_password, new_password)
        response_data = await self._request("post", "user_account_modify", data=data)
        return models.APIResult.from_dict(response_data)

    # Private Helper Methods
    async def _request(
        self, http_method: str, func: str, files: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        url = kwargs.pop("url", _constants.RESOURCE_URL)
        params = kwargs.pop("params", {})
        if "access_token" not in params:
            params["access_token"] = self._token.access_token
        if func:
            params["func"] = func

        try:
            data = await self._execute_request(self._client, http_method, url, params=params, files=files, **kwargs)

            if isinstance(data, dict) and data.get("error") == "expired_token":
                await self._perform_token_refresh()
                params["access_token"] = self._token.access_token
                data = await self._execute_request(self._client, http_method, url, params=params, files=files, **kwargs)

            if isinstance(data, dict) and data.get("result") is not True and "access_token" not in data:
                raise APIError(data.get("error", "Unknown API error"))

            return data
        except APIError as e:
            if e.response and e.response.status_code == 401:
                raise AuthenticationError("Invalid or expired token.", response=e.response) from e
            raise

    async def _perform_token_refresh(self) -> models.RefreshTokenResult:
        if self._token.refresh_token:
            data = _utils.prepare_refresh_token_payload(self._token.refresh_token)
            response = await self._request("post", "", data=data, url=_constants.TOKEN_URL)
        elif self._token.device_code:
            params = _utils.prepare_device_code_params(self._token.device_code)
            response = await self._request("get", "", params=params, url=_constants.DEVICE_AUTHORIZE_URL)
        else:
            raise AuthenticationError("Session expired. No refresh token or device code available.")

        if "access_token" not in response:
            raise AuthenticationError("Token refresh failed. The response did not contain a new access token.")

        self._token.access_token = response["access_token"]
        if self._on_token_refresh:
            self._on_token_refresh(self._token)

        return models.RefreshTokenResult.from_dict(response)

    async def _handle_torrent_file_async(self, torrent_file: str) -> Dict[str, Any]:
        if torrent_file.startswith(("http://", "https://")):
            async with httpx.AsyncClient() as client:
                response = await client.get(torrent_file)
                response.raise_for_status()
                return {"torrent_file": response.content}
        else:
            path = anyio.Path(torrent_file)
            content = await path.read_bytes()
            return {"torrent_file": content}

    async def _delete_item(self, item_type: str, item_id: str) -> models.APIResult:
        data = _utils.prepare_delete_item_payload(item_type, item_id)
        response_data = await self._request("post", "delete", data=data)
        return models.APIResult.from_dict(response_data)

    @classmethod
    async def _create_client_from_auth(
        cls: Type["AsyncSeedr"],
        auth_callable: Callable[[httpx.AsyncClient], Coroutine[Any, Any, Dict[str, Any]]],
        token_callable: Callable[[Dict[str, Any]], Dict[str, Any]],
        on_token_refresh: Optional[Callable[[Token], None]],
        httpx_client: Optional[httpx.AsyncClient],
        **httpx_kwargs: Any,
    ) -> "AsyncSeedr":
        client = httpx_client or httpx.AsyncClient(**httpx_kwargs)
        success = False
        try:
            response_data = await auth_callable(client)
            token_extras = token_callable(response_data)
            token = Token(
                access_token=response_data["access_token"],
                refresh_token=response_data.get("refresh_token"),
                **token_extras,
            )
            instance = cls(
                token, on_token_refresh=on_token_refresh, httpx_client=client, **httpx_kwargs
            )
            success = True
            return instance
        finally:
            if httpx_client is None and not success:
                await client.aclose()

    @classmethod
    async def _execute_request(
        cls: Type["AsyncSeedr"],
        client: httpx.AsyncClient,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        try:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if 500 <= e.response.status_code < 600:
                message = f"Server error: {e.response.status_code} {e.response.reason_phrase}"
                raise ServerError(message, response=e.response) from e
            raise APIError(f"API error: {e.response.status_code}", response=e.response) from e
        except httpx.RequestError as e:
            raise NetworkError(str(e)) from e

    @classmethod
    async def _perform_auth_request(
        cls: Type["AsyncSeedr"],
        client: httpx.AsyncClient,
        method: str,
        url: str,
        error_message: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        try:
            return await cls._execute_request(client, method, url, **kwargs)
        except APIError as e:
            raise AuthenticationError(error_message, response=e.response) from e

    # Dunder Methods (Context Management)
    async def close(self) -> None:
        if self._manages_client_lifecycle:
            await self._client.aclose()

    async def __aenter__(self) -> "AsyncSeedr":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()