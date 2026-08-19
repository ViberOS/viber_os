from __future__ import annotations

import calendar
from datetime import datetime

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

from modules.core.navigation import close_current_view

MESES = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]


def verificar_ano_valido(ano: int) -> bool:
    return ano >= 1


def verificar_mes_valido(mes: int) -> bool:
    return 1 <= mes <= 12


def verificar_dia_valido(dia: int, ano: int, mes: int) -> bool:
    try:
        _, ultimo_dia = calendar.monthrange(ano, mes)
    except calendar.IllegalMonthError:
        return False
    return ano >= 1 and 1 <= dia <= ultimo_dia


def _calendar_render(ano: int, mes: int, dia_escolhido: int, goto_buffer: str | None, erro_msg: str) -> Align:
    cal = calendar.monthcalendar(ano, mes)
    tabela = Table(title=f"[bold green3]{MESES[mes - 1].upper()} / {ano}[/bold green3]", show_lines=True, header_style="bold green3")
    for d in ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]:
        tabela.add_column(d, justify="center")
    for semana in cal:
        linha = [
            f"[bold green1][{dia}][/bold green1]" if dia == dia_escolhido else (str(dia) if dia else "")
            for dia in semana
        ]
        tabela.add_row(*linha)

    titulo = Panel(Align.center(text2art("CALENDARIO")), style="green", box=box.DOUBLE)
    if goto_buffer is None:
        footer = Text("←→ / A,D: Mês | G: Ir para DD/MM/AAAA | Q/Esc: Voltar", style="dim green", justify="center")
    else:
        footer = Text()
        footer.append("Ir para data: ", style="green")
        footer.append(goto_buffer + "█", style="bold white")
        footer.append("   Enter confirma | Esc cancela", style="dim green")
        footer.justify = "center"
    if erro_msg:
        footer.append("\n" + erro_msg, style="bold red")

    return Align.center(Panel(Group(titulo, tabela, footer), border_style="green"), vertical="middle")


class CalendarWidget(Widget):
    can_focus = True

    def __init__(self) -> None:
        super().__init__()
        agora = datetime.now()
        self.ano = agora.year
        self.mes = agora.month
        self.dia = agora.day
        self.goto_buffer: str | None = None
        self.erro_msg = ""

    def on_mount(self) -> None:
        self.focus()

    def _move_month(self, delta: int) -> None:
        total = self.ano * 12 + (self.mes - 1) + delta
        if total < 12:  # não existe ano 0 no calendar do Python
            self.ano, self.mes = 1, 1
        else:
            self.ano, zero_based = divmod(total, 12)
            self.mes = zero_based + 1
        self.dia = min(self.dia, calendar.monthrange(self.ano, self.mes)[1])

    def _confirm_goto(self) -> None:
        raw = (self.goto_buffer or "").strip().replace("-", "/")
        try:
            dia, mes, ano = (int(part) for part in raw.split("/"))
        except (ValueError, TypeError):
            self.erro_msg = "Formato inválido. Use DD/MM/AAAA."
            return
        if not verificar_dia_valido(dia, ano, mes):
            self.erro_msg = "Data inválida."
            return
        self.dia, self.mes, self.ano = dia, mes, ano
        self.goto_buffer = None
        self.erro_msg = ""

    def on_key(self, event: Key) -> None:
        key = event.key.lower()
        if self.goto_buffer is not None:
            if key == "escape":
                self.goto_buffer = None
                self.erro_msg = ""
            elif key == "enter":
                self._confirm_goto()
            elif key == "backspace":
                self.goto_buffer = self.goto_buffer[:-1]
                self.erro_msg = ""
            elif len(event.character or "") == 1 and (event.character.isdigit() or event.character in "/-"):
                if len(self.goto_buffer) < 10:
                    self.goto_buffer += event.character
                    self.erro_msg = ""
            else:
                return
            event.stop()
            self.refresh()
            return

        if key in {"left", "a"}:
            self._move_month(-1)
        elif key in {"right", "d"}:
            self._move_month(1)
        elif key == "g":
            self.goto_buffer = ""
            self.erro_msg = ""
        elif key in {"q", "escape"}:
            close_current_view(self)
        else:
            return
        event.stop()
        self.refresh()

    def render(self) -> RenderResult:
        return _calendar_render(self.ano, self.mes, self.dia, self.goto_buffer, self.erro_msg)


class CalendarApp(App[None]):
    CSS = """
    Screen { align: center middle; background: #000000; }
    CalendarWidget { width: 85%; height: 90%; }
    """

    def compose(self) -> ComposeResult:
        yield CalendarWidget()


def calendario() -> None:
    from modules.achievements.main_achievements import desbloquear
    desbloquear("cal_primeira_vez")
    CalendarApp(ansi_color=True).run(mouse=False)


if __name__ == "__main__":
    calendario()
