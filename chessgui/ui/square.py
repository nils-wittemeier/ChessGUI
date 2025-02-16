""" This module implements the squares on the chess board as a graphical elements"""
from pathlib import Path

import tkinter as tk
from tkinter.font import Font

from .svg import SVGContainer
from ..colors import _COLORS


class Square:
    """This class implement a square on the chess board as a GUI element"""

    font_scale = 0.14

    def __init__(self, canvas: tk.Canvas, rank: int, file: int):
        self._canvas = canvas
        self._size = 1
        self._x = file
        self._y = rank
        self._id = canvas.create_rectangle(0, 0, 1, 1, outline="")
        self._row = rank
        self._col = file
        self._is_highlighted = False
        self.last_move = False
        self.selected = False
        self.move_highlight = None
        self.color = "light" if (rank + file) % 2 == 0 else "dark"
        self._canvas.bind("<Configure>", self.draw, add=True)

        self.font = Font(
            family="Roboto",
            size=int(self.font_scale * self._canvas.winfo_height()),
            weight="bold",
        )

        self.rank_label = None
        self.file_label = None
        self.add_label(
            rank=file if rank == 0 else None,
            file=rank if file == 0 else None,
        )

        self._circlesvg = SVGContainer(
            Path("chessgui/icons/Circle.svg"),
            self._canvas,
            posx=self._x + self._size / 2,
            posy=self._y + self._size / 2,
            scale=1/8)
        self._circlesvg.hide()

    @property
    def color(self):
        """Square color"""
        return self._color

    @property
    def row(self):
        """Zero-based row index"""
        return self._row

    @property
    def col(self):
        """Zero-based column index"""
        return self._col

    @property
    def coords(self):
        """Coordinates"""
        return self._row, self._col

    @color.setter
    def color(self, s: str):
        if s.lower() not in ["light", "dark"]:
            raise ValueError(f"Square: invalid color specifier: {s}")
        self._color = s.lower()
        self.refresh_color()

    def refresh_color(self):
        """Set background color"""
        if self.selected:
            hl_type = "selected"
        elif self.last_move:
            hl_type = "moved"
        else:
            hl_type = "none"

        self._canvas.itemconfig(
            self._id, fill=_COLORS["board"]["background"][hl_type][self.color]
        )

    def toggle_selected(self):
        """Toggle highlighting of selected square"""
        self.selected = not self.selected
        self.refresh_color()

    def clear_selected(self):
        """Turn  off highlighting of selected square"""
        self.selected = False
        self.refresh_color()

    def toggle_move_target(self):
        """Toggle highlighting of selected square"""
        if self._circlesvg.is_visible:
            self._circlesvg.hide()
        else:
            self._circlesvg.show()
        self.refresh_color()

    def hide_move_target(self):
        """Toggle highlighting of selected square"""
        if self._circlesvg.is_visible:
            self._circlesvg.hide()
        self.refresh_color()

    def toggle_moved(self):
        """Toggle highlighting of selected square"""
        self.last_move = not self.last_move
        self.refresh_color()

    def to_index(self):
        return self.row, self.col

    def to_algebraic(self):
        """Return algebraic notation for current square"""
        row, col = self.to_index()
        return "abcdefgh"[row] + str(8 - col)

    def draw(self, event):
        self._size = event.width / 8
        self._x = x0 = self.col * self._size
        x1 = (self.col + 1) * self._size
        self._y = y0 = (7 - self.row) * self._size
        y1 = (8 - self.row) * self._size

        self._canvas.coords(self._id, x0, y0, x1, y1)
        self.font.configure(size=int(self.font_scale * self._size))
        self._circlesvg.update_pos(x0 + self._size / 2, y0 + self._size / 2)

        if self.rank_label is not None:
            self._canvas.moveto(
                self.rank_label, x0 + int(0.9 * self._size), y0 + int(0.83 * self._size)
            )

        if self.file_label is not None:
            self._canvas.moveto(
                self.file_label,
                x0 + int(0.04 * self._size),
                y0 + int(0.04 * self._size),
            )

    def add_label(self, rank: int | None = None, file: int | None = None):
        """Add rank of file label to this square"""
        if rank is not None:
            self.rank_label = self._canvas.create_text(
                int(0.96 * self._size),
                self._size,
                text="abcdefgh"[rank],
                font=self.font,
                anchor="se",
                fill=_COLORS["board"]["foreground"][self._color],
            )

        if file is not None:
            self.file_label = self._canvas.create_text(
                int(0.04 * self._size),
                int(0.04 * self._size),
                text=str(file + 1),
                font=self.font,
                anchor="nw",
                fill=_COLORS["board"]["foreground"][self._color],
            )
