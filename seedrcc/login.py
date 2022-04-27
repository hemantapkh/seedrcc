import requests
from base64 import b64encode


def createToken(response, refreshToken=None, deviceCode=None):
    token = {"access_token": response['access_token']}

    if refreshToken or 'refresh_token' in response:
        token['refresh_token'] = refreshToken or response['refresh_token']

    if deviceCode:
        token['device_code'] = deviceCode

    token = b64encode(str(token).encode()).decode()
    return token


class Login():
    """This class contains the methods to generate a login token

    Args:
        email (str, optional): Email address of seedr account
        password (str, optional): Password of seedr account

    Example:
        Logging with email and password

        >>> seedr = Login('foo@foo.com', 'password')

    Example:
        Authorizing with device code

        >>> seedr = Login()
    """
    def __init__(self, email=None, password=None):
        self.email = email
        self.password = password
        self.token = None

    def getDeviceCode(self):
        """
        Generate device and user code

        Example:
            >>> response = seedr.getDeviceCode()
            >>> print(response)
        """
        url = 'https://www.seedr.cc/api/device/code?client_id=seedr_xbmc'

        response = requests.get(url)
        return response.json()

    def authorize(self, deviceCode=None):
        """
        Authorize and get a token for seedr account

        Args:
            deviceCode (str, optional): Device code from
                getDeviceCode() method.

        Example:
            Authorizing with email and password

            >>> response = seedr.authorize()
            >>> print(response)
            >>> print(seedr.token)

        Example:
            Authorizing with device code

            >>> response = seedr.authorize(deviceCode)
            >>> print(response)
            >>> print(seedr.token)

        Note:
            You must use the token from the instance variable 'token'
            instead of the 'access_token' or 'refresh_token' from the
            response.
        """

        if deviceCode:
            url = 'https://www.seedr.cc/api/device/authorize'

            params = {
                'client_id': 'seedr_xbmc',
                'device_code': deviceCode
            }

            response = requests.get(url, params=params).json()

        elif self.email and self.password:
            url = 'https://www.seedr.cc/oauth_test/token.php'

            data = {
                'grant_type': 'password',
                'client_id': 'seedr_chrome',
                'type': 'login',
                'username': self.email,
                'password': self.password
            }

            response = requests.post(url, data=data).json()

        else:
            raise Exception('No device code or email/password provided')

        if 'access_token' in response:
            self.token = createToken(response, deviceCode=deviceCode)

        return response
