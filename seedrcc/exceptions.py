from typing import Optional

import httpx


class SeedrError(Exception):
    """Base exception for all seedrcc errors."""


class APIError(SeedrError):
    """Raised when the API returns an error."""

    def __init__(self, message: str, response: Optional[httpx.Response] = None) -> None:
        super().__init__(message)
        self.response = response


class AuthenticationError(SeedrError):
    """Raised when authentication or re-authentication fails."""
