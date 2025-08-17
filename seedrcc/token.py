import base64
import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

from .exceptions import TokenError


@dataclass(frozen=True)
class Token:
    """
    Represents the authentication tokens for a Seedr session.
    """

    access_token: str
    refresh_token: Optional[str] = None
    device_code: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Returns the token data as a dictionary, excluding any fields that are None.
        """
        return asdict(self, dict_factory=lambda x: {k: v for (k, v) in x if v is not None})

    def to_json(self) -> str:
        """
        Returns the token data as a JSON string.
        """
        return json.dumps(self.to_dict())

    def to_base64(self) -> str:
        """
        Returns the token data as a Base64-encoded JSON string.
        """
        json_str = self.to_json()
        return base64.b64encode(json_str.encode("utf-8")).decode("utf-8")

    def __iter__(self):
        """Allows the object to be converted to a dict using dict()."""
        yield from self.to_dict().items()

    def __str__(self) -> str:
        """
        Returns the JSON representation of the token.
        """
        return self.to_json()

    def __repr__(self) -> str:
        """
        Provides a safe, masked representation of the Token that avoids leaking secrets.
        """

        def _mask(value: Optional[str]) -> str:
            if value is None:
                return "None"
            return f"{value[:5]}****"

        parts = [
            f"access_token={_mask(self.access_token)}",
            f"refresh_token={_mask(self.refresh_token)}",
            f"device_code={_mask(self.device_code)}",
        ]
        return f"Token({', '.join(parts)})"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Token":
        """
        Creates a Token object from a dictionary.
        """
        try:
            return cls(**data)
        except TypeError as e:
            raise TokenError(f"Failed to create Token from dictionary: {e}") from e

    @classmethod
    def from_json(cls, json_str: str) -> "Token":
        """
        Creates a Token object from a JSON string.
        """
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise TokenError(f"Failed to decode JSON: {e}") from e

    @classmethod
    def from_base64(cls, b64_str: str) -> "Token":
        """
        Creates a Token object from a Base64-encoded JSON string.
        """
        try:
            json_str = base64.b64decode(b64_str).decode("utf-8")
            return cls.from_json(json_str)
        except (ValueError, TypeError) as e:
            raise TokenError(f"Failed to decode Base64 string: {e}") from e
