from __future__ import annotations

from modules.caixa_som import caixa_som
from modules.core.logger import logger
from modules.core.paths import USER_DATA_FILE
from modules.core.security import hash_password, verify_password
from modules.core.storage import load_json, save_json


def boot() -> None:
    """Inicialização visual do ViberOS usando Textual."""
    logger.info("Boot started")
    try:
        caixa_som.init()
        caixa_som.tocar_musica(
            "playstation-2-startup-intro-ps2.mp3",
            loop=0,
            salvar_musica_atual=False,
            transicao=False,
        )
    except Exception:
        logger.exception("Boot audio unavailable")

    from modules.ui.lifecycle import run_boot
    run_boot()


def boas_vindas() -> None:
    """Splash pós-login em Textual e início da playlist do sistema."""
    try:
        caixa_som.init()
        caixa_som.tocar_musica(
            "ViberOS.mp3", volume=0.5, loop=0, salvar_musica_atual=True
        )
    except Exception:
        logger.exception("Welcome music unavailable")

    from modules.ui.lifecycle import run_welcome
    run_welcome()


def coletar_dados() -> bool:
    """Executa o wizard Textual de criação do usuário local."""
    from modules.ui.lifecycle import run_user_setup

    profile = run_user_setup()
    if not profile or "idade" not in profile:
        logger.warning("User setup cancelled before creating a profile")
        return False

    idade = int(profile["idade"])
    if idade < 18:
        save_json(USER_DATA_FILE, {"idade": idade})
        return True

    nome = str(profile.get("nome", "")).strip()
    senha = str(profile.get("senha", ""))
    if len(nome) < 3 or len(senha) < 4:
        logger.warning("Textual user setup returned incomplete data")
        return False

    salt, password_hash = hash_password(senha)
    save_json(
        USER_DATA_FILE,
        {
            "idade": idade,
            "nome": nome,
            "password_salt": salt,
            "password_hash": password_hash,
        },
    )
    logger.info("Local user profile created")
    return True


def menor_idade() -> None:
    """Mostra o bloqueio etário no Textual."""
    from modules.ui.lifecycle import run_age_blocked
    run_age_blocked()


def checar_senha(primeira_vez: bool = False) -> bool:
    if primeira_vez:
        return True

    dados = load_json(USER_DATA_FILE, {})
    if not dados:
        return False

    def validar(senha: str) -> bool:
        valid = False
        if dados.get("password_hash") and dados.get("password_salt"):
            valid = verify_password(senha, dados["password_salt"], dados["password_hash"])
        elif "senha" in dados:
            # Migração automática do formato antigo (texto puro) para PBKDF2.
            valid = senha == str(dados.get("senha", ""))
            if valid:
                salt, password_hash = hash_password(senha)
                dados.pop("senha", None)
                dados["password_salt"] = salt
                dados["password_hash"] = password_hash
                save_json(USER_DATA_FILE, dados)
                logger.info("Migrated legacy plaintext password")
        return valid

    from modules.ui.lifecycle import run_password_login
    return run_password_login(validar)


# Compatibilidade com o nome antigo enquanto o restante do projeto é refinado.
def checar_sehha(primeira_vez: bool = False) -> bool:
    return checar_senha(primeira_vez)


def desligamento() -> None:
    """Fallback de desligamento Textual para saídas fora do App principal."""
    try:
        caixa_som.pausar_musica()
    except Exception:
        pass

    from modules.ui.lifecycle import run_shutdown
    run_shutdown()
    logger.info("ViberOS shutdown")


if __name__ == "__main__":
    boot()
    if coletar_dados():
        checar_senha(primeira_vez=True)
    desligamento()
