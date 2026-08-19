from __future__ import annotations

from pathlib import Path

from art import text2art
from rich import box
from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.text import Text
from textual.app import App, ComposeResult, RenderResult
from textual.events import Key
from textual.widget import Widget

from modules.achievements.main_achievements import desbloquear
from modules.caixa_som import caixa_som
from modules.core.logger import logger
from modules.core.navigation import close_current_view


_MUSIC_LOGO = text2art("MUSICAS")


def draw_biblioteca(musicas: list[Path], selected: int, error_message: str = "") -> Align:
    titulo = Panel(Align.center(_MUSIC_LOGO), style="green", box=box.DOUBLE)

    lista = Text()
    if not musicas:
        lista.append("\nNenhuma música disponível.\n", style="yellow")
    else:
        for i, music in enumerate(musicas):
            numero = f"{i + 1:02d}"
            if i == selected:
                lista.append(f"\n[{numero}]  ▶  {music.stem}\n", style="bold green")
            else:
                lista.append(f"\n[{numero}]     {music.stem}\n", style="dim green")

    atual_raw = caixa_som.get_musica_atual() or "—"
    atual = "Mudo" if atual_raw == "mute" else Path(str(atual_raw)).stem
    musica_atual = Text(f"\nMúsica atual: {atual}\n", justify="center", style="bold green")
    dicas = Text(
        "↑ ↓: Navegar | Enter: Tocar | N: Próxima | M: Mudo | Q/Esc: Voltar",
        justify="center",
        style="dim green",
    )
    itens = [titulo, lista, musica_atual]
    if error_message:
        itens.append(Text(error_message, justify="center", style="bold red"))
    itens.append(dicas)
    panel = Panel(Group(*itens), border_style="green")
    return Align.center(panel, vertical="middle")


class MusicLibraryWidget(Widget):
    can_focus = True

    def __init__(self) -> None:
        super().__init__()
        self.musicas = caixa_som.listar_musicas()
        self.selected = 0
        self.error_message = ""

    def on_mount(self) -> None:
        try:
            caixa_som.init()
        except Exception:
            logger.exception("Music library could not initialize audio")
            self.error_message = "Áudio indisponível. Veja logs/viber_os.log."
        self.focus()
        self.set_interval(0.5, self._tick)

    def _tick(self) -> None:
        # Recarrega para incluir músicas liberadas por conquistas durante a sessão.
        try:
            novas = caixa_som.listar_musicas()
            if novas != self.musicas:
                self.musicas = novas
                self.selected = min(self.selected, max(0, len(self.musicas) - 1))
        except Exception:
            logger.exception("Music library refresh failed")
            self.error_message = "Falha ao atualizar a biblioteca. Veja o log."
        self.refresh()

    def on_key(self, event: Key) -> None:
        key = event.key.lower()
        handled = True
        try:
            if key == "up" and self.musicas:
                self.selected = (self.selected - 1) % len(self.musicas)
            elif key == "down" and self.musicas:
                self.selected = (self.selected + 1) % len(self.musicas)
            elif key == "enter" and self.musicas:
                caixa_som.tocar_musica(self.musicas[self.selected].name, loop=0)
                desbloquear("sys_musica")
                self.error_message = ""
            elif key == "n":
                caixa_som.tocar_proxima()
                self.error_message = ""
            elif key == "m":
                if caixa_som.get_musica_atual() == "mute":
                    caixa_som.desmutar()
                else:
                    caixa_som.mutar()
                self.error_message = ""
            elif key in {"q", "escape"}:
                close_current_view(self)
            else:
                handled = False
        except Exception:
            logger.exception("Music library input failed: %s", key)
            self.error_message = "Erro no controle de áudio. Veja logs/viber_os.log."

        if not handled:
            return
        event.stop()
        self.refresh()

    def render(self) -> RenderResult:
        try:
            return draw_biblioteca(self.musicas, self.selected, self.error_message)
        except Exception:
            logger.exception("Music library render failed")
            return Align.center(
                Panel(
                    Text("Biblioteca de músicas encontrou um erro. Pressione Q para voltar.", justify="center"),
                    border_style="red",
                ),
                vertical="middle",
            )


class MusicLibraryApp(App[None]):
    CSS = """
    Screen { align: center middle; background: #000000; }
    MusicLibraryWidget { width: 80%; height: 90%; }
    """

    def on_mount(self) -> None:
        caixa_som.set_scheduler(lambda delay, callback: self.set_timer(delay, callback))
        self.set_interval(0.5, caixa_som.atualizar_playlist)

    def on_unmount(self) -> None:
        caixa_som.clear_scheduler()

    def compose(self) -> ComposeResult:
        yield MusicLibraryWidget()


def biblioteca_musicas() -> None:
    MusicLibraryApp(ansi_color=True).run(mouse=False)


if __name__ == "__main__":
    biblioteca_musicas()
