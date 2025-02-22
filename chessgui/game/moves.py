""" Implements a """

from typing import Optional

from .piece import ChessPiece


class Move:

    def __init__(
        self,
        piece: ChessPiece,
        origin: tuple[int, int],
        target: tuple[int, int],
        captured_piece: Optional[ChessPiece] = None,
        promote_to: Optional[ChessPiece] = None,
        rook_move = None,
    ) -> None:
        """_summary_

        Args:
            piece (ChessPiece): The piece that is moving
            origin (tuple[int, int]): The square from where the piece is moving.
            target (tuple[int, int]): The square to where the piece is moving.
            captured_piece (Optional[ChessPiece], optional): The piece being capture. Defaults to None.
            promote_to (Optional[ChessPiece], optional): The piece being promoted to. Defaults to None.
            rook_move (Move, optional): The move which the rook perform during castling. Defaults to None.

        Raises:
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_
        """
        self.piece = piece
        if piece.coords != origin:
            raise ValueError(
                "The provided origin does not match the piece's current coordinates.", 
                piece.coords, origin
            )
        if target == origin:
            raise ValueError(
                "The move is invalid because the origin and target are the same."
            )
        self.origin = origin
        self.target = target
        if captured_piece is not None:
            if captured_piece.coords != target:
                raise ValueError(
                    "The provided coordinates of the captured piece's coorindates do not match "
                    "target square."
                )
            if captured_piece.color == piece.color:
                raise ValueError(
                    "The captured piece's has the same color as the capturing piece."
                )
        self.captured_piece = captured_piece

        if promote_to is not None:
            if piece.name != "Pawn":
                raise ValueError("The promoting piece is not a pawn.")
            if promote_to.color != piece.color:
                raise ValueError("The piece is promoting to a different color.")
            if target[0] != (7 if piece.is_white else 0):
                raise ValueError(
                    "The piece is promoting is not at the edge of the board."
                )
        self.promote_to = promote_to
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
        if not isinstance(value, Move):
            raise ValueError(
                "Equality can only be evaluated with another instance of the Move class"
            )

        return (
            self.piece == value.piece
            and self.origin == value.origin
            and self.target == value.target
            and self.captured_piece == value.captured_piece
            and self.promote_to == value.promote_to
        )

    @property
    def is_capture(self):
        """Whether this move is a capture."""
        return self.captured_piece is not None

    @property
    def is_promotion(self):
        """Whether this move is a promotion"""
        is_pawn = self.piece.name == "Pawn"
        reached_end = (
            self.target[0] == 7 if self.piece.is_white else self.target[0] == 0
        )
        return is_pawn and reached_end
    
    @property
    def is_castling(self):
        """Whether this move is a castling."""
        return self.rook_move is not None
