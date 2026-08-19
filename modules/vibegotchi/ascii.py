from pathlib import Path

from modules.core.storage import load_json

SAVE_PATH = Path(__file__).parent / "dados" / "vibes.json"

_FALLBACK = {
    "normal": " /\\_/\\\n( °.° )\n/ >💻 ",
    "feliz": " /\\_/\\\n( ^_^ )\n/ >🎉 ",
    "triste": " /\\_/\\\n( ~_~ )\n/ >💔 ",
    "cansado": " /\\_/\\\n( -_- ) zZ\n/ >🛌 ",
    "sem_aura": " /\\_/\\\n( x_x )\n/ >⚰️ ",
}


def pegar_vibe(pet) -> str:
    vibes = load_json(SAVE_PATH, _FALLBACK)
    if not isinstance(vibes, dict):
        vibes = _FALLBACK

    if pet.aura <= 0:
        return vibes.get("sem_aura", _FALLBACK["sem_aura"])
    if pet.energia < 20:
        return vibes.get("cansado", _FALLBACK["cansado"])
    if pet.humor > 70:
        return vibes.get("feliz", _FALLBACK["feliz"])
    if pet.humor < 30:
        return vibes.get("triste", _FALLBACK["triste"])
    return vibes.get("normal", _FALLBACK["normal"])
