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

- **Full API Coverage:** All major Seedr API endpoints are supported.
- **Both Sync and Async:** Use `seedrcc.Seedr` for a synchronous client or `seedrcc.AsyncSeedr` for an asynchronous one.
- **Robust Authentication:** Handles all authentication flows, including automatic token refreshes.
- **Modern and Typed:** Built with modern Python features and fully type-hinted for a better developer experience.
- **Clean Object Models:** API responses are parsed into clean, easy-to-use dataclasses.

## Installation

Install the library from PyPI using `pip` or your favorite package manager.

```bash
pip install seedrcc
```

## Basic Usage

### Synchronous

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

### Asynchronous

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

## Saving and Reusing a Token

To avoid logging in every time, you can save the `Token` object after your first login and reuse it in the future.

The `Token` object has several methods to convert it for storage or use:

- [`token.to_json()`][seedrcc.token.Token.to_json]: Converts the token to a JSON string, perfect for saving in text files.
- [`token.to_base64()`][seedrcc.token.Token.to_base64]: Converts the token to a simple Base64 string, great for databases or environment variables.
- [`token.to_dict()`][seedrcc.token.Token.to_dict]: Converts the token to a Python dictionary for in-memory use.

You can then use the corresponding `Token.from_...()` method to load it back.

```python
from seedrcc import Seedr, Token

# Assume 'client' is an authenticated client from a previous session
# client = Seedr.from_password("your_email@example.com", "your_password")

# 1. Get the token and convert it to a JSON string
token = client.token
json_string = token.to_json()

# You would typically save this string to a file or database.
print(f"Saved token: {json_string}")


# 2. In a new session, load the token from the saved string
reloaded_token = Token.from_json(json_string)

# 3. Initialize the client directly with the reloaded token
with Seedr(token=reloaded_token) as new_client:
    settings = new_client.get_settings()
    print(f"Successfully re-authenticated as {settings.account.username}")
```

## Handling Token Refreshes

The client will automatically refresh expired access tokens. If you are storing the token to reuse it later, you should provide a callback function to be notified of the new token.

The `on_token_refresh` argument can be passed to any factory method (`from_password`, etc.) or to the client constructor.

When using the `AsyncSeedr` client, you can provide an `async` function for the callback. If a regular synchronous function is provided instead, it will be safely executed in a separate thread to prevent blocking the asynchronous event loop.

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

If you need to pass additional arguments to your callback (like a user ID), you can use a `lambda` for a synchronous callback. For an `async` callback, the recommended approach is to use `functools.partial`.

```python
import functools

# Synchronous example with lambda
def save_token_for_user(token: Token, user_id: int):
    print(f"Saving new token for user {user_id}")
    # ... save to database ...

user_id = 123
client = Seedr.from_password(
    "user", "pass",
    on_token_refresh=lambda token: save_token_for_user(token, user_id)
)

# Asynchronous example with functools.partial
async def save_token_for_user_async(token: Token, user_id: int):
    print(f"Saving new token for user {user_id}")
    # ... save to database ...

user_id = 456
async_callback = functools.partial(save_token_for_user_async, user_id=user_id)
async_client = await AsyncSeedr.from_password(
    "user", "pass", on_token_refresh=async_callback
)
```

## Next Steps

- **API Reference:** Dive into the [Synchronous Client](sync_client.md) or the [Asynchronous Client](async_client.md) reference for detailed information on all available methods.
- **License:** This project is licensed under the MIT License. See the `LICENSE` file for details.
- **Contributing:** Contributions are welcome! Please see the project on [GitHub](https://github.com/hemantapkh/seedrcc).