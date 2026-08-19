from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from rich import box
from rich.align import Align
from rich.console import Group
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Input, RichLog, Static

from modules.caixa_som import caixa_som
from modules.ui.branding import viberos_logo
from modules.core.logger import logger
from modules.core.paths import ROOT_DIR
from modules.core.settings import VERSION
from modules.gerenciar_pastas import gerenciador_pastas
from modules.shell.commands import CommandProcessor, CommandResult
from modules.shell.vibash import VibashScreen


APP_MENU = (
    ("1", "Calendário", "calendar"),
    ("2", "Biblioteca de músicas", "music"),
    ("3", "Vibegotchi", "vibegotchi"),
    ("4", "Vibe Invaders", "vibe_invaders"),
    ("5", "Conquistas", "achievements"),
    ("6", "Vibash", "vibash"),
    ("7", "Ajuda", "help"),
    ("8", "Desligar sistema", "shutdown"),
)


def _plain_path() -> str:
    return (
        gerenciador_pastas.get_caminho_home()
        .replace("[magenta]", "")
        .replace("[/magenta]", "")
    )


def _local_datetime_label() -> tuple[str, str]:
    """Retorna data e hora no fuso configurado no sistema do usuário."""
    now = datetime.now().astimezone()
    raw_offset = now.strftime("%z")
    utc_offset = f"UTC{raw_offset[:3]}:{raw_offset[3:]}" if raw_offset else "UTC"
    return now.strftime("%Y-%m-%d"), f"{now.strftime('%H:%M')} ({utc_offset})"


def render_main_header(display_name: str) -> Group:
    current = Path(caixa_som.get_musica_atual()).stem
    current_date, current_time = _local_datetime_label()
    info = Panel(
        Align.center(
            f"User: {display_name}  |  Music: {current}  |  Date: {current_date}  |  Time: {current_time}  |  Version: {VERSION}"
        ),
        border_style="green",
        box=box.SIMPLE_HEAD,
        expand=False,
    )
    logo = Panel(
        Align.center(viberos_logo()),
        border_style="green",
        box=box.DOUBLE,
    )
    title = Panel(
        "[bold green]Lista de Aplicativos[/bold green]",
        border_style="green",
        box=box.SIMPLE_HEAD,
        expand=False,
    )
    return Group(Align.center(info), logo, Align.center(title))


def render_app_list() -> Panel:
    lines: list[str] = []
    for number, label, _ in APP_MENU:
        lines.append(f"[{number}] {label}")
        lines.append("")
    return Panel("\n".join(lines).rstrip(), border_style="green")


