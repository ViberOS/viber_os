from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
MODULES_DIR = ROOT_DIR / "modules"
DATA_DIR = ROOT_DIR / "dados"
MEDIA_DIR = ROOT_DIR / "medias"
MUSIC_DIR = MEDIA_DIR / "sons" / "musicas"
SFX_DIR = MEDIA_DIR / "sons" / "efeitos"
LOG_DIR = ROOT_DIR / "logs"
HOME_DIR = MODULES_DIR / "home"

USER_DATA_FILE = DATA_DIR / "dados_usuario.json"
MUSIC_STATE_FILE = DATA_DIR / "musica.json"
SETTINGS_FILE = DATA_DIR / "config.json"
