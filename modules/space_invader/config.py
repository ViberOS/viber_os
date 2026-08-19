FPS = 20
WIDTH  = 40
HEIGHT = 20

# ── estilos ───────────────────────────────────────────────────────────────────
STYLES = {
    "retro": {
        "PLAYER_CHAR":    "A",
        "ENEMY_CHAR":     "W",
        "BULLET_CHAR":    "|",
        "EXPLOSION_CHAR": "*",
    },
    "vibe": {
        "PLAYER_CHAR":    "Λ",
        "ENEMY_CHAR":     "▼",
        "BULLET_CHAR":    "|",
        "EXPLOSION_CHAR": "✹",
    },
}

# valores ativos — alterados em runtime por apply_style()
PLAYER_CHAR    = "A"
ENEMY_CHAR     = "W"
BULLET_CHAR    = "|"
EXPLOSION_CHAR = "*"


_current_style = "retro"


def apply_style(style: str) -> None:
    """Aplica o estilo escolhido nas constantes globais."""
    import modules.space_invader.config as _cfg
    chars = STYLES.get(style, STYLES["retro"])
    _cfg.PLAYER_CHAR    = chars["PLAYER_CHAR"]
    _cfg.ENEMY_CHAR     = chars["ENEMY_CHAR"]
    _cfg.BULLET_CHAR    = chars["BULLET_CHAR"]
    _cfg.EXPLOSION_CHAR = chars["EXPLOSION_CHAR"]
    _cfg._current_style = style
