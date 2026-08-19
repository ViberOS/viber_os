# ── migração pro Textual ───────────────────────────────────────────────────
# Este arquivo NÃO foi alterado na migração.
# game.draw() continua retornando Rich Panel/Align — o Textual os renderiza
# nativamente via VibeInvadersWidget.render() em widget.py.
# ─────────────────────────────────────────────────────────────────────────────
import random
import os
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from modules.achievements.main_achievements import desbloquear
from modules.space_invader import config
from modules.space_invader.config import WIDTH, HEIGHT
from modules.space_invader import sound
from modules.space_invader.boss import Boss

BOSS_WAVE = int(os.environ.get("VIBEROS_BOSS_WAVE", "10"))


def _formation_linha() -> list:
    return [[x, 2] for x in range(5, WIDTH - 5, 4)]


def _formation_v() -> list:
    center = WIDTH // 2
    xs = [center - 8, center - 4, center, center + 4, center + 8]
    return [[x, 2 + abs(x - center) // 2] for x in xs]


def _formation_disperso() -> list:
    xs = random.sample(range(3, WIDTH - 3), 6)
    return [[x, random.randint(1, 4)] for x in xs]


def _formation_duas_fileiras() -> list:
    fileira1 = [[x, 2] for x in range(5, WIDTH - 6, 9)]
    fileira2 = [[x, 5] for x in range(9, WIDTH - 6, 9)]
    return fileira1 + fileira2


_FORMATIONS = [
    _formation_linha,
    _formation_v,
    _formation_disperso,
    _formation_duas_fileiras,
]


def _make_wave(wave_number: int) -> list:
    formation = random.choice(_FORMATIONS)
    return formation()


class Game:
    def __init__(self, highscore):
        self.player_pos = WIDTH // 2
        self.bullet = None
        self.game_over = False
        self.score = 0
        self.highscore = highscore

        #w
        self.wave = 1
        self.enemies = _make_wave(self.wave)
        self.enemy_speed = 0.05
        self._speed_increment = 0.001  # era 0.01, reduzido 90%
        self._wave_cleared = False

        #ex
        self.explosions = []

        # boss
        self.boss = None
        self.victory = False

        sound.play_music()


    def _current_speed(self) -> float:
        return self.enemy_speed + self._speed_increment * (self.wave - 1)

   
    def update(self) -> None:

        # ── modo boss ────────────────────────────────────────────────────────
        if self.boss:
            # bala do player
            if self.bullet:
                self.bullet[1] -= 1
                if self.bullet[1] < 0:
                    self.bullet = None

            # colisão bala × escudo
            if self.bullet and self.boss.shield_active:
                bx, by = self.bullet[0], self.bullet[1]
                shield_y = self.boss.y + 3
                if (by == shield_y
                        and abs(int(self.boss.x) - bx) <= 2):
                    self.bullet = None

            # colisão bala × boss (cobre as 3 linhas do sprite)
            if self.bullet and self.boss.hp > 0 and self.boss.intro_done:
                bx, by = self.bullet[0], self.bullet[1]
                if (abs(int(self.boss.x) - bx) <= 1
                        and self.boss.y <= by <= self.boss.y + 2):
                    self.boss.hit()
                    self.bullet = None

            # canhão × player
            if self.boss.cannon_active:
                cannon_progress = int((24 - self.boss._cannon_timer) / 24 * HEIGHT)
                cannon_bottom = self.boss.y + 3 + cannon_progress
                if (self.boss._cannon_x == self.player_pos
                        and cannon_bottom >= HEIGHT - 1):
                    self.game_over = True
                    sound.play_defeat()
                    return

            # bala do boss × player
            for bull in self.boss.bullets:
                if (int(bull[1]) >= HEIGHT - 1
                        and abs(int(bull[0]) - self.player_pos) <= 1):
                    self.game_over = True
                    sound.play_defeat()
                    return

            self.boss.update(self.player_pos)

            if self.boss.defeated:
                self.victory = True
                self.score += 500

            return

        # ── modo normal ───────────────────────────────────────────────────────
        if self.bullet:
            self.bullet[1] -= 1
            if self.bullet[1] < 0:
                self.bullet = None

        # colisão bala × inimigo
        if self.bullet:
            for enemy in self.enemies:
                if (enemy[0] == self.bullet[0]
                        and abs(enemy[1] - self.bullet[1]) <= 1.0):
                    self.explosions.append([enemy[0], int(enemy[1]), 8])
                    self.enemies.remove(enemy)
                    self.bullet = None
                    self.score += 10
                    sound.play_explosion()
                    break

        # explosões
        for exp in self.explosions:
            exp[2] -= 1
        self.explosions = [e for e in self.explosions if e[2] > 0]

        # movimento inimigos
        speed = self._current_speed()
        for enemy in self.enemies:
            enemy[1] += speed
            if int(enemy[1]) >= HEIGHT - 1:
                self.game_over = True

        if self.game_over:
            sound.play_defeat()
            return

        # respawn / próxima onda
        if not self.enemies and not self._wave_cleared:
            self._wave_cleared = True
            self.wave += 1
            self.score += self.wave * 50

            # conquistas de wave
            if self.wave == 2:
                desbloquear("vi_primeira_onda")
            elif self.wave == 5:
                desbloquear("vi_wave_5")

            if self.wave == BOSS_WAVE:
                self.boss = Boss()
                # não reseta _wave_cleared para não spawnar inimigos junto
            else:
                self.enemies = _make_wave(self.wave)
                self._wave_cleared = False


    def handle_input(self, key) -> None:
        if (key == b'a' or key == b'K') and self.player_pos > 0:
            self.player_pos -= 1
        elif (key == b'd' or key == b'M') and self.player_pos < WIDTH - 1:
            self.player_pos += 1
        elif key == b' ' and self.bullet is None:
            self.bullet = [self.player_pos, HEIGHT - 2]
            sound.play_shoot()

   
    def draw(self) -> Align:
        # delega pro boss quando tiver ativo
        if self.boss:
            return self.boss.draw(
                self.player_pos, self.bullet,
                self.score, self.highscore
            )

        screen = [[" " for _ in range(WIDTH)] for _ in range(HEIGHT)]

        screen[HEIGHT - 1][self.player_pos] = config.PLAYER_CHAR

        if self.bullet:
            screen[int(self.bullet[1])][self.bullet[0]] = config.BULLET_CHAR

        for ex, ey in self.enemies:
            screen[int(ey)][ex] = config.ENEMY_CHAR

        for ex, ey, frames in self.explosions:
            if 0 <= ey < HEIGHT and 0 <= ex < WIDTH:
                screen[ey][ex] = config.EXPLOSION_CHAR if frames > 4 else "*"

        text = Text()
        for row in screen:
            text.append("".join(row) + "\n")

        panel = Panel(
            text,
            border_style="green",
            width=WIDTH + 4,
            height=HEIGHT + 4,
            expand=False,
            title=(
                f"[green]WAVE: {self.wave} | "
                f"SCORE: {self.score} | "
                f"HIGH: {self.highscore}[/green]"
            )
        )

        return Align.center(panel, vertical="middle")
