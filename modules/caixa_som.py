from __future__ import annotations

import random
from pathlib import Path

from pygame import mixer

from modules.core.logger import logger
from modules.core.paths import MUSIC_DIR, MUSIC_STATE_FILE, SFX_DIR
from modules.core.settings import settings
from modules.core.storage import load_json, save_json


class CaixaSom:
    """Gerenciador central de áudio do ViberOS.

    A música usa ``pygame.mixer.music`` (streaming). Por isso as transições são
    sequenciais: fade-out da faixa atual e fade-in da próxima, sem carregar duas
    músicas inteiras na memória ao mesmo tempo.
    """

    _instance = None
    _SYSTEM_TRACKS = {
        "playstation-2-startup-intro-ps2.mp3",
        "Rickroll.mp3",
        "homens_queimem_a_vila.mp3",
        "felou.mp3",
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_configured", False):
            return
        self._configured = True

        self.musicas = MUSIC_DIR
        self.efeitos = SFX_DIR
        self.musica_atual = MUSIC_STATE_FILE

        raw = load_json(MUSIC_STATE_FILE, {"musica_atual": "ViberOS.mp3"})
        old_current = str(raw.get("musica_atual", "ViberOS.mp3"))
        self._muted = bool(raw.get("muted", old_current == "mute"))
        self._current_track = "ViberOS.mp3" if old_current == "mute" else old_current

        self._playlist_enabled = False
        self._queue: list[str] = []
        self._transition_id = 0
        self._transitioning = False
        # No runtime Textual, toda operação de pygame.mixer.music fica na
        # mesma thread do event loop. Isso evita disputar o mixer entre
        # threads enquanto o terminal está em application mode.
        self._scheduler = None

    def init(self) -> None:
        if not mixer.get_init():
            try:
                mixer.init()
                logger.info("Audio mixer initialized")
            except Exception:
                logger.exception("Failed to initialize audio mixer")
                raise

    def set_scheduler(self, scheduler) -> None:
        """Registra o scheduler do Textual para transições sem threads.

        ``scheduler(delay_seconds, callback)`` deve agendar o callback no
        event loop da interface. Fora do ViberOS integrado, a troca continua
        funcionando sem fade-out bloqueante e mantém apenas o fade-in.
        """
        self._scheduler = scheduler

    def clear_scheduler(self) -> None:
        self._scheduler = None

    def _cancel_transition(self) -> None:
        self._transition_id += 1
        self._transitioning = False

    def _save_state(self) -> None:
        save_json(
            MUSIC_STATE_FILE,
            {
                "musica_atual": self._current_track,
                "muted": self._muted,
                "autoplay": settings.music_autoplay,
                "shuffle": settings.music_shuffle,
            },
        )

    def get_musica_atual(self) -> str:
        return "mute" if self._muted else self._current_track

    def tocar_efeito(self, nome_efeito: str, volume: float = 1) -> None:
        self.init()
        try:
            efeito = mixer.Sound(Path(self.efeitos / nome_efeito))
            efeito.set_volume(max(0.0, min(volume * settings.effects_volume, 1.0)))
            efeito.play()
        except Exception:
            logger.exception("Failed to play sound effect: %s", nome_efeito)

    def _play_now(self, nome_musica: str, *, volume: float, loop: int, fadein_ms: int = 0) -> None:
        self.init()
        caminho = Path(self.musicas / nome_musica)
        if not caminho.exists():
            logger.warning("Music file not found: %s", caminho)
            return

        mixer.music.load(caminho)
        mixer.music.set_volume(max(0.0, min(volume, 1.0)))
        mixer.music.play(loop, fade_ms=max(0, int(fadein_ms)))
        logger.info("Music started: %s", nome_musica)

    def tocar_musica(
        self,
        nome_musica: str | Path,
        volume: float | None = None,
        salvar_musica_atual: bool = True,
        loop: int = -1,
        fadeout: float = 0,
        *,
        fadein: int | None = None,
        transicao: bool | None = None,
    ) -> None:
        """Toca uma música mantendo compatibilidade com a API antiga.

        Faixas escolhidas pelo usuário (``salvar_musica_atual=True``) entram no
        modo playlist e usam transição suave. Faixas de apps/jogos são tratadas
        como contexto temporário e não entram na fila automática.
        """
        nome = str(nome_musica)
        volume = settings.music_volume if volume is None else volume

        if nome == "mute":
            self.mutar()
            return

        if self._muted and salvar_musica_atual:
            self._muted = False

        if salvar_musica_atual:
            self._current_track = nome
            self._playlist_enabled = settings.music_autoplay
            self._refill_queue(exclude={nome})
            self._save_state()
        else:
            # Música de boot, easter egg ou aplicativo: não deixa a playlist
            # interromper o contexto antes de o app devolver o controle.
            self._playlist_enabled = False
            self._cancel_transition()

        # Compatibilidade: o antigo argumento fadeout significava iniciar a
        # faixa e já agendar seu fade-out (usado na tela de boot).
        if fadeout:
            self._play_now(nome, volume=volume, loop=loop, fadein_ms=fadein or 0)
            mixer.music.fadeout(int(fadeout))
            return

        if transicao is None:
            transicao = salvar_musica_atual and self.get_busy_music()

        fade_ms = settings.music_fade_ms if fadein is None else max(0, int(fadein))
        if transicao:
            self._transition(nome, volume=volume, loop=loop, fade_ms=fade_ms)
        else:
            # Invalida callbacks de uma transição anterior antes de tocar
            # diretamente. Sem isso, um timer antigo ainda poderia baixar o
            # volume da faixa recém-iniciada.
            self._cancel_transition()
            self._play_now(nome, volume=volume, loop=loop, fadein_ms=fade_ms if (salvar_musica_atual or fadein is not None) else 0)

    def _transition(self, nome: str, *, volume: float, loop: int, fade_ms: int) -> None:
        """Troca de faixa sem usar pygame em threads de fundo.

        Com Textual ativo, o volume atual cai em pequenos passos agendados no
        próprio event loop; ao chegar a zero a nova faixa começa com o fade-in
        nativo do pygame. Em wrappers standalone, a troca é imediata com
        fade-in para não bloquear a TUI com ``mixer.music.fadeout``.
        """
        self._transition_id += 1
        transition_id = self._transition_id
        self._transitioning = True

        def still_current() -> bool:
            return transition_id == self._transition_id

        def finish() -> None:
            if not still_current():
                return
            try:
                self._play_now(nome, volume=volume, loop=loop, fadein_ms=fade_ms)
            except Exception:
                logger.exception("Music transition failed: %s", nome)
            finally:
                if still_current():
                    self._transitioning = False

        scheduler = self._scheduler
        if scheduler is None or fade_ms <= 0 or not self.get_busy_music():
            finish()
            return

        try:
            start_volume = mixer.music.get_volume()
        except Exception:
            start_volume = volume

        steps = max(4, min(16, fade_ms // 100 or 4))
        total_seconds = fade_ms / 1000.0

        # O último passo de volume precisa acontecer *antes* de ``finish``.
        # Antes ambos eram agendados para o mesmo instante; dependendo da ordem
        # do event loop, a faixa nova podia iniciar e logo depois receber
        # ``set_volume(0)``, ficando muda até o usuário trocar/mutar novamente.
        for step in range(1, steps + 1):
            delay = total_seconds * step / (steps + 1)

            def lower_volume(step=step) -> None:
                if not still_current() or not mixer.get_init():
                    return
                try:
                    fraction = max(0.0, 1.0 - step / steps)
                    mixer.music.set_volume(start_volume * fraction)
                except Exception:
                    logger.exception("Could not update music fade volume")

            scheduler(delay, lower_volume)

        scheduler(total_seconds, finish)

    def _refill_queue(self, *, exclude: set[str] | None = None) -> None:
        exclude = exclude or set()
        tracks = [p.name for p in self.listar_musicas() if p.name not in exclude]
        if settings.music_shuffle:
            random.shuffle(tracks)
        self._queue = tracks

    def tocar_proxima(self) -> str | None:
        if self._muted:
            return None

        if not self._queue:
            self._refill_queue(exclude={self._current_track})
        if not self._queue:
            return None

        proxima = self._queue.pop(0)
        self._current_track = proxima
        self._playlist_enabled = settings.music_autoplay
        self._save_state()
        busy = self.get_busy_music()

        if busy:
            self._transition(
                proxima,
                volume=settings.music_volume,
                loop=0,
                fade_ms=settings.music_fade_ms,
            )
        else:
            self._play_now(proxima, volume=settings.music_volume, loop=0, fadein_ms=settings.music_fade_ms)
        return proxima

    def atualizar_playlist(self) -> None:
        """Avança a playlist quando a faixa atual termina."""
        if (
            settings.music_autoplay
            and self._playlist_enabled
            and not self._muted
            and not self._transitioning
            and not self.get_busy_music()
        ):
            self.tocar_proxima()

    def garantir_playlist(self) -> None:
        """Retoma a trilha do sistema depois de sair de um app/jogo."""
        if self._muted or not settings.music_autoplay:
            return
        self._playlist_enabled = True
        if not self.get_busy_music():
            if self._current_track and (self.musicas / self._current_track).exists():
                self._play_now(
                    self._current_track,
                    volume=settings.music_volume,
                    loop=0,
                    fadein_ms=settings.music_fade_ms,
                )
            else:
                self.tocar_proxima()

    def mutar(self) -> None:
        self._muted = True
        self._playlist_enabled = False
        self._cancel_transition()
        if mixer.get_init() and mixer.music.get_busy():
            mixer.music.stop()
        self._save_state()
        logger.info("Music muted")

    def desmutar(self) -> None:
        self._muted = False
        self._playlist_enabled = settings.music_autoplay
        self._save_state()
        self.garantir_playlist()

    def set_volume(self, volume: float) -> None:
        settings.music_volume = max(0.0, min(float(volume), 1.0))
        settings.save()
        if mixer.get_init():
            mixer.music.set_volume(settings.music_volume)

    def pausar_musica(self) -> None:
        self._cancel_transition()
        self._playlist_enabled = False
        if mixer.get_init():
            mixer.music.stop()

    def get_busy_music(self) -> bool:
        return bool(mixer.get_init() and mixer.music.get_busy())

    def listar_musicas(self) -> list[Path]:
        if not self.musicas.exists():
            return []
        musicas = [
            m for m in self.musicas.glob("*.mp3")
            if m.name not in self._SYSTEM_TRACKS
        ]
        return sorted(musicas, key=lambda p: p.name.casefold())


caixa_som = CaixaSom()

if __name__ == "__main__":
    caixa_som.init()
    caixa_som.tocar_efeito("error.ogg.mp3")
