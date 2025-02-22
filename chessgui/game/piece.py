""" Implement chess piece"""

from stockfish import Stockfish


class ChessPiece:
    """Base class for all chess pieces."""

    def __init__(
        self,
        piece: Stockfish.Piece,
        row: int,
        col: int,
    ):
        if isinstance(piece, str):
            self._type = Stockfish.Piece(piece)
        else:
            if not isinstance(piece, Stockfish.Piece):
                raise ValueError(f'Can not create ChessPiece using a piece of type {type(piece)}.')
            self._type = piece
        self.row = row
        self.col = col

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.color} {self.name} ({self.row}, {self.col})>"
    
    def __eq__(self, value):
        if value is None:
            return False
        if not isinstance(value, ChessPiece):
            raise ValueError('Equality can only be evaluated with another instance of the ChessPiece class.')
        return (self._type == value._type and self.row == value.row and self.col == value.col)

    @property
    def coords(self):
        """Coordinates"""
        return self.row, self.col

    @property
    def type(self) -> Stockfish.Piece:
        """Equivalent stockfish piece type"""
        return self._type

    @property
    def color(self) -> str:
        """Color of piece (white or black)."""
        return "white" if self.is_white else "black"

    @property
    def is_white(self) -> bool:
        """Color of piece (white or black )."""
        if self._type is None:
            raise ValueError("Piece type None does not have a color.")
        return "WHITE" in self._type.name

    @property
    def name(self) -> str:
        """Name of piece."""
        if self._type is None:
            return None
        return self._type.name.split("_")[-1].capitalize()

    @property
    def symbol(self) -> str:
        """Short name of piece."""
        c = {
            "King": "K",
            "Queen": "Q",
            "Rook": "R",
            "Bishop": "B",
            "Knight": "N",
            "Pawn": "P",
        }[self.name]
        return c.upper() if self.is_white else c.lower()

    def update_position(self, row, col):
        """Update position"""
        self.row = row
        self.col = col

    def promote(self, promote_to: Stockfish.Piece):
        """Promote this piece to a new piece."""
        self._type = promote_to
