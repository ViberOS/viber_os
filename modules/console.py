from rich.console import Console
from modules.caixa_som import caixa_som

import os

console = Console(style='green')

def limpar_tela() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')

def som_erro(func):
    def wrapper(*args, **kwargs):
        caixa_som.init()

        func(*args, **kwargs)

        caixa_som.tocar_efeito('error.ogg.mp3')

    return wrapper

@som_erro
def erro(msg: str) -> None:
    console.print(f'[bold red]Erro:[/bold red] {msg}\n')

@som_erro
def aviso(msg: str) -> None:
    console.print(f'[bold yellow]Aviso:[/bold yellow] {msg}\n')
