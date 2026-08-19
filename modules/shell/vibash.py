from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Input, RichLog, Static

from modules.caixa_som import caixa_som
from modules.core.logger import logger
from modules.core.settings import VERSION
from modules.ui.branding import viberos_logo
from modules.gerenciar_pastas import gerenciador_pastas
from modules.shell.commands import CommandProcessor, CommandResult


def _plain_path() -> str:
    return (
        gerenciador_pastas.get_caminho_home()
        .replace("[magenta]", "")
        .replace("[/magenta]", "")
    )


class ShellInput(Input):
    """Input com histórico de comandos e autocomplete simples."""

    BINDINGS = [
        Binding("up", "history_previous", show=False),
        Binding("down", "history_next", show=False),
        Binding("tab", "autocomplete", show=False),
        Binding("q", "quick_back", show=False, priority=True),
    ]

    def __init__(self, commands: tuple[str, ...], **kwargs: Any):
        super().__init__(**kwargs)
        self._viber_commands = commands
        self._viber_history: list[str] = []
        self._viber_history_index = 0

    def add_history(self, command: str) -> None:
        command = command.strip()
        if command and (not self._viber_history or self._viber_history[-1] != command):
            self._viber_history.append(command)
            self._viber_history = self._viber_history[-100:]
        self._viber_history_index = len(self._viber_history)

    def action_history_previous(self) -> None:
        if not self._viber_history:
            return
        self._viber_history_index = max(0, self._viber_history_index - 1)
        self.value = self._viber_history[self._viber_history_index]
        self.cursor_position = len(self.value)

    def action_history_next(self) -> None:
        if not self._viber_history:
            return
        self._viber_history_index = min(len(self._viber_history), self._viber_history_index + 1)
        self.value = "" if self._viber_history_index == len(self._viber_history) else self._viber_history[self._viber_history_index]
        self.cursor_position = len(self.value)

    def action_autocomplete(self) -> None:
        prefix = self.value.strip().lower()
        if not prefix or " " in prefix:
            return
        matches = [cmd for cmd in self._viber_commands if cmd.startswith(prefix)]
        if len(matches) == 1:
            self.value = matches[0] + " "
            self.cursor_position = len(self.value)

    def action_quick_back(self) -> None:
        """Q em uma linha vazia volta ao menu; durante digitação continua sendo texto."""
        if not self.value:
            back = getattr(self.screen, "action_back_to_menu", None)
            if callable(back):
                back()
            return

        pos = self.cursor_position
        self.value = self.value[:pos] + "q" + self.value[pos:]
        self.cursor_position = pos + 1


