from __future__ import annotations

import random
import time
from typing import Any

from art import text2art
from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.timer import Timer
from textual.widgets import RichLog, Static

from modules.caixa_som import caixa_som
from modules.core.logger import logger
from modules.core.navigation import close_current_view


class SecretScreen(Screen[None]):
    """Base comum para os easter eggs do ViberOS no runtime Textual.

    O prefixo ``_viber_`` é intencional: classes do Textual herdam de
    ``MessagePump`` e possuem vários atributos privados próprios. Evitar nomes
    genéricos como ``_closing`` / ``_timers`` impede colisões com o framework.
    """

    BINDINGS = [
        Binding("q", "close_secret", "Voltar", show=True, priority=True),
        Binding("escape", "close_secret", "Voltar", show=False, priority=True),
    ]

    owns_music = False

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._viber_secret_closing = False
        self._viber_owned_timers: list[Timer] = []

    @property
    def secret_closing(self) -> bool:
        return self._viber_secret_closing

    def prepare_for_close(self) -> None:
        """Marca a Screen como encerrando antes do dismiss assíncrono."""
        self._viber_secret_closing = True

    def _track_timer(self, timer: Timer) -> Timer:
        """Registra timers criados pelo easter egg para cleanup no unmount."""
        self._viber_owned_timers.append(timer)
        return timer

    def action_close_secret(self) -> None:
        if self._viber_secret_closing:
            return
        self.prepare_for_close()
        # A navegação integrada usa Screen.dismiss(); em wrappers standalone,
        # close_current_view mantém o comportamento de encerrar o App.
        close_current_view(self)

    def on_unmount(self) -> None:
        self._viber_secret_closing = True
        for timer in self._viber_owned_timers:
            try:
                timer.stop()
            except Exception:
                pass
        self._viber_owned_timers.clear()
        # A limpeza de música fica no lifecycle da Screen, não só no atalho Q.
        # Assim Ctrl+C, término natural ou uma exceção de render também limpam
        # corretamente o contexto sonoro do easter egg.
        if self.owns_music:
            try:
                caixa_som.pausar_musica()
            except Exception:
                logger.exception("Could not stop secret music")