class MainMenuScreen(Screen):
    """Menu clássico do ViberOS, agora dentro do runtime Textual."""

    AUTO_FOCUS = "#classic-command"

    CSS = """
    MainMenuScreen {
        background: #000000;
        color: #00ff66;
        layout: vertical;
    }

    #classic-header {
        height: auto;
        margin: 0 1;
    }

    #classic-apps {
        height: auto;
        margin: 0 2;
    }

    #classic-output {
        height: 1fr;
        min-height: 3;
        max-height: 12;
        margin: 0 2;
        background: #000000;
        color: #d8ffe7;
        scrollbar-color: #00aa55;
        scrollbar-background: #001a0d;
    }

    #classic-prompt-row {
        height: 3;
        margin: 0 1 1 1;
        align-vertical: middle;
    }

    #classic-prompt {
        width: auto;
        min-width: 18;
        padding: 0 1;
        color: #00ff66;
    }

    #classic-command {
        width: 1fr;
        border: none;
        background: #001008;
        color: #ffffff;
    }

    #classic-command:focus {
        border: none;
    }
    """

    def __init__(self, username: str, display_name: str):
        super().__init__()
        self.username = username
        self.display_name = display_name
        self.processor = CommandProcessor(username, display_name)
        self.pending_delete: str | None = None

    def compose(self) -> ComposeResult:
        yield Static(id="classic-header")
        yield Static(id="classic-apps")
        yield RichLog(id="classic-output", markup=True, highlight=False, wrap=True)
        with Horizontal(id="classic-prompt-row"):
            yield Static(id="classic-prompt")
            yield Input(id="classic-command", placeholder="Digite um número ou comando...")

    def on_mount(self) -> None:
        caixa_som.init()
        caixa_som.garantir_playlist()
        self._refresh_menu()
        self.query_one("#classic-command", Input).focus()
        self.set_interval(0.75, self._refresh_header)
        logger.info("Classic Textual menu mounted")

    def on_screen_resume(self) -> None:
        caixa_som.garantir_playlist()
        self._refresh_menu()
        self.call_after_refresh(self.query_one("#classic-command", Input).focus)

    def _refresh_header(self) -> None:
        self.query_one("#classic-header", Static).update(render_main_header(self.display_name))
        self._update_prompt()

    def _refresh_menu(self) -> None:
        self._refresh_header()
        self.query_one("#classic-apps", Static).update(render_app_list())

    def _update_prompt(self) -> None:
        if self.pending_delete:
            prompt = f"Remover {self.pending_delete}? (S/N) >"
        else:
            prompt = f"{self.username}@viber-os:{_plain_path()} >"
        self.query_one("#classic-prompt", Static).update(prompt)

    def _write(self, item: Any) -> None:
        self.query_one("#classic-output", RichLog).write(item)

    def _clear_output(self) -> None:
        self.query_one("#classic-output", RichLog).clear()

    @on(Input.Submitted, "#classic-command")
    def submitted(self, event: Input.Submitted) -> None:
        raw = event.value.strip()
        event.input.value = ""

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
            event.input.focus()
            return

        if not raw:
            return

        # Mantém os atalhos numéricos do menu original e inclui o Vibash.
        direct = {
            "1": "calendar",
            "2": "music",
            "3": "vibegotchi",
            "4": "vibe_invaders",
            "5": "achievements",
            "6": "vibash",
            "7": "help",
            "8": "shutdown",
            "calendar": "calendar",
            "music": "music",
            "vibegotchi": "vibegotchi",
            "vibe_invaders": "vibe_invaders",
            "achievements": "achievements",
            "conquistas": "achievements",
            "vibash": "vibash",
            # aliases antigos durante a transição de nome
            "vibershell": "vibash",
            "shell": "vibash",
        }
        key = raw.lower()
        if key in direct:
            target = direct[key]
            if target == "help":
                self._show_help()
            elif target == "shutdown":
                self.app.request_shutdown()
            else:
                self.app.open_module(target)
            return

        if key == "help":
            self._show_help()
            return
        if key == "shutdown":
            self.app.request_shutdown()
            return

        # O menu clássico continua aceitando os comandos antigos; Vibash é
        # a experiência de terminal completa com histórico e autocomplete.
        entered = Text()
        entered.append(f"{self.username}@viber-os:{_plain_path()} > ", style="bright_green")
        entered.append(raw, style="white")
        self._write(entered)
        view_changed = self._apply_result(self.processor.execute(raw))
        self._update_prompt()
        if not view_changed:
            event.input.focus()

    def _show_help(self) -> None:
        try:
            markdown = Markdown((ROOT_DIR / "modules" / "help.md").read_text(encoding="utf-8"))
            self._write(Panel(markdown, border_style="green"))
        except OSError:
            self._write(Text("Não foi possível abrir a ajuda.", style="bold red"))

    def _apply_result(self, result: CommandResult) -> bool:
        """Aplica resultado e informa se outra tela assumiu o foco."""
        view_changed = False
        if result.clear:
            self._clear_output()
        for item in result.output:
            self._write(item)
        if result.confirm_delete:
            self.pending_delete = result.confirm_delete
            self._write(Text(f"Confirmar exclusão de {result.confirm_delete}?", style="yellow"))
        if result.launch:
            self.app.open_module(result.launch, *result.launch_args)
            view_changed = True
        if result.back_to_menu:
            # Já estamos no menu principal.
            pass
        if result.shutdown:
            self.app.request_shutdown()
            view_changed = True
        if result.redraw and not view_changed:
            self._refresh_menu()
        return view_changed


class CalendarScreen(Screen):
    CSS = """CalendarScreen { background: #000000; align: center middle; } CalendarWidget { width: 85%; height: 90%; }"""
    def compose(self) -> ComposeResult:
        from modules.calendario import CalendarWidget
        yield CalendarWidget()
    def on_mount(self) -> None:
        from modules.achievements.main_achievements import desbloquear
        desbloquear("cal_primeira_vez")


class MusicScreen(Screen):
    CSS = """MusicScreen { background: #000000; align: center middle; } MusicLibraryWidget { width: 80%; height: 90%; }"""
    def compose(self) -> ComposeResult:
        from modules.biblioteca import MusicLibraryWidget
        yield MusicLibraryWidget()


class AchievementsScreen(Screen):
    CSS = """AchievementsScreen { background: #000000; align: center middle; } AchievementsWidget { width: 90%; height: 95%; }"""
    def compose(self) -> ComposeResult:
        from modules.achievements.main_achievements import AchievementsWidget
        yield AchievementsWidget()


class VibegotchiScreen(Screen):
    CSS = """
    VibegotchiScreen { background: #000000; align: center middle; }
    VibegotchiView { width: 100%; height: 100%; align: center middle; }
    #content { width: 85%; height: auto; max-height: 100%; }
    #create-box { width: 72; height: auto; padding: 1 2; border: double #00cc66; align-horizontal: center; }
    #create-message { width: 100%; height: auto; text-align: center; margin-bottom: 1; }
    #name-row { width: 100%; height: 3; align-horizontal: center; }
    #name { width: 80%; max-width: 56; }
    #name-hint { width: 100%; height: 2; text-align: center; color: #008f45; margin-top: 1; }
    .hidden { display: none; }
    """
    def compose(self) -> ComposeResult:
        from modules.vibegotchi.main_vibegotchi import VibegotchiView
        yield VibegotchiView()


