# importação de rich
from rich.live import Live
from rich.text import Text

# outras importações
from modules.console import console
import time, random
from threading import Thread, Event
from art import text2art

LOGO = text2art('ViberOS').splitlines()

COLORS = ["red", "green", "yellow", "blue", "magenta", "cyan", "bright_white"]

logo_w = max(len(line) for line in LOGO)
logo_h = len(LOGO)

def draw(x, y, color, cols, rows):
    grid = [[" "] * cols for _ in range(rows)]
    for i, line in enumerate(LOGO):
        for j, ch in enumerate(line):
            r, c = y + i, x + j
            if 0 <= r < rows and 0 <= c < cols:
                grid[r][c] = ch
    text = Text()
    for i, row in enumerate(grid):
        text.append("".join(row), style=color)
        if i < rows - 1:
            text.append("\n")
    return text

def dvd():
    stop = Event()
    Thread(target=lambda: (input(), stop.set()), daemon=True).start()

    x, y = 2, 2
    dx, dy = 1, 1
    color = random.choice(COLORS)

    with Live("", refresh_per_second=24, screen=True) as live:
        while not stop.is_set():
            cols, rows = console.size
            hit = False
            if x + dx < 0 or x + dx + logo_w > cols:
                dx *= -1
                hit = True
            if y + dy < 0 or y + dy + logo_h > rows:
                dy *= -1
                hit = True
            if hit:
                color = random.choice([c for c in COLORS if c != color])
            x += dx
            y += dy
            live.update(draw(x, y, color, cols, rows))
            time.sleep(0.04)