class VibashScreen(Screen):
    """Terminal completo do ViberOS dentro do mesmo App Textual do menu."""

    AUTO_FOCUS = "#command"

    BINDINGS = [
        Binding("escape", "back_to_menu", "Menu", show=False),
        Binding("ctrl+l", "clear_log", "Limpar terminal", show=False),
    ]

    CSS = """
    VibashScreen {
        background: #000000;
        color: #00ff66;
        layout: vertical;
    }

    #status {
        height: auto;
        margin: 0 1;
    }

    #terminal {
        height: 1fr;
        margin: 0 1;
        border: round #008f45;
        background: #000000;
        scrollbar-color: #00aa55;
        scrollbar-background: #001a0d;
    }

    #prompt-row {
        height: 3;
        margin: 0 1 1 1;
        align-vertical: middle;
    }

    #prompt {
        width: auto;
        min-width: 20;
        padding: 0 1;
        color: #00ff66;
    }

    #command {
        width: 1fr;
        border: none;
        background: #001008;
        color: #d8ffe7;
    }

    #command:focus { border: none; }
    """

    def __init__(self, username: str, display_name: str):
        super().__init__()
        self.username = username
        self.display_name = display_name
        self.processor = CommandProcessor(username, display_name)
        self.pending_delete: str | None = None
        self._viber_welcomed = False

    def compose(self) -> ComposeResult:
        yield Static(id="status")
        yield RichLog(id="terminal", markup=True, highlight=False, wrap=True)
        with Horizontal(id="prompt-row"):
            yield Static(id="prompt")
            yield ShellInput(self.processor.PUBLIC_COMMANDS, id="command", placeholder="Digite um comando...")

    def on_mount(self) -> None:
        self._update_status()
        self._update_prompt()
        if not self._viber_welcomed:
            self.query_one("#terminal", RichLog).write(
                Text("Vibash pronto. Digite help para ver os comandos. Q em uma linha vazia volta ao menu.", style="dim green")
            )
            self._viber_welcomed = True
        self.focus_command()
        caixa_som.init()
        caixa_som.garantir_playlist()
        self.set_interval(0.5, self._heartbeat)
        logger.info("Vibash screen mounted")

    def on_screen_resume(self) -> None:
        """Restaura contexto e foco sempre que o Vibash volta ao topo da pilha."""
        try:
            caixa_som.garantir_playlist()
        except Exception:
            logger.exception("Could not restore playlist when Vibash resumed")
        self._update_status()
        self._update_prompt()
        self.call_after_refresh(self.focus_command)

    def focus_command(self) -> None:
        self.query_one("#command", ShellInput).focus()

    def _heartbeat(self) -> None:
        self._update_status()
        self._update_prompt()

    def _update_status(self) -> None:
        current = Path(caixa_som.get_musica_atual()).stem
        top = Text(
            f"Vibash  |  Q: Menu  |  User: {self.display_name}  |  Music: {current}  |  Date: {date.today()}  |  Version: {VERSION}",
            style="green",
            justify="center",
        )
        logo = Text(viberos_logo(), style="bold green", justify="center")
        self.query_one("#status", Static).update(Panel(Group(top, Align.center(logo)), border_style="green"))

    def _update_prompt(self) -> None:
        if self.pending_delete:
            prompt = f"Remover {self.pending_delete}? (S/N) >"
        else:
            prompt = f"{self.username}@viber-os:{_plain_path()} >"
        self.query_one("#prompt", Static).update(prompt)

    @on(Input.Submitted, "#command")
    def submitted(self, event: Input.Submitted) -> None:
        command_input = self.query_one("#command", ShellInput)
        raw = event.value.strip()
        command_input.value = ""

        if self.pending_delete:
            answer = raw.lower()
            if answer not in {"s", "sim", "y", "yes", "n", "nao", "não", "no"}:
                self._write(Text("Responda S ou N.", style="yellow"))
                return
            filename = self.pending_delete
            self.pending_delete = None
            result = self.processor.confirm_delete(filename, answer in {"s", "sim", "y", "yes"})
            self._apply_result(result)
            self._update_prompt()
            self.focus_command()
            return

        if not raw:
            return

        command_input.add_history(raw)
        entered = Text()
        entered.append(f"{self.username}@viber-os:{_plain_path()} > ", style="bright_green")
        entered.append(raw, style="white")
        self._write(entered)

        result = self.processor.execute(raw)
        view_changed = self._apply_result(result)
        self._update_prompt()
        if not view_changed:
            self.call_after_refresh(self.focus_command)

    def _apply_result(self, result: CommandResult) -> bool:
        """Aplica resultado e evita refocar o Input enquanto uma child Screen abre."""
        view_changed = False
        log = self.query_one("#terminal", RichLog)
        if result.clear:
            log.clear()
        for item in result.output:
            self._write(item)
        if result.confirm_delete:
            self.pending_delete = result.confirm_delete
            self._write(Text(f"Confirmar exclusão de {result.confirm_delete}?", style="yellow"))
        if result.launch:
            self._launch(result.launch, *result.launch_args)
            view_changed = True
        if result.back_to_menu:
            self.action_back_to_menu()
            return True
        if result.shutdown:
            request = getattr(self.app, "request_shutdown", None)
            if callable(request):
                request()
            else:
                self.app.exit(True)
            view_changed = True
        if result.redraw and not view_changed:
            self._update_status()
        return view_changed

    def _write(self, item: Any) -> None:
        self.query_one("#terminal", RichLog).write(item)

    def _launch(self, name: str, *args: Any) -> None:
        """Abre apps no mesmo runtime Textual; legados ficam a cargo do App raiz."""
        logger.info("Vibash launch request: %s", name)
        opener = getattr(self.app, "open_module", None)
        if callable(opener):
            opener(name, *args)
            return

        # Não inicia outro App.run() por dentro de uma sessão Textual. O wrapper
        # standalone VibashApp também implementa open_module, então chegar aqui
        # indica um host customizado/incompleto.
        logger.warning("Current Textual host does not expose open_module: %s", name)
        self._write(Text(f"Módulo {name} indisponível neste host Textual.", style="yellow"))
        self.call_after_refresh(self.focus_command)

    def action_back_to_menu(self) -> None:
        close = getattr(self.app, "close_active_screen", None)
        if callable(close):
            close()
        else:
            self.app.exit(False)

    def action_clear_log(self) -> None:
        self.query_one("#terminal", RichLog).clear()


