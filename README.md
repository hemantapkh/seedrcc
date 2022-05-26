<p align="center">
<img src="https://raw.githubusercontent.com/hemantapkh/seedrcc/master/docs/images/seedrcc.png" align="center" height=250 alt="seedrpy logo" />
</p>

<h2 align='center'>Python API Wrapper of Seedr.cc</h2>

<p align="center">
<a href="https://pypi.org/project/seedrcc">
<img src='https://img.shields.io/pypi/v/seedrcc.svg'>
</a>
<a href="https://pepy.tech/project/seedrcc">
<img src='https://pepy.tech/badge/seedrcc'>
</a>
<a href="https://tinyurl.com/visitors-stats">
<img src='https://visitor-badge.laobi.icu/badge?page_id=hemantapkh.seedrcc'>
</a>
<a href="https://github.com/hemantapkh/seedrcc/stargazers">
<img src="https://img.shields.io/github/stars/hemantapkh/seedrcc" alt="Stars"/>
</a>
<a href="https://github.com/hemantapkh/seedrcc/issues">
<img src="https://img.shields.io/github/issues/hemantapkh/seedrcc" alt="Issues"/>
</a>
<br>
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png">

## Table of Contents
- [Installation](#installation)
- [How I got the API endpoints?](#how-i-got-the-api-endpoints)
- [Start Guide](#start-guide)
    - [Getting Token](#getting-token)
        - [Logging with Username and Password](#logging-with-username-and-password)
        - [Authorizing with device code](#authorizing-with-device-code)
    - [Basic Examples](#basic-examples)
    - [Managing token](#managing-token)
        - [Callback function](#callback-function)
            - [Function with single argument](#callback-function-with-single-argument)
            - [Function with multiple arguments](#callback-function-with-multiple-arguments)
- [Detailed Documentation](#documentation)
- [Contributing](#contributing)
- [Projects using this API](#projects-using-this-api)
- [License](#license)

## Installation
- Install via [PyPi](https://www.pypi.org/project/seedrcc)
    ```bash
    pip install seedrcc
    ```

- Install from the source
    ```bash
    git clone https://github.com/hemantapkh/seedrcc && cd seedrcc && python setup.py sdist && pip install dist/*
    ```

## How I got the API endpoints

Seedr don't provide an [API](https://www.seedr.cc/docs/api/rest/v1/) to the freemium users. However, Seedr has a [chrome](https://github.com/DannyZB/seedr_chrome) and [kodi](https://github.com/DannyZB/seedr_chrome) extension that works for all users. Some of the endpoints (very few) are extracted from these extensions. 

After analyzing the requests sent by the seedr site (old version), I found the seedr-site API (which needs captcha) are quiet similar to that of seedr-chrome and seedr-kode API. So, I just predicted the other endpoints.

**This API works for all users since it uses the seedr-chrome and seedr-kodi API.**

## Start guide

----

### Getting Token

There are two methods to get the account token. You can login with username/password or by authorizing with device code. 


#### Logging with Username and Password

This method uses the seedr Chrome extension API.
```python
from seedrcc import Login

seedr = Login('foo@bar.com', 'password')

response = seedr.authorize()
print(response)

# Getting the token 
print(seedr.token)
```

### Authorizing with device code

This method uses the seedr kodi API.

**To use this method, generate a device & user code. Paste the user code in https://seedr.cc/devices and authorize with the device code.**

```python
from seedrcc import Login

seedr = Login()

deviceCode = seedr.getDeviceCode()
# Go to https://seedr.cc/devices and paste the user code
print(deviceCode)

# Authorize with device code
response = seedr.authorize(deviceCode['device_code'])
print(response)

# Getting the token
seedr.token
```

**✏️ Note: You must use the token from the instance variable ‘token’ instead of the ‘access_token’ or ‘refresh_token’ from the response.**

----

### Basic Examples

For all available methods, please refer to the [documentation](https://seedrcc.readthedocs.org/en/latest/). Also, it is recommended to set a callback function, read more about it [here](#managing-token).

```python
from seedrcc import Seedr

account = Seedr(token='token')

# Getting user settings
print(account.getSettings())

# Adding torrent
response = account.addTorrent('magnetlink')
print(response)

#Listing folder contents
response = account.listContents()
print(response)
```

----

### Managing token

The access token may expire after certain time and need to be refreshed. However, this process is handled by the module and you don't have to worry about it. 

**⚠️ The token is updated after this process and if you are storing the token in a file/database and reading the token from it, It is recommended to update the token in the database/file using the callback function. If you do not update the token in such case, the module will refresh the token in each session which will cost extra request and increase the response time.**

#### Callback function

You can set a callback function which will be called automatically each time the token is refreshed. You can use such function to deal with the refreshed token.

**✏️ Note: The callback function must have at least one parameter. The first parameter of the callback function will be the updated token.**

#### Callback function with single argument

Here is an example of callback function with a single argument which read and update the token in a file called `token.txt`.

```python
# Read the token from token.txt
token = open('token.txt', 'r').read().strip()

# Defining the callback function
def afterRefresh(token):
    with open('token.txt', 'w') as f:
        f.write(token)

account = Seedr(token, callbackFunc=afterRefresh)
```

#### Callback function with multiple arguments

In situations where you need to pass multiple arguments to the callback function, you can use the lambda function. Callback function with multiple arguments can be useful if your app is dealing with multiple users.

Here is an example of callback function with multiple arguments which will update the token of certain user in the database after the token of that user is refreshed.

```python
# Defining the callback function
def afterRefresh(token, userId):
    # Add your code to deal with the database
    print(f'Token of the user {userId} is updated.')

# Creating a Seedr object for user 12345
account = Seedr(token='token', callbackFunc=lambda token: afterRefresh(token, userId='12345'))
```

----

## Documentation

The detailled documentation of each methods is available [here](https://seedrcc.readthedocs.org/en/latest/).


## Contributing

Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


*Thanks to every [contributors](https://github.com/hemantapkh/seedrcc/graphs/contributors) who have contributed in this project.*

## Projects using this API

* Torrent Seedr - Telegram bot to download torrents ([Source code](https://github.com/hemantapkh/torrentseedr), [Link](https://t.me/torrentseedrbot)).

Want to list your project here? Just make a pull request.

## License

Distributed under the MIT License. See [LICENSE](https://github.com/hemantapkh/seedrcc/blob/main/LICENSE) for more information.

---

Author/Maintainer: [Hemanta Pokharel](https://twitter.com/hemantapkh)