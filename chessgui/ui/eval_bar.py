"""This module implements the graphical interface for an evaluation bar"""

from math import tanh

import tkinter as tk
from tkinter.font import Font

from .colors import _COLORS

_PIECE_COLORS = {"light": "#FFFFFF", "dark": "#272932"}


class EvalBar:
    """The graphical interface for an evaluation bar"""

    def __init__(self, parent: tk.Frame):
        self.evaluation = {"type": "cp", "value": 0.0}

        self.parent = parent
        self.parent.bind("<Configure>", self.config_callback, add=True)

        self._canvas = tk.Canvas(self.parent, highlightthickness=2)
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        self._canvas.grid(row=0, column=0, sticky="nsew")

        self.width = 0.5
        self.height = 1.0

        self.white_bar = self._canvas.create_rectangle(
            0, 0, 2, 2, fill=_COLORS["evalbar"]["light"], outline=""
        )

        self.black_bar = self._canvas.create_rectangle(
            1, 1, 2, 2, fill=_COLORS["evalbar"]["dark"], outline=""
        )

        self.font = Font(size=int(0.2 * self.width), weight="bold")
        self.black_eval = self._canvas.create_text(
            int(0.08 * self.width),
            int(0.08 * self.width),
            font=self.font,
            fill=_PIECE_COLORS["light"],
            anchor="center",
            text="",
        )
        self.white_eval = self._canvas.create_text(
            int(0.08 * self.width),
            self.height - int(0.08 * self.width),
            font=self.font,
            fill=_PIECE_COLORS["dark"],
            anchor="center",
            text="",
        )

    def config_callback(self, event):
        self.redraw(event.width, event.height)

    def redraw(self, parent_width, parent_height):

        height = parent_height

        bar_width = min(100, parent_width // 2)
        x0 = bar_width // 2
        x1 = x0 + bar_width
        y0 = 0
        y1 = height

        self._canvas.coords(self.black_eval, (x0 + x1) // 2, x0 // 2)
        self._canvas.coords(self.white_eval, (x0 + x1) // 2, height - x0 // 2)
        self._canvas.coords(self.white_bar, x0, y0, x1, y1)

        if self.evaluation["type"] == "cp":
            value = self.evaluation["value"] / 100
            y1 = int(height * 0.5 * (1 - tanh(value / 6.8)))
            if y1 > height:
                y1 = height
            if y1 < 0:
                y1 = 0
        else:
            if self.evaluation["value"] > 0:
                y1 = 0
            else:
                y1 = height
        self._canvas.coords(self.black_bar, x0, y0, x1, y1)

        self.font.configure(size=int(0.2 * bar_width))

    def update_eval(self, evaluation: dict) -> None:
        """Update evaluation displayed

        This function changes the height of the bars and alters the text displayed
        withing

        Args:
            evaluation (dict) : A dictionary of the current advantage with
                                "type" as "cp" (centipawns) or "mate" (checkmate in).

        """
        self.evaluation = evaluation
        if self.evaluation["type"] == "cp":
            value = self.evaluation["value"] / 100
            if value > 0.1:
                self._canvas.itemconfigure(self.white_eval, text=f"{value:.1f}")
                self._canvas.itemconfigure(self.black_eval, text="")
            elif value < 0.1:
                self._canvas.itemconfigure(self.white_eval, text="")
                self._canvas.itemconfigure(self.black_eval, text=f"{value:.1f}")
        else:
            value = self.evaluation["value"]
            if value > 0:
                self._canvas.itemconfigure(self.white_eval, text=f"M{value:.1f}")
                self._canvas.itemconfigure(self.black_eval, text="")
            else:
                self._canvas.itemconfigure(self.white_eval, text="")
                self._canvas.itemconfigure(self.black_eval, text=f"M{value:d}")
        self.redraw(self.parent.winfo_width(), self.parent.winfo_height())
