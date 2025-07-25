from dataclasses import dataclass, field, fields
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class BaseModel:
    """Base model with a raw data field."""
    _raw: Dict[str, Any] = field(repr=False, compare=False, init=False)

    def raw(self) -> Dict[str, Any]:
        """Returns the raw, unmodified dictionary from the API response."""
        return self._raw

    @classmethod
    def from_dict(cls, data: dict):
        """
        Creates a model instance from a dictionary, ignoring unknown fields.
        This is the generic constructor. Complex models should override this.
        """
        # Use `fields` from dataclasses to get all defined fields for the class
        model_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in model_fields}
        instance = cls(**filtered_data)
        instance._raw = data
        return instance


@dataclass
class File(BaseModel):
    """Represents a file within Seedr."""
    id: int
    name: str
    size: int
    folder_id: int
    storage: str
    last_updated: Optional[datetime] = None
    stream_link: Optional[str] = None
    stream_audio: Optional[str] = None
    video_codec: Optional[str] = None
    video_height: Optional[int] = None
    video_width: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> "File":
        """Creates a File object from a dictionary."""
        last_updated_str = data.get("last_updated")
        last_updated_dt = None
        if last_updated_str:
            try:
                last_updated_dt = datetime.strptime(
                    last_updated_str, "%Y-%m-%d %H:%M:%S"
                )
            except (ValueError, TypeError):
                pass  # Keep it as None if parsing fails

        instance = cls(
            id=data["id"],
            name=data["name"],
            size=data["size"],
            folder_id=data["folder_id"],
            storage=data["storage"],
            last_updated=last_updated_dt,
            stream_link=data.get("stream_link"),
            stream_audio=data.get("stream_audio"),
            video_codec=data.get("video_codec"),
            video_height=data.get("video_height"),
            video_width=data.get("video_width"),
        )
        instance._raw = data
        return instance


@dataclass
class Folder(BaseModel):
    """Represents a folder within Seedr, which can contain files and other folders."""
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
    parent_id: Optional[int] = None
    timestamp: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Folder":
        """Creates a Folder object from a dictionary, recursively."""
        sub_folders_data = data.get("folders", [])
        sub_folders = [cls.from_dict(f) for f in sub_folders_data]

        files_data = data.get("files", [])
        files = [File.from_dict(f) for f in files_data]

        torrents_data = data.get("torrents", [])
        torrents = [Torrent.from_dict(t) for t in torrents_data]

        parent_id = data.get("parent_id", data.get("parent"))

        last_updated_str = data.get("last_update", data.get("timestamp"))
        last_updated_dt = None
        if last_updated_str:
            try:
                # Handle both string and potential integer timestamps
                if isinstance(last_updated_str, int):
                    last_updated_dt = datetime.fromtimestamp(last_updated_str)
                else:
                    last_updated_dt = datetime.strptime(
                        last_updated_str, "%Y-%m-%d %H:%M:%S"
                    )
            except (ValueError, TypeError):
                pass  # Keep it as None if parsing fails

        timestamp_str = data.get("timestamp")
        timestamp_dt = None
        if timestamp_str:
            try:
                if isinstance(timestamp_str, int):
                    timestamp_dt = datetime.fromtimestamp(timestamp_str)
                else:
                    timestamp_dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                pass

        instance = cls(
            id=data.get("id") or data.get("folder_id") or 0,
            name=data.get("name", ""),
            fullname=data.get("fullname", data.get("name", "")),
            size=data.get("size", 0),
            last_update=last_updated_dt,
            is_shared=data.get("is_shared", False),
            play_audio=data.get("play_audio", False),
            play_video=data.get("play_video", False),
            folders=sub_folders,
            files=files,
            torrents=torrents,
            parent_id=parent_id,
            timestamp=timestamp_dt,
        )
        instance._raw = data
        return instance


@dataclass
class FetchFileResult(BaseModel):
    """Represents the result of fetching a file's download URL."""
    result: bool
    url: str
    name: str
    size: int
    code: Optional[int] = None


@dataclass
class CreateArchiveResult(BaseModel):
    """Represents the result of creating an archive."""
    result: bool
    archive_id: int
    archive_url: str
    code: Optional[int] = None


@dataclass
class AccountSettings:
    """Represents the user's configurable account settings."""
    allow_remote_access: bool
    site_language: str
    subtitles_language: str
    email_announcements: bool
    email_newsletter: bool


@dataclass
class AccountInfo:
    """Represents the user's account status and information."""
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


@dataclass
class UserSettings(BaseModel):
    """Represents the complete user settings and account information."""
    settings: AccountSettings
    account: AccountInfo
    country: str

    @classmethod
    def from_dict(cls, data: dict) -> "UserSettings":
        """Creates a UserSettings object from the API response dictionary."""
        settings_data = data.get("settings", {})
        account_data = data.get("account", {})

        instance = cls(
            settings=AccountSettings(**settings_data),
            account=AccountInfo(**account_data),
            country=data.get("country", ""),
        )
        instance._raw = data
        return instance


@dataclass
class Device(BaseModel):
    """Represents a device connected to the user's account."""
    client_id: str
    client_name: str
    device_code: str
    tk: str


@dataclass
class MemoryBandwidth(BaseModel):
    """Represents the user's memory and bandwidth usage."""
    bandwidth_used: int
    bandwidth_max: int
    space_used: int
    space_max: int
    is_premium: int


@dataclass
class APIResult(BaseModel):
    """Represents a generic, simple API result."""
    result: bool
    code: Optional[int] = None


@dataclass
class AddTorrentResult(BaseModel):
    """Represents the result of adding a torrent."""
    result: bool
    user_torrent_id: int
    title: str
    torrent_hash: str
    code: Optional[int] = None


@dataclass
class Torrent(BaseModel):
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
        """Creates a Torrent object from a dictionary."""
        last_updated_str = data.get("last_update")
        last_updated_dt = None
        if last_updated_str:
            try:
                last_updated_dt = datetime.strptime(
                    last_updated_str, "%Y-%m-%d %H:%M:%S"
                )
            except (ValueError, TypeError):
                pass

        instance = cls(
            id=data["id"],
            name=data["name"],
            size=data["size"],
            hash=data["hash"],
            progress=data["progress"],
            last_update=last_updated_dt,
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
        instance._raw = data
        return instance
