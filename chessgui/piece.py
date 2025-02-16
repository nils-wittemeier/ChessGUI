""" Implement chess pieces as GUI elements"""
from stockfish import Stockfish

_UTF8_Pieces = {
    Stockfish.Piece.WHITE_KING : "♔",
    Stockfish.Piece.WHITE_QUEEN : "♕",
    Stockfish.Piece.WHITE_ROOK : "♖",
    Stockfish.Piece.WHITE_BISHOP : "♗",
    Stockfish.Piece.WHITE_KNIGHT : "♘",
    Stockfish.Piece.WHITE_PAWN : "♙",
    Stockfish.Piece.BLACK_KING : "♚",
    Stockfish.Piece.BLACK_QUEEN : "♛",
    Stockfish.Piece.BLACK_ROOK : "♜",
    Stockfish.Piece.BLACK_BISHOP : "♝",
    Stockfish.Piece.BLACK_KNIGHT : "♞",
    Stockfish.Piece.BLACK_PAWN : "♟",
}

class ChessPiece:
    """Base class for all chess pieces."""

    def __init__(
        self,
        piece: Stockfish.Piece,
        row: int,
        col: int,
    ):
        self.row = row
        self.col = col
        self._type = piece

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.color} {self.name} ({self.row}, {self.col})>'

    @property
    def coords(self):
        """Coordinates"""
        return self.row, self.col
    
    @property
    def type(self) -> str:
        """Color of piece (white or black)."""
        return self._type
    
    @property
    def color(self) -> str:
        """Color of piece (white or black)."""
        return "white" if self.is_white else "black"

    @property
    def is_white(self) -> bool:
        """Color of piece (white or black )."""
        if self._type is None:
            raise ValueError('Piece type None does not have a color.')
        return "WHITE" in self._type.name

    @property
    def name(self) -> str:
        """Name of piece."""
        if self._type is None:
            return None
        return self._type.name.split("_")[-1].capitalize()
    
    @property
    def short_name(self) -> str:
        """Short name of piece."""
        return self._name[1].lower()
    
    def update_position(self, row, col):
        """ Update position """
        self.row = row
        self.col = col

    def promote(self, promote_to: Stockfish.Piece):
        self._type = promote_to
        self._name = promote_to.name.split("_")[-1].capitalize()
    