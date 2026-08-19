from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from modules.core.logger import logger
from modules.core.paths import HOME_DIR


@dataclass(slots=True)
class ResultadoFS:
    ok: bool
    mensagem: str = ""


@dataclass(slots=True)
class ItemFS:
    nome: str
    diretorio: bool
    tamanho: int = 0


@dataclass(slots=True)
class ListagemFS:
    ok: bool
    caminho: str
    itens: list[ItemFS]
    erro: str = ""

    @property
    def quantidade_pastas(self) -> int:
        return sum(item.diretorio for item in self.itens)

    @property
    def quantidade_arquivos(self) -> int:
        return sum(not item.diretorio for item in self.itens)

    @property
    def tamanho_arquivos(self) -> int:
        return sum(item.tamanho for item in self.itens if not item.diretorio)


class GerenciadorPastas:
    """Sistema de arquivos virtual do ViberOS, limitado a ``modules/home``."""

    def __init__(self):
        HOME_DIR.mkdir(parents=True, exist_ok=True)
        self.raiz = HOME_DIR.resolve()
        self.caminho_atual = self.raiz

    def _resolver(self, nome: str | Path = "") -> Path | None:
        nome = str(nome).strip()
        if nome == "/home":
            candidato = self.raiz
        elif nome.startswith("/home/"):
            candidato = (self.raiz / nome.removeprefix("/home/")).resolve()
        else:
            candidato = (self.caminho_atual / nome).resolve() if nome else self.caminho_atual.resolve()
        try:
            candidato.relative_to(self.raiz)
        except ValueError:
            logger.warning("Blocked path escape attempt")
            return None
        return candidato

    def arquivo_existe(self, nome_arquivo: str) -> bool:
        caminho = self._resolver(nome_arquivo)
        return bool(caminho is not None and caminho.exists() and caminho.is_file())

    def get_caminho_home(self, sumprimir_home: bool = True) -> str:
        atual = self.caminho_atual.resolve()
        relativo = atual.relative_to(self.raiz)
        if not relativo.parts:
            return "/home"

        partes = list(relativo.parts)
        if sumprimir_home and len(partes) >= 1:
            # Mantém a convenção visual antiga: dentro do usuário, exibe ~.
            if len(partes) == 1:
                return "[magenta]~[/magenta]"
            return "[magenta]~[/magenta]/" + "/".join(partes[1:])
        return "/home/" + "/".join(partes)

    def criar_pasta_resultado(self, nome_pasta: str) -> ResultadoFS:
        caminho = self._resolver(nome_pasta)
        if caminho is None:
            return ResultadoFS(False, "Caminho inválido.")
        try:
            caminho.mkdir(parents=True, exist_ok=False)
            return ResultadoFS(True, f"Diretório [bold]{nome_pasta}[/bold] criado com sucesso.")
        except FileExistsError:
            return ResultadoFS(False, f"O diretório [bold]{nome_pasta}[/bold] já existe.")
        except OSError as exc:
            logger.warning("mkdir failed: %s", type(exc).__name__)
            return ResultadoFS(False, "Não foi possível criar o diretório.")

    def criar_pasta(self, nome_pasta: str) -> None:
        from modules.console import console, erro
        resultado = self.criar_pasta_resultado(nome_pasta)
        (console.print if resultado.ok else erro)(resultado.mensagem + ("\n" if resultado.ok else ""))

    def criar_arquivo_resultado(self, nome_arquivo: str) -> ResultadoFS:
        caminho = self._resolver(nome_arquivo)
        if caminho is None:
            return ResultadoFS(False, "Caminho inválido.")
        try:
            caminho.parent.mkdir(parents=True, exist_ok=True)
            caminho.touch(exist_ok=False)
            return ResultadoFS(True, f"Arquivo [bold]{nome_arquivo}[/bold] criado com sucesso.")
        except FileExistsError:
            return ResultadoFS(False, f"O arquivo [bold]{nome_arquivo}[/bold] já existe.")
        except OSError:
            return ResultadoFS(False, "Não foi possível criar o arquivo.")

    def criar_arquivo(self, nome_arquivo: str) -> None:
        from modules.console import console, erro
        resultado = self.criar_arquivo_resultado(nome_arquivo)
        (console.print if resultado.ok else erro)(resultado.mensagem + ("\n" if resultado.ok else ""))

    def listar_pasta_resultado(self, nome_pasta: str = "") -> ListagemFS:
        caminho = self._resolver(nome_pasta)
        if caminho is None or not caminho.exists() or not caminho.is_dir():
            return ListagemFS(False, "", [], "Caminho não encontrado.")

        itens: list[ItemFS] = []
        try:
            for item in sorted(caminho.iterdir(), key=lambda p: (not p.is_dir(), p.name.casefold())):
                itens.append(ItemFS(item.name, item.is_dir(), 0 if item.is_dir() else item.stat().st_size))
        except OSError:
            return ListagemFS(False, "", [], "Não foi possível listar o diretório.")

        rel = caminho.relative_to(self.raiz)
        caminho_visual = "/home" + (("/" + rel.as_posix()) if rel.parts else "")
        return ListagemFS(True, caminho_visual, itens)

    def listar_pasta(self, nome_pasta: str = "") -> None:
        from modules.console import console, erro
        lista = self.listar_pasta_resultado(nome_pasta)
        if not lista.ok:
            erro(lista.erro)
            return
        if nome_pasta:
            console.print(f"\n[magenta][bold]Diretório:[/bold] {lista.caminho}[/magenta]")
        console.print()
        for item in lista.itens:
            tipo = "DIR" if item.diretorio else "ARQ"
            console.print(f"[green]<[/green][magenta]{tipo}[/magenta][green]>[/green] [magenta]{item.nome}[/magenta]")
        console.print(
            f"\n    {lista.quantidade_arquivos} {'Arquivo' if lista.quantidade_arquivos == 1 else 'Arquivos'}"
            f"    |   {lista.tamanho_arquivos} bytes"
        )
        console.print(f"    {lista.quantidade_pastas} {'Diretório' if lista.quantidade_pastas == 1 else 'Diretórios'}\n")

    def trocar_pasta_resultado(self, nome_pasta: str) -> ResultadoFS:
        if nome_pasta == "..":
            if self.caminho_atual.resolve() == self.raiz:
                return ResultadoFS(True)
            self.caminho_atual = self.caminho_atual.parent
            return ResultadoFS(True)

        novo = self._resolver(nome_pasta)
        if novo is not None and novo.exists() and novo.is_dir():
            self.caminho_atual = novo
            return ResultadoFS(True)
        return ResultadoFS(False, "Caminho não encontrado.")

    def trocar_pasta(self, nome_pasta: str) -> None:
        from modules.console import erro
        resultado = self.trocar_pasta_resultado(nome_pasta)
        if not resultado.ok:
            erro(resultado.mensagem)

    def deletar_pasta_resultado(self, nome_pasta: str) -> ResultadoFS:
        caminho = self._resolver(nome_pasta)
        if caminho is None or caminho == self.raiz:
            return ResultadoFS(False, "Diretório inválido.")
        if not caminho.exists() or not caminho.is_dir():
            return ResultadoFS(False, f"Pasta [bold]{nome_pasta}[/bold] não encontrada.")
        try:
            caminho.rmdir()
            return ResultadoFS(True, f"Diretório [bold]{nome_pasta}[/bold] deletado com sucesso.")
        except OSError:
            return ResultadoFS(False, "Só é possível deletar pastas vazias.")

    def deletar_pasta(self, nome_pasta: str) -> None:
        from modules.console import console, erro
        resultado = self.deletar_pasta_resultado(nome_pasta)
        (console.print if resultado.ok else erro)(resultado.mensagem + ("\n" if resultado.ok else ""))

    def deletar_arquivo_resultado(self, nome_arquivo: str) -> ResultadoFS:
        caminho = self._resolver(nome_arquivo)
        if caminho is None or not caminho.exists() or not caminho.is_file():
            return ResultadoFS(False, f"Arquivo [bold]{nome_arquivo}[/bold] não encontrado.")
        try:
            caminho.unlink()
            return ResultadoFS(True, f"Arquivo [bold]{nome_arquivo}[/bold] deletado com sucesso.")
        except OSError:
            return ResultadoFS(False, "Não foi possível deletar o arquivo.")

    def deletar_arquivo(self, nome_arquivo: str) -> None:
        from modules.console import console, erro, aviso
        caminho = self._resolver(nome_arquivo)
        if caminho is None or not caminho.exists() or not caminho.is_file():
            erro(f"Arquivo {nome_arquivo} não encontrado.")
            return
        while True:
            certeza = console.input(
                f">>> Deseja mesmo excluir [bold]{nome_arquivo}[/bold]? Ele não poderá ser recuperado depois. (S/N) "
            ).strip().lower()
            if certeza in {"s", "n"}:
                break
            aviso("Resposta inválida. Digite apenas S ou N.\n")
        if certeza == "s":
            resultado = self.deletar_arquivo_resultado(nome_arquivo)
            (console.print if resultado.ok else erro)(resultado.mensagem + ("\n" if resultado.ok else ""))

    def ler_arquivo_resultado(self, nome_arquivo: str) -> ResultadoFS:
        arquivo = self._resolver(nome_arquivo)
        if arquivo is None or not arquivo.exists() or not arquivo.is_file():
            return ResultadoFS(False, f"Arquivo [bold]{nome_arquivo}[/bold] não encontrado.")
        try:
            return ResultadoFS(True, arquivo.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            return ResultadoFS(False, "Não foi possível ler o arquivo como texto UTF-8.")

    def ler_arquivo(self, nome_arquivo: str) -> None:
        from modules.console import console, erro
        resultado = self.ler_arquivo_resultado(nome_arquivo)
        if resultado.ok:
            console.print(f"{resultado.mensagem}\n")
        else:
            erro(resultado.mensagem)

    def adicionar_arquivo_resultado(self, nome_arquivo: str, texto: str) -> ResultadoFS:
        arquivo = self._resolver(nome_arquivo)
        if arquivo is None:
            return ResultadoFS(False, "Caminho inválido.")
        try:
            arquivo.parent.mkdir(parents=True, exist_ok=True)
            with arquivo.open("a", encoding="utf-8") as handle:
                handle.write(texto)
            return ResultadoFS(True)
        except OSError:
            return ResultadoFS(False, "Não foi possível escrever no arquivo.")

    def adicionar_arquivo(self, nome_arquivo: str, texto: str) -> None:
        from modules.console import erro
        resultado = self.adicionar_arquivo_resultado(nome_arquivo, texto)
        if not resultado.ok:
            erro(resultado.mensagem)


gerenciador_pastas = GerenciadorPastas()
