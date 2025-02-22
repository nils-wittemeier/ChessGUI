""" This module defines the Game class, which handles the current games state
and check that the game rules. """

from pathlib import Path
from typing import Optional

from stockfish import Stockfish

from .piece import ChessPiece
from .moves import Move

_STARTING_POS = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
_STARTING_POS = "r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1"
# _STARTING_POS = "8/P6k/8/8/8/8/K6p/8 w - - 0 1"
# _STARTING_POS = "8/8/8/5k2/3K4/8/8/8 w - - 0 1"

_stockfish_root = Path("/Users/Juijan/stockfish")
_stockfish_exe = _stockfish_root / "stockfish-windows-x86-64-avx2.exe"


class MoveTreeNode:
    """Implementation of double-linked graph"""

    def __init__(self, parent):
        self._parent = parent
        self._children = {}
        self._order: list[Move] = []

    def add_child(self, move: Move):
        """Add a child to this node of the move tree"""
        if move not in self._children:
            self._children[move] = MoveTreeNode(self)
            self._order.append(move)

    def remove_child(self, move: Move):
        """Remove a child to this node of the move tree"""
        if move in self._children:
            self._children.pop(move)
            self._order.remove(move)

    def get_child(self, move: Optional[Move] = None) -> str:
        """Retrieve child of this node"""
        if move is None:
            move = self._order[0]
        return self._children[move]


class MoveTree:
    """Manages move tree, keeps track of current position and moving along the tree."""

    def __init__(self):
        self._root = MoveTreeNode(None)
        self._tip = self._root

    def add_child(self, move: str):
        """Add child at currently active tip"""
        self._tip.add_child(move)
        self._tip = self._tip.children[move]

    def move_up(self):
        """Move up one level"""
        self._tip = self._tip.parent

    def move_down(self, move: str | None = None):
        """Move down on level"""
        self._tip = self._tip.get_child(move)


class GameState:
    """Track the current state of the game"""

    def __init__(self):
        self._pieces = [None] * 64
        self._is_white_active = True
        self._en_passant_target = None
        self.castling_rights = {"K": True, "Q": True, "k": True, "q": True}
        self._moves = 0
        self._half_moves = 0
        self._move_graph = MoveTree
        self._current_moves = []
        self._starting_pos = _STARTING_POS
        self.load_fen_string(self._starting_pos)

    def load_fen_string(self, fen_str: str) -> None:
        """
        Load game state from a FEN string

        Args:
            fen_str (str):  FEN string of board position.
        """
        # Split fen string into blocks
        fen_blocks = fen_str.split(" ")

        row_fen = fen_blocks[0].split("/")

        for row, s in enumerate(row_fen):
            col = 0
            for c in s:
                if c.isdigit():
                    for i in range(int(c)):
                        self.place_piece_on(row, col+i, None)
                    col += int(c)
                else:
                    piece = ChessPiece(c, row, col)
                    self.place_piece_on(row, col, piece)
                    col += 1

        # Parse active color
        self._is_white_active = fen_blocks[1] == "w"

        # Parse castling rights
        for key in self.castling_rights:
            self.castling_rights[key] = key in fen_blocks[2]

        # Parse en passant target square
        if fen_blocks[3] == "-":
            self._en_passant_target = None
        else:
            self._en_passant_target = self.algebraic_to_index(fen_blocks[3])

        # Parse number of moves and half moves
        self._moves = int(fen_blocks[4])
        self._half_moves = int(fen_blocks[5])

    @staticmethod
    def algebraic_to_index(pos: str) -> tuple[int] | None:
        """
        Convert square identifier from algebraic notation to pair of zero-based indices.

        Args:
            pos (str): The identifier in algebraic notation.

        Returns:
            row (int): The zero-based row index of the square.
            col (int): The zero-based column index of the square.
        """
        row = int(pos[1]) - 1
        col = "abcdefgh".index(pos[0])
        return row, col

    @staticmethod
    def index_to_algebraic(row: int, col: int) -> str:
        """
        Convert a pair of zero-based indices to algebraic notation.

        Algebraic notations uses letters a, b, c, d, e, f, g, and h to indentify
        the columns followed by the one-based index of the row.

        Args:
            row (int): The zero-based row index of the square.
            col (int): The zero-based column index of the square.

        Returns:
            pos (str): The identifier in algebraic notation.
        """
        return "abcdefgh"[col] + str(8 - row)

    def get_piece_on(self, row: int, col: int) -> ChessPiece:
        """
        Retrieve piece currently on a given square

        Args:
            row (int): The zero-based row index of the square.
            col (int): The zero-based column index of the square.

        Returns:
            piece (ChessPiece) : The piece currently occupying the square.
        """
        return self._pieces[8 * row + col]

    def is_occupied(self, row: int, col: int):
        """Check whether a given square on the board is currently occupied"""
        return self.get_piece_on(row, col) is not None

    def is_en_passant_target(self, row: int, col: int):
        """Check whether a given square can be targeted by en passant capture"""
        return self._en_passant_target == (row, col)

    def place_piece_on(self, row: int, col: int, piece: ChessPiece) -> None:
        """
        Place piece on a given square

        Args:
            piece (ChessPiece) : The piece that should occupy the square.
            row (int): The zero-based row index of the square.
            col (int): The zero-based column index of the square.
        """
        self._pieces[8 * row + col] = piece
        if piece and piece.coords != (row, col):
            piece.update_position(row, col)

    def get_active_color(self) -> str:
        """The currently active color, whose turn it is to move."""
        return "white" if self._is_white_active else "black"

    @property
    def is_white_active(self) -> bool:
        """Whether white is the currently active color

        Returns:
            bool: Whether white is the currently active color
        """
        return self._is_white_active

    @property
    def active_color(self) -> str:
        """Color which has to make the next move."""
        return "white" if self._is_white_active else "black"

    def make_move(self, move: Move):
        """Implement the logic to check if the move is allowed and update the board accordingly

        Args:
            move (_type_): # TODO
        """
        self._current_moves.append(move)
        # self._move_graph.current_tip.append(move)
        self._is_white_active = not self._is_white_active
        if move.is_castling:
            if move.piece.is_white:
                self.castling_rights['K'] = False
                self.castling_rights['Q'] = False
            else:
                self.castling_rights['k'] = False
                self.castling_rights['q'] = False
            self.place_piece_on(*move.rook_move.target, self.get_piece_on(*move.rook_move.origin))
            self.place_piece_on(*move.rook_move.origin, None)
        self.place_piece_on(*move.target, self.get_piece_on(*move.origin))
        self.place_piece_on(*move.origin, None)

    def is_enpassant_target(self, row, col):
        """
        Check if a given Square can be target for en passant capture.

        Args:
            row (int): The zero-based row index of the square.
            col (int): The zero-based column index of the square.

        Return:
            is_en_passant_target (bool): whether a given square can be target for en passant
                                         caputre.
        """
        if (row, col) == self._en_passant_target:
            return True
        return False

    def find_king(self, color) -> tuple[int, int]:
        for row in range(8):
            for col in range(8):
                if self.is_occupied(row, col):
                    piece = self.get_piece_on(row, col)
                    if piece.color == color and piece.name.capitalize() == "King":
                        return (row, col)

        raise ValueError(
            f"{self.__class__.__name__}._find_king: Can not find the {color} king on the board."
        )
