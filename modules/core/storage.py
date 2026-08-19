"""Leitura/escrita JSON tolerante a falhas e com gravação atômica."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def load_json(path: Path, default: Any) -> Any:
    path = Path(path)
    if not path.exists():
        return default.copy() if isinstance(default, dict) else list(default) if isinstance(default, list) else default

    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (json.JSONDecodeError, OSError, TypeError):
        # Não derruba o ViberOS por causa de save/config corrompido.
        return default.copy() if isinstance(default, dict) else list(default) if isinstance(default, list) else default


def save_json(path: Path, data: Any, *, indent: int = 4) -> None:
    """Salva JSON por arquivo temporário + replace para reduzir corrupção."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")

    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=indent, ensure_ascii=False)
        handle.flush()
        os.fsync(handle.fileno())

    tmp.replace(path)
