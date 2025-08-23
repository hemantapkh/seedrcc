<p align="center">
  <img src="https://raw.githubusercontent.com/hemantapkh/seedrcc/master/docs/images/seedrcc.png" width="250" alt="seedrcc logo">
</p>

<h1 align="center">seedrcc</h1>

<p align="center">
  <strong>A comprehensive Python API wrapper for seedr.cc.</strong>
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

**seedrcc** provides a clean Python interface for the Seedr API, with support for both synchronous and asynchronous operations.

<details>
<summary><strong>Table of Contents</strong></summary>

- [✨ Features](#-features)
- [📦 Installation](#-installation)
- [🚀 Usage](#-usage)
- [🗺️ How I Found the Endpoints](#️-how-i-found-the-endpoints)
- [📚 Documentation](#-documentation)
- [🙌 Contributing](#-contributing)
- [📄 License](#-license)

</details>

## ✨ Features

- **Complete API Coverage:** All major Seedr API endpoints are supported.
- **Works for All Users:** Fully functional for both free and premium Seedr accounts.
- **Sync & Async:** Includes `seedrcc.Seedr` for synchronous operations and `seedrcc.AsyncSeedr` for asynchronous ones.
- **Robust Authentication:** Handles all authentication flows, including automatic token refreshes.
- **Fully Typed:** Provides type hints for all methods and models to improve code quality and clarity.
- **Custom Exceptions:** Provides specific exceptions for API, network, and authentication errors.
- **Dataclass Models:** API responses are parsed into clean, easy-to-use dataclasses.

## 📦 Installation

Install from PyPI:

```bash
pip install seedrcc
```

Or, install the latest version directly from GitHub:

```bash
pip install git+https://github.com/hemantapkh/seedrcc.git
```

## 🚀 Usage

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

<a name="how-i-got-the-api-endpoints"></a>
## 🗺️ How I Found the Endpoints

While Seedr.cc offers a premium [API](https://www.seedr.cc/docs/api/rest/v1/), it is not available to free users. This library was built by studying the network requests from the official **[Kodi](https://github.com/DannyZB/seedr_kodi)** and **[Chrome](https://github.com/DannyZB/seedr_chrome)** extensions.

Further analysis of the main Seedr website's network traffic revealed a very similar API pattern, which made it possible to implement the full feature set. Because the library uses the same API as the official tools, it works reliably for all users.

## 📚 Documentation

For a complete guide to every available method, data model, and advanced features like saving sessions, please see the **[Full Documentation](https://seedrcc.readthedocs.io/)**.

## 🙌 Contributing

Contributions are welcome! If you'd like to help, please feel free to fork the repository, create a feature branch, and open a pull request.

## 📄 License

This project is distributed under the MIT License. See `LICENSE` for more information.

---
Author/Maintainer: [Hemanta Pokharel](https://hemantapkh.com) ([GitHub](https://github.com/hemantapkh))

