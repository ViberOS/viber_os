import time
import random
from modules.console import console
from rich.live import Live
from rich.text import Text

def hacker(segundos: float) -> None:
    cols, rows = console.size
    streams = {x: random.randint(-rows, 0) for x in range(cols)}

    with Live("", refresh_per_second=20, screen=True) as live:
        end = time.time() + segundos
        while time.time() < end:
            grid = [[" "] * cols for _ in range(rows)]
            for x, y in streams.items():
                for i in range(12):
                    r = y - i
                    if 0 <= r < rows:
                        grid[r][x] = random.choice("01")
                streams[x] = y + 1 if y < rows + 12 else random.randint(-rows, 0)
            frame = Text("\n".join("".join(row) for row in grid), style="green")
            live.update(frame)
            time.sleep(0.05)