def algebraic_to_index(pos: str) -> tuple[int] | None:
    """
    Convert square identifier from algebraic notation to pair of zero-based indices.

    Args:
        pos (str): The identifier in algebraic notation.

    Returns:
        row (int): The zero-based row index of the square.
        col (int): The zero-based column index of the square.
    """
    row = 8 - int(pos[1])
    col = "abcdefgh".index(pos[0])
    return row, col


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
    return "abcdefgh"[col] + str(8 - row)
