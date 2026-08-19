from __future__ import annotations

from typing import Callable

from art import text2art
from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Input, Static

from modules.core.logger import logger
from modules.ui.branding import viberos_logo

try:
    from winsound import Beep as _windows_beep
except ImportError:  # Linux/macOS
    _windows_beep = None


def _beep(freq: int = 900, duration_ms: int = 180) -> None:
    if _windows_beep is None:
        return
    try:
        _windows_beep(freq, duration_ms)
    except RuntimeError:
        pass


def _bar(current: int, total: int, width: int = 40) -> str:
    total = max(1, total)
    filled = round(width * current / total)
    return "█" * filled + "░" * (width - filled)


class LifecycleScreen(Screen):
    """Tela reaproveitável para boot e desligamento do ViberOS."""

    CSS = """
    LifecycleScreen {
        background: #000000;
        color: #00ff66;
        align: center middle;
    }

    #lifecycle-box {
        width: 72;
        height: auto;
        padding: 1 2;
        border: double #00cc66;
        background: #000000;
    }

    #lifecycle-logo {
        height: auto;
        color: #00ff66;
        text-align: center;
        margin-bottom: 1;
    }

    #lifecycle-stage {
        height: 2;
        text-align: center;
        color: #d8ffe7;
    }

    #lifecycle-progress {
        height: 2;
        text-align: center;
        color: #00ff66;
    }

    #lifecycle-footer {
        height: 2;
        text-align: center;
        color: #008f45;
    }
    """

    def __init__(
        self,
        *,
        mode: str,
        stages: tuple[str, ...],
        interval: float,
        done_message: str,
        on_complete: Callable[[], None] | None = None,
        beep: bool = False,
    ) -> None:
        super().__init__()
        self.mode = mode
        self.stages = stages
        self.interval = interval
        self.done_message = done_message
        self.on_complete = on_complete
        self.beep = beep
        self.index = 0
        self._viber_finished = False

    def compose(self) -> ComposeResult:
        logo = viberos_logo() if self.mode == "boot" else text2art("SHUTDOWN", font="mini")
        with Vertical(id="lifecycle-box"):
            yield Static(logo, id="lifecycle-logo")
            yield Static("Preparando...", id="lifecycle-stage")
            yield Static(_bar(0, len(self.stages)), id="lifecycle-progress")
            yield Static("", id="lifecycle-footer")

    def on_mount(self) -> None:
        logger.info("Textual lifecycle started: %s", self.mode)
        self._advance()
        self.set_interval(self.interval, self._advance)

    def _advance(self) -> None:
        if self._viber_finished:
            return
        if self.index < len(self.stages):
            if self.beep:
                _beep()
            self.query_one("#lifecycle-stage", Static).update(self.stages[self.index])
            self.index += 1
            self.query_one("#lifecycle-progress", Static).update(
                _bar(self.index, len(self.stages))
            )
            self.query_one("#lifecycle-footer", Static).update(
                f"{self.index}/{len(self.stages)}"
            )
            return

        self._viber_finished = True
        self.query_one("#lifecycle-stage", Static).update(
            Text(self.done_message, style="bold bright_green", justify="center")
        )
        self.query_one("#lifecycle-footer", Static).update("")
        logger.info("Textual lifecycle completed: %s", self.mode)
        if self.on_complete is not None:
            callback = self.on_complete
            self.on_complete = None
            self.set_timer(0.45, callback)
        else:
            self.set_timer(0.45, self.app.exit)


class LifecycleApp(App[None]):
    CSS = "Screen { background: #000000; }"

    def __init__(self, screen: LifecycleScreen) -> None:
        super().__init__(ansi_color=True)
        self.lifecycle_screen = screen

    def on_mount(self) -> None:
        self.push_screen(self.lifecycle_screen)


