<p align="center">
  <img src="images/seedrcc.png" width="250" alt="seedrcc logo">
</p>

<h1 align="center">seedrcc</h1>

<p align="center">
  <strong>A complete, modern, and fully-featured Python API wrapper for seedr.cc.</strong>
</p>

<p align="center">
<a href="https://pypi.org/project/seedrcc">
<img src='https://img.shields.io/pypi/v/seedrcc.svg'>
</a>
<a href="https://pepy.tech/project/seedrcc">
<img src='https://pepy.tech/badge/seedrcc'>
</a>
<a href="https://github.com/hemantapkh/seedrcc/stargazers">
<img src="https://img.shields.io/github/stars/hemantapkh/seedrcc" alt="Stars"/>
</a>
<a href="https://github.com/hemantapkh/seedrcc/issues">
<img src="https://img.shields.io/github/issues/hemantapkh/seedrcc" alt="Issues"/>
</a>
</p>

---

**seedrcc** provides a clean, modern, and fully-featured interface for interacting with the Seedr API, with support for both synchronous and asynchronous operations.

## Features

-   **Full API Coverage:** All major Seedr API endpoints are supported.
-   **Both Sync and Async:** Use `seedrcc.Seedr` for a synchronous client or `seedrcc.AsyncSeedr` for an asynchronous one.
-   **Robust Authentication:** Handles all authentication flows, including automatic token refreshes.
-   **Modern and Typed:** Built with modern Python features and fully type-hinted for a better developer experience.
-   **Clean Object Models:** API responses are parsed into clean, easy-to-use dataclasses.

## Getting Started

### Installation

Install the library from PyPI using `pip` or your favorite package manager.

```bash
pip install seedrcc
```

### Synchronous Usage

Here's a quick example of how to get started with the synchronous client.

```python
from seedrcc import Seedr

# Authenticate using your username and password
with Seedr.from_password("your_email@example.com", "your_password") as client:
    # Get your account settings
    settings = client.get_settings()
    print(f"Hello, {settings.account.username}!")

    # Add a new torrent
    torrent = client.add_torrent(magnet_link="magnet:?xt=urn:btih:...")
    print(f"Added torrent: {torrent.title}")
```

### Asynchronous Usage

The library also provides a fully asynchronous client.

```python
import asyncio
from seedrcc import AsyncSeedr

async def main():
    # Authenticate using your username and password
    async with AsyncSeedr.from_password("your_email@example.com", "your_password") as client:
        # Get your account settings
        settings = await client.get_settings()
        print(f"Hello, {settings.account.username}!")

        # Add a new torrent
        torrent = await client.add_torrent(magnet_link="magnet:?xt=urn:btih:...")
        print(f"Added torrent: {torrent.title}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Handling Token Refreshes

The client will automatically refresh expired access tokens. If you are storing the token to reuse it later, you should provide a callback function to be notified of the new token.

The `on_token_refresh` argument can be passed to any factory method (`from_password`, etc.) or to the client constructor.

**Callback with a single argument:**

```python
from seedrcc import Seedr, Token

def save_token(token: Token):
    # This function will be called whenever the token is refreshed.
    # You should save the new token data to your database or file.
    print(f"New token received: {token.access_token}")
    with open("token.json", "w") as f:
        f.write(token.to_json())

# When creating the client, pass the callback function.
client = Seedr.from_password("user", "pass", on_token_refresh=save_token)
```

**Callback with multiple arguments:**

If you need to pass additional arguments to your callback (like a user ID), you can use a `lambda`.

```python
def save_token_for_user(token: Token, user_id: int):
    print(f"Saving new token for user {user_id}")
    # ... save to database ...

user_id = 123
client = Seedr.from_password(
    "user", "pass",
    on_token_refresh=lambda token: save_token_for_user(token, user_id)
)
```

## Next Steps

-   **API Reference:** Dive into the [Synchronous Client](sync_client.md) or the [Asynchronous Client](async_client.md) reference for detailed information on all available methods.
-   **License:** This project is licensed under the MIT License. See the `LICENSE` file for details.
-   **Contributing:** Contributions are welcome! Please see the project on [GitHub](https://github.com/hemantapkh/seedrcc).
