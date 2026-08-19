"""
main_vibe_invader.py  ·  motor gráfico: Textual
------------------------------------------------
Substitui integralmente o loop Rich/Live + msvcrt.
Toda a lógica de jogo (game.py, boss.py, config.py,
save.py, sound.py) permanece sem alterações.
"""

from textual.app import App, ComposeResult
from textual.binding import Binding

from modules.space_invader.widget import VibeInvadersWidget


class VibeInvadersApp(App):
    """Aplicação Textual do Vibe Invaders."""

    # Remove os bindings padrão do Textual que interferem no jogo
    BINDINGS = [
        Binding("ctrl+c", "quit", "Sair", show=False, priority=True),
    ]

    CSS = """
    Screen {
        align: center middle;
        background: #000000;
    }
    VibeInvadersWidget {
        width: auto;
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        yield VibeInvadersWidget()


def main() -> None:
    # ansi_color=True: preserva as cores ANSI exatas do Rich (green, yellow,
    # red, dim green…) sem que o Textual as converta para seu tema interno.
    # Passa no __init__, não no run() — run() não aceita esse parâmetro.
    VibeInvadersApp(ansi_color=True).run(mouse=False)


if __name__ == "__main__":
    main()
