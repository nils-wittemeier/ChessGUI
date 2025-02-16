""" Implements a graphical interface for allowing users to selecting a piece
    when promoting a pawn."""

from pathlib import Path
from math import ceil, floor

import tkinter as tk
import tksvg
from stockfish import Stockfish

from .svg import ChessPieceSVG
from ..piece import ChessPiece


class PromotionSelector:
    """This class implement the GUI element for selecting a piece for when
    promoting a pawn.
    """

    def __init__(
        self,
        container: tk.Frame,
        position: tuple[int],
        color_is_white: bool = True,
        visible: bool = False,
    ):

        self.container = container
        self.position = position
        self.visible = visible
        self.callback = None

        self._canvas = tk.Canvas(self.container, highlightthickness=0)
        self._options_canvas = tk.Canvas(self._canvas, highlightthickness=0)

        self._svgs = []
        self._pieces = []
        pieces = "QRBN" if color_is_white else "nbrq"
        for i, p in enumerate(pieces):
            piece = ChessPiece(Stockfish.Piece(p), 7-i, 0)
            self._pieces.append(piece)
            self._svgs.append(ChessPieceSVG(piece, self._options_canvas, 1.0))

        self._options_canvas.bind("<Button-1>", self.select)
        self._canvas.bind("<Button-1>", self.cancel)
        self.container.bind("<Configure>", self.config_callback, add=True)

    @property
    def _is_at_top(self):
        return self.position[0] > 4
    
    @property
    def _width(self):
        return self._canvas.winfo_width()
    
    def select(self, event):
        """Callback for piece selection

        Args:
            TODO: fill

        """
        index = int(event.y / self._width)
        self.callback(self._pieces[index])
        self.hide()

    def cancel(self, event):  # pylint: disable=unused-argument
        """Cancel piece selection"""
        self.hide()

    def config_callback(self, event):
        """Resize the graphical element to match updated size of container"""
        self.resize(event.width)

    def resize(self, container_size):
        """Resize the graphical element to match updated size of container"""
        # place the window, giving it an explicit size
        if self.visible:
            canvas_width = container_size / 8
            button_height = container_size / 16
            canvas_height = container_size / 2 + button_height

            canvas_posx = container_size * self.position[1] / 8
            canvas_poxy = (7 - self.position[0]) * canvas_width
            if not self._is_at_top:
                canvas_poxy += canvas_width - canvas_height

            if self._is_at_top:
                button_posy = canvas_height - button_height / 2
            else:
                button_posy = button_height / 2

            self._canvas.place(
                in_=self.container,
                x=canvas_posx,
                y=canvas_poxy,
                width=canvas_width,
                height=canvas_height,
            )

            self._options_canvas.place(
                in_=self._canvas,
                x=0,
                y=0 if self._is_at_top else button_height,
                width=canvas_width,
                height=canvas_height - button_height,
            )

            self.cross_svg = tksvg.SvgImage(
                data=Path("chessgui/icons/Cross.svg").read_text("UTF-8"),
                scaletoheight=max(1, canvas_width),
            )
            self._canvas.create_image(
                canvas_width / 2, button_posy, image=self.cross_svg
            )

    def hide(self):
        """Hide graphical element"""
        if self.visible:
            self.visible = False
            self.callback = None
            self._canvas.place_forget()

    def show(self):
        """Make graphical element visible"""
        self.visible = True
        self.resize(self.container.winfo_width())

    def open(self, position, callback):
        """Reveal the graphical element at a give position and pass the callback
        to be triggered on piece selection.

        Args:
            position (tuple[int]) : pair of zero-based integers defining the position on the board
                                    where the element should appear
            callback (func): function to be called upon piece selection
        """
        self.position = position
        self.callback = callback
        self.show()
