""" This module defines the Game class, which handles the current games state
and check that the game rules. """

from pathlib import Path

from stockfish import Stockfish

from .piece import ChessPiece
from .moves import Move

_STARTING_POS = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
_STARTING_POS = "8/P6k/8/8/8/8/K6p/8 w - - 0 1"

_stockfish_root = Path("/Users/Juijan/stockfish")
_stockfish_exe = _stockfish_root / "stockfish-windows-x86-64-avx2.exe"


class MoveTreeNode:
    """Implementation of double-linked graph"""

    def __init__(self, parent):
        self._parent = parent
        self._children = {}
        self._order = []

    @property
    def parent(self):
        return self._parent

    def add_child(self, move: str):
        if move not in self._children:
            self._children[move] = MoveTreeNode(self)
            self._order.append(move)

    def remove_child(self, move: str):
        if move in self._children:
            self._children.pop(move)
            self._order.remove(move)

    def get_child(self, move: str | None = None) -> str:
        if move is None:
            move = self._order[0]
        return self._children[move]


class MoveTree:
    def __init__(self):
        self._root = MoveTreeNode(None)
        self._tip = self._root

    def add_child(self, move: str):
        # Only add if key doesn't exist
        self._tip.add_child(move)
        self._tip = self._tip.children[move]

    def move_up(self):
        """Move up one level"""
        self._tip = self._tip.parent

    def move_down(self, move: str | None = None):
        """Move down on level"""
        self._tip = self._tip.get_child(move)

