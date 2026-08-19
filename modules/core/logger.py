from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from modules.core.paths import LOG_DIR

LOG_DIR.mkdir(parents=True, exist_ok=True)
_LOG_FILE = LOG_DIR / "viber_os.log"

logger = logging.getLogger("viber_os")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    handler = RotatingFileHandler(
        _LOG_FILE,
        maxBytes=512_000,
        backupCount=3,
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(handler)


def command_name(raw: str) -> str:
    """Retorna só o nome do comando para não gravar conteúdo do usuário no log."""
    raw = raw.strip()
    return raw.split(maxsplit=1)[0].lower() if raw else "<empty>"
