from ..caixa_som import caixa_som


SOUNDS_DIR = "vibe_invader/"

def play_music() -> None:
    caixa_som.tocar_musica(f'{SOUNDS_DIR}vibe_space.mp3', 0.3, False, loop=-1, transicao=False)

def play_boss_music() -> None:
    caixa_som.tocar_musica(f'{SOUNDS_DIR}vibe_boss.mp3', 0.5, False, loop=-1, transicao=False)

def stop_music() -> None:
    caixa_som.pausar_musica()

def play_shoot() -> None:
    efeito = f'{SOUNDS_DIR}shoot.ogg'
    caixa_som.tocar_efeito(efeito, 0.4)

def play_defeat() -> None:
    efeito = f'{SOUNDS_DIR}defeat.ogg'
    caixa_som.tocar_efeito(efeito, 0.4)

def play_explosion() -> None:
    caixa_som.tocar_efeito(f'{SOUNDS_DIR}explosion.ogg')

