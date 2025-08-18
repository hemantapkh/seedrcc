from dataclasses import dataclass, field, fields
from datetime import datetime
from typing import Any, Dict, List, Optional

from ._utils import parse_datetime

__all__ = [
    "File",
    "Torrent",
    "Folder",
    "ListContentsResult",
    "UserSettings",
    "AccountInfo",
    "AccountSettings",
    "FetchFileResult",
    "DeviceCode",
    "CreateArchiveResult",
    "Device",
    "MemoryBandwidth",
    "AddTorrentResult",
    "APIResult",
    "RefreshTokenResult",
    "ScannedTorrent",
    "ScanPageResult",
]


@dataclass(frozen=True)
class _BaseModel:
    """Base model with a raw data field. Internal use only."""

    _raw: Dict[str, Any] = field(repr=False, compare=False, init=False)

    def get_raw(self) -> Dict[str, Any]:
        """Returns the raw, unmodified dictionary from the API response."""
        return self._raw

    @classmethod
    def from_dict(cls, data: dict):
        """Creates a model instance from a dictionary, ignoring unknown fields."""
        model_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in model_fields}
        instance = cls(**filtered_data)
        object.__setattr__(instance, "_raw", data)
        return instance


@dataclass(frozen=True)
class Torrent(_BaseModel):
    """Represents a torrent in the user's account."""

    id: int
    name: str
    size: int
    hash: str
    progress: str
    last_update: Optional[datetime]
    folder: str = ""
    download_rate: int = 0
    upload_rate: int = 0
    torrent_quality: Optional[int] = None
    connected_to: int = 0
    downloading_from: int = 0
    uploading_to: int = 0
    seeders: int = 0
    leechers: int = 0
    warnings: Optional[str] = None
    stopped: int = 0
    progress_url: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Torrent":
        instance = cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            size=data.get("size", 0),
            hash=data.get("hash", ""),
            progress=data.get("progress", ""),
            last_update=parse_datetime(data.get("last_update")),
            folder=data.get("folder", ""),
            download_rate=data.get("download_rate", 0),
            upload_rate=data.get("upload_rate", 0),
            torrent_quality=data.get("torrent_quality"),
            connected_to=data.get("connected_to", 0),
            downloading_from=data.get("downloading_from", 0),
            uploading_to=data.get("uploading_to", 0),
            seeders=data.get("seeders", 0),
            leechers=data.get("leechers", 0),
            warnings=data.get("warnings"),
            stopped=data.get("stopped", 0),
            progress_url=data.get("progress_url"),
        )
        object.__setattr__(instance, "_raw", data)
        return instance


@dataclass(frozen=True)
class File(_BaseModel):
    """Represents a file within Seedr."""

    file_id: int
    name: str
    size: int
    folder_id: int
    folder_file_id: int
    hash: str
    last_update: Optional[datetime] = None
    play_audio: bool = False
    play_video: bool = False
    video_progress: Optional[str] = None
    is_lost: int = 0
    thumb: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "File":
        instance = cls(
            file_id=data.get("file_id", 0),
            name=data.get("name", ""),
            size=data.get("size", 0),
            folder_id=data.get("folder_id", 0),
            folder_file_id=data.get("folder_file_id", 0),
            hash=data.get("hash", ""),
            last_update=parse_datetime(data.get("last_update")),
            play_audio=data.get("play_audio", False),
            play_video=data.get("play_video", False),
            video_progress=data.get("video_progress"),
            is_lost=data.get("is_lost", 0),
            thumb=data.get("thumb"),
        )
        object.__setattr__(instance, "_raw", data)
        return instance


@dataclass(frozen=True)
class Folder(_BaseModel):
    """Represents a folder, which can contain files, torrents, and other folders."""

    id: int
    name: str
    fullname: str
    size: int
    last_update: Optional[datetime]
    is_shared: bool
    play_audio: bool
    play_video: bool
    folders: List["Folder"] = field(default_factory=list)
    files: List[File] = field(default_factory=list)
    torrents: List["Torrent"] = field(default_factory=list)
    parent: Optional[int] = None
    timestamp: Optional[datetime] = None
    indexes: List[Any] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "Folder":
        instance = cls(
            id=data.get("id") or data.get("folder_id") or 0,
            name=data.get("name", ""),
            fullname=data.get("fullname", data.get("name", "")),
            size=data.get("size", 0),
            last_update=parse_datetime(data.get("last_update") or data.get("timestamp")),
            is_shared=data.get("is_shared", False),
            play_audio=data.get("play_audio", False),
            play_video=data.get("play_video", False),
            folders=[Folder.from_dict(f) for f in data.get("folders", [])],
            files=[File.from_dict(f) for f in data.get("files", [])],
            torrents=[Torrent.from_dict(t) for t in data.get("torrents", [])],
            parent=data.get("parent"),
            timestamp=parse_datetime(data.get("timestamp")),
            indexes=data.get("indexes", []),
        )
        object.__setattr__(instance, "_raw", data)
        return instance


@dataclass(frozen=True)
class AccountSettings(_BaseModel):
    """Represents the nested 'settings' object in the user settings response."""

    allow_remote_access: bool
    site_language: str
    subtitles_language: str
    email_announcements: bool
    email_newsletter: bool


