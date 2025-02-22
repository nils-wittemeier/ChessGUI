import unittest
from itertools import product

from parameterized import parameterized

from chessgui.game.piece import ChessPiece


class TestChessPiece(unittest.TestCase):

    @parameterized.expand(
        [
            ["P", "Pawn", True, "white", "P"],
            ["Q", "Queen", True, "white", "Q"],
            ["B", "Bishop", True, "white", "B"],
            ["p", "Pawn", False, "black", "p"],
            ["n", "Knight", False, "black", "n"],
            ["k", "King", False, "black", "k"],
        ]
    )
    def test_piece_initialization(self, piece, name, is_white, color, symbol):
        piece = ChessPiece(piece, 0, 0)
        self.assertEqual(piece.name, name)
        self.assertEqual(piece.is_white, is_white)
        self.assertEqual(piece.color, color)
        self.assertEqual(piece.symbol, symbol)

    @parameterized.expand(
        ["x", None, 1],
    )
    def test_piece_invalid_initialization(self, *args):
        with self.assertRaises(ValueError):
            ChessPiece(args[0], 0, 0)

    @parameterized.expand(
        product(
            product(
                ["B", "b", "P"],
                [(0, 0), (0, 2)],
                [(0, 1), (2, 1)],
            ),
            repeat=2,
        )
    )
    def test_move_equality(self, args1, args2):

        piece1 = ChessPiece(*args1)
        piece2 = ChessPiece(*args2)

        self.assertEqual(piece1 == piece2, args1 == args2)

    @parameterized.expand(
        [
            [(0, 0), (7, 0)],
            [(0, 0), (10, 0)],
            [(0, 0), (7, 0)],
            [(0, 0), (7, 0)],
            [(0, 0), (7, 0)],
        ]
    )
    def test_piece_moving(self, start, stop):
        piece = ChessPiece("P", *start)
        self.assertEqual(piece.coords, start)
        piece.update_position(*stop)
        self.assertEqual(piece.coords, stop)
