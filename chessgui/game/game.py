from copy import copy, deepcopy
from itertools import product
from typing import Optional

from .utils import algebraic_to_index, index_to_algebraic
from ..errors import IllegalMoveError
from .state import GameState
from .moves import Move
from .tree import GameTree, GameTreeNode
from .result import GameResult
from .piece import ChessPiece

from stockfish import Stockfish


class ChessGame:
    """Class implementing rules of chess:
    - how pieces move
    - checking if moves are legal
    - checking if game has finished1
    """

    NUM_SQUARES = 8

    def __init__(self):
        self.state = GameState.from_fen_string()
        self.move_tree = GameTree(deepcopy(self.state))

    def smith_to_move(self, move_str):
        """Return a move corresponding from Smith notation"""
        origin = algebraic_to_index(move_str[0:2])
        target = algebraic_to_index(move_str[2:])
        try:
            promote_to = move_str[4]
        except IndexError:
            promote_to = None

        return ChessGame._generate_move(self.state, origin, target, promote_to)

    def leads_to_promotion(self, move: Move):
        """"""
        if move.piece.name == "Pawn":
            return move.target[0] == {"white": 0, "black": ChessGame.NUM_SQUARES - 1}.get(
                move.piece.color
            )
        return False

    def make_move(self, move: Move):
        """Implement the logic to check if the move is allowed and update the board accordingly

        Args:
            move (_type_): # TODO
        """

        if move.piece is None:
            raise IllegalMoveError("You cannot make moves from empty squares")
        if self.state.active_color != move.piece.color:
            raise IllegalMoveError(
                f"Cannot move piece of color {move.piece.color}, because it is {self.state.active_color}'s turn."
            )
        if not move in self.get_possible_moves_from(move.origin, include_promotion_options=True):
            raise IllegalMoveError(f"{move} is not legal in the current position.")

        # self._move_graph.current_tip.append(move)
        self.state.is_white_active = not self.state.is_white_active
        if move.is_castling:
            # Remove castling rights
            if move.piece.is_white:
                self.state.castling_rights["K"] = False
                self.state.castling_rights["Q"] = False
            else:
                self.state.castling_rights["k"] = False
                self.state.castling_rights["q"] = False
            # Move rook and king
            rook = self.state.get_piece_on(*move.rook_move.origin)
            king = self.state.get_piece_on(*move.origin)
            self.state.place_piece_on(*move.rook_move.origin, None)
            self.state.place_piece_on(*move.origin, None)
            self.state.place_piece_on(*move.rook_move.target, rook)
            self.state.place_piece_on(*move.target, king)
        else:

            if move.piece.name == "King":
                if move.piece.is_white:
                    self.state.castling_rights["K"] = False
                    self.state.castling_rights["Q"] = False
                else:
                    self.state.castling_rights["k"] = False
                    self.state.castling_rights["q"] = False
            elif move.piece.name == "Rook":
                if move.piece.is_white:
                    if move.origin == (ChessGame.NUM_SQUARES - 1, 0):
                        # Remove queen side castling right
                        self.state.castling_rights["Q"] = False
                    elif move.origin == (ChessGame.NUM_SQUARES - 1, ChessGame.NUM_SQUARES - 1):
                        # Remove kingside castling right
                        self.state.castling_rights["K"] = False
                else:
                    if move.origin == (0, 0):
                        # Remove queen side castling right
                        self.state.castling_rights["q"] = False
                    elif move.origin == (0, ChessGame.NUM_SQUARES - 1):
                        # Remove kingside castling right
                        self.state.castling_rights["k"] = False

            self.state.en_passant_target = None
            if move.is_double_move:
                self.state.en_passant_target = (
                    (move.origin[0] + move.target[0]) // 2,
                    move.origin[1],
                )

            if move.piece.name == "Pawn" or move.is_capture:
                self.state.half_moves = 0
            else:
                self.state.half_moves += 1

            if self.state.active_color == "white":
                self.state.moves += 1

            if move.is_capture:
                self.state.place_piece_on(*move.captured_piece.coords, None)
            if move.is_promotion:
                self.state.place_piece_on(*move.target, move.promote_to)
            else:
                self.state.place_piece_on(*move.target, move.piece)

            self.state.place_piece_on(*move.origin, None)

        self.move_tree.make_move(move, self.move_to_smith(move), self.state.to_fen_string())

    def get_all_legal_moves(self):
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.state.get_piece_on(row, col)
                if piece is not None and piece.color == self.state.active_color:
                    moves += self.get_possible_moves_from((row, col))

        return moves

    def get_possible_moves_from(
        self, square: tuple[int, int], include_promotion_options=False
    ) -> list[Move]:
        """
        Retrieve list of all possible moves that can be by the piece
        currently occupying a give square

        Args:
            row (int): The zero-based row index of the square.
            col (int): The zero-based column index of the square.

        Returns:
            piece (ChessPiece) : The piece currently occupying the square.
        """
        return self._get_possible_moves_from(
            square, self.state, check_safe=True, include_promotion_options=include_promotion_options
        )

    @staticmethod
    def _get_possible_moves_from(
        square: tuple[int, int],
        state: GameState,
        check_safe=False,
        **kwargs,
    ) -> list[Move]:
        piece = state.get_piece_on(*square)
        moves = getattr(ChessGame, f"_get_possible_{piece.name.lower()}_moves")(
            square, state, **kwargs
        )

        if check_safe:
            moves = [move for move in moves if ChessGame.is_move_safe(move, state)]

        return moves

    @staticmethod
    def _get_possible_king_moves(
        origin: tuple[int, int],
        state: GameState,
        **kwargs,
    ) -> list[tuple[int, int]]:
        """
        Calculate all possible moves for a king from its current position on the chessboard.

        The king can move one squares along a row, column, or diagonal. This function calculates
        and returns all positions (as tuples of row and column) that the king can reach
        from its current position without jumping off the board.

        Args:
            origin (Square): The chess square object representing the king's current position on
                             the board.

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
        piece = state.get_piece_on(*origin)

        # Check each move offset
        for row_offset, col_offset in move_offsets:
            new_row, new_col = origin[0] + row_offset, origin[1] + col_offset

            # If the new position is within the bounds of the chessboard, add it to possible moves
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                if not state.is_occupied(new_row, new_col):
                    possible_moves.append(
                        ChessGame._generate_move(state, origin, (new_row, new_col))
                    )
                elif state.get_piece_on(new_row, new_col).is_white != piece.is_white:
                    # If the square is occupied by an opponent's piece, add it to possible moves
                    possible_moves.append(
                        ChessGame._generate_move(state, origin, (new_row, new_col))
                    )

        # Check king side castling
        if state.castling_rights["K" if piece.is_white else "k"]:
            target = origin[0], 6
            # Check path is free
            for col in range(origin[1] + 1, target[1] + 1):
                tmp_square = (origin[0], col)
                if state.is_occupied(*tmp_square):
                    break
            else:
                possible_moves.append(ChessGame._generate_move(state, origin, target))

        if state.castling_rights["Q" if piece.is_white else "q"]:
            target = origin[0], 2
            # Check path is free
            for col in range(target[1] - 1, origin[1]):
                tmp_square = (origin[0], col)
                if state.is_occupied(*tmp_square):
                    break
            else:
                possible_moves.append(ChessGame._generate_move(state, origin, target))

        return possible_moves

    @staticmethod
    def _get_possible_queen_moves(
        origin: tuple[int, int],
        state: GameState,
        **kwargs,
    ) -> list[tuple[int, int]]:
        """
        Calculate all possible moves for a queen from its current position on the chessboard.

        The queen can move any number of squares along a row, column, or diagonal. This function
        calculates and returns all positions (as tuples of row and column) that the queen can reach
        from its current position without jumping off the board.

        Args:
            origin (Square): The chess square object representing the queen's current position on
                             the board.

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
        piece = state.get_piece_on(*origin)

        # Check each move offset
        for row_offset, col_offset in move_offsets:
            new_row, new_col = origin[0] + row_offset, origin[1] + col_offset
            # If the new position is within the bounds of the chessboard, add it to possible moves
            # and continue in the same direction
            while 0 <= new_row < 8 and 0 <= new_col < 8:
                if not state.is_occupied(new_row, new_col):
                    possible_moves.append(
                        ChessGame._generate_move(state, origin, (new_row, new_col))
                    )
                elif state.get_piece_on(new_row, new_col).is_white != piece.is_white:
                    # If the square is occupied by an opponent's piece, add it to possible moves
                    possible_moves.append(
                        ChessGame._generate_move(state, origin, (new_row, new_col))
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

    @staticmethod
    def _get_possible_rook_moves(
        origin: tuple[int, int],
        state: GameState,
        **kwargs,
    ) -> list[tuple[int, int]]:
        """
        Calculate all possible moves for a rook from its current position on the chessboard.

        The rook can move any number of squares along a row or column without jumping over other
        pieces. This function also checks if the square the piece is trying to move to is occupied
        by another piece before adding it to the list of possible moves.

        Args:
            origin (Square): The square object representing the rook's current position on the
                             board.

        Returns:
            list of tuple: A list containing all possible move positions as tuples, where each
                            tuple represents a row and column index on the chessboard.
        """
        # Define all possible direction in which the rook move: any direction
        move_offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        # List to hold all possible moves
        possible_moves = []

        # Color of the rook
        piece = state.get_piece_on(*origin)

        # Check each move offset
        for row_offset, col_offset in move_offsets:
            new_row, new_col = origin[0] + row_offset, origin[1] + col_offset
            # If the new position is within the bounds of the chessboard, add it to possible moves
            # and continue in the same direction
            while 0 <= new_row < 8 and 0 <= new_col < 8:
                if not state.is_occupied(new_row, new_col):
                    possible_moves.append(
                        ChessGame._generate_move(state, origin, (new_row, new_col))
                    )
                elif state.get_piece_on(new_row, new_col).is_white != piece.is_white:
                    # If the square is occupied by an opponent's piece, add it to possible moves
                    possible_moves.append(
                        ChessGame._generate_move(state, origin, (new_row, new_col))
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

    @staticmethod
    def _get_possible_bishop_moves(
        origin: tuple[int, int],
        state: GameState,
        **kwargs,
    ) -> list[tuple[int, int]]:
        """
        Calculate all possible moves for a bishop from its current position on the chessboard.

        The bishop can move any number of squares along a diagonal without jumping over other
        pieces. This function returns a list with all possible squares the bishop can move to,
        including possible captures.

        Args:
            origin (Square): The square object representing the rook's current position on the
                             board.
        Returns:
            list of tuple: A list containing all possible move positions as tuples, where each tuple
                            represents a row and column index on the chessboard.
        """
        # Define all possible direction in which the bishop move: any direction
        move_offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        # List to hold all possible moves
        possible_moves = []

        # Color of the bishop
        piece = state.get_piece_on(*origin)

        # Check each move offset
        for row_offset, col_offset in move_offsets:
            new_row, new_col = origin[0] + row_offset, origin[1] + col_offset
            # If the new position is within the bounds of the chessboard, add it to possible moves
            # and continue in the same direction
            while 0 <= new_row < 8 and 0 <= new_col < 8:
                if not state.is_occupied(new_row, new_col):
                    possible_moves.append(
                        ChessGame._generate_move(state, origin, (new_row, new_col))
                    )
                elif state.get_piece_on(new_row, new_col).is_white != piece.is_white:
                    # If the square is occupied by an opponent's piece, add it to possible moves
                    possible_moves.append(
                        ChessGame._generate_move(state, origin, (new_row, new_col))
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

    @staticmethod
    def _get_possible_knight_moves(
        origin: tuple[int, int],
        state: GameState,
        **kwargs,
    ) -> list[tuple[int, int]]:
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
        piece = state.get_piece_on(*origin)

        # Check each move offset
        for row_offset, col_offset in move_offsets:
            target = origin[0] + row_offset, origin[1] + col_offset
            # If the new position is within the bounds of the chessboard, add it to possible moves
            if 0 <= target[0] < 8 and 0 <= target[1] < 8:
                if not state.is_occupied(*target):
                    possible_moves.append(ChessGame._generate_move(state, origin, target))
                elif state.get_piece_on(*target).is_white != piece.is_white:
                    # If the square is occupied by an opponent's piece, add it to possible moves
                    possible_moves.append(ChessGame._generate_move(state, origin, target))

        return possible_moves

    @staticmethod
    def _get_possible_pawn_moves(
        origin: tuple[int, int],
        state: GameState,
        include_promotion_options: bool = False,
        **kwargs,
    ) -> list[tuple[int, int]]:

        # List to hold all possible moves
        possible_moves = []

        # Color of the pawn
        piece = state.get_piece_on(*origin)
        is_white = piece.is_white

        # Determine the direction of movement based on color (white or black)
        if is_white:
            move_offset = (-1, 0)  # White pawns move up the board
            double_move = (-2, 0)  # Double move from starting position
        else:
            move_offset = (1, 0)  # Black pawns move down the board
            double_move = (2, 0)  # Double move from starting position

        promotion_options = "qrbn"
        if piece.is_white:
            promotion_options = promotion_options.upper()

        def append_move(state, origin, target):
            if not include_promotion_options:
                possible_moves.append(ChessGame._generate_move(state, origin, target))
            else:
                for promote_to in promotion_options:
                    possible_moves.append(
                        ChessGame._generate_move(state, origin, target, promote_to=promote_to)
                    )

        # Check one square forward
        target = (origin[0] + move_offset[0], origin[1])
        if 0 <= target[0] < 8:
            if not state.is_occupied(*target):
                append_move(state, origin, target)

        # Check two squares forward (only if it's the pawn's first move)
        if (is_white and origin[0] == 6) or (not is_white and origin[0] == 1):
            target = (origin[0] + double_move[0], origin[1])
            if 0 <= target[0] < 8:
                if not state.is_occupied(*target):
                    append_move(state, origin, target)

        # Check for captures on the diagonals
        capture_offsets = [(-1, -1), (-1, 1)] if is_white else [(1, -1), (1, 1)]
        for offset in capture_offsets:
            target = origin[0] + offset[0], origin[1] + offset[1]
            if 0 <= target[0] < 8 and 0 <= target[1] < 8:
                # Check if target square is occupied by opposite color
                if state.is_occupied(*target):
                    if state.get_piece_on(*target).is_white != is_white:
                        append_move(state, origin, target)

        # En passant capture check
        enpassant_offsets = [(-1, -1), (-1, 1)] if is_white else [(1, -1), (1, 1)]
        for offset in enpassant_offsets:
            target = (origin[0] + offset[0], origin[1] + offset[1])
            if 0 <= target[0] < 8 and 0 <= target[1] < 8:
                if state.is_enpassant_target(*target):
                    append_move(state, origin, target)

        return possible_moves

    @staticmethod
    def is_move_safe(
        move: Move,
        state: GameState,
    ) -> bool:
        """
        Check if moving the piece to the move.target square would put the player in check.

        Args:
            origin (Square): The current position of the chess piece.
            destination (Square): The proposed new position for the chess piece.

        Returns:
            bool: True if moving the piece to the destination square would not
                    put the player in check, False otherwise.
        """
        # Simulate the move on a hypothetical board
        temp_state = deepcopy(state)
        temp_state.place_piece_on(*move.target, copy(move.piece))
        temp_state.place_piece_on(*move.origin, None)

        # Check if the king is in check after the move
        king_square = temp_state.find_king(move.piece.color)

        safe = not ChessGame.is_attacked(king_square, move.piece.color, temp_state)

        if move.is_castling:
            for col in range(move.origin[1], move.target[1] + 1):
                safe = safe and not ChessGame.is_attacked(
                    (move.origin[0], col),
                    move.piece.color,
                    state,
                )

        return safe

    @staticmethod
    def is_attacked(
        square: tuple[int, int],
        defending_color: str,
        state: GameState,
    ) -> bool:
        """
        Check if the square is under attack by opponent's pieces.

        Args:
            king_square (Square): The square which may or may not be attacked.
            defending_color (str): Color of side that might be attacked ('white' or 'black')

        Returns:
            bool: True if the square is under attack, False otherwise.
        """
        # Iterate over all squares on the board
        for attack_origin in product(range(8), repeat=2):
            # Check if there is an opponent's piece on this square
            if (
                state.is_occupied(*attack_origin)
                and state.get_piece_on(*attack_origin).color != defending_color
            ):
                possible_moves = ChessGame._get_possible_moves_from(
                    attack_origin, state, check_safe=False
                )
                # Check if any of these moves include attacking the king's square
                for move in possible_moves:
                    if move.target == square:
                        return True

        return False

    @staticmethod
    def _generate_move(
        state: GameState,
        origin: tuple[int, int],
        target: tuple[int, int],
        promote_to: Optional[str] = None,
    ) -> Move:
        # Basic move info
        piece = state.get_piece_on(*origin)

        # Captures
        captured_piece = state.get_piece_on(*target)
        if captured_piece is not None:
            if piece.name == "Rook" and captured_piece.name == "King":
                if piece.color == captured_piece.color:
                    captured_piece = None
        else:
            if piece.name == "Pawn" and target == state.en_passant_target:
                if state.en_passant_target[0] == 2:
                    captured_piece = state.get_piece_on(4, target[1])
                else:
                    captured_piece = state.get_piece_on(3, target[1])

        # Promotions
        if promote_to is not None:
            promote_to = ChessPiece(Stockfish.Piece(promote_to), *target)
            if target[0] != (0 if piece.is_white else ChessGame.NUM_SQUARES - 1):
                raise ValueError("Promotion can only occur at the edge of the board.")

        # Castling is a combination of two moves.
        rook_move = None
        if piece.name == "King" and abs(origin[1] - target[1]) > 1:
            # Castling
            if origin[1] > target[1]:
                # Queenside
                rook_origin = (origin[0], 0)
                rook_target = (target[0], target[1] + 1)
            else:
                rook_origin = (origin[0], ChessGame.NUM_SQUARES - 1)
                rook_target = (target[0], target[1] - 1)
            rook_move = ChessGame._generate_move(state, rook_origin, rook_target)

        return Move(piece, origin, target, captured_piece, promote_to, rook_move)

    def game_result(self):
        # 50 moves since capture or pawn move
        if self.state.half_moves >= 100:
            return GameResult.DRAW_BY_50_MOVE

        # TODO Three fold repitition
        #   - move up the tree checking if state was equal to current state
        #   - captures or promotions are early exit conditions
        #     return GameResult.DRAW_BY_REPETION

        # TODO insufficient material
        # 1) Both sides have one of the following
        #    a) king
        #    b) king and bishop
        #    c) king and knight
        #     return GameResult.DRAW_INSUFFICIENT_MATERIAL

        # No legal moves left:
        if len(self.get_all_legal_moves()) == 0:
            king_square = self.state.find_king(self.state.active_color)
            if ChessGame.is_attacked(king_square, self.state.active_color, self.state):
                # Checkmate
                if self.state.is_white_active:
                    return GameResult.WIN_BLACK_CHECKMATE
                return GameResult.WIN_WHITE_CHECKMATE
            # Stalemate
            return GameResult.DRAW_BY_STALEMATE

        return None

    def goto(self, node: GameTreeNode):
        self.move_tree.pointer = node
        self.state.load_fen_string(node.fen)

    def move_to_smith(self, move: Move):
        smith_str = ""
        if move.piece.name != "Pawn":
            smith_str += move.piece.symbol.upper()
        ambigous = [False, False]
        for row in range(8):
            for col in range(8):
                if (row, col) == move.origin:
                    continue
                piece = self.state.get_piece_on(row, col)
                if piece is None:
                    continue
                if piece.symbol == move.piece.symbol:
                    if move.target in [m.target for m in self.get_possible_moves_from((row, col))]:
                        # A piece of the same type can also move to this square
                        if row == move.origin[0]:
                            ambigous[0] = True
                        elif col == move.origin[1]:
                            ambigous[1] = True

        if ambigous[0]:
            smith_str += index_to_algebraic(*move.origin)[0]
        if ambigous[1]:
            smith_str += index_to_algebraic(*move.origin)[1]

        if move.captured_piece is not None:
            if move.piece.name == "Pawn":
                smith_str += index_to_algebraic(*move.origin)[0]
            smith_str += "x"
        smith_str += index_to_algebraic(*move.target)

        return smith_str
