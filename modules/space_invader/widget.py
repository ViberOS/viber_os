"""
widget.py  ·  VibeInvadersWidget
---------------------------------
Widget Textual que encapsula todo o loop de jogo.
"""

from __future__ import annotations

from textual.widget import Widget
from textual.app import RenderResult
from textual.events import Key

from modules.space_invader.game import Game
from modules.space_invader.menu_vibe_invader import (
    draw_menu,
    draw_gameover,
    draw_victory,
    tick_anim,
    reset_anim,
)
from modules.space_invader.save import (
    load_highscore,
    save_highscore,
    load_style,
    save_style,
)
from modules.space_invader.config import FPS, apply_style
from modules.space_invader import sound
from modules.core.navigation import close_current_view


_KEY_MAP: dict[str, bytes] = {
    "up":    b'H',
    "down":  b'P',
    "left":  b'K',
    "right": b'M',
    "a":     b'a',
    "d":     b'd',
    "space": b' ',
    "enter": b'\r',
}


class VibeInvadersWidget(Widget):
    """Widget que roda a máquina de estados do Vibe Invaders."""

    can_focus = True

    def __init__(self) -> None:
        super().__init__()

        self._viber_state:         str       = "menu"
        self._viber_game:          Game|None = None
        self._viber_menu_selected: int       = 0
        self._viber_highscore:     int       = load_highscore()
        self._viber_style:         str       = load_style()
        self._viber_gameover_tick: int       = 0
        self._viber_victory_tick:  int       = 0

        apply_style(self._viber_style)

    def on_mount(self) -> None:
        self.focus()
        sound.play_music()
        reset_anim()
        self.set_interval(1 / FPS, self._tick)

    # ── loop principal ───────────────────────────────────────────────────────
    def _tick(self) -> None:
        if self._viber_state == "menu":
            tick_anim()

        elif self._viber_state == "game":
            assert self._viber_game is not None
            self._viber_game.update()

            if self._viber_game.game_over:
                if self._viber_game.score > self._viber_highscore:
                    save_highscore(self._viber_game.score)
                    self._viber_highscore = self._viber_game.score
                sound.stop_music()
                self._viber_state = "gameover"
                self._viber_gameover_tick = 0

            elif self._viber_game.victory:
                if self._viber_game.score > self._viber_highscore:
                    save_highscore(self._viber_game.score)
                    self._viber_highscore = self._viber_game.score
                sound.stop_music()
                self._viber_state = "victory"
                self._viber_victory_tick = 0

        elif self._viber_state == "gameover":
            self._viber_gameover_tick += 1
            if self._viber_gameover_tick >= 72:
                sound.play_music()
                self._viber_state = "menu"
                reset_anim()

        elif self._viber_state == "victory":
            self._viber_victory_tick += 1
            if self._viber_victory_tick >= 96:
                sound.play_music()
                self._viber_state = "menu"
                reset_anim()

        self.refresh()

    # ── input ────────────────────────────────────────────────────────────────
    def on_key(self, event: Key) -> None:
        event.stop()

        key = _KEY_MAP.get(event.key)
        if key is None and len(event.key) == 1:
            key = event.key.encode()

        if self._viber_state == "menu":
            if event.key.lower() in {"q", "escape"}:
                sound.stop_music()
                close_current_view(self)
                return
            # qualquer tecla reseta a animação idle
            if key:
                reset_anim()
            self._handle_menu_key(key)

        elif self._viber_state == "game":
            if key and self._viber_game:
                self._viber_game.handle_input(key)

        elif self._viber_state in ("gameover", "victory"):
            if key:
                sound.play_music()
                self._viber_state = "menu"
                reset_anim()
                self.refresh()

    def _handle_menu_key(self, key: bytes | None) -> None:
        if key is None:
            return

        from modules.space_invader.menu_vibe_invader import handle_menu_input

        result, new_style, self._viber_menu_selected = handle_menu_input(
            key, self._viber_style, self._viber_menu_selected
        )

        if new_style != self._viber_style:
            self._viber_style = new_style
            apply_style(self._viber_style)
            save_style(self._viber_style)

        if result == "game":
            self._viber_game = Game(self._viber_highscore)
            self._viber_state = "game"

        elif result == "exit":
            sound.stop_music()
            close_current_view(self)

    # ── render ───────────────────────────────────────────────────────────────
    def render(self) -> RenderResult:
        if self._viber_state == "menu":
            return draw_menu(self._viber_style, self._viber_menu_selected)

        elif self._viber_state == "game":
            assert self._viber_game is not None
            return self._viber_game.draw()

        elif self._viber_state == "gameover":
            assert self._viber_game is not None
            return draw_gameover(
                self._viber_game.wave, self._viber_game.score, self._viber_highscore
            )

        elif self._viber_state == "victory":
            assert self._viber_game is not None
            return draw_victory(self._viber_game.score, self._viber_highscore)

        return draw_menu(self._viber_style, self._viber_menu_selected)