class RickAsciiScreen(SecretScreen):
    """Rickroll convertido para ASCII e renderizado diretamente pelo Textual."""

    owns_music = True

    CSS = """
    RickAsciiScreen {
        background: #000000;
        color: #00ff66;
        layout: vertical;
    }

    #rick-frame {
        height: 1fr;
        width: 1fr;
        content-align: center middle;
        overflow: hidden hidden;
        color: #00ff66;
    }

    #rick-footer {
        height: 1;
        text-align: center;
        color: #008f45;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._viber_capture = None
        self._viber_ascii_player = None
        self._viber_frame_timer = None

    def compose(self) -> ComposeResult:
        yield Static("Preparando vídeo ASCII...", id="rick-frame")
        yield Static("Q / Esc: voltar", id="rick-footer")

    def on_mount(self) -> None:
        from modules.achievements.main_achievements import desbloquear
        from modules.video2ascii import VideoAscii

        desbloquear("sys_segredo")
        self._viber_ascii_player = VideoAscii("rickroll.mp4")

        try:
            import cv2

            self._viber_capture = cv2.VideoCapture(str(self._viber_ascii_player.path))
            fps = float(self._viber_capture.get(cv2.CAP_PROP_FPS) or 0)
            if fps <= 0:
                fps = 24.0
            # Terminais dificilmente ganham algo acima de 30 FPS e limitar o
            # refresh evita o vídeo ASCII monopolizar o event loop.
            fps = min(max(fps, 8.0), 30.0)
            self._viber_frame_timer = self._track_timer(
                self.set_interval(1.0 / fps, self._next_frame, name="viber-rick-frames")
            )
        except Exception:
            logger.exception("Could not initialize Textual ASCII video")
            self.query_one("#rick-frame", Static).update(
                Text(
                    "Não foi possível iniciar o vídeo ASCII.\nQ para voltar.",
                    style="bold red",
                    justify="center",
                )
            )
            return

        try:
            caixa_som.tocar_musica(
                "Rickroll.mp3",
                0.8,
                False,
                0,
                fadein=350,
                transicao=False,
            )
        except Exception:
            logger.exception("Rickroll audio unavailable")

        logger.info("Textual secret started: rick")

    def _next_frame(self) -> None:
        if self.secret_closing or self._viber_capture is None or self._viber_ascii_player is None:
            return

        ret, frame = self._viber_capture.read()
        if not ret:
            self.action_close_secret()
            return

        target = self.query_one("#rick-frame", Static)
        width = max(20, target.size.width - 2)
        height = max(6, target.size.height - 1)
        try:
            rendered = self._viber_ascii_player.get_ascii_frame(
                frame,
                width=width,
                max_height=height,
            )
            target.update(Align.center(rendered, vertical="middle"))
        except Exception:
            logger.exception("ASCII video frame rendering failed")
            self.action_close_secret()

    def on_unmount(self) -> None:
        if self._viber_frame_timer is not None:
            try:
                self._viber_frame_timer.stop()
            except Exception:
                pass
            self._viber_frame_timer = None
        if self._viber_capture is not None:
            try:
                self._viber_capture.release()
            except Exception:
                pass
            self._viber_capture = None
        super().on_unmount()
        logger.info("Textual secret stopped: rick")


class MatrixScreen(SecretScreen):
    """Chuva Matrix sem Rich.Live e sem suspender o App Textual."""

    CSS = """
    MatrixScreen {
        background: #000000;
        color: #00ff44;
        layout: vertical;
    }

    #matrix-canvas {
        height: 1fr;
        width: 1fr;
        overflow: hidden hidden;
    }

    #matrix-footer {
        height: 1;
        text-align: center;
        color: #006622;
    }
    """

    def __init__(self, seconds: float = 10.0) -> None:
        super().__init__()
        self.seconds = max(0.1, float(seconds))
        self._viber_started_at = 0.0
        self._viber_streams: list[int] = []
        self._viber_canvas_shape = (0, 0)

    def compose(self) -> ComposeResult:
        yield Static(id="matrix-canvas")
        yield Static("Q / Esc: voltar", id="matrix-footer")

    def on_mount(self) -> None:
        self._viber_started_at = time.monotonic()
        self._track_timer(
            self.set_interval(0.05, self._tick, name="viber-matrix-animation")
        )
        logger.info("Textual secret started: matrix (%.2fs)", self.seconds)

    def _tick(self) -> None:
        if self.secret_closing:
            return
        try:
            if time.monotonic() - self._viber_started_at >= self.seconds:
                self.action_close_secret()
                return

            canvas = self.query_one("#matrix-canvas", Static)
            cols = max(8, canvas.size.width)
            rows = max(4, canvas.size.height)
            shape = (cols, rows)
            if shape != self._viber_canvas_shape:
                self._viber_canvas_shape = shape
                self._viber_streams = [random.randint(-rows, 0) for _ in range(cols)]

            grid = [[" "] * cols for _ in range(rows)]
            for x, y in enumerate(self._viber_streams):
                for i in range(12):
                    r = y - i
                    if 0 <= r < rows:
                        grid[r][x] = random.choice("01")
                self._viber_streams[x] = y + 1 if y < rows + 12 else random.randint(-rows, 0)

            canvas.update(Text("\n".join("".join(row) for row in grid), style="green"))
        except Exception:
            logger.exception("Matrix Textual animation failed")
            self.action_close_secret()


_DVD_LOGO = text2art("ViberOS").splitlines()
_DVD_COLORS = ["red", "green", "yellow", "blue", "magenta", "cyan", "bright_white"]
_DVD_W = max((len(line) for line in _DVD_LOGO), default=1)
_DVD_H = max(len(_DVD_LOGO), 1)


class DVDScreen(SecretScreen):
    """Logo quicando nas bordas, agora como animação nativa do Textual."""

    CSS = """
    DVDScreen {
        background: #000000;
        layout: vertical;
    }

    #dvd-canvas {
        height: 1fr;
        width: 1fr;
        overflow: hidden hidden;
    }

    #dvd-footer {
        height: 1;
        text-align: center;
        color: #555555;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._viber_x = 2
        self._viber_y = 1
        self._viber_dx = 1
        self._viber_dy = 1
        self._viber_color = random.choice(_DVD_COLORS)

    def compose(self) -> ComposeResult:
        yield Static(id="dvd-canvas")
        yield Static("Q / Esc: voltar", id="dvd-footer")

    def on_mount(self) -> None:
        from modules.achievements.main_achievements import desbloquear

        desbloquear("sys_segredo")
        self._track_timer(
            self.set_interval(0.04, self._tick, name="viber-dvd-animation")
        )
        logger.info("Textual secret started: dvd")

    def _tick(self) -> None:
        if self.secret_closing:
            return
        try:
            canvas = self.query_one("#dvd-canvas", Static)
            cols = max(_DVD_W + 1, canvas.size.width)
            rows = max(_DVD_H + 1, canvas.size.height)

            max_x = max(0, cols - _DVD_W)
            max_y = max(0, rows - _DVD_H)
            self._viber_x = min(max(self._viber_x, 0), max_x)
            self._viber_y = min(max(self._viber_y, 0), max_y)

            hit = False
            if self._viber_x + self._viber_dx < 0 or self._viber_x + self._viber_dx > max_x:
                self._viber_dx *= -1
                hit = True
            if self._viber_y + self._viber_dy < 0 or self._viber_y + self._viber_dy > max_y:
                self._viber_dy *= -1
                hit = True
            if hit:
                choices = [color for color in _DVD_COLORS if color != self._viber_color]
                self._viber_color = random.choice(choices or _DVD_COLORS)

            self._viber_x += self._viber_dx
            self._viber_y += self._viber_dy

            grid = [[" "] * cols for _ in range(rows)]
            for row_offset, line in enumerate(_DVD_LOGO):
                yy = self._viber_y + row_offset
                if not 0 <= yy < rows:
                    continue
                for col_offset, char in enumerate(line):
                    xx = self._viber_x + col_offset
                    if 0 <= xx < cols:
                        grid[yy][xx] = char

            canvas.update(Text("\n".join("".join(row) for row in grid), style=self._viber_color))
        except Exception:
            logger.exception("DVD Textual animation failed")
            self.action_close_secret()


