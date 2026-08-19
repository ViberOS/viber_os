from __future__ import annotations

import shutil
from pathlib import Path

from art import text2art
from rich import box
from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.app import App, ComposeResult, RenderResult
from textual.events import Key
from textual.widget import Widget

from modules.core.logger import logger
from modules.core.navigation import close_current_view
from modules.core.storage import load_json, save_json

_MUSICAS_DIR = Path(__file__).parents[2] / "medias" / "sons" / "musicas"
_CONQUISTAS_DIR = _MUSICAS_DIR / "conquistas"
_SAVE = Path(__file__).parent / "conquistas.json"

CONQUISTAS = [
    ("sys_primeiro_login", "Bem-vindo ao ViberOS", "Faça login pela primeira vez", None),
    ("sys_musica", "Bom Gosto", "Toque uma música na biblioteca", None),
    ("sys_segredo", "Curioso feito um gato", "Descubra um comando secreto", "memory_drift.mp3"),
    ("vi_primeira_onda", "Primeira Onda", "Complete a wave 1 no Vibe Invaders", None),
    ("vi_wave_5", "Resistência", "Chegue até a wave 5 no Vibe Invaders", None),
    ("vi_boss_derrotado", "Vibe Hero", "Derrote o Vibe Destroyer na dificuldade Vibe (Difícil)", "happy_vibe.mp3"),
    ("vg_nomeado", ":O", "Dê um nome pro seu Vibegotchi", None),
    ("vg_cuidado", "Amigo do Gochinho", "Alimente o seu Vibegotchi 3 vezes", None),
    ("vg_aura", "Transcendência", "Faça seu Vibegotchi atingir a aura máxima", None),
    ("cal_primeira_vez", "Que dia é hoje?", "Acesse o calendário pela primeira vez", None),
]


def _load() -> set[str]:
    data = load_json(_SAVE, [])
    return set(data) if isinstance(data, list) else set()


def _save(desbloqueadas: set[str]) -> None:
    save_json(_SAVE, sorted(desbloqueadas))


def _desbloquear_musica(arquivo: str) -> bool:
    origem = _CONQUISTAS_DIR / arquivo
    destino = _MUSICAS_DIR / arquivo
    if not origem.exists():
        logger.warning("Achievement reward track missing: %s", arquivo)
        return False
    if destino.exists():
        return False
    try:
        shutil.copy2(origem, destino)
        logger.info("Achievement reward track unlocked: %s", arquivo)
        return True
    except OSError:
        logger.exception("Could not copy achievement reward track: %s", arquivo)
        return False


def desbloquear(achievement_id: str) -> bool:
    desbloqueadas = _load()
    if achievement_id in desbloqueadas:
        return False

    known = next((item for item in CONQUISTAS if item[0] == achievement_id), None)
    if known is None:
        logger.warning("Unknown achievement id: %s", achievement_id)
        return False

    desbloqueadas.add(achievement_id)
    _save(desbloqueadas)
    logger.info("Achievement unlocked: %s", achievement_id)

    musica = known[3]
    if musica:
        _desbloquear_musica(musica)
    return True


def esta_desbloqueada(achievement_id: str) -> bool:
    return achievement_id in _load()


def render_achievements(desbloqueadas: set[str]) -> Align:
    titulo = Text(text2art("Conquistas"), style="green", justify="center")
    table = Table(
        box=box.SIMPLE_HEAD,
        border_style="green",
        expand=True,
        show_header=False,
        padding=(0, 2),
    )
    table.add_column("check", width=3, no_wrap=True)
    table.add_column("info", ratio=1)

    for aid, titulo_ach, descricao, musica in CONQUISTAS:
        unlocked = aid in desbloqueadas
        check = Text("☑" if unlocked else "☐", style="bold green" if unlocked else "dim white")
        nome = Text(titulo_ach, style="bold green" if unlocked else "bold white")
        desc = Text(descricao, style="green" if unlocked else "dim white")
        if musica:
            nome.append(" 🎵" if unlocked else " 🔒", style="bold green" if unlocked else "dim white")
        table.add_row(check, Group(nome, desc))
        table.add_section()

    total = len(CONQUISTAS)
    feitas = len(desbloqueadas & {a[0] for a in CONQUISTAS})
    rodape = Text(f"\n{feitas}/{total} conquistas desbloqueadas\nQ/Esc: Voltar", style="dim green", justify="center")
    panel = Panel(Group(titulo, table, rodape), border_style="green", title="[bold green]Conquistas[/bold green]")
    return Align.center(panel, vertical="middle")


class AchievementsWidget(Widget):
    can_focus = True

    def on_mount(self) -> None:
        self.focus()

    def on_key(self, event: Key) -> None:
        if event.key.lower() in {"q", "escape"}:
            event.stop()
            close_current_view(self)

    def render(self) -> RenderResult:
        return render_achievements(_load())


class AchievementsApp(App[None]):
    CSS = """
    Screen { background: #000000; align: center middle; }
    AchievementsWidget { width: 90%; height: 95%; }
    """

    def compose(self) -> ComposeResult:
        yield AchievementsWidget()


def main() -> None:
    AchievementsApp(ansi_color=True).run(mouse=False)


if __name__ == "__main__":
    main()
