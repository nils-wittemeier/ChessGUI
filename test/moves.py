import unittest
from itertools import product

from parameterized import parameterized

from chessgui.game.moves import Move
from chessgui.game.piece import ChessPiece


class TestMove(unittest.TestCase):

    def test_move_initialization(self):
        """Test initialization for moves without capture or promotion"""
        origin = (1, 3)
        target = (3, 3)
        piece = ChessPiece("B", *origin)

        move = Move(piece, origin, target)
        self.assertEqual(move.piece, piece)
        self.assertEqual(move.origin, origin)
        self.assertEqual(move.target, target)
        self.assertIsNone(move.captured_piece)
        self.assertIsNone(move.promote_to)

    def test_move_with_captured_piece(self):
        """Test initialization for moves that capture of a piece"""
        piece = ChessPiece("B", 0, 0)
        captured_piece = ChessPiece("b", 1, 0)
        move = Move(piece, (0, 0), (1, 0), captured_piece=captured_piece)
        self.assertEqual(move.captured_piece, captured_piece)

    def test_move_with_promotion(self):
        """Test initialization for moves with piece promotion"""
        piece = ChessPiece("P", 6, 0)
        promote_to = ChessPiece("B", 7, 0)
        move = Move(piece, (6, 0), (7, 0), promote_to=promote_to)
        self.assertEqual(move.promote_to, promote_to)

    @parameterized.expand(
        [
            [
                "b",
                "B",
                None,
                (1, 2),
                (1, 5),
                (1, 3),
                (1, 3),
            ],  # Origin doesn't match piece position
            [
                "b",
                "B",
                None,
                (0, 0),
                (0, 0),
                (6, 1),
                (1, 3),
            ],  # Captured piece not on target
            [
                "b",
                "B",
                None,
                (1, 3),
                (1, 3),
                (1, 3),
                (1, 3),
            ],  # Origin and destination are the same
            [
                "b",
                "n",
                None,
                (1, 3),
                (1, 3),
                (1, 3),
                (1, 3),
            ],  # Captured piece is of the same color
            [
                "b",
                None,
                "q",
                (3, 3),
                (3, 3),
                (1, 1),
                (1, 1),
            ],  # Promotion of piece other than pawn
            [
                "p",
                None,
                "Q",
                (6, 3),
                (6, 3),
                (7, 3),
                (7, 3),
            ],  # Promotion to different color
            [
                "p",
                None,
                "b",
                (5, 3),
                (5, 3),
                (6, 3),
                (6, 3),
            ],  # Promotion not on 1st/8th rank
        ]
    )
    def test_piece_invalid_initialization(self, *args):
        kwargs = {}
        kwargs["origin"] = args[4]
        kwargs["target"] = args[6]
        kwargs["piece"] = ChessPiece(args[0], *args[3])
        if args[1] is not None:
            kwargs["captured_piece"] = ChessPiece(args[1], *args[5])
        if args[2] is not None:
            kwargs["promote_to"] = ChessPiece(args[2], *args[5])
        with self.assertRaises(ValueError):
            Move(**kwargs)

    def test_move_repr(self):
        origin = (6, 2)
        target = (7, 3)
        piece = ChessPiece("P", *origin)
        captured_piece = ChessPiece("p", *target)
        promote_to = ChessPiece("Q", *target)
        move = Move(piece, origin, target, captured_piece, promote_to)
        self.assertEqual(
            repr(move),
            "<Move: Pawn moving from (6, 2) to (7, 3) ; capturing Pawn ; promoting to Queen>",
        )

    @parameterized.expand(
        product(
            product(
                ["P"],
                ["r", None],
                ["B", None],
                [(6, 0), (6, 2)],
                [(7, 1), (7, 1)],
            ),
            repeat=2,
        )
    )
    def test_move_equality(self, args1, args2):

        def create_move(*args):
            kwargs = {}
            kwargs["piece"] = ChessPiece(args[0], *args[3])
            kwargs["origin"] = args[3]
            kwargs["target"] = args[4]
            if args[1] is not None:
                kwargs["captured_piece"] = ChessPiece(args[1], *args[4])
            if args[2] is not None:
                kwargs["promote_to"] = ChessPiece(args[2], *args[4])
            return Move(**kwargs)

        move1 = create_move(*args1)
        move2 = create_move(*args2)

        self.assertEqual(move1 == move2, args1 == args2)
