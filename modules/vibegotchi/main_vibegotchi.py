from __future__ import annotations

import time
from pathlib import Path

from art import text2art
from rich import box
from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.events import Key
from textual.containers import Horizontal, Vertical
from textual.widgets import Input, Static
from textual.widget import Widget

from modules.core.navigation import close_current_view

from modules.achievements.main_achievements import desbloquear
from modules.core.storage import load_json, save_json
from modules.vibegotchi.ascii import pegar_vibe
from modules.vibegotchi.pet import Vibegotchi

_VIBEGOTCHI_LOGO = text2art("VIBEGOTCHI")

SAVE = Path(__file__).parent / "dados" / "save.json"
ACOES = ["Alimentar", "Brincar", "Dormir", "Sair"]


def salvar_jogo(pet: Vibegotchi) -> None:
    save_json(SAVE, pet.para_dict())


def carregar_jogo() -> Vibegotchi | None:
    dados = load_json(SAVE, {})
    if not isinstance(dados, dict) or not dados.get("nome"):
        return None
    try:
        return Vibegotchi.de_dict(dados)
    except (KeyError, TypeError, ValueError):
        return None


def checar_vida(pet: Vibegotchi) -> str | None:
    condicoes = [
        (pet.aura <= 0, f"{pet.nome} perdeu toda a sua aura e se foi..."),
        (pet.aura >= 1000, f"{pet.nome} atingiu a aura máxima e se tornou um ser de pura energia!"),
        (pet.fome >= 100, f"{pet.nome} morreu de fome..."),
        (pet.fome <= -1, f"{pet.nome} morreu de tanto comer..."),
        (pet.energia <= 0, f"{pet.nome} morreu de exaustão..."),
        (pet.humor <= 0, f"{pet.nome} morreu de tristeza..."),
    ]
    for condicao, mensagem in condicoes:
        if condicao:
            if pet.aura >= 1000:
                desbloquear("vg_aura")
            try:
                SAVE.unlink(missing_ok=True)
            except OSError:
                pass
            return mensagem
    return None


def render_pet(pet: Vibegotchi, selected: int, message: str = "") -> Align:
    if pet.aura <= 20:
        cor = "red"
    elif pet.humor > 70:
        cor = "yellow"
    else:
        cor = "cyan"

    titulo = Panel(Align.center(_VIBEGOTCHI_LOGO), style="green", box=box.DOUBLE)
    painel_pet = Panel(Align.center(pegar_vibe(pet)), title=f"🐾 {pet.nome}", border_style=cor)

    status = Text()
    status.append(f"Fome: {pet.fome}\n", style="green")
    status.append(f"Energia: {pet.energia}\n", style="yellow")
    status.append(f"Humor: {pet.humor}\n", style="magenta")
    status.append(f"Aura: {pet.aura}", style="cyan")
    painel_status = Panel(status, title="Status", border_style="green")

    acoes = Text(justify="center")
    acoes.append("Ações:\n\n", style="bold green")
    for i, acao in enumerate(ACOES):
        acoes.append(f"{'▶' if i == selected else ' '}  {acao}\n\n", style="bold green" if i == selected else "dim green")
    acoes.append("↑ ↓: Navegar | Enter: Confirmar | Q/Esc: Voltar", style="dim green")
    if message:
        acoes.append("\n\n" + message, style="bold yellow")

    return Align.center(Panel(Group(titulo, painel_pet, painel_status, Panel(acoes, border_style="green"))), vertical="middle")