@dataclass(frozen=True)
class AccountInfo(_BaseModel):
    """Represents the nested 'account' object in the user settings response."""

    username: str
    user_id: int
    premium: int
    package_id: int
    package_name: str
    space_used: int
    space_max: int
    bandwidth_used: int
    email: str
    wishlist: list
    invites: int
    invites_accepted: int
    max_invites: int


@dataclass(frozen=True)
class UserSettings(_BaseModel):
    """Represents the complete response from the get_settings endpoint."""

    result: bool
    code: int
    settings: AccountSettings
    account: AccountInfo
    country: str

    @classmethod
    def from_dict(cls, data: dict) -> "UserSettings":
        instance = cls(
            result=data.get("result", False),
            code=data.get("code", 0),
            settings=AccountSettings.from_dict(data.get("settings", {})),
            account=AccountInfo.from_dict(data.get("account", {})),
            country=data.get("country", ""),
        )
        object.__setattr__(instance, "_raw", data)
        return instance


@dataclass(frozen=True)
class MemoryBandwidth(_BaseModel):
    """Represents the user's memory and bandwidth usage details."""

    bandwidth_used: int
    bandwidth_max: int
    space_used: int
    space_max: int
    is_premium: int


@dataclass(frozen=True)
class Device(_BaseModel):
    """Represents a device connected to the user's account."""

    client_id: str
    client_name: str
    device_code: str
    tk: str


@dataclass(frozen=True)
class DeviceCode(_BaseModel):
    """Represents the codes used in the device authentication flow."""

    expires_in: int
    interval: int
    device_code: str
    user_code: str
    verification_url: str


@dataclass(frozen=True)
class ScannedTorrent(_BaseModel):
    """Represents a torrent found by the scan_page method."""

    id: int
    hash: str
    size: int
    title: str
    magnet: str
    last_use: Optional[datetime]
    pct: float
    filenames: List[str] = field(default_factory=list)
    filesizes: List[int] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "ScannedTorrent":
        instance = cls(
            id=data.get("id", 0),
            hash=data.get("hash", ""),
            size=data.get("size", 0),
            title=data.get("title", ""),
            magnet=data.get("magnet", ""),
            last_use=parse_datetime(data.get("last_use")),
            pct=data.get("pct", 0.0),
            filenames=data.get("filenames", []),
            filesizes=data.get("filesizes", []),
        )
        object.__setattr__(instance, "_raw", data)
        return instance


@dataclass(frozen=True)
class ListContentsResult(Folder):
    """Represents the result of listing folder contents, including account metadata."""

    space_used: int = 0
    space_max: int = 0
    saw_walkthrough: int = 0
    type: str = ""
    t: List[Optional[datetime]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "ListContentsResult":
        folder = Folder.from_dict(data)
        instance = cls(
            id=folder.id,
            name=folder.name,
            fullname=folder.fullname,
            size=folder.size,
            last_update=folder.last_update,
            is_shared=folder.is_shared,
            play_audio=folder.play_audio,
            play_video=folder.play_video,
            folders=folder.folders,
            files=folder.files,
            torrents=folder.torrents,
            parent=folder.parent,
            timestamp=folder.timestamp,
            indexes=folder.indexes,
            space_used=data.get("space_used", 0),
            space_max=data.get("space_max", 0),
            saw_walkthrough=data.get("saw_walkthrough", 0),
            type=data.get("type", ""),
            t=[parse_datetime(ts) for ts in data.get("t", [])],
        )
        object.__setattr__(instance, "_raw", data)
        return instance


@dataclass(frozen=True)
class AddTorrentResult(_BaseModel):
    """Represents the result of adding a torrent."""

    result: bool
    user_torrent_id: int
    title: str
    torrent_hash: str
    code: Optional[int] = None


@dataclass(frozen=True)
class CreateArchiveResult(_BaseModel):
    """Represents the result of a request to create an archive."""

    result: bool
    archive_id: int
    archive_url: str
    code: Optional[int] = None


@dataclass(frozen=True)
class FetchFileResult(_BaseModel):
    """Represents the result of a request to fetch a file, including the download URL."""

    result: bool
    url: str
    name: str
    size: int
    code: Optional[int] = None


@dataclass(frozen=True)
class RefreshTokenResult(_BaseModel):
    """Represents the response from a token refresh."""

    access_token: str
    expires_in: int
    token_type: str
    scope: Optional[str] = None


@dataclass(frozen=True)
class ScanPageResult(_BaseModel):
    """Represents the full result of a scan_page request."""

    result: bool
    torrents: List[ScannedTorrent]

    @classmethod
    def from_dict(cls, data: dict) -> "ScanPageResult":
        instance = cls(
            result=data.get("result", False), torrents=[ScannedTorrent.from_dict(t) for t in data.get("torrents", [])]
        )
        object.__setattr__(instance, "_raw", data)
        return instance


@dataclass(frozen=True)
class APIResult(_BaseModel):
    """Represents a generic API result for operations that return a simple success/failure."""

    result: bool
    code: Optional[int] = None
