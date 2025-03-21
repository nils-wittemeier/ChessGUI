"""This module defines the Game class, which handles the current games state
and check that the game rules."""

from pathlib import Path
from typing import Optional

from .utils import index_to_algebraic, algebraic_to_index
from .piece import ChessPiece

_STARTING_POS = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
# _STARTING_POS = "r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1"
_STARTING_POS = "8/P6k/8/8/8/8/K6p/8 w - - 0 1"
# _STARTING_POS = "7k/Q7/6K1/8/8/8/8/8 w - - 0 1"
# _STARTING_POS = "7K/q7/6k1/8/8/8/8/8 w - - 0 1"
# _STARTING_POS = "8/8/8/5k2/3K4/8/8/8 w - - 0 1"


class GameState:
    """Track the current state of the game"""

    def __init__(self):
        self._pieces = [None] * 64
        self.is_white_active = True
        self.en_passant_target = None
        self.castling_rights = {"K": True, "Q": True, "k": True, "q": True}
        self.moves = 0
        self.half_moves = 0
        self.load_fen_string(_STARTING_POS)

    def __hash__(self):
        return hash(self.to_fen_string())

    def load_fen_string(self, fen_str: str):
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
                        self.place_piece_on(row, col + i, None)
                    col += int(c)
                else:
                    piece = ChessPiece(c, row, col)
                    self.place_piece_on(row, col, piece)
                    col += 1

        # Parse active color
        self.is_white_active = fen_blocks[1] == "w"

        # Parse castling rights
        for key in self.castling_rights:
            self.castling_rights[key] = key in fen_blocks[2]

        # Parse en passant target square
        if fen_blocks[3] == "-":
            self.en_passant_target = None
        else:
            self.en_passant_target = algebraic_to_index(fen_blocks[3])

        # Parse number of moves and half moves
        self.half_moves = int(fen_blocks[4])
        self.moves = int(fen_blocks[5])

        return self

    @staticmethod
    def from_fen_string(fen_str: Optional[str] = None):
        """
        Load game state from a FEN string

        Args:
            fen_str (str):  FEN string of board position.
        """
        game_state = GameState()
        # Split fen string into blocks
        if fen_str is not None:
            game_state.load_fen_string(fen_str)
        else:
            game_state.load_fen_string(_STARTING_POS)

        return game_state

    def to_fen_string(self) -> str:
        s = ""
        for row in range(8):
            n_pawns = 0
            if row > 0:
                s += "/"
            for col in range(8):
                piece = self.get_piece_on(row, col)
                if piece is not None:
                    if n_pawns > 0:
                        s += f"{n_pawns}"
                        n_pawns = 0
                    s += piece.symbol
                else:
                    n_pawns += 1
            if n_pawns > 0:
                s += f"{n_pawns}"
        s += " "
        s += "w" if self.is_white_active else "b"
        s += " "
        castling_allow = False
        for k, v in self.castling_rights.items():
            if v:
                s += k
                castling_allow = True
        if not castling_allow:
            s += "-"
        s += " "
        if self.en_passant_target is not None:
            s += index_to_algebraic(*self.en_passant_target)
        else:
            s += "-"
        s += f" {self.half_moves} {self.moves}"
        return s

    def __repr__(self) -> str:
        out_lines = []
        for row in range(8):
            out_lines.append("+---" * 8 + "+")
            line = "|"
            for col in range(8):
                piece = self.get_piece_on(row, col)
                if piece is not None:
                    line += f" {piece.utf8_symbol} |"
                else:
                    line += "   |"
            out_lines.append(line)
        out_lines.append("+---" * 8 + "+")

        return "\n".join(out_lines)

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
        return self.en_passant_target == (row, col)

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
        return "white" if self.is_white_active else "black"

    @property
    def active_color(self) -> str:
        """Color which has to make the next move."""
        return "white" if self.is_white_active else "black"

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
        if (row, col) == self.en_passant_target:
            return True
        return False

    def find_king(
        self,
        color: str,
    ) -> tuple[int, int]:
        for row in range(8):
            for col in range(8):
                if self.is_occupied(row, col):
                    piece = self.get_piece_on(row, col)
                    if piece.color == color and piece.name.capitalize() == "King":
                        return (row, col)

        raise ValueError(
            f"{self.__class__.__name__}._find_king: Can not find the {color} king on the board."
        )

    # def is_over(self):
