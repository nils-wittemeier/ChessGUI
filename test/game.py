# import unittest
# from unittest.mock import patch, MagicMock
# from chessgui.game.piece import ChessPiece
# from chessgui.game.moves import Move

# class TestGame(unittest.TestCase):

#     def setUp(self):
#         self.game = Game()  # Assuming Game class is defined elsewhere and has necessary setup

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

# GameState
# ===========
# Basics
# --------
# - load string, check positions of pieces
# - setup a position and convert to FEN
# - remeber to check all possible flags
# - conversion from to algebraic
# Making moves
# ------------
# - check piece positions after move
# - check that active color switches
# Include:
# * Normal moves
# * En passant
#    - Make double move(s) and check en passant target
# * Castling
#    - check that castling removes castling rights
#    - check that moving the king removes castling rights
#    - check that moving a rook remove the corresponding castling right

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