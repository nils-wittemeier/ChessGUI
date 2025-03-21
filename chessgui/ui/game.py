"""
This module provides a graphical user interface (GUI) for playing chess, including the main GameUI
class which manages the overall layout and interaction elements of the game.
"""

from pathlib import Path
import tkinter as tk
from functools import partial
from multiprocessing import Process

from stockfish import Stockfish

from ..game.piece import ChessPiece
from ..game.game import ChessGame
from ..game.tree import GameTreeNode
from ..game.moves import Move
from .board import Board
from .eval_bar import EvalBar
from .sidebar_right import SecondSideBar
from .promotion_selector import PromotionSelector
from .square import Square
from .result_screen import GameResultScreen


class GameUI:
    """
    GameUI class which sets up the main components of the chess game GUI.

    Args:
        parent (tk.Frame): The parent widget that contains this UI element. It should be a
                            tkinter Frame object.
    """

    def __init__(self, parent: tk.Frame, stockfish_exe: str):
        self.parent = parent
        self.parent.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)

        self.padding_frame = tk.Frame(parent, background="#eeeeee")
        self.padding_frame.grid(row=0, column=0, sticky="nsew")
        self.padding_frame.rowconfigure(0, weight=1)
        self.padding_frame.columnconfigure(0, weight=1)
        self.padding_frame.bind("<Configure>", self.enforce_aspect_ratio)

        self.board_frame = tk.Frame(self.padding_frame, highlightthickness=0)
        self.board_frame.rowconfigure(0, weight=1)
        self.board_frame.columnconfigure(0, weight=1)

        self.left_sidebar = tk.Frame(self.padding_frame, highlightthickness=0)
        self.right_sidebar = tk.Frame(self.padding_frame, highlightthickness=0)

        # Initialize game state
        self.game = ChessGame()
        self.selected_square = None
        self._possible_moves = []

        # Create UI elements
        self.board = Board(self.board_frame)
        self.board.load_piece_positions(self.game.state)
        self.board._canvas.bind("<Button-1>", self.on_click_callback)
        self.white_selector = PromotionSelector(self.board_frame, (6, 1), True, False)
        self.black_selector = PromotionSelector(self.board_frame, (1, 6), False, False)
        self.eval_bar = EvalBar(self.left_sidebar)
        self.moves_overview = SecondSideBar(
            self.right_sidebar, self.game.move_tree, self.change_position_callback
        )

        # Engine
        if Path(stockfish_exe).is_file():
            try:
                self.engine = Stockfish(path=stockfish_exe)
            except OSError:
                tk.messagebox.showwarning("No engine selected", "Warning: selected executable could not be loaded.")

            self.engine.set_fen_position(self.game.state.to_fen_string())
            self.eval_bar.update_eval(self.engine.get_evaluation())
            self.eval_proc = Process(target=self.eval_bar.update_eval(self.engine.get_evaluation()))
        else:
            tk.messagebox.showwarning("No engine selected", "Warning: no valid stockfish executable was selected.")
            self.engine = None
            self.eval_proc = None

    def enforce_aspect_ratio(self, event: tk.Event):
        """
        Enforce the correct aspect ratio of the chess board by resizing and repositioning its components.

        Args:
            event (tk.Event): The tkinter event triggered when the window is resized. It contains information about the new size of the window.

        Returns:
            None
        """
        left_sidebar_width = min(100, int(0.1 * event.width))
        right_sidebar_width = min(250, 0.25 * event.width)
        right_side_bar_height = 0.2 * event.height
        if (
            event.height - right_side_bar_height
            > event.width - right_sidebar_width - left_sidebar_width
        ):
            desired_size = min(
                event.width - left_sidebar_width, event.height - right_side_bar_height
            )
            right_sidebar_width = desired_size
            right_side_bar_pos = (left_sidebar_width, desired_size)
            y0 = 0
        else:
            right_sidebar_width = min(250, 0.25 * event.width)
            desired_size = min(event.height, event.width - left_sidebar_width - right_sidebar_width)
            right_side_bar_height = desired_size
            right_side_bar_pos = (left_sidebar_width + desired_size, 0)

            y0 = (event.height - desired_size) // 3

        self.board_frame.place(
            in_=self.padding_frame,
            x=left_sidebar_width,
            y=y0,
            width=desired_size,
            height=desired_size,
        )

        self.left_sidebar.place(
            in_=self.padding_frame,
            x=0,
            y=y0,
            width=left_sidebar_width,
            height=desired_size,
        )

        self.right_sidebar.place(
            in_=self.padding_frame,
            x=right_side_bar_pos[0],
            y=y0 + right_side_bar_pos[1],
            width=right_sidebar_width,
            height=right_side_bar_height,
        )

    def on_click_callback(self, event):
        """Callback for clicks on the board"""
        # Check whether a square has already been selected
        if (self.game.move_tree.pointer != self.game.move_tree.tip):
            return
        
        square = self.board.get_square_from_coords(event.x, event.y)
        if self.selected_square is None:
            self.select_square(square)
        else:
            # Check if moving from the already selected to the newly clicked square is a legal move
            self.clear_selection()
            for move in self._possible_moves:
                if square.coords == move.target:
                    if self.game.leads_to_promotion(move):
                        selector = getattr(self, f"{self.game.state.active_color}_selector")
                        selector.open(move.target, callback=partial(self.move_piece, move))
                    else:
                        self.move_piece(move)
                    break
            else:
                self.on_click_callback(event)

        result = self.game.game_result()
        if result is not None:
            GameResultScreen(self.board_frame, result)

    def select_square(self, square: Square) -> None:
        """Select a square on the chess board to highlight possible moves

        Args:
            square (Square): The square.
        """
        # Check if selected square is occupied and by a piece of the active color
        self.board.hide_moves()
        piece = self.game.state.get_piece_on(*square.coords)
        if piece is not None:
            if piece.color == self.game.state.get_active_color():
                self.board.select_square(square.row, square.col)
                self._possible_moves = self.game.get_possible_moves_from(square.coords)
                self.board.show_moves(self._possible_moves)
                self.selected_square = square

    def clear_selection(self) -> None:
        """Clear square selection"""
        self.board.hide_moves()
        self.board.clear_selection()
        self.selected_square = None

    def move_piece(self, move: Move, promote_to: ChessPiece = None):
        move.promote_to = promote_to
        self.game.make_move(move)
        self.board.make_move(move)
        self.moves_overview.make_move(self.game.move_tree.pointer)
        if self.engine is not None:
            self.engine.set_fen_position(self.game.state.to_fen_string())
            if self.eval_proc.is_alive():
                self.eval_proc.kill()
            self.eval_proc = Process(target=self.eval_bar.update_eval(self.engine.get_evaluation()))
            self.eval_proc.run()

    def change_position_callback(self, node: GameTreeNode):
        self.clear_selection()
        self.game.goto(node)
        self.board.load_piece_positions(self.game.state)