class UserSetupScreen(Screen):
    """Wizard Textual do primeiro acesso: idade -> nome -> senha."""

    AUTO_FOCUS = "#setup-input"

    CSS = """
    UserSetupScreen {
        background: #000000;
        color: #00ff66;
        align: center middle;
    }

    #setup-box {
        width: 70;
        height: auto;
        padding: 1 3;
        border: double #00cc66;
        background: #000000;
    }

    #setup-logo {
        height: auto;
        text-align: center;
        color: #00ff66;
        margin-bottom: 1;
    }

    #setup-progress {
        height: 1;
        text-align: center;
        color: #008f45;
        margin-bottom: 1;
    }

    #setup-prompt {
        height: 2;
        text-align: center;
        color: #d8ffe7;
    }

    #setup-input {
        width: 100%;
        background: #001008;
        color: #ffffff;
        border: tall #00aa55;
    }

    #setup-error {
        height: 2;
        text-align: center;
        color: #ff5555;
        margin-top: 1;
    }

    #setup-hint {
        height: 2;
        text-align: center;
        color: #008f45;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.step = "age"
        self.data: dict[str, object] = {}

    def compose(self) -> ComposeResult:
        with Vertical(id="setup-box"):
            yield Static(viberos_logo(), id="setup-logo")
            yield Static("Configuração inicial  •  Etapa 1/3", id="setup-progress")
            yield Static("DIGITE SUA IDADE:", id="setup-prompt")
            yield Input(id="setup-input", placeholder="Idade")
            yield Static("", id="setup-error")
            yield Static("Enter para continuar", id="setup-hint")

    def on_mount(self) -> None:
        self.query_one("#setup-input", Input).focus()
        logger.info("Textual user setup started")

    def _set_error(self, message: str) -> None:
        self.query_one("#setup-error", Static).update(message)

    def _next_step(self, *, step: str, progress: str, prompt: str, placeholder: str, password: bool = False) -> None:
        self.step = step
        field = self.query_one("#setup-input", Input)
        field.value = ""
        field.placeholder = placeholder
        field.password = password
        self.query_one("#setup-progress", Static).update(progress)
        self.query_one("#setup-prompt", Static).update(prompt)
        self._set_error("")
        self.call_after_refresh(field.focus)

    @on(Input.Submitted, "#setup-input")
    def submit_step(self, event: Input.Submitted) -> None:
        raw = event.value.strip()

        if self.step == "age":
            try:
                age = int(raw)
            except ValueError:
                self._set_error("Digite apenas números.")
                return
            if age < 0 or age > 125:
                self._set_error("Idade inválida.")
                return

            self.data["idade"] = age
            if age < 18:
                logger.info("User setup stopped after age gate")
                self.app.exit(dict(self.data))
                return

            self._next_step(
                step="name",
                progress="Configuração inicial  •  Etapa 2/3",
                prompt="DIGITE SEU NOME DE USUÁRIO:",
                placeholder="Nome de usuário",
            )
            return

        if self.step == "name":
            if len(raw) < 3:
                self._set_error("O nome deve possuir pelo menos 3 caracteres.")
                return
            self.data["nome"] = raw
            self._next_step(
                step="password",
                progress="Configuração inicial  •  Etapa 3/3",
                prompt="DEFINA SUA SENHA:",
                placeholder="Senha",
                password=True,
            )
            return

        if len(raw) < 4:
            self._set_error("Use pelo menos 4 caracteres na senha.")
            return

        self.data["senha"] = raw
        self.query_one("#setup-progress", Static).update("Configuração concluída")
        self.query_one("#setup-prompt", Static).update("Usuário criado com sucesso.")
        event.input.disabled = True
        self._set_error("")
        logger.info("Textual user setup completed")
        self.set_timer(0.35, lambda: self.app.exit(dict(self.data)))


class UserSetupApp(App[dict[str, object] | None]):
    CSS = "Screen { background: #000000; }"

    def on_mount(self) -> None:
        self.push_screen(UserSetupScreen())


class PasswordLoginScreen(Screen):
    AUTO_FOCUS = "#login-input"

    CSS = """
    PasswordLoginScreen {
        background: #000000;
        color: #00ff66;
        align: center middle;
    }

    #login-box {
        width: 70;
        height: auto;
        padding: 1 3;
        border: double #00cc66;
        background: #000000;
    }

    #login-logo {
        height: auto;
        text-align: center;
        color: #00ff66;
        margin-bottom: 1;
    }

    #login-prompt {
        height: 2;
        text-align: center;
        color: #d8ffe7;
    }

    #login-input {
        width: 100%;
        background: #001008;
        color: #ffffff;
        border: tall #00aa55;
    }

    #login-status {
        height: 3;
        text-align: center;
        color: #ff5555;
        margin-top: 1;
    }
    """

    def __init__(self, validator: Callable[[str], bool], max_attempts: int = 3) -> None:
        super().__init__()
        self.validator = validator
        self.max_attempts = max_attempts
        self.attempts = 0

    def compose(self) -> ComposeResult:
        with Vertical(id="login-box"):
            yield Static(viberos_logo(), id="login-logo")
            yield Static("DIGITE SUA SENHA:", id="login-prompt")
            yield Input(id="login-input", placeholder="Senha", password=True)
            yield Static("", id="login-status")

    def on_mount(self) -> None:
        self.query_one("#login-input", Input).focus()
        logger.info("Textual password login started")

    @on(Input.Submitted, "#login-input")
    def submit_password(self, event: Input.Submitted) -> None:
        password = event.value
        event.input.value = ""
        try:
            valid = self.validator(password)
        except Exception:
            logger.exception("Password validator failed")
            valid = False

        if valid:
            logger.info("Textual password login succeeded")
            self.app.exit(True)
            return

        self.attempts += 1
        remaining = self.max_attempts - self.attempts
        if remaining <= 0:
            self.query_one("#login-status", Static).update(
                "Senha incorreta. Desligamento forçado."
            )
            event.input.disabled = True
            logger.warning("Textual password login failed after %s attempts", self.max_attempts)
            self.set_timer(0.45, lambda: self.app.exit(False))
            return

        self.query_one("#login-status", Static).update(
            f"Senha incorreta. {remaining} tentativa(s) restante(s)."
        )
        self.call_after_refresh(event.input.focus)


class PasswordLoginApp(App[bool]):
    CSS = "Screen { background: #000000; }"

    def __init__(self, validator: Callable[[str], bool]) -> None:
        super().__init__(ansi_color=True)
        self.validator = validator

    def on_mount(self) -> None:
        self.push_screen(PasswordLoginScreen(self.validator))


class AgeBlockedApp(App[None]):
    BINDINGS = [Binding("enter", "close", "Continuar", show=False)]
    CSS = """
    Screen {
        background: #000000;
        color: #00ff66;
        align: center middle;
    }
    #age-box {
        width: 72;
        height: auto;
        padding: 2 3;
        border: double #00cc66;
        background: #000000;
    }
    #age-message {
        height: auto;
        text-align: center;
        color: #00ff66;
    }
    #age-hint {
        height: 2;
        text-align: center;
        color: #008f45;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="age-box"):
            yield Static(
                "Acesso bloqueado no Brasil devido à sua idade.",
                id="age-message",
            )
            yield Static("Pressione Enter para continuar.", id="age-hint")

    def action_close(self) -> None:
        self.exit()


