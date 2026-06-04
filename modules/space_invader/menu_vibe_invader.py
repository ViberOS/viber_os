from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.console import Group
from art import text2art

MENU_ITEMS = ["jogar", "estilo", "sair"]


def draw_menu(style: str = "retro", selected: int = 0) -> Align:
    titulo = Text(text2art("VIBE  INVADERS"), style="green")
    versao = Text("v1.1\n", style="dim green", justify="center")

    # labels exibidos — estilo mostra o valor atual
    labels = [
        "Jogar",
        f"Estilo:  {'RETRO (Easy)' if style == 'retro' else 'VIBE (Hard)'}",
        "Sair",
    ]

    menu = Text(justify="center")
    menu.append("\n")
    for i, label in enumerate(labels):
        if i == selected:
            menu.append(f"▶  {label}\n\n", style="bold green")
        else:
            menu.append(f"   {label}\n\n", style="dim green")

    ctrl_text = Text(justify="center")
    ctrl_text.append("↑ ↓: Navegar  |  Enter: Confirmar\n", style="bold green")
    ctrl_text.append("A: Esquerda (←)  |  D: Direita (→)  |  Space: Atirar", style="dim green")
    controles = Align(ctrl_text, vertical="bottom", align="center")

    conteudo = Group(titulo, versao, menu, controles)
    panel = Panel(conteudo, border_style="green", height=20)
    return Align.center(panel, vertical="middle")


def draw_gameover(wave, score, highscore) -> Align:
    titulo = Text(text2art("GAME OVER"), style="bold red")

    dados = Text(justify="center")
    dados.append("\n\n")
    dados.append(f"{'WAVE':<12}{wave}\n\n", style="bold green")
    dados.append(f"{'SCORE':<12}{score}\n\n", style="bold green")
    dados.append(f"{'HIGHSCORE':<12}{highscore}\n", style="bold green")

    conteudo = Group(titulo, dados)

    panel = Panel(
        Align.center(conteudo, vertical="middle"),
        border_style="green",
        height=20,
        expand=False,
    )

    return Align.center(panel, vertical="middle")


def draw_victory(score, highscore) -> Align:
    titulo = Text(text2art("YOU  WIN"), style="bold yellow")

    dados = Text(justify="center")
    dados.append("\n\n")
    dados.append("BOSS DERROTADO!\n\n", style="bold yellow")
    dados.append(f"{'SCORE':<12}{score}\n\n", style="bold green")
    dados.append(f"{'HIGHSCORE':<12}{highscore}\n", style="bold green")

    conteudo = Group(titulo, dados)

    panel = Panel(
        Align.center(conteudo, vertical="middle"),
        border_style="yellow",
        height=20,
        expand=False,
    )

    return Align.center(panel, vertical="middle")


def handle_menu_input(key, style: str = "retro", selected: int = 0):
    # navegação com setas (msvcrt já consumiu o \xe0, chega só b'H' ou b'P')
    if key == b'H':   # seta cima
        selected = (selected - 1) % len(MENU_ITEMS)

    elif key == b'P':  # seta baixo
        selected = (selected + 1) % len(MENU_ITEMS)

    # confirma com Enter
    elif key in (b'\r', b'\n'):
        item = MENU_ITEMS[selected]

        if item == "jogar":
            return "game", style, selected
        elif item == "estilo":
            new_style = "vibe" if style == "retro" else "retro"
            return "menu", new_style, selected
        elif item == "sair":
            return "exit", style, selected
    
    elif key in (b'K', b'M'):
        item = MENU_ITEMS[selected]

        if item == "estilo":
            new_style = "vibe" if style == "retro" else "retro"
            return "menu", new_style, selected

    return "menu", style, selected
