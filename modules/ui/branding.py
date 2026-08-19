"""Elementos visuais compartilhados do ViberOS.

Centraliza a identidade ASCII para evitar que telas diferentes usem fontes
ou variações visuais sem querer.
"""
from __future__ import annotations

from art import text2art


def viberos_logo() -> str:
    """Retorna o mesmo logo ASCII usado no menu clássico do ViberOS."""
    return text2art("ViberOS")