class VibashApp(App[bool]):
    """Wrapper standalone que usa a mesma navegação por telas do ViberOS."""

    def __init__(self, username: str, display_name: str):
        super().__init__(ansi_color=True)
        self.username = username
        self.display_name = display_name
        self._viber_shell = VibashScreen(username, display_name)
        self._viber_shutdown_requested = False

    def on_mount(self) -> None:
        self.push_screen(self._viber_shell)

    def _push_view(self, screen: Screen) -> None:
        self.push_screen(screen, callback=self._after_view_closed)

    def _after_view_closed(self, _result: object = None) -> None:
        try:
            caixa_som.garantir_playlist()
        except Exception:
            logger.exception("Could not restore playlist in standalone Vibash")
        self.call_after_refresh(self._viber_shell.focus_command)

    def open_module(self, name: str, *args: Any) -> None:
        # Imports tardios evitam ciclo durante a importação de modules.ui.app.
        from modules.ui.app import (
            AchievementsScreen, CalendarScreen, MusicScreen,
            VibegotchiScreen, VibeInvadersScreen,
        )
        screens = {
            "calendar": CalendarScreen,
            "music": MusicScreen,
            "vibegotchi": VibegotchiScreen,
            "vibe_invaders": VibeInvadersScreen,
            "achievements": AchievementsScreen,
        }
        factory = screens.get(name)
        if factory is not None:
            if name == "vibe_invaders":
                caixa_som.pausar_musica()
            self._push_view(factory())
            return

        if name in {"rick", "dvd", "hacker", "soldar", "felou"}:
            from modules.ui.secrets import make_secret_screen
            secret = make_secret_screen(name, *args)
            if secret is not None:
                self._push_view(secret)
                return

        self._viber_shell._write(Text(f"Módulo {name} não disponível neste modo.", style="yellow"))

    def close_active_screen(self) -> None:
        if self.screen is self._viber_shell:
            self.exit(False)
            return
        try:
            prepare = getattr(self.screen, "prepare_for_close", None)
            if callable(prepare):
                prepare()
            self.screen.dismiss(None)
        except Exception:
            logger.exception("Could not dismiss standalone Vibash child screen")
            self.call_after_refresh(self._viber_shell.focus_command)

    def request_shutdown(self) -> None:
        if self._viber_shutdown_requested:
            return
        self._viber_shutdown_requested = True
        try:
            caixa_som.pausar_musica()
        except Exception:
            logger.exception("Could not stop music before Vibash shutdown")
        from modules.ui.lifecycle import make_shutdown_screen
        self.push_screen(make_shutdown_screen(lambda: self.exit(True)))


def run_vibash(username: str, display_name: str) -> bool:
    return bool(VibashApp(username, display_name).run(mouse=False))
