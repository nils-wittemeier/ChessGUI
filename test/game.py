import unittest
from chessgui.game.state import GameState

from itertools import product

# from unittest.mock import patch, MagicMock
# from chessgui.game.piece import ChessPiece
from chessgui.game.moves import Move
from parameterized import parameterized


class TestGame(unittest.TestCase):

    def setUp(self):
        self.game = GameState()

    @parameterized.expand(
        [
            [
                "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
                "w",
                "KQkq",
                "-",
                "0",
                "0",
            ],
            [
                "r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R",
                "b",
                "qQkK",
                "a3",
                "1",
                "10",
            ],
            [
                "2nK4/4B3/8/4R1b1/pp1p2pp/2pbR3/2P3P1/2k5",
                "w",
                "qK",
                "h6",
                "1",
                "54",
            ],
            [
                "Brb5/5Kp1/1pP2PP1/5RP1/1QP1RP1p/B2k1P2/p1pp4/5n2",
                "b",
                "-",
                "d6",
                "12",
                "43",
            ],
            [
                "8/4b3/4P3/8/8/8/1nK2k2/8",
                "b",
                "-",
                "-",
                "0",
                "43",
            ],
        ]
    )
    def test_load_fen_string(
        self,
        pieces,
        active_color,
        castling_rights,
        en_passant_target,
        half_moves,
        moves,
    ):

        def parse_piece(row):
            for c in row:
                if c.isdigit():
                    for _ in range(int(c)):
                        yield None
                else:
                    yield c

        fen_str = (
            pieces
            + " "
            + " ".join([active_color, castling_rights, en_passant_target, half_moves, moves])
        )
        self.game.load_fen_string(fen_str)

        for row in range(8):
            piece_iter = parse_piece(pieces.split("/")[row])
            for col in range(8):
                piece = self.game.get_piece_on(row, col)
                if piece is not None:
                    self.assertEqual(piece.symbol, next(piece_iter))
                else:
                    self.assertEqual(piece, next(piece_iter))

        self.assertEqual(self.game.active_color[0], active_color)
        for k, v in self.game.castling_rights.items():
            self.assertEqual(k in castling_rights, v)
        self.assertEqual(self.game.moves, int(moves))
        self.assertEqual(self.game.half_moves, int(half_moves))

    def assertFENEqual(self, fen1, fen2):
        fen_blocks = zip(fen1.split(" "), fen2.split(" "))
        self.assertEqual(*next(fen_blocks))  # Piece Positions: must match exactly
        self.assertEqual(*next(fen_blocks))  # Active Color
        self.assertEqual(*map(set, next(fen_blocks)))  # Castling Rights: ignore order
        self.assertEqual(*next(fen_blocks))  # En Passant
        self.assertEqual(*next(fen_blocks))  # Half moves
        self.assertEqual(*next(fen_blocks))  # Moves

    @parameterized.expand(
        [
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0",
            "r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b qQkK a3 1 10",
            "2nK4/4B3/8/4R1b1/pp1p2pp/2pbR3/2P3P1/2k5 w qK h6 1 54",
            "Brb5/5Kp1/1pP2PP1/5RP1/1QP1RP1p/B2k1P2/p1pp4/5n2 b - d6 12 43",
            "8/4b3/4P3/8/8/8/1nK2k2/8 b - - 0 43",
        ]
    )
    def test_get_fen(self, fen_str):
        self.game.load_fen_string(fen_str)

        self.assertFENEqual(fen_str, self.game.to_fen_string())

    @parameterized.expand(
        [
            [  # Double pawn move -- check that en passant is recorded
                "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0",
                "d2d4",
                "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 0",
            ],
            [  # Normal pawn move -- check that half move counter is reset
                "r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/2N2N2/PPPP1PPP/R1BQK2R b KQkq - 5 4",
                "d7d6",
                "r1bqk1nr/ppp2ppp/2np4/2b1p3/2B1P3/2N2N2/PPPP1PPP/R1BQK2R w KQkq - 0 5",
            ],
            [  # Castling
                "r1bqk1nr/ppp2ppp/2np4/2b1p3/2B1P3/2N2N2/PPPP1PPP/R1BQK2R w KQkq - 0 5",
                "e1g1",
                "r1bqk1nr/ppp2ppp/2np4/2b1p3/2B1P3/2N2N2/PPPP1PPP/R1BQ1RK1 b kq - 1 5",
            ],
            [  # Capture
                "r1bqk2r/ppp1nppp/2np4/2b1p3/2B1P3/2N2N2/PPPP1PPP/R1BQ1RK1 w kq - 2 6",
                "c4f7",
                "r1bqk2r/ppp1nBpp/2np4/2b1p3/4P3/2N2N2/PPPP1PPP/R1BQ1RK1 b kq - 0 6",
            ],
            [  # King move -- remove castling rights
                "r1bqk2r/ppp1nBpp/2np4/2b1p3/4P3/2N2N2/PPPP1PPP/R1BQ1RK1 b kq - 0 6",
                "e8f7",
                "r1bq3r/ppp1nkpp/2np4/2b1p3/4P3/2N2N2/PPPP1PPP/R1BQ1RK1 w - - 0 7",
            ],
            [  # Rook move -- remove castling rights
                "r3k2r/ppp1qppp/2np4/2b1p3/2B1P1b1/3P1N2/PPP2PPP/R1BQ1RK1 b kq - 0 8",
                "a8d8",
                "3rk2r/ppp1qppp/2np4/2b1p3/2B1P1b1/3P1N2/PPP2PPP/R1BQ1RK1 w k - 1 9",
            ],
            [  # En passant caputre - white
                "3rk2r/p1p1qppp/3p4/Ppb1p3/2BnP1b1/3P1N2/1PP2PPP/R1BQ1RK1 w k b6 0 11",
                "a5b6",
                "3rk2r/p1p1qppp/1P1p4/2b1p3/2BnP1b1/3P1N2/1PP2PPP/R1BQ1RK1 b k - 0 11",
            ],
            [  # En passant caputre - black
                "3rk2r/1pp1qppp/2np4/2b1p3/pPB1P1b1/P2P1N2/2PB1PPP/R2Q1RK1 b k b3 0 11",
                "a4b3",
                "3rk2r/1pp1qppp/2np4/2b1p3/2B1P1b1/Pp1P1N2/2PB1PPP/R2Q1RK1 w k - 0 12",
            ],
        ]
    )
    def test_make_moves(self, initial_fen, move_str, result):
        self.game.load_fen_string(initial_fen)
        self.game.make_move(self.game.smith_to_move(move_str))
        self.assertFENEqual(self.game.to_fen_string(), result)

    # 1) No piece on origin
    # 2) Piece doesn't move like requested (for each type of piece)
    # 3) Move that would put king in check
    # 4) Moving king into check
    # 5) Origin or target out of bounds
    def test_invalid_moves(self):
        pass

    # 1) 50 move rule (half_move == 100)
    # 2) in sufficient material
    # 3) 3-fold repitition
    # 4) Stale mate
    # 5) Check mate
    def test_game_end(self):
        pass


