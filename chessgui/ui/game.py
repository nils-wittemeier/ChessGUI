"""
This module provides a graphical user interface (GUI) for playing chess, including the main GameUI
class which manages the overall layout and interaction elements of the game.
"""

from functools import partial

import tkinter as tk

from .promotion_selector import PromotionSelector
from ..game import GameState, Move
from .board import Board
from .square import Square
from ..piece import ChessPiece


class GameUI:
    """
    GameUI class which sets up the main components of the chess game GUI.

    Args:
        parent (tk.Frame): The parent widget that contains this UI element. It should be a
                            tkinter Frame object.
    """

    def __init__(self, parent: tk.Frame):
        self.parent = parent
        self.parent.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)

        self.padding_frame = tk.Frame(parent, background="bisque")
        self.padding_frame.grid(row=0, column=0, sticky="nsew")
        self.padding_frame.rowconfigure(0, weight=1)
        self.padding_frame.columnconfigure(0, weight=1)
        self.padding_frame.bind("<Configure>", self.enforce_aspect_ratio)

        self.content_frame = tk.Frame(self.padding_frame, highlightthickness=0)
        self.content_frame.grid(row=0, column=0, sticky="nsew")
        self.content_frame.rowconfigure(0, weight=1)
        self.content_frame.columnconfigure(0, weight=1)

        # Initialize game state
        self.game_state = GameState()
        self.selected_square = None
        self._possible_moves = []

        # Create UI elements
        self.board = Board(self.content_frame)
        self.board.load_piece_positions(self.game_state)
        self.board._canvas.bind("<Button-1>", self.on_click_callback)

        self.white_selector = PromotionSelector(self.content_frame, (6, 1), True, False)
        self.black_selector = PromotionSelector(self.content_frame, (1, 6), False, False)

    def enforce_aspect_ratio(self, event: tk.Event):
        """
        Enforce the correct aspect ratio of the chess board by resizing and repositioning its components.

        Args:
            event (tk.Event): The tkinter event triggered when the window is resized. It contains information about the new size of the window.

        Returns:
            None
        """
        desired_size = min(event.width, event.height)
        self.content_frame.place(
            in_=self.padding_frame, x=0, y=0, width=desired_size, height=desired_size
        )

    def on_click_callback(self, event):
        """Callback for clicks on the board"""
        # Check whether a square has already been selected
        square = self.board.get_square_from_coords(event.x, event.y)
        if self.selected_square is None:
            self.select_square(square)
        else:
            move = Move(
                self.game_state.get_piece_on(*self.selected_square.coords),
                self.selected_square.coords,
                square.coords,
                self.game_state.get_piece_on(*square.coords),
            )
            # Check if moving from the already selected to the newly clicked square is a legal move
            self.clear_selection()
            if move in self._possible_moves:
                if move.is_promotion:
                    selector = getattr(self, f"{self.game_state.active_color}_selector")
                    selector.open(move.target, callback=partial(self.move_piece, move))
                else:
                    self.move_piece(move)
            else:
                self.on_click_callback(event)
            

    def select_square(self, square: Square) -> None:
        """Select a square on the chess board to highlight possible moves

        Args:
            square (Square): The square.
        """
        # Check if selected square is occupied and by a piece of the active color
        self.board.hide_moves()
        piece = self.game_state.get_piece_on(square.row, square.col)
        if piece is not None:
            if piece.color == self.game_state.get_active_color():
                self.board.select_square(square.row, square.col)
                self._possible_moves = self.game_state.get_possible_moves_from(
                    square.row, square.col
                )
                self.board.show_moves(self._possible_moves)
                self.selected_square = square

    def clear_selection(self) -> None:
        """Clear square selection"""
        self.board.hide_moves()
        self.board.clear_selection()
        self.selected_square = None

    def move_piece(self, move : Move, promote_to: ChessPiece = None):
        self.game_state.make_move(move, promote_to)
        self.board.make_move(move, promote_to)
