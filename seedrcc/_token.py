import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


@dataclass
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
        # Use a custom dict_factory to filter out None values
        return asdict(self, dict_factory=lambda x: {k: v for (k, v) in x if v is not None})

    def to_json(self) -> str:
        """
        Returns the token data as a JSON string.
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Token":
        """Creates a Token object from a dictionary."""
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> "Token":
        """
        Creates a Token object from a JSON string.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