#     @patch('game.Game._possible_bishop_moves')
#     @patch('game.Game._possible_knight_moves')
#     @patch('game.Game._possible_pawn_moves')
#     @patch('game.Game._possible_rook_moves')
#     def test_calculate_all_moves(self, mock_rook, mock_knight, mock_pawn, mock_bishop):
#         # Mocking the return values for all possible moves methods
#         mock_rook.return_value = [Move()]
#         mock_knight.return_value = [Move()]
#         mock_pawn.return_value = [Move()]
#         mock_bishop.return_value = [Move()]

#         # Test the calculation of all moves
#         self.assertEqual(self.game.calculate_all_moves(), [Move()]*4)

#     @patch('game.Game._possible_rook_moves')
#     def test_get_rook_moves(self, mock_rook):
#         # Mocking the return value for rook moves method
#         mock_rook.return_value = [Move()]
#         self.assertEqual(self.game.get_rook_moves(), [Move()])

#     @patch('game.Game._possible_bishop_moves')
#     def test_get_bishop_moves(self, mock_bishop):
#         # Mocking the return value for bishop moves method
#         mock_bishop.return_value = [Move()]
#         self.assertEqual(self.game.get_bishop_moves(), [Move()])

#     @patch('game.Game._possible_knight_moves')
#     def test_get_knight_moves(self, mock_knight):
#         # Mocking the return value for knight moves method
#         mock_knight.return_value = [Move()]
#         self.assertEqual(self.game.get_knight_moves(), [Move()])

#     @patch('game.Game._possible_pawn_moves')
#     def test_get_pawn_moves(self, mock_pawn):
#         # Mocking the return value for pawn moves method
#         mock_pawn.return_value = [Move()]
#         self.assertEqual(self.game.get_pawn_moves(), [Move()])

x
# MoveTracker
# ===========
# - appending moves linearly and branching
# - moving along the tree
# Q: Find a string representation for dict or something that is easy to compare.

# GameLogic
# ==========
# How do we approach this?
# 1) Setup position
# 2) Try to make moves / ask information
# 3)
