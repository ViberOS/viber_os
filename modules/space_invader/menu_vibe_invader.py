"""
menu_vibe_invader.py
"""

from __future__ import annotations
import random
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.console import Group
from art import text2art

from modules.space_invader.config import WIDTH, HEIGHT

MENU_ITEMS = ["jogar", "estilo", "sair"]

_W = WIDTH + 4   # 44
_H = HEIGHT + 4  # 24

# ── letras do INVADERS pré-renderizadas em mini ───────────────────────────────
_WORD    = "INVADERS"
_N       = len(_WORD)
_LETTERS : list[list[str]] = []
_BASE_X  : list[int]       = []
_WIDTHS  : list[int]       = []

_x = 0
for _i, _ch in enumerate(_WORD):
    _rows = text2art(_ch, font="mini").split("\n")[:3]
    while len(_rows) < 3:
        _rows.append("")
    _w = max((len(r) for r in _rows), default=4)
    _rows = [r.ljust(_w) for r in _rows]
    _LETTERS.append(_rows)
    _BASE_X.append(_x)
    _WIDTHS.append(_w)
    _x += _w + (1 if _i < _N - 2 else 0)  # 1 espaço entre letras exceto as 2 últimas

_TOTAL_W = _x  # 40

_CENTERS = [_BASE_X[i] + _WIDTHS[i] // 2 for i in range(_N)]
_BROKEN_Y = [0, 2, 1, 0, 2, 0, 1, 2]
_MID      = _N // 2
_SPREAD_X = [(i - _MID) * 4 for i in range(_N)]
_TARGETS  = [1, 4, 7]   # N, D, S

_VIBE_LINES = text2art("VIBE", font="mini").split("\n")[:3]

# Canvas: 5 linhas de INVADERS + 4 linhas de zona de balas = 9 fixas
_INV_ROWS   = 5
_BZONE_ROWS = 4
_CANVAS_H   = _INV_ROWS + _BZONE_ROWS  # 9


def _render_canvas(y_off: list[int], x_off: list[int],
                   shake: dict[int, int],
                   bullets: list[dict]) -> list[tuple[str, bool]]:
    """
    Retorna 9 linhas de (texto, tem_bala).
    'tem_bala' indica se essa linha tem algum '|' de bala — renderizado em branco.
    """
    MARGIN = 15
    CANVAS_W = _TOTAL_W + MARGIN * 1

    # grade de chars — INVADERS nas linhas 0-4
    grid = [[" "] * CANVAS_W for _ in range(_CANVAS_H)]

    for idx in range(_N):
        xpos = _BASE_X[idx] + x_off[idx] + shake.get(idx, 0) + MARGIN
        yo   = y_off[idx]
        for row_i, line in enumerate(_LETTERS[idx]):
            ar = row_i + yo
            for col_i, ch in enumerate(line):
                nx = xpos + col_i
                if 0 <= ar < _INV_ROWS and 0 <= nx < CANVAS_W:
                    grid[ar][nx] = ch

    # posições das balas na grade (para saber onde pintar de branco)
    bullet_cells: set[tuple[int, int]] = set()
    for b in bullets:
        # bala.y é float de 0.0 (topo INVADERS) a _BZONE_ROWS (fundo zona)
        row = _INV_ROWS + int(b["y"])   # linha no canvas
        col = b["x"] + MARGIN
        if 0 <= row < _CANVAS_H and 0 <= col < CANVAS_W:
            bullet_cells.add((row, col))

    # recorta pra _TOTAL_W colunas
    start = MARGIN
    end   = MARGIN + _TOTAL_W + 1
    result = []
    for ri in range(_CANVAS_H):
        row_str = "".join(grid[ri][start:end])
        has_bullet = any(c == ri for (c, _) in bullet_cells if start <= _ < end)
        # substitui células de bala no texto pela posição correta
        if has_bullet:
            chars = list(row_str)
            for (c, col) in bullet_cells:
                if c == ri:
                    ci = col - start
                    if 0 <= ci < len(chars):
                        chars[ci] = "|"
            row_str = "".join(chars)
        result.append((row_str, has_bullet,
                       [(col - start) for (c, col) in bullet_cells if c == ri
                        and start <= col < end]))
    return result  # list of (str, bool, [bullet_x_positions])


# ── animação ──────────────────────────────────────────────────────────────────
class _MenuAnim:
    IDLE_FRAMES   = 20 * 20
    BROKEN_FRAMES =  5 * 20
    SHAKE_DUR     =  6
    SHAKE_STRONG  = 12
    FIX_RATE      =  6

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._phase        : str             = "idle"
        self._tick         : int             = 0
        self._bullets      : list[dict]      = []
        self._hits         : set[int]        = set()
        self._y_off        : list[int]       = [0] * _N
        self._x_off        : list[int]       = [0] * _N
        self._shake        : dict[int, list] = {}
        self._strong_shake : int             = 0
        self._fix_cursor   : int             = 0
        self._fix_tick     : int             = 0

    def notify_input(self) -> None:
        self.reset()

    def tick(self) -> None:
        self._tick += 1

        if self._phase == "idle":
            if self._tick >= self.IDLE_FRAMES:
                self._start_shooting()

        elif self._phase == "shooting":
            self._update_bullets()

        elif self._phase == "broken":
            if self._tick >= self.BROKEN_FRAMES:
                self._phase      = "fixing"
                self._tick       = 0
                self._fix_cursor = 0
                self._fix_tick   = 0

        elif self._phase == "fixing":
            self._fix_tick += 1
            if self._fix_tick >= self.FIX_RATE:
                self._fix_tick = 0
                if self._fix_cursor < _N:
                    i = self._fix_cursor
                    self._x_off[i] = 0
                    self._y_off[i] = 0
                    self._shake[i] = [4, 1]
                    self._fix_cursor += 1
                else:
                    self.reset()

        for k in list(self._shake.keys()):
            self._shake[k][0] -= 1
            if self._shake[k][0] <= 0:
                del self._shake[k]

        if self._strong_shake > 0:
            self._strong_shake -= 1

    def _start_shooting(self) -> None:
        self._phase   = "shooting"
        self._tick    = 0
        self._bullets = []
        self._hits    = set()
        # balas começam no fundo da zona (_BZONE_ROWS-1) com 3 frames de distância
        for launch_i, letter_idx in enumerate(_TARGETS):
            self._bullets.append({
                "x"   : _CENTERS[letter_idx],
                "y"   : float(_BZONE_ROWS - 1 - launch_i * 1.2),
                "li"  : letter_idx,
                "hit" : False,
            })

    def _update_bullets(self) -> None:
        for b in self._bullets:
            if b["hit"]:
                continue
            b["y"] -= 0.35   # sobe no canvas (y decresce)

            if b["y"] <= 0:  # chegou na zona do INVADERS
                b["hit"] = True
                li = b["li"]
                self._hits.add(li)

                if len(self._hits) == len(_TARGETS):
                    self._strong_shake = self.SHAKE_STRONG
                    self._y_off        = list(_BROKEN_Y)
                    self._x_off        = list(_SPREAD_X)
                    self._phase        = "broken"
                    self._tick         = 0
                else:
                    self._shake[li] = [self.SHAKE_DUR, random.choice([-1, 1])]

        # limpa balas que já acertaram
        self._bullets = [b for b in self._bullets if not b["hit"]]

        # ciclo não terminou mas balas acabaram — reinicia
        if not self._bullets and self._phase == "shooting":
            if len(self._hits) < len(_TARGETS):
                self.reset()

    def get_shake(self) -> dict[int, int]:
        result: dict[int, int] = {}
        if self._strong_shake > 0:
            d = 2 if self._strong_shake > 6 else 1
            d = d if self._strong_shake % 2 == 0 else -d
            for i in range(_N):
                result[i] = d
        else:
            for li, (frames, direction) in self._shake.items():
                result[li] = direction if frames % 2 == 0 else -direction
        return result

    @property
    def bullets(self) -> list[dict]:
        return [b for b in self._bullets if not b["hit"]]

    @property
    def y_off(self) -> list[int]: return self._y_off
    @property
    def x_off(self) -> list[int]: return self._x_off


_anim = _MenuAnim()


def reset_anim() -> None:
    _anim.reset()

def tick_anim() -> None:
    _anim.tick()


# ── draw_menu ─────────────────────────────────────────────────────────────────
def draw_menu(style: str = "retro", selected: int = 0) -> Align:

    # VIBE
    vibe_text = Text(justify="center")
    for line in _VIBE_LINES:
        vibe_text.append(line + "\n", style="bold green")

    # canvas unificado (INVADERS + balas) — 9 linhas fixas
    canvas_rows = _render_canvas(
        _anim.y_off, _anim.x_off, _anim.get_shake(), _anim.bullets
    )

    canvas_text = Text(justify="center")
    for (row_str, _, bullet_cols) in canvas_rows:
        if not bullet_cols:
            # linha sem bala — tudo verde
            canvas_text.append(row_str + "\n", style="bold green")
        else:
            # linha com bala(s) — pinta char a char
            for ci, ch in enumerate(row_str):
                if ci in bullet_cols:
                    canvas_text.append(ch, style="bold white")
                else:
                    canvas_text.append(ch, style="bold green")
            canvas_text.append("\n")

    versao = Text("v1.2", style="dim green", justify="center")

    labels = [
        "Jogar",
        f"Estilo:  {'RETRO (Easy)' if style == 'retro' else 'VIBE (Hard)'}",
        "Voltar ao ViberOS",
    ]
    menu = Text(justify="center")
    menu.append("\n")
    for i, label in enumerate(labels):
        if i == selected:
            menu.append(f"▶  {label}\n\n", style="bold green")
        else:
            menu.append(f"   {label}\n\n", style="dim green")

    ctrl = Text(justify="center")
    ctrl.append("↑ ↓: Navegar  |  Enter: Confirmar\n", style="bold green")
    ctrl.append("A/←: Esquerda  |  D/→: Direita  |  Espaço: Atirar  |  Q: Voltar (menu)",
                style="dim green")

    conteudo = Group(vibe_text, canvas_text, versao, menu, ctrl)

    panel = Panel(
        conteudo,
        border_style="green",
        width=_W,
        height=_H,
        expand=False,
    )
    return Align.center(panel, vertical="middle")


# ── gameover / victory ────────────────────────────────────────────────────────
def draw_gameover(wave: int, score: int, highscore: int) -> Align:
    titulo = Text(justify="center")
    for line in text2art("GAME OVER", font="mini").split("\n")[:3]:
        titulo.append(line + "\n", style="bold red")
    dados = Text(justify="center")
    dados.append("\n")
    dados.append(f"{'WAVE':<12}{wave}\n\n",        style="bold green")
    dados.append(f"{'SCORE':<12}{score}\n\n",       style="bold green")
    dados.append(f"{'HIGHSCORE':<12}{highscore}\n", style="bold green")
    panel = Panel(
        Align.center(Group(titulo, dados), vertical="middle"),
        border_style="green", width=_W, height=_H, expand=False,
    )
    return Align.center(panel, vertical="middle")


def draw_victory(score: int, highscore: int) -> Align:
    titulo = Text(justify="center")
    for line in text2art("YOU WIN", font="mini").split("\n")[:3]:
        titulo.append(line + "\n", style="bold yellow")
    dados = Text(justify="center")
    dados.append("\n")
    dados.append("BOSS DERROTADO!\n\n",              style="bold yellow")
    dados.append(f"{'SCORE':<12}{score}\n\n",        style="bold green")
    dados.append(f"{'HIGHSCORE':<12}{highscore}\n",  style="bold green")
    panel = Panel(
        Align.center(Group(titulo, dados), vertical="middle"),
        border_style="yellow", width=_W, height=_H, expand=False,
    )
    return Align.center(panel, vertical="middle")


# ── input ─────────────────────────────────────────────────────────────────────
def handle_menu_input(
    key: bytes | None,
    style: str = "retro",
    selected: int = 0,
) -> tuple[str, str, int]:
    if key is None:
        return "menu", style, selected
    if key == b'H':
        selected = (selected - 1) % len(MENU_ITEMS)
    elif key == b'P':
        selected = (selected + 1) % len(MENU_ITEMS)
    elif key in (b'\r', b'\n'):
        item = MENU_ITEMS[selected]
        if item == "jogar":   return "game", style, selected
        elif item == "estilo": return "menu", _toggle_style(style), selected
        elif item == "sair":   return "exit", style, selected
    elif key in (b'K', b'M'):
        if MENU_ITEMS[selected] == "estilo":
            return "menu", _toggle_style(style), selected
    return "menu", style, selected


def _toggle_style(current: str) -> str:
    return "vibe" if current == "retro" else "retro"
