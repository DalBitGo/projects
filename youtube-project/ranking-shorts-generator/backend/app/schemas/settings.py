from pydantic import BaseModel
from typing import Optional


class VideoSettings(BaseModel):
    default_duration: int = 7
    quality: str = "high"
    fps: int = 30


class TextOverlaySettings(BaseModel):
    font: str = "Arial-Bold"
    color: str = "#FFFFFF"
    position: str = "top-center"


class BackgroundMusicSettings(BaseModel):
    default_track: str = "energetic_1.mp3"
    volume: float = 0.3


class GeneralSettings(BaseModel):
    auto_approve: bool = False
    auto_delete_temp: bool = True


class Settings(BaseModel):
    video: VideoSettings
    text_overlay: TextOverlaySettings
    background_music: BackgroundMusicSettings
    general: GeneralSettings


class SettingsUpdate(BaseModel):
    video: Optional[VideoSettings] = None
    text_overlay: Optional[TextOverlaySettings] = None
    background_music: Optional[BackgroundMusicSettings] = None
    general: Optional[GeneralSettings] = None