class GameState:

    def __init__(self):
        self._pieces = [None] * 64
        self._engine = Stockfish(path=_stockfish_exe)
        self._is_white_active = True
        self._en_passant_target = None
        self._castling_rights = {"K": True, "Q": True, "k": True, "q": True}
        self._moves = 0
        self._half_moves = 0
        self._move_graph = MoveTree
        self._current_moves = []
        self._starting_pos = _STARTING_POS
        self.load_fen_string(self._starting_pos)

    def load_fen_string(self, fen_str: str) -> None:
        """
        Load game state from a FEN string

        Args:
            fen_str (str):  FEN string of board position.
        """

        self._engine.set_fen_position(fen_str)
        for row in range(8):
            for col in range(8):
                a_ind = self.index_to_algebraic(row, col)
                stockfish_piece = self._engine.get_what_is_on_square(a_ind)
                if stockfish_piece is not None:
                    piece = ChessPiece(stockfish_piece, row, col)
                    self.place_piece_on(row, col, piece)
                else:
                    self.place_piece_on(row, col, None)

        # Split fen string into blocks
        fen_blocks = fen_str.split(" ")

        # Parse active color
        self._is_white_active = fen_blocks[1] == "w"

        # Parse castling rights
        for key in self._castling_rights:
            self._castling_rights[key] = key in fen_blocks[2]

        # Parse en passant target square
        if fen_blocks[3] == "-":
            self._en_passant_target = None
        else:
            self._en_passant_target = self.algebraic_to_index(fen_blocks[3])

        # Parse number of moves and half moves
        self._moves = int(fen_blocks[4])
        self._half_moves = int(fen_blocks[5])

    @staticmethod
    def algebraic_to_index(pos: str) -> tuple[int] | None:
        """
        Convert square identifier from algebraic notation to pair of zero-based indices.

        Args:
            pos (str): The identifier in algebraic notation.

        Returns:
            row (int): The zero-based row index of the square.
            col (int): The zero-based column index of the square.
        """
        row = int(pos[1]) - 1
        col = "abcdefgh".index(pos[0])
        return row, col

    @staticmethod
    def index_to_algebraic(row: int, col: int) -> str:
        """
        Convert a pair of zero-based indices to algebraic notation.

        Algebraic notations uses letters a, b, c, d, e, f, g, and h to indentify
        the columns followed by the one-based index of the row.

        Args:
            row (int): The zero-based row index of the square.
            col (int): The zero-based column index of the square.

        Returns:
            pos (str): The identifier in algebraic notation.
        """
        return "abcdefgh"[col] + str(row + 1)

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
        return self.get_piece_on(row, col) is not None

    def is_en_passant_target(self, row: int, col: int):
        return self._en_passant_target == (row, col)

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

    def get_possible_moves_from(self, row: int, col: int) -> list[Move]:
        """
        Retrieve list of all possible moves that can be by the piece
        currently occupying a give square

        Args:
            row (int): The zero-based row index of the square.
            col (int): The zero-based column index of the square.

        Returns:
            piece (ChessPiece) : The piece currently occupying the square.
        """
        return self._get_possible_moves_from(row, col, True)

    def _get_possible_moves_from(self, row: int, col: int, check_legal=False) -> list[Move]:
        piece = self.get_piece_on(row, col)

        moves = getattr(self, f"_possible_{piece.name.lower()}_moves")(row, col)

        if check_legal:
            moves = [move for move in moves if self._is_legal_move(move)]

        return moves

    def get_active_color(self) -> str:
        """The currently active color, whose turn it is to move."""
        return "white" if self._is_white_active else "black"

    @property
    def is_white_active(self) -> bool:
        """Whether white is the currently active color

        Returns:
            bool: Whether white is the currently active color
        """
        return self._is_white_active

    @property
    def active_color(self) -> str:
        return "white" if self._is_white_active else "black"

    def make_move(self, move: Move, promote_to: ChessPiece):
        """Implement the logic to check if the move is allowed and update the board accordingly

        Args:
            move (_type_): # TODO
        """
        self._current_moves.append(move)
        # self._move_graph.current_tip.append(move)
        self._is_white_active = not self._is_white_active
        self.place_piece_on(*move.target, self.get_piece_on(*move.origin))
        self.place_piece_on(*move.origin, None)

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
        if (row, col) == self._en_passant_target:
            return True
        return False

    def _possible_king_moves(self, row, col) -> list[tuple[int]]:
        """
        Calculate all possible moves for a king from its current position on the chessboard.

        The king can move one squares along a row, column, or diagonal. This function calculates
        and returns all positions (as tuples of row and column) that the king can reach
        from its current position without jumping off the board.

        Args:
            origin (Square): The chess square object representing the king's current position on
                             the board.
            board (ChessBoard): The chessboard object which contains information about all pieces
                                and their positions.

        Returns:
            list of tuple: A list containing all possible move positions as tuples, where each tuple
                           represents a row and column index on the chessboard.
        """
        # Define all possible moves a king can make: one step in any direction
        move_offsets = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]

        # List to hold all possible moves
        possible_moves = []

        # Color of the king
        piece = self.get_piece_on(row, col)
        is_white = piece.is_white

        # Check each move offset
        for row_offset, col_offset in move_offsets:
            new_row, new_col = row + row_offset, col + col_offset

            # If the new position is within the bounds of the chessboard, add it to possible moves
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                if not self.is_occupied(new_row, new_col):
                    possible_moves.append(
                        Move(
                            piece,
                            (row, col),
                            (new_row, new_col),
                            self.get_piece_on(new_row, new_col),
                        )
                    )
                elif self.get_piece_on(new_row, new_col).is_white != is_white:
                    # If the square is occupied by an opponent's piece, add it to possible moves
                    possible_moves.append(
                        Move(
                            piece,
                            (row, col),
                            (new_row, new_col),
                            self.get_piece_on(new_row, new_col),
                        )
                    )

        return possible_moves

    def _possible_queen_moves(self, row: int, col: int) -> list[tuple[int]]:
        """
        Calculate all possible moves for a queen from its current position on the chessboard.

        The queen can move any number of squares along a row, column, or diagonal. This function
        calculates and returns all positions (as tuples of row and column) that the queen can reach
        from its current position without jumping off the board.

        Args:
            origin (Square): The chess square object representing the queen's current position on
                             the board.
            board (ChessBoard): The chessboard object which contains information about all pieces
                                and their positions.

        Returns:
            list of tuple: A list containing all possible move positions as tuples, where each
                           tuple represents a row and column index on the chessboard.
        """
        # Define all possible direction in which the queen move: any direction
        move_offsets = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        ]
        # List to hold all possible moves
        possible_moves = []

        # Color of the king
        piece = self.get_piece_on(row, col)
        is_white = piece.is_white

        # Check each move offset
        for row_offset, col_offset in move_offsets:
            new_row, new_col = row + row_offset, col + col_offset
            # If the new position is within the bounds of the chessboard, add it to possible moves
            # and continue in the same direction
            while 0 <= new_row < 8 and 0 <= new_col < 8:
                if not self.is_occupied(new_row, new_col):
                    possible_moves.append(
                        Move(
                            piece,
                            (row, col),
                            (new_row, new_col),
                            self.get_piece_on(new_row, new_col),
                        )
                    )
                elif self.get_piece_on(new_row, new_col).is_white != is_white:
                    # If the square is occupied by an opponent's piece, add it to possible moves
                    possible_moves.append(
                        Move(
                            piece,
                            (row, col),
                            (new_row, new_col),
                            self.get_piece_on(new_row, new_col),
                        )
                    )
                    # Stop moving in this direction further
                    break
                else:
                    # The square is occupied by a piece of the same color
                    # So stop moving in this direction
                    break
                new_row += row_offset
                new_col += col_offset

        return possible_moves

    def _possible_rook_moves(self, row: int, col: int) -> list[tuple[int]]:
        """
        Calculate all possible moves for a rook from its current position on the chessboard.

        The rook can move any number of squares along a row or column without jumping over other
        pieces. This function also checks if the square the piece is trying to move to is occupied
        by another piece before adding it to the list of possible moves.

        Args:
            origin (Square): The square object representing the rook's current position on the
                             board.
            board (ChessBoard): The chessboard object which contains information about all pieces
                                and their positions.

        Returns:
            list of tuple: A list containing all possible move positions as tuples, where each
                           tuple represents a row and column index on the chessboard.
        """
        # Define all possible direction in which the rook move: any direction
        move_offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        # List to hold all possible moves
        possible_moves = []

        # Color of the rook
        piece = self.get_piece_on(row, col)
        is_white = piece.is_white

        # Check each move offset
        for row_offset, col_offset in move_offsets:
            new_row, new_col = row + row_offset, col + col_offset
            # If the new position is within the bounds of the chessboard, add it to possible moves
            # and continue in the same direction
            while 0 <= new_row < 8 and 0 <= new_col < 8:
                if not self.is_occupied(new_row, new_col):
                    possible_moves.append(
                        Move(
                            piece,
                            (row, col),
                            (new_row, new_col),
                            self.get_piece_on(new_row, new_col),
                        )
                    )
                elif self.get_piece_on(new_row, new_col).color != is_white:
                    # If the square is occupied by an opponent's piece, add it to possible moves
                    possible_moves.append(
                        Move(
                            piece,
                            (row, col),
                            (new_row, new_col),
                            self.get_piece_on(new_row, new_col),
                        )
                    )
                    # Stop moving in this direction further
                    break
                else:
                    # The square is occupied by a piece of the same color,
                    # So stop moving in this direction
                    break
                new_row += row_offset
                new_col += col_offset

        return possible_moves

    def _possible_bishop_moves(self, row: int, col: int) -> list[tuple[int]]:
        """
        Calculate all possible moves for a bishop from its current position on the chessboard.

        The bishop can move any number of squares along a diagonal without jumping over other
        pieces. This function returns a list with all possible squares the bishop can move to,
        including possible captures.

        Args:
            origin (Square): The square object representing the rook's current position on the
                             board.
            board (ChessBoard): The chessboard object which contains information about all pieces
                                and their positions.

        Returns:
            list of tuple: A list containing all possible move positions as tuples, where each tuple
                           represents a row and column index on the chessboard.
        """
        # Define all possible direction in which the bishop move: any direction
        move_offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        # List to hold all possible moves
        possible_moves = []

        # Color of the bishop
        piece = self.get_piece_on(row, col)
        is_white = piece.is_white

        # Check each move offset
        for row_offset, col_offset in move_offsets:
            new_row, new_col = row + row_offset, col + col_offset
            # If the new position is within the bounds of the chessboard, add it to possible moves
            # and continue in the same direction
            while 0 <= new_row < 8 and 0 <= new_col < 8:
                if not self.is_occupied(new_row, new_col):
                    possible_moves.append(
                        Move(
                            piece,
                            (row, col),
                            (new_row, new_col),
                            self.get_piece_on(new_row, new_col),
                        )
                    )
                elif self.get_piece_on(new_row, new_col).color != is_white:
                    # If the square is occupied by an opponent's piece, add it to possible moves
                    possible_moves.append(
                        Move(
                            piece,
                            (row, col),
                            (new_row, new_col),
                            self.get_piece_on(new_row, new_col),
                        )
                    )
                    # Stop moving in this direction further
                    break
                else:
                    # The square is occupied by a piece of the same color
                    # So stop moving in this direction
                    break
                new_row += row_offset
                new_col += col_offset

        return possible_moves

    def _possible_knight_moves(self, row: int, col: int) -> list[tuple[int]]:
        # Define all possible direction in which the knight move: any direction
        move_offsets = [
            (-2, -1),
            (-2, 1),
            (-1, -2),
            (-1, 2),
            (1, -2),
            (1, 2),
            (2, -1),
            (2, 1),
        ]

        # List to hold all possible moves
        possible_moves = []

        # Color of the knight
        piece = self.get_piece_on(row, col)
        is_white = piece.is_white

        # Check each move offset
        for row_offset, col_offset in move_offsets:
            new_row, new_col = row + row_offset, col + col_offset
            # If the new position is within the bounds of the chessboard, add it to possible moves
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                if not self.is_occupied(new_row, new_col):
                    possible_moves.append(
                        Move(
                            piece,
                            (row, col),
                            (new_row, new_col),
                            self.get_piece_on(new_row, new_col),
                        )
                    )
                elif self.get_piece_on(new_row, new_col).color != is_white:
                    # If the square is occupied by an opponent's piece, add it to possible moves
                    possible_moves.append(
                        Move(
                            piece,
                            (row, col),
                            (new_row, new_col),
                            self.get_piece_on(new_row, new_col),
                        )
                    )

        return possible_moves

    def _possible_pawn_moves(self, row: int, col: int) -> list[tuple[int]]:

        # List to hold all possible moves
        possible_moves = []

        # Color of the pawn
        piece = self.get_piece_on(row, col)
        is_white = piece.is_white

        # Determine the direction of movement based on color (white or black)
        if is_white:
            move_offset = (1, 0)  # White pawns move up the board
            double_move = (2, 0)  # Double move from starting position
        else:
            move_offset = (-1, 0)  # Black pawns move down the board
            double_move = (-2, 0)  # Double move from starting position

        # Check one square forward
        new_row = row + move_offset[0]
        if 0 <= new_row < 8:
            if not self.is_occupied(new_row, col):
                possible_moves.append(
                    Move(
                        piece,
                        (row, col),
                        (new_row, col),
                        self.get_piece_on(new_row, col),
                    )
                )

        # Check two squares forward (only if it's the pawn's first move)
        if (is_white and row == 1) or (not is_white and row == 6):
            new_row = row + double_move[0]
            if 0 <= new_row < 8:
                if not self.is_occupied(new_row, col):
                    possible_moves.append(
                        Move(
                            piece,
                            (row, col),
                            (new_row, col),
                            self.get_piece_on(new_row, col),
                        )
                    )

        # Check for captures on the diagonals
        capture_offsets = [(1, -1), (1, 1)] if is_white else [(-1, -1), (-1, 1)]
        for offset in capture_offsets:
            new_row, new_col = row + offset[0], col + offset[1]
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                # Check if target square is occupied by opposite color
                if self.is_occupied(new_row, new_col):
                    if self.get_piece_on(new_row, new_col).color != is_white:
                        possible_moves.append(
                            Move(
                                piece,
                                (row, col),
                                (new_row, new_col),
                                self.get_piece_on(new_row, new_col),
                            )
                        )

        # En passant capture check
        enpassant_offsets = [(1, -1), (1, 1)] if is_white else [(-1, -1), (-1, 1)]
        for offset in enpassant_offsets:
            new_row, new_col = row + offset[0], col + offset[1]
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                if (
                    self.is_enpassant_target(new_row, new_col)
                    and self.get_piece_on(new_row, new_col).color != is_white
                ):
                    possible_moves.append(
                        Move(
                            piece,
                            (row, col),
                            (new_row, new_col),
                            self.get_piece_on(new_row, new_col),
                        )
                    )

        return possible_moves

    def _is_legal_move(self, move) -> bool:
        if not self.is_move_safe(move.origin, move.target):
            return False
        # TODO : add check whether move is castling and castling is allowed
        # TODO : add check whether move is en passant and that is currently allowed
        return True

    def is_move_safe(self, origin, destination) -> bool:
        """
        Check if moving the piece to the destination square would put the player in check.

        Args:
            origin (Square): The current position of the chess piece.
            destination (Square): The proposed new position for the chess piece.

        Returns:
            bool: True if moving the piece to the destination square would not put the player in check, False otherwise.
        """
        # Simulate the move on a hypothetical board
        temp_piece = self.get_piece_on(*destination)
        moving_piece = self.get_piece_on(*origin)
        self.place_piece_on(*destination, moving_piece)
        self.place_piece_on(*origin, None)
        print('temp_piece', temp_piece, *destination)
        print('moving_piece', moving_piece, *origin)

        # Check if the king is in check after the move
        for row in range(8):
            for col in range(8):
                if self.is_occupied(row, col):
                    piece = self.get_piece_on(row, col)
                    if (
                        piece.color == moving_piece.color
                        and piece.name.capitalize() == "King"
                    ):
                        print('king square', row, col)
                        if self._is_attacked((row, col)):
                            safe = False
                            break
            else:
                continue
            break
        else:
            safe = True

        # Restore the original board configuration
        self.place_piece_on(*origin, moving_piece)
        self.place_piece_on(*destination, temp_piece)

        return safe

    def _is_attacked(self, square) -> bool:
        """
        Check if the square is under attack by opponent's pieces.

        Args:
            king_square (Square): The square which may or may not be attacked.

        Returns:
            bool: True if the square is under attack, False otherwise.
        """
        # Define the opponent's color
        oponent_is_white = self.get_piece_on(*square).is_white

        # Iterate over all squares on the board
        for row in range(8):
            for col in range(8):

                # Check if there is an opponent's piece on this square
                if (
                    self.is_occupied(row, col)
                    and self.get_piece_on(row, col).is_white != oponent_is_white
                ):
                    possible_moves = self._get_possible_moves_from(row, col, False)
                    # Check if any of these moves include attacking the king's square
                    for move in possible_moves:
                        if move.target == square:
                            return True

        return False
