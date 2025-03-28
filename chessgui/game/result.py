from enum import Enum


class GameResult(Enum):
    WIN_BLACK_CHECKMATE = -2
    WIN_BLACK_RESIGNATION = -1
    DRAW_BY_STALEMATE = 0
    WIN_WHITE_CHECKMATE = 1
    WIN_WHITE_RESIGNATION = 2
    DRAW_BY_REPETION = 5
    DRAW_BY_50_MOVE = 6
    DRAW_INSUFFICIENT_MATERIAL = 7
