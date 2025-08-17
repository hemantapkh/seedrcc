<p align="center">
  <img src="https://raw.githubusercontent.com/hemantapkh/seedrcc/master/docs/images/seedrcc.png" width="250" alt="seedrcc logo">
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

**seedrcc** provides a clean, robust, and fully-featured interface for interacting with the Seedr API, with first-class support for both synchronous and asynchronous operations.

## Features

- **Complete API Coverage:** All major Seedr API endpoints are supported.
- **Sync & Async:** Use `seedrcc.Seedr` for a synchronous client or `seedrcc.AsyncSeedr` for an asynchronous one.
- **Robust Authentication:** Handles all authentication flows, including automatic token refreshes.
- **Modern & Typed:** Built with modern Python features and fully type-hinted for a superior developer experience.
- **Pydantic Models:** API responses are parsed into clean, easy-to-use Pydantic models.

## Installation

Install from PyPI:

```bash
pip install seedrcc
```

Or, install the latest version directly from GitHub:

```bash
pip install git+https://github.com/hemantapkh/seedrcc.git
```

## Usage

### Synchronous Example (with Device Authentication)

```python
from seedrcc import Seedr

# 1. Get the device and user codes from the API.
codes = Seedr.get_device_code()

# 2. Open the verification URL (https://seedr.cc/devices) and enter the user code.
print(f"Please go to {codes.verification_url} and enter the code: {codes.user_code}")
input("Press Enter after authorizing the device.")

# 3. Create the client using the device_code.
with Seedr.from_device_code(codes.device_code) as client:
    settings = client.get_settings()
    print(f"Success! Hello, {settings.account.username}")
```

### Asynchronous Example (with Password Authentication)

```python
import asyncio
from seedrcc import AsyncSeedr

async def main():
    # Authenticate using your username and password.
    async with AsyncSeedr.from_password("your_email@example.com", "your_password") as client:
        # Get your account settings.
        settings = await client.get_settings()
        print(f"Hello, {settings.account.username}!")

if __name__ == "__main__":
    asyncio.run(main())
```

## How I Found the Endpoints

While Seedr.cc offers a premium [API](https://www.seedr.cc/docs/api/rest/v1/), it is not available to free users. This library was built by studying the network requests from the official **[Kodi](https://github.com/DannyZB/seedr_kodi)** and **[Chrome](https://github.com/DannyZB/seedr_chrome)** extensions.

Further analysis of the main Seedr website's network traffic revealed a very similar API pattern, which made it possible to implement the full feature set. Because the library uses the same API as the official tools, it works reliably for all users.

## Documentation

For a complete guide to every available method, data model, and advanced features like saving sessions, please see the **[Full Documentation](https://seedrcc.readthedocs.io/)**.

## Contributing

Contributions are welcome! If you'd like to help, please feel free to fork the repository, create a feature branch, and open a pull request.

## License

This project is distributed under the MIT License. See `LICENSE` for more information.

---
Author/Maintainer: [Hemanta Pokharel](https://hemantapkh.com) ([GitHub](https://github.com/hemantapkh))