class SoldarScreen(SecretScreen):
    """Easter egg do Kratos apresentado como sequência Textual temporizada."""

    owns_music = True

    CSS = """
    SoldarScreen {
        background: #000000;
        color: #ffffff;
        layout: vertical;
    }

    #soldar-log {
        height: 1fr;
        margin: 1 2;
        border: double #aa0000;
        background: #000000;
        content-align: center middle;
    }

    #soldar-footer {
        height: 1;
        text-align: center;
        color: #662222;
    }
    """

    _LINES = (
        (0.0, "[bold red]Kratos:[/bold red] Homens, queimem a vila!!!!!"),
        (2.0, "E o tempo de Atenas"),
        (4.0, "Destruam turo"),
        (5.0, "e toros!!!"),
        (7.0, "Vamos soldar nosso senhor ARESS!!!!!"),
        (9.5, "Vamos homens acabem com tudo!!!"),
    )

    def __init__(self) -> None:
        super().__init__()

    def compose(self) -> ComposeResult:
        yield RichLog(id="soldar-log", markup=True, highlight=False, wrap=True)
        yield Static("Q / Esc: voltar", id="soldar-footer")

    def on_mount(self) -> None:
        from modules.achievements.main_achievements import desbloquear

        desbloquear("sys_segredo")
        try:
            caixa_som.tocar_musica(
                "homens_queimem_a_vila.mp3",
                0.8,
                False,
                0,
                fadein=250,
                transicao=False,
            )
        except Exception:
            logger.exception("Soldar easter egg audio unavailable")

        _, first_line = self._LINES[0]
        self._append(first_line)
        for delay, line in self._LINES[1:]:
            self._track_timer(
                self.set_timer(
                    delay,
                    lambda line=line: self._append(line),
                    name=f"viber-soldar-line-{delay:g}",
                )
            )
        self._track_timer(
            self.set_timer(12.0, self.action_close_secret, name="viber-soldar-close")
        )
        logger.info("Textual secret started: soldar")

    def _append(self, line: str) -> None:
        if self.secret_closing:
            return
        self.query_one("#soldar-log", RichLog).write(line)

    def on_unmount(self) -> None:
        super().on_unmount()
        logger.info("Textual secret stopped: soldar")

SECRET_SCREEN_FACTORIES = {
    "rick": lambda *args: RickAsciiScreen(),
    "dvd": lambda *args: DVDScreen(),
    "hacker": lambda *args: MatrixScreen(float(args[0]) if args else 10.0),
    "soldar": lambda *args: SoldarScreen(),
}


def make_secret_screen(name: str, *args: Any) -> Screen | None:
    factory = SECRET_SCREEN_FACTORIES.get(name)
    return factory(*args) if factory else None
