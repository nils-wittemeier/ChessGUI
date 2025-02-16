"""
This module provides classes and functions for representing chess pieces.

It contains functionality to :
 - evaluate their possible moves on a chess board
 - load SVGs needed to render them on the chess board

Additionally, there is a function to create an instance of any chess piece based on the stockfish
piece type for convenience.

"""

import tkinter as tk
from pathlib import Path

import tksvg
from ..piece import ChessPiece

_PIECE_SVGS = {
    "white": {
        "King": Path("chessgui/icons/Chess_klt45.svg"),
        "Queen": Path("chessgui/icons/Chess_qlt45.svg"),
        "Rook": Path("chessgui/icons/Chess_rlt45.svg"),
        "Bishop": Path("chessgui/icons/Chess_blt45.svg"),
        "Knight": Path("chessgui/icons/Chess_nlt45.svg"),
        "Pawn": Path("chessgui/icons/Chess_plt45.svg"),
    },
    "black": {
        "King": Path("chessgui/icons/Chess_kdt45.svg"),
        "Queen": Path("chessgui/icons/Chess_qdt45.svg"),
        "Rook": Path("chessgui/icons/Chess_rdt45.svg"),
        "Bishop": Path("chessgui/icons/Chess_bdt45.svg"),
        "Knight": Path("chessgui/icons/Chess_ndt45.svg"),
        "Pawn": Path("chessgui/icons/Chess_pdt45.svg"),
    },
}


class SVGContainer:
    def __init__(self, file, canvas: tk.Canvas, posx: int, posy: int, scale: float):
        self._canvas = canvas
        self._posx = posx
        self._posy = posy
        self._scale = scale

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
        return self._posx

    @property
    def posy(self):
        """y coordinate"""
        return self._posy

    def scale_svg(self, size: int) -> tksvg.SvgImage:
        """SVG string for piece render."""
        if self._is_visible:
            self._svg_img = tksvg.SvgImage(data=self._svg_string, scaletoheight=size)
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
        self.scale_svg(event.width * self._scale)

    def show(self):
        self._is_visible = True
        self.scale_svg(self.size)

    def hide(self):
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

    @property
    def posx(self):
        return (self._piece.col + 0.5) * self.size

    @property
    def posy(self):
        return (7 - self._piece.row + 0.5) * self.size

    def move_to(self, row, col):
        self._piece.row = row
        self._piece.col = col
        self.scale_svg(self._svg_img.height())

    def promote(self, promote_to: ChessPiece):
        self._piece.promote(promote_to.type)
        self._svg_string = _PIECE_SVGS[self._piece.color][self._piece.name].read_text()
        self.scale_svg(self._svg_img.height())
