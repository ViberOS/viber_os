"""Entrada da interface principal do ViberOS.

Por padrão inicia o menu clássico recriado em Textual. O Vibash é uma
opção dentro dele. O menu Rich antigo continua disponível apenas como modo
legado explícito via ``VIBEROS_LEGACY_SHELL=1`` durante a migração.
"""
from __future__ import annotations

import os

from modules.core.logger import logger


def menu(nome: str, nome_dados: str) -> bool:
    if os.environ.get("VIBEROS_LEGACY_SHELL") == "1":
        from modules.menu_legacy import menu as legacy_menu
        legacy_menu(nome, nome_dados)
        return False

    try:
        from modules.ui.app import run_viberos
        return run_viberos(nome, nome_dados)
    except ImportError:
        logger.exception("Textual is required by the 1.2 refactor")
        raise
    except Exception:
        # Não mistura automaticamente Rich legado com um runtime Textual que
        # acabou de falhar. Isso preserva traceback/log e evita trocar o dono
        # do terminal no meio de uma exceção. O fallback segue disponível pelo
        # opt-in VIBEROS_LEGACY_SHELL=1.
        logger.exception("Integrated Textual UI failed")
        raise
