
import httpx

from . import _constants, models


def get_device_code() -> models.DeviceCode:
    """
    Step 1 of the device flow. Gets the device and user codes required for authorization.

    This is a public utility function that can be called without creating a client instance.
    It will not be automatically documented by Sphinx unless this module is explicitly
    included, as it is not part of the main `seedrcc` namespace.

    Example:
        >>> from seedrcc.auth import get_device_code
        >>> codes = get_device_code()
        >>> print(f"Go to {codes.verification_url} and enter {codes.user_code}")

    Returns:
        A `DeviceCode` object containing the necessary information for the next step.
    """
    params = {"client_id": _constants.DEVICE_CLIENT_ID}
    with httpx.Client() as client:
        response = client.get(_constants.DEVICE_CODE_URL, params=params)
        response.raise_for_status()
        response_data = response.json()
    return models.DeviceCode.from_dict(response_data)
