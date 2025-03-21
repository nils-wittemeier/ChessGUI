"""
This module provides classes and functions for representing chess pieces.

It contains functionality to :
 - evaluate their possible moves on a chess board
 - load SVGs needed to render them on the chess board

Additionally, there is a function to create an instance of any chess piece based on the stockfish
piece type for convenience.

"""

import tkinter as tk
from typing import Optional

import tksvg

from ..files import get_icon
from ..game.piece import ChessPiece

_PIECE_SVGS = {
    "white": {
        "King": get_icon("Chess_klt45"),
        "Queen": get_icon("Chess_qlt45"),
        "Rook": get_icon("Chess_rlt45"),
        "Bishop": get_icon("Chess_blt45"),
        "Knight": get_icon("Chess_nlt45"),
        "Pawn": get_icon("Chess_plt45"),
    },
    "black": {
        "King": get_icon("Chess_kdt45"),
        "Queen": get_icon("Chess_qdt45"),
        "Rook": get_icon("Chess_rdt45"),
        "Bishop": get_icon("Chess_bdt45"),
        "Knight": get_icon("Chess_ndt45"),
        "Pawn": get_icon("Chess_pdt45"),
    },
}


class SVGContainer:
    def __init__(
        self,
        file,
        canvas: tk.Canvas,
        posx: float,
        posy: float,
        scale: tuple[float, float],
        centered: Optional[bool] = False
    ):
        self._canvas = canvas
        self._posx = posx
        self._posy = posy
        self._scale = scale
        self._centered = centered

        self._svg_string = file.read_text("UTF-8")
        self._svg_img = None
        self._svg_handle = None
        self._is_visible = True

        self.scale_svg(100)
        self._canvas.bind("<Configure>", self.draw, add=True)

    @property
    def size(self):
        """Size of SVG image"""
        return self._svg_img.height()

    @property
    def posx(self):
        """x coordinate"""
        if self._centered:
            return self._canvas.winfo_width() * 0.5
        else:
            return self._posx

    @property
    def posy(self):
        """y coordinate"""
        if self._centered:
            return self._canvas.winfo_height() * 0.5
        else:
            return self._posy

    def scale_svg(self, size: int) -> tksvg.SvgImage:
        """SVG string for piece render."""
        self._svg_img = tksvg.SvgImage(data=self._svg_string, scaletoheight=size)
        if self._is_visible:
            self._svg_handle = self._canvas.create_image(
                self.posx,
                self.posy,
                image=self._svg_img,
            )

    def update_pos(self, posx, posy):
        self._posx = posx
        self._posy = posy
        self.scale_svg(self.size)

    def draw(self, event):
        """Resize the canvas and reposition pieces when resized.

        Args:
            event (tkinter.Event): The event triggered by resizing.

        Returns:
            None
        """
        self.scale_svg(event.height * self._scale[1] * 0.95)

    def show(self):
        self._is_visible = True
        self.scale_svg(self.size)

    def remove(self):
        self._canvas.delete(self._svg_handle)
        self._is_visible = False

    @property
    def is_visible(self):
        return self._is_visible


class ChessPieceSVG(SVGContainer):
    """Base class for all chess pieces."""

    def __init__(
        self,
        piece: ChessPiece,
        canvas: tk.Canvas,
        scale: float,
    ):
        self._piece = piece
        super().__init__(
            _PIECE_SVGS[self._piece.color][self._piece.name],
            canvas,
            self._piece.col,
            (7 - self._piece.row),
            scale,
        )

    def __repr__(self):
        return self._piece.type.__repr__

    @property
    def posx(self):
        return self._canvas.winfo_width() * self._scale[0] * (self._piece.col + 0.5)

    @property
    def posy(self):
        return self._canvas.winfo_height() * self._scale[1] * (self._piece.row + 0.5)

    def move_to(self, row, col):
        self._piece.row = row
        self._piece.col = col
        self.scale_svg(self._svg_img.height())

    def promote(self, promote_to: ChessPiece):
        self._piece.promote(promote_to.type)
        self._svg_string = _PIECE_SVGS[self._piece.color][self._piece.name].read_text()
        self.scale_svg(self._svg_img.height())
