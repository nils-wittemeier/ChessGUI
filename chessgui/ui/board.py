""" This module implements a chess board as a graphical elements"""

import tkinter as tk

from ..game.moves import Move
from ..game.piece import ChessPiece
from ..game.state import GameState
from ..ui.square import Square
from .svg import ChessPieceSVG


class Board:
    """The graphical element representing a chess board"""

    def __init__(self, content_frame: tk.Frame):
        self._canvas = tk.Canvas(content_frame, highlightthickness=0)
        self._canvas.grid(row=0, column=0, sticky="nsew")
        self._squares: list[Square] = [Square(self._canvas, i // 8, i % 8) for i in range(64)]
        self._pieces: dict[tuple[int, int], ChessPieceSVG] = {}
        content_frame.bind("<Configure>", self.draw)

    @property
    def size(self) -> int:
        return self._canvas.winfo_width()

    def load_piece_positions(self, game_state: GameState):
        """Setup of all pieces acording to the current game state

        Args:
            game_state (GameState): _description_
        """
        self._pieces = {}
        for row in range(8):
            for col in range(8):
                piece = game_state.get_piece_on(row, col)
                if piece is not None:
                    self._pieces[(row,col)] = ChessPieceSVG(piece, self._canvas, 1 / 8)

    def get_square(self, row: int, col: int) -> Square:
        """Return the square in a given row and column.

        Args:
            row (int): The zero-based row index of the square.
            col (int): The zero-based column index of the square.

        Returns:
            Square: The square at the position.
        """
        return self._squares[8 * row + col]

    def coords_to_index(self, x: int, y: int) -> tuple[int]:
        """
        Convert to coordinates on the canvas to row and column index of the
        corresponding square.

        Args:
            x (float): The x coordinate.
            y (float): The y coordiante.

        Returns:
            tuple[int] : The row and column index
        """
        col = int(8 * x / self.size)
        row = int(8 * y / self.size)
        return row, col

    def get_square_from_coords(self, x: float, y: float) -> Square:
        """
        Return the square corresponding to a set of coordinates on the canvas

        Args:
            x (float): The x coordinate.
            y (float): The y coordiante.

        Returns:
            tuple[int] : The row and column index
        """
        return self.get_square(*self.coords_to_index(x, y))

    def get_piece_on(self, row: int, col: int) -> ChessPiece:
        return self._pieces[(row, col)]

    def select_square(self, row: int, col: int):
        """TODO

        Args:
            row (int): The zero-based row index of the square.
            col (int): The zero-based column index of the square.
        """
        # Check whether a square has already been selected
        square = self.get_square(row, col)
        # square.

        square.toggle_selected()

    def draw(self, event):
        for square in self._squares:
            square.draw(event)
        for piece in self._pieces.values():
            piece.draw(event)

    def clear_selection(self):
        """Clear all selected squares."""
        for square in self._squares:
            square.clear_selected()

    def show_moves(self, moves : list[Move]):
        """Highlight possible moves."""
        for move in moves:
            self.get_square(*move.target).show_move_target(move.is_capture)

    def hide_moves(self):
        """Hide possible moves that were highlight."""
        for square in self._squares:
            square.hide_move_target()


    def make_move(self, move: Move):
        """Make a move on the chess board"""
        piece = self._pieces.pop(move.origin)
        if move.is_promotion:
            piece.promote(move.promote_to)
        if move.is_capture:
            captured_piece = self._pieces.pop(move.target)
            captured_piece.hide()
        self._pieces[move.target] = piece
        piece.move_to(*move.target)
        if move.is_castling:
            print(move.rook_move)
            self.make_move(move.rook_move)
