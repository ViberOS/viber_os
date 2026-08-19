# ── MIGRAÇÃO Rich → Textual ───────────────────────────────────────────────────
# Este arquivo NÃO foi alterado na migração.
# Boss.draw() retorna Rich Panel/Align — consumido por VibeInvadersWidget.
# ─────────────────────────────────────────────────────────────────────────────
import random
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.console import Group
from modules.space_invader import config
from modules.space_invader.config import WIDTH, HEIGHT
from modules.space_invader import sound

# ── constantes do boss ────────────────────────────────────────────────────────
BOSS_MAX_HP = 25

# sprites vibe — box-drawing largura 1 garantida
_FRAMES_VIBE = {
    1: [                        # nave — calmo
        ["◄╦►", "╠╬╣", "◄╩►"],
        ["◄╦►", "╠╋╣", "◄╩►"],
    ],
    2: [                        # escudo — agitado
        ["╔╦╗", "╠╬╣", "╚╩╝"],
        ["╔╦╗", "╠╪╣", "╚╩╝"],
    ],
    3: [                        # caveira — frenético
        ["▄╦▄", "╠╳╣", "▀╩▀"],
        ["▄╦▄", "╠✕╣", "▀╩▀"],
    ],
}

# sprites retro — ASCII clássico
_FRAMES_RETRO = {
    1: [
        ["\\^/", "[W]", "/ \\"],
        [" ^ ", "[W]", "/ \\"],
    ],
    2: [
        [">^<", "{W}", "\\ /"],
        ["-^-", "{W}", "\\ /"],
    ],
    3: [
        ["*^*", "<W>", "* *"],
        ["!^!", "<W>", "! !"],
    ],
}

# cor da borda por fase
_BORDER = {1: "green", 2: "yellow", 3: "red"}

# velocidade lateral por fase — reduzida 65%
_SPEED = {1: 0.14, 2: 0.28, 3: 0.49}

# intervalo entre tiros (em frames) por fase
_FIRE_RATE = {1: 55, 2: 35, 3: 30}

# quantidade de balas por fase
_BULLET_COUNT = {1: 1, 2: 2, 3: 3}


