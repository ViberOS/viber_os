from __future__ import annotations

from dataclasses import asdict, dataclass

from modules.core.paths import SETTINGS_FILE
from modules.core.storage import load_json, save_json

VERSION = "1.2.0"
KERNEL_VERSION = "Viberlinux 1.2.0"


@dataclass(slots=True)
class SystemSettings:
    theme: str = "vibe-green"
    language: str = "pt-BR"
    music_volume: float = 0.5
    effects_volume: float = 1.0
    music_autoplay: bool = True
    music_shuffle: bool = True
    music_fade_ms: int = 1600
    show_changelog_after_update: bool = True

    @classmethod
    def load(cls) -> "SystemSettings":
        raw = load_json(SETTINGS_FILE, {})
        valid = {key: value for key, value in raw.items() if key in cls.__dataclass_fields__}
        settings = cls(**valid)
        settings.music_volume = max(0.0, min(float(settings.music_volume), 1.0))
        settings.effects_volume = max(0.0, min(float(settings.effects_volume), 1.0))
        settings.music_fade_ms = max(0, min(int(settings.music_fade_ms), 10_000))
        return settings

    def save(self) -> None:
        save_json(SETTINGS_FILE, asdict(self))


settings = SystemSettings.load()
