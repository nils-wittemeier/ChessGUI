"""Implements a"""

from typing import Optional, Self

from stockfish import Stockfish

from ..errors import IllegalMoveError
from .piece import ChessPiece


class Move:

    def __init__(
        self,
        piece: ChessPiece,
        origin: tuple[int, int],
        target: tuple[int, int],
        captured_piece: Optional[ChessPiece] = None,
        promote_to: Optional[str] = None,
        rook_move: Optional[Self] = None,
    ) -> None:
        """_summary_

        Args:
            piece (ChessPiece): The piece that is moving
            origin (tuple[int, int]): The square from where the piece is moving.
            target (tuple[int, int]): The square to where the piece is moving.
            captured_piece (ChessPiece, optional): The piece being capture.
                Defaults to `None`.
            promote_to (ChessPiece, optional): The piece being promoted to.
                Defaults to `None`.
            rook_move (Move, optional): The move which the rook perform during castling.
                Defaults to `None`.

        Raises:
            IllegalMoveError: If the piece moves to the square it currently is occupying
                (not a move).
            IllegalMoveError: If a piece is trying to move to a square occupied
                by a piece of the same color.
            ValueError: If the color of the moving piece does not match the
                color of `promote_to`.
        """

        # Basic move info
        self.origin = origin
        self.piece = piece
        self.target = target

        if target == self.origin:
            raise IllegalMoveError(
                "The move is invalid because the origin and target are the same."
            )

        # Captures
        if captured_piece is not None:
            if self.piece.name == "Rook" and captured_piece.name == "King":
                if self.piece.color == captured_piece.color:
                    captured_piece = None

            if captured_piece.color == self.piece.color:
                raise IllegalMoveError(
                    "The captured piece's has the same color as the capturing piece."
                )
        self.captured_piece = captured_piece

        # Promotions
        self.promote_to = None
        if promote_to is not None:
            if self.piece.name != "Pawn":
                raise IllegalMoveError("Only Pawn can promote.")
            self.promote_to = promote_to
            if self.promote_to.color != self.piece.color:
                raise ValueError("The piece is promoting to a different color.")

        self.rook_move = rook_move

    def __repr__(self):
        s = f"<{self.__class__.__name__}: {self.piece.name}"
        s += f" moving from {self.origin} to {self.target}"
        if self.is_capture:
            s += f" ; capturing {self.captured_piece.name}"
        if self.promote_to:
            s += f" ; promoting to {self.promote_to.name}"
        return s + ">"

    def __eq__(self, value):
        """Evaluate equality
        Raises
            ValueError: If right handside of equality is not an instance of
                the class `Move`.
        """
        if not isinstance(value, Move):
            raise ValueError(
                "Equality can only be evaluated with another instance of the Move class"
            )

        is_equal = self.piece == value.piece
        is_equal &= self.origin == value.origin
        is_equal &= self.target == value.target
        is_equal &= self.captured_piece == value.captured_piece
        try:
            is_equal &= self.promote_to.type == value.promote_to.type
        except AttributeError:
            is_equal &= self.promote_to == value.promote_to

        return is_equal

    def __hash__(self):
        return hash((self.piece.name, self.origin, self.target))

    @property
    def is_capture(self):
        """Whether this move is a capture."""
        return self.captured_piece is not None

    @property
    def is_promotion(self):
        """Whether this move is a promotion"""
        return self.promote_to is not None

    @property
    def is_castling(self):
        """Whether this move is a castling."""
        return self.rook_move is not None

    @property
    def is_double_move(self):
        if self.piece.name != "Pawn":
            return False

        return abs(self.origin[0] - self.target[0]) == 2
