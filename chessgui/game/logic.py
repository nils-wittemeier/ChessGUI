import sys

from copy import copy, deepcopy
from itertools import product

from .moves import Move
from .state import GameState


def get_possible_moves_from(
    square: tuple[int, int], game_state: GameState
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
    return _get_possible_moves_from(square, game_state, True)


def _get_possible_moves_from(
    square: tuple[int, int],
    game_state: GameState,
    check_legal=False,
) -> list[Move]:
    piece = game_state.get_piece_on(*square)
    current_module = sys.modules[__name__]
    moves = getattr(current_module, f"_get_possible_{piece.name.lower()}_moves")(
        square, game_state
    )

    if check_legal:
        moves = [move for move in moves if is_legal_move(move, game_state)]

    return moves


def _get_possible_king_moves(
    origin: tuple[int, int],
    game_state: GameState,
) -> list[tuple[int, int]]:
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
    piece = game_state.get_piece_on(*origin)

    # Check each move offset
    for row_offset, col_offset in move_offsets:
        new_row, new_col = origin[0] + row_offset, origin[1] + col_offset

        # If the new position is within the bounds of the chessboard, add it to possible moves
        if 0 <= new_row < 8 and 0 <= new_col < 8:
            if not game_state.is_occupied(new_row, new_col):
                possible_moves.append(Move(piece, origin, (new_row, new_col)))
            elif game_state.get_piece_on(new_row, new_col).is_white != piece.is_white:
                # If the square is occupied by an opponent's piece, add it to possible moves
                possible_moves.append(
                    Move(
                        piece,
                        origin,
                        (new_row, new_col),
                        game_state.get_piece_on(new_row, new_col),
                    )
                )

    # Check king side castling
    if game_state.castling_rights["K" if piece.is_white else "k"]:
        new_king_square = (origin[0], 6)
        old_rook_square = (origin[0], 7)
        new_rook_square = (origin[0], 5)
        # Check path is free
        print(f'<Castling from: {origin} to {new_king_square}>')
        for col in range(origin[1]+1, 7):
            tmp_square = (origin[0], col)
            print(f'\t Square {tmp_square} is occupied? {game_state.is_occupied(*tmp_square)}')
            if game_state.is_occupied(*tmp_square):
                break
        else:
            possible_moves.append(
                Move(
                    piece,
                    origin,
                    new_king_square,
                    rook_move=Move(
                        game_state.get_piece_on(*old_rook_square),
                        old_rook_square,
                        new_rook_square,
                    ),
                )
            )

    return possible_moves


def _get_possible_queen_moves(
    origin: tuple[int, int],
    game_state: GameState,
) -> list[tuple[int, int]]:
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
    piece = game_state.get_piece_on(*origin)

    # Check each move offset
    for row_offset, col_offset in move_offsets:
        new_row, new_col = origin[0] + row_offset, origin[1] + col_offset
        # If the new position is within the bounds of the chessboard, add it to possible moves
        # and continue in the same direction
        while 0 <= new_row < 8 and 0 <= new_col < 8:
            if not game_state.is_occupied(new_row, new_col):
                possible_moves.append(Move(piece, origin, (new_row, new_col)))
            elif game_state.get_piece_on(new_row, new_col).is_white != piece.is_white:
                # If the square is occupied by an opponent's piece, add it to possible moves
                possible_moves.append(
                    Move(
                        piece,
                        origin,
                        (new_row, new_col),
                        game_state.get_piece_on(new_row, new_col),
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


def _get_possible_rook_moves(
    origin: tuple[int, int],
    game_state: GameState,
) -> list[tuple[int, int]]:
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
    piece = game_state.get_piece_on(*origin)

    # Check each move offset
    for row_offset, col_offset in move_offsets:
        new_row, new_col = origin[0] + row_offset, origin[1] + col_offset
        # If the new position is within the bounds of the chessboard, add it to possible moves
        # and continue in the same direction
        while 0 <= new_row < 8 and 0 <= new_col < 8:
            if not game_state.is_occupied(new_row, new_col):
                possible_moves.append(Move(piece, origin, (new_row, new_col)))
            elif game_state.get_piece_on(new_row, new_col).is_white != piece.is_white:
                # If the square is occupied by an opponent's piece, add it to possible moves
                possible_moves.append(
                    Move(
                        piece,
                        origin,
                        (new_row, new_col),
                        game_state.get_piece_on(new_row, new_col),
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


def _get_possible_bishop_moves(
    origin: tuple[int, int],
    game_state: GameState,
) -> list[tuple[int, int]]:
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
    piece = game_state.get_piece_on(*origin)

    # Check each move offset
    for row_offset, col_offset in move_offsets:
        new_row, new_col = origin[0] + row_offset, origin[1] + col_offset
        # If the new position is within the bounds of the chessboard, add it to possible moves
        # and continue in the same direction
        while 0 <= new_row < 8 and 0 <= new_col < 8:
            if not game_state.is_occupied(new_row, new_col):
                possible_moves.append(Move(piece, origin, (new_row, new_col)))
            elif game_state.get_piece_on(new_row, new_col).is_white != piece.is_white:
                # If the square is occupied by an opponent's piece, add it to possible moves
                possible_moves.append(
                    Move(
                        piece,
                        origin,
                        (new_row, new_col),
                        game_state.get_piece_on(new_row, new_col),
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


def _get_possible_knight_moves(
    origin: tuple[int, int],
    game_state: GameState,
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
    piece = game_state.get_piece_on(*origin)

    # Check each move offset
    for row_offset, col_offset in move_offsets:
        target = origin[0] + row_offset, origin[1] + col_offset
        # If the new position is within the bounds of the chessboard, add it to possible moves
        if 0 <= target[0] < 8 and 0 <= target[1] < 8:
            if not game_state.is_occupied(*target):
                possible_moves.append(Move(piece, origin, target))
            elif game_state.get_piece_on(*target).is_white != piece.is_white:
                # If the square is occupied by an opponent's piece, add it to possible moves
                possible_moves.append(
                    Move(piece, origin, target, game_state.get_piece_on(*target))
                )

    return possible_moves


def _get_possible_pawn_moves(
    origin: tuple[int, int],
    game_state: GameState,
) -> list[tuple[int, int]]:

    # List to hold all possible moves
    possible_moves = []

    # Color of the pawn
    piece = game_state.get_piece_on(*origin)
    is_white = piece.is_white

    # Determine the direction of movement based on color (white or black)
    if is_white:
        move_offset = (-1, 0)  # White pawns move up the board
        double_move = (-2, 0)  # Double move from starting position
    else:
        move_offset = (1, 0)  # Black pawns move down the board
        double_move = (2, 0)  # Double move from starting position

    # Check one square forward
    target = (origin[0] + move_offset[0], origin[1])
    if 0 <= target[0] < 8:
        if not game_state.is_occupied(*target):
            possible_moves.append(Move(piece, origin, target))

    # Check two squares forward (only if it's the pawn's first move)
    if (is_white and origin[0] == 6) or (not is_white and origin[0] == 1):
        target = (origin[0] + double_move[0], origin[1])
        if 0 <= target[0] < 8:
            if not game_state.is_occupied(*target):
                possible_moves.append(Move(piece, origin, target))

    # Check for captures on the diagonals
    capture_offsets = [(-1, -1), (-1, 1)] if is_white else [(1, -1), (1, 1)]
    for offset in capture_offsets:
        target = origin[0] + offset[0], origin[1] + offset[1]
        if 0 <= target[0] < 8 and 0 <= target[1] < 8:
            # Check if target square is occupied by opposite color
            if game_state.is_occupied(*target):
                if game_state.get_piece_on(*target).is_white != is_white:
                    possible_moves.append(
                        Move(piece, origin, target, game_state.get_piece_on(*target))
                    )

    # En passant capture check
    enpassant_offsets = [(-1, -1), (-1, 1)] if is_white else [(1, -1), (1, 1)]
    for offset in enpassant_offsets:
        target = (origin[0] + offset[0], origin[1] + offset[1])
        if 0 <= target[0] < 8 and 0 <= target[1] < 8:
            if (
                game_state.is_enpassant_target(*target)
                and game_state.get_piece_on(*target).is_white != is_white
            ):
                possible_moves.append(
                    Move(piece, origin, target, game_state.get_piece_on(*target))
                )

    return possible_moves


def is_legal_move(move: Move, game_state: GameState) -> bool:
    if not is_move_safe(move, game_state):
        return False
    # TODO : add check whether move is castling and castling is allowed
    # TODO : add check whether move is en passant and that is currently allowed
    return True


def is_move_safe(move: Move, game_state: GameState) -> bool:
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
    temp_state = deepcopy(game_state)
    temp_state.place_piece_on(*move.target, copy(move.piece))
    temp_state.place_piece_on(*move.origin, None)

    # Check if the king is in check after the move
    king_square = temp_state.find_king(move.piece.color)

    safe = not is_attacked(king_square, move.piece.color, temp_state)

    if move.is_castling:
        for col in range(move.origin[1], move.target[1] + 1):
            safe = safe and not is_attacked(
                (move.origin[0], col), move.piece.color, game_state
            )

    return safe


def is_attacked(
    square: tuple[int, int],
    defending_color: str,
    game_state: GameState,
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
            game_state.is_occupied(*attack_origin)
            and game_state.get_piece_on(*attack_origin).color != defending_color
        ):
            possible_moves = _get_possible_moves_from(attack_origin, game_state, False)
            # Check if any of these moves include attacking the king's square
            for move in possible_moves:
                if move.target == square:
                    return True

    return False