class VibegotchiView(Widget):
    """Conteúdo do Vibegotchi reutilizável dentro do ViberOS Textual."""

    can_focus = True

    def __init__(self) -> None:
        super().__init__()
        self.pet = carregar_jogo()
        self.selected = 0
        self.last_time = time.monotonic()
        self.message = ""
        self.dead = False

    def compose(self) -> ComposeResult:
        yield Static(id="content")
        with Vertical(id="create-box"):
            yield Static("Crie seu Vibegotchi para começar.", id="create-message")
            with Horizontal(id="name-row"):
                yield Input(placeholder="Nome do Vibegotchi", id="name")
            yield Static("Enter: Criar  |  Esc: Voltar", id="name-hint")

    def on_mount(self) -> None:
        name_input = self.query_one("#name", Input)
        create_box = self.query_one("#create-box", Vertical)
        content = self.query_one("#content", Static)
        if self.pet is None:
            content.add_class("hidden")
            create_box.remove_class("hidden")
            name_input.focus()
        else:
            create_box.add_class("hidden")
            content.remove_class("hidden")
            self.focus()
            self._refresh_view()
        self.set_interval(0.5, self._tick)

    @on(Input.Submitted, "#name")
    def create_pet(self, event: Input.Submitted) -> None:
        nome = event.value.strip()
        if len(nome) < 1:
            return
        self.pet = Vibegotchi(nome)
        salvar_jogo(self.pet)
        desbloquear("vg_nomeado")
        self.query_one("#create-box", Vertical).add_class("hidden")
        self.query_one("#content", Static).remove_class("hidden")
        self.last_time = time.monotonic()
        self._refresh_view()
        self.focus()

    def _tick(self) -> None:
        if self.pet is None or self.dead:
            return
        now = time.monotonic()
        if now - self.last_time >= 2:
            steps = int((now - self.last_time) // 2)
            # Evita que uma longa suspensão externa mate o pet de uma vez.
            steps = min(steps, 5)
            for _ in range(steps):
                self.pet.passar_tempo()
            self.last_time = now
            salvar_jogo(self.pet)
            death = checar_vida(self.pet)
            if death:
                self.dead = True
                self.message = death + "  Pressione qualquer tecla para voltar."
            self._refresh_view()

    def on_key(self, event: Key) -> None:
        if self.query_one("#name", Input).has_focus:
            if event.key.lower() == "escape":
                event.stop()
                close_current_view(self)
            return
        if self.pet is None:
            return
        if self.dead:
            event.stop()
            close_current_view(self)
            return

        key = event.key.lower()
        if key == "up":
            self.selected = (self.selected - 1) % len(ACOES)
        elif key == "down":
            self.selected = (self.selected + 1) % len(ACOES)
        elif key == "enter":
            self._execute_action()
        elif key in {"q", "escape"}:
            salvar_jogo(self.pet)
            close_current_view(self)
        else:
            return
        event.stop()
        self._refresh_view()

    def _execute_action(self) -> None:
        assert self.pet is not None
        if self.selected == 0:
            self.pet.alimentar()
            if self.pet.vezes_alimentado >= 3:
                desbloquear("vg_cuidado")
            self.message = f"{self.pet.nome} foi alimentado."
        elif self.selected == 1:
            self.pet.brincar()
            self.message = f"{self.pet.nome} brincou com você."
        elif self.selected == 2:
            self.pet.dormir()
            self.message = f"{self.pet.nome} descansou."
        elif self.selected == 3:
            salvar_jogo(self.pet)
            close_current_view(self)
            return
        death = checar_vida(self.pet)
        if death:
            self.dead = True
            self.message = death + "  Pressione qualquer tecla para voltar."
            return
        self.pet.limitar_valores()
        salvar_jogo(self.pet)

    def _refresh_view(self) -> None:
        if self.pet is not None:
            self.query_one("#content", Static).update(render_pet(self.pet, self.selected, self.message))


class VibegotchiApp(App[None]):
    CSS = """
    Screen { background: #000000; align: center middle; }
    VibegotchiView { width: 100%; height: 100%; align: center middle; }
    #content { width: 85%; height: auto; max-height: 100%; }
    #create-box { width: 72; height: auto; padding: 1 2; border: double #00cc66; align-horizontal: center; }
    #create-message { width: 100%; height: auto; text-align: center; margin-bottom: 1; color: #00ff66; }
    #name-row { width: 100%; height: 3; align-horizontal: center; }
    #name { width: 80%; max-width: 56; }
    #name-hint { width: 100%; height: 2; text-align: center; color: #008f45; margin-top: 1; }
    .hidden { display: none; }
    """

    def compose(self) -> ComposeResult:
        yield VibegotchiView()

def play() -> None:
    VibegotchiApp().run(mouse=False)


if __name__ == "__main__":
    play()
