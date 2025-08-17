import json
from typing import Optional

import httpx


class SeedrError(Exception):
    """Base exception for all seedrcc errors."""


class APIError(SeedrError):
    """
    Raised when the API returns an error.

    Attributes:
        response (Optional[httpx.Response]): The full HTTP response object.
        code (Optional[int]): The custom error code from the API response body.
        error_type (Optional[str]): The type of error from the API response body (e.g., 'parsing_error').
    """

    def __init__(self, message: str, response: Optional[httpx.Response] = None) -> None:
        super().__init__(message)
        self.response = response
        self.code: Optional[int] = None
        self.error_type: Optional[str] = None

        if response:
            try:
                data = response.json()
                if isinstance(data, dict):
                    self.code = data.get("code")
                    self.error_type = data.get("result")
            except (json.JSONDecodeError, KeyError):
                # Not a valid JSON API error, or keys are missing.
                # We just have the raw response.
                pass


class ServerError(SeedrError):
    """Raised for 5xx server-side errors."""

    def __init__(self, message: str, response: Optional[httpx.Response] = None) -> None:
        super().__init__(message)
        self.response = response


class AuthenticationError(SeedrError):
    """
    Raised when authentication or re-authentication fails.

    Attributes:
        response (Optional[httpx.Response]): The full HTTP response object from the failed auth attempt.
        error_type (Optional[str]): The error type from the API response body (e.g., 'invalid_grant').
    """

    def __init__(self, message: str, response: Optional[httpx.Response] = None) -> None:
        self.response = response
        self.error_type: Optional[str] = None

        # Attempt to parse a more specific error message from the response
        if response:
            try:
                data = response.json()
                if isinstance(data, dict):
                    # Use 'error_description' as the main message if available
                    if "error_description" in data:
                        message = data["error_description"]
                    self.error_type = data.get("error")
            except (json.JSONDecodeError, KeyError):
                # Not a valid JSON API error, just use the initial message.
                pass

        super().__init__(message)


class NetworkError(SeedrError):
    """Raised for network-level errors, such as timeouts or connection problems."""

    pass


class TokenError(SeedrError):
    """Raised for errors related to token serialization or deserialization."""

    pass
