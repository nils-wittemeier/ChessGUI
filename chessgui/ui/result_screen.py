import tkinter as tk
from tkinter.font import Font

from ..game.result import GameResult


class GameResultScreen:

    def __init__(
        self,
        container: tk.Frame,
        result: GameResult,
    ):
        self.container = container

        self._shadow = tk.Canvas(self.container, bg="#333333", highlightthickness=0)
        self._canvas = tk.Canvas(self.container, highlightthickness=0)
        match (result):
            case GameResult.WIN_WHITE_CHECKMATE | GameResult.WIN_WHITE_RESIGNATION:
                self.title = "White wins."
                self._header_color = "#6f9e77"
            case GameResult.WIN_BLACK_CHECKMATE | GameResult.WIN_BLACK_RESIGNATION:
                self.title = "Black wins"
                self._header_color = "#a3563b"
            case _:
                self.title = "Draw"
                self._header_color = "#aaaaaa"
        match (result):
            case GameResult.WIN_BLACK_RESIGNATION | GameResult.WIN_WHITE_RESIGNATION:
                self.subtitle = "by resignation"
            case GameResult.WIN_BLACK_CHECKMATE | GameResult.WIN_WHITE_CHECKMATE:
                self.subtitle = "by checkmate"
            case GameResult.DRAW_INSUFFICIENT_MATERIAL:
                self.subtitle = "by insufficient material"
            case GameResult.DRAW_BY_50_MOVE:
                self.subtitle = "by 50-move rule"
            case GameResult.DRAW_BY_REPETION:
                self.subtitle = "by three-fold repetition"
            case GameResult.DRAW_BY_STALEMATE:
                self.subtitle = "by stalemate"

        self._header_id = self._canvas.create_polygon(
            [(0, 0), (1, 0)], fill=self._header_color, outline=""
        )

        self.container.bind("<Configure>", self.config_callback, add=True)
        container_size = self.container.winfo_height()
        self.title_font = Font(
            size=container_size // 30,
            weight="bold",
        )

        self._title_id = self._canvas.create_text(
            container_size * 0.3,
            container_size * 0.12,
            text=self.title,
            font=self.title_font,
            anchor="center",
            fill="#ffffff",
        )

        self.subtitle_font = Font(
            size=container_size // 45,
            slant="italic",
            weight="bold",
        )

        self._subtitle_id = self._canvas.create_text(
            container_size * 0.3,
            container_size * 0.18,
            text=self.subtitle,
            font=self.subtitle_font,
            anchor="center",
        )

        self.resize(self.container.winfo_width())

    def config_callback(self, event):
        """Resize the graphical element to match updated size of container"""
        self.resize(event.width)

    def resize(self, container_size):
        # place the window, giving it an explicit size
        canvas_width = 0.6 * container_size
        canvas_height = container_size / 3

        canvas_posx = (container_size - canvas_width) / 2
        canvas_posy = (container_size - canvas_height) / 2

        self._shadow.place(
            in_=self.container,
            x=canvas_posx + 3,
            y=canvas_posy + 3,
            width=canvas_width,
            height=canvas_height,
        )

        self._canvas.place(
            in_=self.container,
            x=canvas_posx,
            y=canvas_posy,
            width=canvas_width,
            height=canvas_height,
        )

        points = [
            -canvas_width * 0.5,
            -canvas_height * 1.2,
            canvas_width * 1.5,
            -canvas_height * 1.2,
            canvas_width * 1.5,
            canvas_height * 0.45,
            -canvas_width * 0.5,
            canvas_height * 0.45,
            -canvas_width * 0.5,
            -canvas_height * 1.2,
        ]
        self._header_id = self._canvas.create_polygon(
            points, fill=self._header_color, smooth=True, splinesteps=128
        )
        self._canvas.lower(self._header_id)
        self.title_font.configure(size=container_size // 30)

        self._canvas.coords(self._title_id, canvas_width * 0.5, canvas_height * 0.30)

        self.subtitle_font.configure(size=container_size // 45)

        self._canvas.coords(self._subtitle_id, canvas_width * 0.5, canvas_height * 0.54)