# ── classe Boss ───────────────────────────────────────────────────────────────
class Boss:
    def __init__(self):
        self.hp          = BOSS_MAX_HP
        self.x           = float(WIDTH // 2)
        self.y           = 3
        self.direction   = 1
        self.bullets     = []
        self._frame_idx  = 0
        self._frame_tick = 0
        self._fire_tick  = 0
        self.defeated    = False
        self._death_explosions = []
        self._death_timer      = 0

        # fase 1 — mudança aleatória de direção
        self._dir_tick   = 0

        # fase 2 — escudo
        self.shield_active = False
        self._shield_timer = 0
        self._shield_triggered = False  # ativa só uma vez em 12hp

        # fase 3 — canhão
        self.cannon_active  = False
        self._cannon_timer  = 0
        self._cannon_x      = 0
        self._cannon_triggered_5  = False
        self._cannon_triggered_3  = False

        # animação de entrada
        self.intro_tick  = 0
        self.intro_done  = False

        sound.play_boss_music()

    # ── fase atual ────────────────────────────────────────────────────────────
    @property
    def phase(self) -> int:
        if self.hp > 16:
            return 1
        elif self.hp > 8:
            return 2
        else:
            return 3

    # ── sprite atual (3 linhas) ───────────────────────────────────────────────
    @property
    def sprite_lines(self) -> list:
        frames = _FRAMES_VIBE if getattr(config, '_current_style', 'retro') == 'vibe' else _FRAMES_RETRO
        return frames[self.phase][self._frame_idx % len(frames[self.phase])]

    # ── barra de vida ─────────────────────────────────────────────────────────
    def _health_bar(self) -> Text:
        filled = round(self.hp / BOSS_MAX_HP * 10)
        empty  = 10 - filled
        color  = {1: "green", 2: "yellow", 3: "red"}[self.phase]
        bar    = Text()
        bar.append("VIBE DESTROYER  [", style="bold white")
        bar.append("█" * filled, style=color)
        bar.append("░" * empty,  style="dim white")
        bar.append(f"]  {self.hp}/{BOSS_MAX_HP}", style="white")
        return bar

    # ── update ────────────────────────────────────────────────────────────────
    def update(self, player_pos: int) -> None:
        # ---- intro ----
        if not self.intro_done:
            self.intro_tick += 1
            if self.intro_tick >= 48:   # 3 piscadas × 8 frames × 2 = 48 frames (~2s)
                self.intro_done = True
            return

        # ---- morte em cascata ----
        if self.hp <= 0:
            self._death_timer += 1
            for exp in self._death_explosions:
                exp[2] -= 1
            self._death_explosions = [e for e in self._death_explosions if e[2] > 0]

            # adiciona explosões aleatórias enquanto anima
            if self._death_timer % 4 == 0 and self._death_timer < 60:
                for _ in range(3):
                    ex = random.randint(int(self.x) - 6, int(self.x) + 6)
                    ey = random.randint(self.y - 2, self.y + 2)
                    self._death_explosions.append([ex, max(0, ey), 6])
                    sound.play_explosion()

            if self._death_timer >= 72:
                self.defeated = True
            return

        # ---- animação do sprite ----
        self._frame_tick += 1
        speed_ticks = {1: 8, 2: 5, 3: 3}[self.phase]
        if self._frame_tick >= speed_ticks:
            self._frame_tick = 0
            self._frame_idx  = (self._frame_idx + 1) % 4

        # ---- fase 1: mudança aleatória de direção (2% por frame) ----
        if self.phase == 1 and random.random() < 0.02:
            self.direction *= -1

        # ---- movimento lateral ----
        self.x += _SPEED[self.phase] * self.direction
        if self.x >= WIDTH - 4:
            self.x = WIDTH - 4
            self.direction = -1
        elif self.x <= 2:
            self.x = 2
            self.direction = 1

        # ---- fase 2: escudo ativa em 12hp e reativa a cada 96 frames (só vibe) ----
        is_vibe = getattr(config, '_current_style', 'retro') == 'vibe'
        if is_vibe and self.hp <= 12:
            if not self._shield_triggered:
                self._shield_triggered = True
                self.shield_active = True
                self._shield_timer = 40
            elif not self.shield_active:
                self._dir_tick += 1
                if self._dir_tick >= 96:
                    self._dir_tick = 0
                    self.shield_active = True
                    self._shield_timer = 40

        if self.shield_active:
            self._shield_timer -= 1
            if self._shield_timer <= 0:
                self.shield_active = False

        # ---- fase 3: canhão em 5hp e 3hp (só vibe) ----
        if is_vibe and self.hp <= 5 and not self._cannon_triggered_5:
            self._cannon_triggered_5 = True
            self.cannon_active = True
            self._cannon_timer = 56  # dura 2,3 segundos
            self._cannon_x = int(self.x)

        if is_vibe and self.hp <= 3 and not self._cannon_triggered_3:
            self._cannon_triggered_3 = True
            self.cannon_active = True
            self._cannon_timer = 64 # dura 2,5 segundos
            self._cannon_x = int(self.x)

        if self.cannon_active:
            self._cannon_timer -= 1
            self._cannon_x = int(self.x)  # acompanha o boss
            if self._cannon_timer <= 0:
                self.cannon_active = False

        # ---- tiro do boss ----
        self._fire_tick += 1
        if self._fire_tick >= _FIRE_RATE[self.phase]:
            self._fire_tick = 0
            self._shoot(player_pos)

        # ---- balas do boss ----
        for b in self.bullets:
            b[1] += 1
        self.bullets = [b for b in self.bullets if b[1] < HEIGHT]

    # ── disparo ───────────────────────────────────────────────────────────────
    def _shoot(self, player_pos: int) -> None:
        count = _BULLET_COUNT[self.phase]
        bx    = int(self.x)

        if count == 1:
            self.bullets.append([bx, self.y + 1])
        elif count == 2:
            self.bullets.append([bx - 1, self.y + 1])
            self.bullets.append([bx + 1, self.y + 1])
        elif count == 3:
            self.bullets.append([bx,     self.y + 1])
            self.bullets.append([bx - 2, self.y + 1])
            self.bullets.append([bx + 2, self.y + 1])

    # ── recebe dano ───────────────────────────────────────────────────────────
    def hit(self) -> None:
        if self.hp <= 0:
            return
        self.hp -= 1
        sound.play_explosion()
        if self.hp <= 0:
            sound.play_defeat()
            # conquista só no modo vibe
            if getattr(config, '_current_style', 'retro') == 'vibe':
                from modules.achievements.main_achievements import desbloquear
                desbloquear("vi_boss_derrotado")

    # ── draw ──────────────────────────────────────────────────────────────────
    def draw(self, player_pos: int, player_bullet: list | None,
             score: int, highscore: int) -> Align:

        screen = [[" " for _ in range(WIDTH)] for _ in range(HEIGHT)]

        # player
        screen[HEIGHT - 1][player_pos] = config.PLAYER_CHAR

        # bala do player
        if player_bullet:
            by = int(player_bullet[1])
            bx = player_bullet[0]
            if 0 <= by < HEIGHT and 0 <= bx < WIDTH:
                screen[by][bx] = config.BULLET_CHAR

        # boss — sprite 3x3
        bx = int(self.x)
        if self.hp > 0:
            for row_offset, line in enumerate(self.sprite_lines):
                sy = self.y + row_offset
                for col_offset, ch in enumerate(line):
                    nx = bx - 1 + col_offset
                    if 0 <= sy < HEIGHT and 0 <= nx < WIDTH:
                        screen[sy][nx] = ch

        # escudo — linha abaixo do sprite (fase 2, só vibe)
        if self.shield_active:
            shield_y = self.y + 3
            for nx in range(max(0, bx - 2), min(WIDTH, bx + 3)):
                if 0 <= shield_y < HEIGHT:
                    screen[shield_y][nx] = "█"

        # canhão — coluna descendo rápido (fase 3, só vibe)
        if self.cannon_active:
            cannon_progress = int((24 - self._cannon_timer) / 24 * HEIGHT)
            for cy in range(self.y + 3, min(HEIGHT, self.y + 3 + cannon_progress)):
                if 0 <= self._cannon_x < WIDTH:
                    screen[cy][self._cannon_x] = "█"

        # balas do boss
        is_vibe = getattr(config, '_current_style', 'retro') == 'vibe'
        for bull in self.bullets:
            bby, bbx = int(bull[1]), int(bull[0])
            if 0 <= bby < HEIGHT and 0 <= bbx < WIDTH:
                screen[bby][bbx] = "▼" if is_vibe else "!"

        # explosões de morte
        for ex, ey, _ in self._death_explosions:
            if 0 <= ey < HEIGHT and 0 <= ex < WIDTH:
                screen[ey][ex] = config.EXPLOSION_CHAR

        text = Text()
        for row in screen:
            text.append("".join(row) + "\n")

        border = _BORDER[self.phase]
        title_text = (
            f"[{border}]BOSS  "
            f"SCORE: {score} | HIGH: {highscore}[/{border}]"
        )

        # durante a intro mostra painel de anúncio no lugar do jogo
        if not self.intro_done:
            blink_on   = (self.intro_tick % 8) < 4
            titulo_cor = "bold red" if blink_on else "bold green"

            # padding vertical pra centralizar — painel tem HEIGHT+4 linhas
            # borda ocupa 2, conteúdo tem 5 linhas, então padding = (HEIGHT+2-5)//2
            pad = "\n" * ((HEIGHT - 3) // 2)

            intro_text = Text(justify="center")
            intro_text.append(pad)
            intro_text.append("⚠  WAVE 10  ⚠\n\n", style="bold green")
            intro_text.append("VIBE DESTROYER\n\n", style="bold green")
            intro_text.append("prepara-se...\n",    style="green")

            panel = Panel(
                intro_text,
                border_style="green",
                width=WIDTH + 4,
                height=HEIGHT + 4,
                expand=False,
                title=f"[{titulo_cor}]*** BOSS INCOMING ***[/{titulo_cor}]",
            )
            return Align.center(panel, vertical="middle")

        content = Group(text, self._health_bar())

        panel = Panel(
            content,
            border_style=border,
            width=WIDTH + 4,
            height=HEIGHT + 4,
            expand=False,
            title=title_text,
        )

        return Align.center(panel, vertical="middle")
