from __future__ import annotations

import time
from pathlib import Path

import cv2
import numpy as np
from rich.text import Text


class VideoAscii:
    """Converte frames de vídeo em Rich ``Text`` para terminal/Textual.

    A conversão não depende mais do Console/Live global do modo legado. Isso
    mantém o caminho usado pelo Rick Textual puro em termos de controle do
    terminal; ``play()`` preserva o player Rich standalone por compatibilidade.
    """

    def __init__(self, nome_video: str):
        self.path = Path(__file__).parent.parent / "medias" / "videos" / nome_video
        self.width = 80
        # Mantém exatamente a paleta histórica (incluindo espaço inicial).
        self.chars = np.array(list(" @#S%?*+;:,."))

    def get_ascii_frame(self, frame, width=None, max_height=None):
        # 1. Redimensiona mantendo a proporção (0.5 compensa células do terminal).
        h, w = frame.shape[:2]
        target_width = max(1, int(width or self.width))
        height = max(1, int((h / w) * target_width * 0.5))

        if max_height is not None and height > max(1, int(max_height)):
            scale = max(1, int(max_height)) / height
            target_width = max(1, int(target_width * scale))
            height = max(1, int(max_height))

        frame_resized = cv2.resize(frame, (target_width, height))

        # 2. Converte para cinza para calcular o brilho.
        gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)

        # 3. Mapeamento vetorizado com NumPy.
        indices = (gray / 255 * (len(self.chars) - 1)).astype(int)
        ascii_array = self.chars[indices]

        # 4. Junta tudo em uma string e devolve Rich Text, que Textual renderiza.
        ascii_str = "\n".join("".join(row) for row in ascii_array)
        return Text(ascii_str, style="bold green")

    def play(self) -> None:
        """Player Rich legado/standalone, mantido fora do runtime Textual."""
        # Imports locais evitam que a Screen Textual do Rick carregue Live ou o
        # Console global só por importar o conversor de frames.
        from rich.live import Live
        from modules.console import console

        cap = cv2.VideoCapture(str(self.path))
        try:
            fps = float(cap.get(cv2.CAP_PROP_FPS) or 0)
            if fps <= 0:
                fps = 30.0
            frame_duration = 1.0 / fps

            with Live(console=console, screen=True, auto_refresh=False) as live:
                start_time = time.perf_counter()
                frame_count = 0

                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break

                    elapsed = time.perf_counter() - start_time
                    expected_time = frame_count * frame_duration

                    if elapsed < expected_time:
                        time.sleep(expected_time - elapsed)
                    elif elapsed > expected_time + frame_duration:
                        frame_count += 1
                        continue

                    ascii_text = self.get_ascii_frame(frame, width=console.width)
                    live.update(ascii_text, refresh=True)
                    frame_count += 1
        finally:
            cap.release()


if __name__ == "__main__":
    player = VideoAscii("rickroll.mp4")
    player.play()
