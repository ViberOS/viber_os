from __future__ import annotations

from pathlib import Path

from modules.core.storage import load_json, save_json

SAVE_FILE = Path(__file__).parent / "score" / "save.json"


def _load_data() -> dict:
    data = load_json(SAVE_FILE, {})
    return data if isinstance(data, dict) else {}


def load_highscore() -> int:
    try:
        return max(0, int(_load_data().get("highscore", 0)))
    except (TypeError, ValueError):
        return 0


def save_highscore(score) -> None:
    data = _load_data()
    data["highscore"] = max(0, int(score))
    save_json(SAVE_FILE, data)


def load_style() -> str:
    style = str(_load_data().get("style", "retro"))
    return style if style in {"retro", "vibe"} else "retro"


def save_style(style: str) -> None:
    data = _load_data()
    data["style"] = style if style in {"retro", "vibe"} else "retro"
    save_json(SAVE_FILE, data)
