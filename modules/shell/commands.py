from __future__ import annotations

import shlex
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from simpleeval import NumberTooHigh, OperatorNotDefined, SimpleEval

from modules.caixa_som import caixa_som
from modules.core.logger import command_name, logger
from modules.core.paths import ROOT_DIR
from modules.core.settings import KERNEL_VERSION, settings
from modules.gerenciar_pastas import gerenciador_pastas


@dataclass(slots=True)
class CommandResult:
    output: list[Any] = field(default_factory=list)
    clear: bool = False
    shutdown: bool = False
    redraw: bool = False
    launch: str | None = None
    launch_args: tuple[Any, ...] = ()
    confirm_delete: str | None = None
    back_to_menu: bool = False


class CommandProcessor:
    """Interpreta comandos sem depender da interface (Rich ou Textual)."""

    PUBLIC_COMMANDS = (
        "clear", "ls", "cd", "pwd", "mkdir", "touch", "rm", "rmdir",
        "cat", "echo", "man", "help", "whoami", "hostname", "uname",
        "calendar", "music", "vibegotchi", "vibe_invaders", "achievements",
        "settings", "changelog", "logs", "menu", "shutdown", "viber",
    )

    def __init__(self, username: str, display_name: str):
        self.username = username
        self.display_name = display_name

    @staticmethod
    def _ok(message: str) -> Text:
        return Text.from_markup(message, style="green")

    @staticmethod
    def _error(message: str) -> Text:
        return Text.from_markup(f"[bold red]Erro:[/bold red] {message}")

    @staticmethod
    def _warning(message: str) -> Text:
        return Text.from_markup(f"[bold yellow]Aviso:[/bold yellow] {message}")

    def execute(self, raw: str) -> CommandResult:
        raw = raw.strip()
        logger.info("Shell command: %s", command_name(raw))
        if not raw:
            return CommandResult()

        try:
            args = shlex.split(raw, posix=True)
        except ValueError:
            return CommandResult([self._error("Aspas não foram fechadas corretamente.")])
        if not args:
            return CommandResult()

        command = args[0].lower()
        rest = args[1:]

        # Aliases compatíveis com o menu antigo.
        aliases = {
            "1": "calendar", "2": "music", "3": "vibegotchi",
            "4": "vibe_invaders", "5": "achievements", "6": "menu",
            "7": "help", "8": "shutdown", "conquistas": "achievements",
            "whoiam": "whoami",  # typo histórico mantido como alias
            "cd..": "cd",
        }
        if command == "cd..":
            rest = [".."]
        command = aliases.get(command, command)

        if command == "clear":
            return CommandResult(clear=True, redraw=True)
        if command == "whoami":
            return CommandResult([Text(self.display_name, style="magenta")])
        if command == "pwd":
            return CommandResult([Text.from_markup(gerenciador_pastas.get_caminho_home(False))])
        if command == "hostname":
            return CommandResult([Text("vibe-os", style="bright_green")])
        if command == "uname":
            return CommandResult([Text(KERNEL_VERSION)])
        if command == "menu":
            return CommandResult(back_to_menu=True)
        if command == "shutdown":
            return CommandResult(shutdown=True)

        if command == "ls":
            if len(rest) > 1:
                return CommandResult([self._error("Use: ls [caminho]")])
            listing = gerenciador_pastas.listar_pasta_resultado(rest[0] if rest else "")
            if not listing.ok:
                return CommandResult([self._error(listing.erro)])
            text = Text()
            if rest:
                text.append(f"Diretório: {listing.caminho}\n", style="bold magenta")
            for item in listing.itens:
                text.append("<", style="green")
                text.append("DIR" if item.diretorio else "ARQ", style="magenta")
                text.append("> ", style="green")
                text.append(item.nome + "\n", style="magenta")
            text.append(
                f"\n{listing.quantidade_arquivos} arquivo(s) | {listing.tamanho_arquivos} bytes | "
                f"{listing.quantidade_pastas} diretório(s)",
                style="dim green",
            )
            return CommandResult([text])

        if command == "cd":
            if len(rest) != 1:
                return CommandResult([self._error("Use: cd <diretório>")])
            result = gerenciador_pastas.trocar_pasta_resultado(rest[0])
            return CommandResult([] if result.ok else [self._error(result.mensagem)])

        if command == "mkdir":
            if not rest:
                return CommandResult([self._warning("Esperava ao menos um nome de diretório.")])
            output = []
            for name in rest:
                result = gerenciador_pastas.criar_pasta_resultado(name)
                output.append(self._ok(result.mensagem) if result.ok else self._error(result.mensagem))
            return CommandResult(output)

        if command == "touch":
            if len(rest) != 1:
                return CommandResult([self._error("Use: touch <arquivo>")])
            result = gerenciador_pastas.criar_arquivo_resultado(rest[0])
            return CommandResult([self._ok(result.mensagem) if result.ok else self._error(result.mensagem)])

        if command == "rm":
            if len(rest) != 1:
                return CommandResult([self._error("Use: rm <arquivo>")])
            if not gerenciador_pastas.arquivo_existe(rest[0]):
                return CommandResult([self._error(f"Arquivo [bold]{rest[0]}[/bold] não encontrado.")])
            return CommandResult(confirm_delete=rest[0])

        if command == "rmdir":
            if not rest:
                return CommandResult([self._error("Use: rmdir <pasta> [outra_pasta ...]")])
            output = []
            for name in rest:
                result = gerenciador_pastas.deletar_pasta_resultado(name)
                output.append(self._ok(result.mensagem) if result.ok else self._error(result.mensagem))
            return CommandResult(output)

        if command == "cat":
            if len(rest) != 1:
                return CommandResult([self._error("Use: cat <arquivo>")])
            result = gerenciador_pastas.ler_arquivo_resultado(rest[0])
            return CommandResult([Text(result.mensagem)] if result.ok else [self._error(result.mensagem)])

        if command == "echo":
            return self._echo(rest)

        if command == "help":
            return CommandResult([Panel(Markdown((ROOT_DIR / "modules" / "help.md").read_text(encoding="utf-8")))])

        if command == "man":
            if len(rest) != 1:
                return CommandResult([self._error("Use: man <comando>")])
            manual = self._manual(rest[0])
            return CommandResult([manual] if manual else [self._error("Comando não reconhecido.")])

        if command == "calendar":
            return CommandResult(launch="calendar", redraw=True)
        if command == "vibegotchi":
            return CommandResult(launch="vibegotchi", redraw=True)
        if command == "vibe_invaders":
            return CommandResult(launch="vibe_invaders", redraw=True)
        if command == "achievements":
            return CommandResult(launch="achievements", redraw=True)

        if command == "music":
            if not rest:
                return CommandResult(launch="music", redraw=True)
            return self._music(rest)

        if command == "settings":
            return self._settings(rest)

        if command == "changelog":
            path = ROOT_DIR / "CHANGELOG.md"
            return CommandResult([Panel(Markdown(path.read_text(encoding="utf-8")))])

        if command == "logs":
            log_file = ROOT_DIR / "logs" / "viber_os.log"
            if not log_file.exists():
                return CommandResult([Text("Nenhum log gerado ainda.", style="dim green")])
            try:
                lines = log_file.read_text(encoding="utf-8").splitlines()[-30:]
                return CommandResult([Panel(Text("\n".join(lines)), title="Últimos logs", border_style="green")])
            except OSError:
                return CommandResult([self._error("Não foi possível ler o arquivo de log.")])

        if command == "viber":
            return CommandResult([self._warning("Viber está dormindo, por enquanto.")])

        # Comandos secretos continuam funcionando, mas não entram no autocomplete.
        if command == "rick":
            return CommandResult(launch="rick", redraw=True)
        if command == "felou":
            return CommandResult(launch="felou", redraw=True)
        if command in {"dvd", "protect"}:
            return CommandResult(launch="dvd", redraw=True)
        if command in {"soldar", "kratos", "ares"}:
            return CommandResult(launch="soldar", redraw=True)
        if command in {"hacker", "matrix"}:
            seconds = 10.0
            if rest:
                if len(rest) != 1:
                    return CommandResult([self._error("Use: hacker [segundos]")])
                try:
                    seconds = float(rest[0].replace(",", "."))
                except ValueError:
                    return CommandResult([self._error("Tempo inválido.")])
                if seconds <= 0:
                    return CommandResult([self._warning("O tempo deve ser maior que zero.")])
            return CommandResult(launch="hacker", launch_args=(seconds,), redraw=True)

        return self._calculator_or_unknown(raw, command)

    def confirm_delete(self, filename: str, yes: bool) -> CommandResult:
        if not yes:
            return CommandResult([Text("Exclusão cancelada.", style="dim green")])
        result = gerenciador_pastas.deletar_arquivo_resultado(filename)
        return CommandResult([self._ok(result.mensagem) if result.ok else self._error(result.mensagem)])

    def _echo(self, rest: list[str]) -> CommandResult:
        if not rest:
            return CommandResult([Text("")])
        if ">" not in rest:
            return CommandResult([Text(" ".join(rest))])
        if rest.count(">") != 1:
            return CommandResult([self._error("Redirecionamento inválido.")])
        idx = rest.index(">")
        if idx == 0 or idx != len(rest) - 2:
            return CommandResult([self._error("Use: echo <texto> > <arquivo>")])
        text = " ".join(rest[:idx])
        filename = rest[-1]
        result = gerenciador_pastas.adicionar_arquivo_resultado(filename, text)
        return CommandResult([] if result.ok else [self._error(result.mensagem)])

    def _manual(self, target: str) -> Panel | None:
        lines = (ROOT_DIR / "modules" / "help.md").read_text(encoding="utf-8").splitlines()
        needle = f"**{target}:"
        start = next((i for i, line in enumerate(lines) if line.lower().startswith(needle.lower())), None)
        if start is None:
            return None
        end = start + 1
        while end < len(lines):
            line = lines[end]
            if line.startswith("**") or line.startswith("---") or line.startswith("# "):
                break
            end += 1
        return Panel(Markdown("\n".join(lines[start:end])))

    def _music(self, rest: list[str]) -> CommandResult:
        sub = rest[0].lower()
        if sub == "next":
            track = caixa_som.tocar_proxima()
            return CommandResult([Text(f"♫ {Path(track).stem}", style="bold green")] if track else [])
        if sub in {"mute", "mudo"}:
            caixa_som.mutar()
            return CommandResult([Text("Música silenciada.", style="dim green")])
        if sub in {"unmute", "som"}:
            caixa_som.desmutar()
            return CommandResult([Text("Música reativada.", style="green")])
        if sub in {"status", "now", "nowplaying"}:
            return CommandResult([Text(f"♫ {Path(caixa_som.get_musica_atual()).stem}", style="green")])
        return CommandResult([self._error("Use: music [next|mute|unmute|status]")])

    def _settings(self, rest: list[str]) -> CommandResult:
        if not rest:
            text = Text()
            text.append("Configurações globais\n\n", style="bold green")
            text.append(f"volume: {settings.music_volume:.2f}\n")
            text.append(f"fade: {settings.music_fade_ms} ms\n")
            text.append(f"shuffle: {'on' if settings.music_shuffle else 'off'}\n")
            text.append(f"autoplay: {'on' if settings.music_autoplay else 'off'}\n")
            text.append(f"theme: {settings.theme}\n")
            text.append(f"language: {settings.language}\n")
            return CommandResult([text])
        if len(rest) != 2:
            return CommandResult([self._error("Use: settings <volume|fade|shuffle|autoplay> <valor>")])

        key, value = rest[0].lower(), rest[1].lower()
        try:
            if key == "volume":
                settings.music_volume = max(0.0, min(float(value.replace(",", ".")), 1.0))
            elif key == "fade":
                settings.music_fade_ms = max(0, min(int(value), 10_000))
            elif key in {"shuffle", "autoplay"}:
                if value not in {"on", "off"}:
                    raise ValueError
                setattr(settings, f"music_{key}", value == "on")
            else:
                return CommandResult([self._error("Configuração ainda não editável por comando.")])
        except ValueError:
            return CommandResult([self._error("Valor inválido.")])
        settings.save()
        if key == "volume":
            caixa_som.set_volume(settings.music_volume)
        caixa_som.garantir_playlist()
        return CommandResult([Text("Configuração salva.", style="green")])

    def _calculator_or_unknown(self, raw: str, command: str) -> CommandResult:
        calculator = SimpleEval(functions={}, names={})
        calculator.disallow_attributes = True
        try:
            result = calculator.eval(raw.replace(",", "."))
            if isinstance(result, (int, float)):
                return CommandResult([Text(f">>> {result:g}")])
        except ZeroDivisionError:
            return CommandResult([Text(">>> Indefinido ou indeterminado.")])
        except OperatorNotDefined:
            return CommandResult([self._error("Operador desconhecido.")])
        except NumberTooHigh:
            return CommandResult([self._warning("A expressão é grande demais.")])
        except Exception:
            pass
        return CommandResult([self._error(f"Comando [italic]{command}[/italic] desconhecido.")])
