from __future__ import annotations

from modules.achievements.main_achievements import desbloquear
from modules.core.logger import logger
from modules.core.paths import USER_DATA_FILE
from modules.core.storage import load_json
from modules.gerenciar_pastas import gerenciador_pastas
from modules.iniciar import boas_vindas, boot, checar_senha, coletar_dados, desligamento, menor_idade
from modules.menu import menu


def _nome_pasta_usuario(nome: str) -> str:
    seguro = nome.lower()
    for char in " /\\:*?\"<>|":
        seguro = seguro.replace(char, "-")
    return seguro.strip("-.") or "usuario"


def main() -> None:
    boot()

    primeira_vez = not USER_DATA_FILE.exists()
    if primeira_vez:
        if not coletar_dados():
            desligamento()
            return

    dados = load_json(USER_DATA_FILE, {})
    idade_valida = "idade" in dados
    adulto_incompleto = False
    if idade_valida:
        try:
            idade_atual = int(dados.get("idade", 0))
        except (TypeError, ValueError):
            idade_valida = False
            idade_atual = 0
        adulto_incompleto = idade_atual >= 18 and (
            not str(dados.get("nome", "")).strip()
            or not (
                (dados.get("password_hash") and dados.get("password_salt"))
                or "senha" in dados
            )
        )

    if not idade_valida or adulto_incompleto:
        logger.warning("User data invalid or incomplete; collecting again")
        if not coletar_dados():
            desligamento()
            return
        dados = load_json(USER_DATA_FILE, {})
        primeira_vez = True

    if int(dados.get("idade", 0)) < 18:
        menor_idade()
        desligamento()
        return

    if not checar_senha(primeira_vez):
        desligamento()
        return

    desbloquear("sys_primeiro_login")
    boas_vindas()

    nome_dados = str(dados.get("nome", "Usuário"))
    nome = _nome_pasta_usuario(nome_dados)
    user_dir = gerenciador_pastas.raiz / nome
    if not user_dir.exists():
        gerenciador_pastas.criar_pasta_resultado(nome)
    gerenciador_pastas.trocar_pasta_resultado(nome)

    shutdown_animated = False
    try:
        shutdown_animated = bool(menu(nome, nome_dados))
    except (KeyboardInterrupt, EOFError):
        logger.info("Shell interrupted")
    except Exception:
        logger.exception("Fatal shell error")
        raise
    finally:
        # O desligamento normal já acontece dentro do App Textual. Este fallback
        # cobre interrupções, modo legado e encerramentos antes de abrir o menu.
        if not shutdown_animated:
            desligamento()


if __name__ == "__main__":
    main()