class VibeInvadersScreen(Screen):
    CSS = """
    VibeInvadersScreen { background: #000000; align: center middle; }
    VibeInvadersWidget { width: auto; height: auto; }
    """
    def compose(self) -> ComposeResult:
        from modules.space_invader.widget import VibeInvadersWidget
        yield VibeInvadersWidget()


class ViberOSApp(App[bool]):
    """Runtime único do ViberOS.

    O menu clássico, o Vibash e os apps Textual compartilham o mesmo loop.
    Isso evita iniciar um segundo ``App.run()`` dentro do terminal — a causa da
    perda de foco/estado observada na refatoração anterior.
    """

    BINDINGS = [
        Binding("ctrl+c", "back_or_clear", show=False, priority=True),
    ]

    CSS = "Screen { background: #000000; }"

    def __init__(self, username: str, display_name: str):
        super().__init__(ansi_color=True)
        self.username = username
        self.display_name = display_name
        self._viber_shutdown_requested = False

    def on_mount(self) -> None:
        # O áudio usa o mesmo event loop do Textual: nada de pygame.music
        # sendo manipulado por threads enquanto o terminal está em app mode.
        caixa_som.set_scheduler(lambda delay, callback: self.set_timer(delay, callback))
        self.set_interval(0.5, caixa_som.atualizar_playlist)
        self.install_screen(MainMenuScreen(self.username, self.display_name), name="main_menu")
        self.install_screen(VibashScreen(self.username, self.display_name), name="vibash")
        self.push_screen("main_menu")

    def on_unmount(self) -> None:
        caixa_som.clear_scheduler()

    def _push_view(self, screen: Screen | str) -> None:
        """Empilha uma tela e restaura o contexto somente após o dismiss.

        ``pop_screen()`` retorna um AwaitComplete; restaurar foco logo depois
        pode acontecer antes de a tela anterior estar realmente ativa. Usar o
        callback de ``push_screen`` + ``Screen.dismiss`` mantém o lifecycle no
        fluxo esperado pelo Textual.
        """
        self.push_screen(screen, callback=self._after_view_closed)

    def _after_view_closed(self, _result: object = None) -> None:
        try:
            caixa_som.garantir_playlist()
        except Exception:
            logger.exception("Could not restore system playlist after closing view")
        self.call_after_refresh(self._restore_focus)

    def open_module(self, name: str, *args: Any) -> None:
        logger.info("Opening integrated module: %s", name)
        if name in {"vibash", "shell", "vibershell"}:
            self._push_view("vibash")
            return
        if name == "calendar":
            self._push_view(CalendarScreen())
            return
        if name == "music":
            self._push_view(MusicScreen())
            return
        if name == "vibegotchi":
            self._push_view(VibegotchiScreen())
            return
        if name == "vibe_invaders":
            caixa_som.pausar_musica()
            self._push_view(VibeInvadersScreen())
            return
        if name == "achievements":
            self._push_view(AchievementsScreen())
            return
        if name in {"rick", "dvd", "hacker", "soldar", "felou"}:
            from modules.ui.secrets import make_secret_screen
            secret = make_secret_screen(name, *args)
            if secret is not None:
                self._push_view(secret)
                return
        logger.warning("Unknown module requested: %s", name)

    def close_active_screen(self) -> None:
        # Main menu é a raiz visível e nunca deve ser removido pela navegação.
        current = self.screen
        if isinstance(current, MainMenuScreen):
            command = current.query_one("#classic-command", Input)
            command.value = ""
            command.focus()
            return

        try:
            prepare = getattr(current, "prepare_for_close", None)
            if callable(prepare):
                prepare()
            # Não aguardamos aqui: handlers de Screen devem apenas solicitar o
            # dismiss. O callback registrado em _push_view faz o pós-retorno.
            current.dismiss(None)
        except Exception:
            logger.exception("Could not dismiss active Textual screen")
            self.call_after_refresh(self._restore_focus)

    def _restore_focus(self) -> None:
        try:
            if isinstance(self.screen, MainMenuScreen):
                self.screen.query_one("#classic-command", Input).focus()
            elif isinstance(self.screen, VibashScreen):
                self.screen.focus_command()
        except Exception:
            logger.exception("Could not restore Textual input focus")

    def request_shutdown(self) -> None:
        """Mostra o desligamento dentro do mesmo runtime Textual."""
        if self._viber_shutdown_requested:
            return
        self._viber_shutdown_requested = True
        try:
            caixa_som.pausar_musica()
        except Exception:
            logger.exception("Could not stop music before shutdown")
        from modules.ui.lifecycle import make_shutdown_screen
        self.push_screen(make_shutdown_screen(self._finish_shutdown))

    def _finish_shutdown(self) -> None:
        logger.info("ViberOS shutdown completed in Textual UI")
        self.exit(True)

    def action_back_or_clear(self) -> None:
        if self._viber_shutdown_requested:
            return
        self.close_active_screen()



def run_viberos(username: str, display_name: str) -> bool:
    return bool(ViberOSApp(username, display_name).run(mouse=False))
