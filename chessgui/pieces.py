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