def run_boot() -> None:
    stages = (
        "Iniciando aplicativos...",
        "Entrando na vibe...",
        "Codando...",
        "Organizando pastas...",
        "Deixando tudo pronto...",
    )
    LifecycleApp(
        LifecycleScreen(
            mode="boot",
            stages=stages,
            interval=0.70,
            done_message="ViberOS INICIALIZADO COM SUCESSO!",
        )
    ).run(mouse=False)


def run_welcome() -> None:
    LifecycleApp(
        LifecycleScreen(
            mode="boot",
            stages=("Perfil carregado.", "Sessão iniciada."),
            interval=0.35,
            done_message="BEM-VINDO AO ViberOS!",
        )
    ).run(mouse=False)


def run_user_setup() -> dict[str, object] | None:
    return UserSetupApp(ansi_color=True).run(mouse=False)


def run_password_login(validator: Callable[[str], bool]) -> bool:
    return bool(PasswordLoginApp(validator).run(mouse=False))


def run_age_blocked() -> None:
    AgeBlockedApp(ansi_color=True).run(mouse=False)


def make_shutdown_screen(on_complete: Callable[[], None]) -> LifecycleScreen:
    return LifecycleScreen(
        mode="shutdown",
        stages=(
            "Desligando aplicativos...",
            "Saindo da vibe...",
            "Salvando pastas...",
            "Deixando tudo pronto para desligar...",
        ),
        interval=0.35,
        done_message="OBRIGADO POR USAR ViberOS! :)",
        on_complete=on_complete,
        beep=True,
    )


def run_shutdown() -> None:
    screen = LifecycleScreen(
        mode="shutdown",
        stages=(
            "Desligando aplicativos...",
            "Saindo da vibe...",
            "Salvando pastas...",
            "Deixando tudo pronto para desligar...",
        ),
        interval=0.35,
        done_message="OBRIGADO POR USAR ViberOS! :)",
        beep=True,
    )
    LifecycleApp(screen).run(mouse=False)
