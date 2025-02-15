""" This module implements a chess board as an GUI element"""

import tkinter as tk
from functools import partial
from pathlib import Path
from tkinter.font import Font

import tksvg
from stockfish import Stockfish

_stockfish_root = Path("/Users/Juijan/stockfish")
_stockfish_exe = _stockfish_root / "stockfish-windows-x86-64-avx2.exe"

_PIECE_COLORS = {"light": "#FFFFFF", "dark": "#272932"}
_BG_COLORS = {
    "none": {"light": "#E3E1CE", "dark": "#88684E"},
    "selected": {"light": "#F1CA1E", "dark": "#F1CA1E"},
    "moved": {"light": "#F5E07F", "dark": "#C8A60E"},
    "selector": "#FFFFFF",
}

_FG_COLORS = {"light": "#88684E", "dark": "#E3E1CE"}

_STARTING_POS = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
_STARTING_POS = "8/P6k/8/8/8/8/K6p/8 w - - 0 1"


def load_svg(piece, **kwargs):
    return tksvg.SvgImage(data=_PIECE_SVGS[piece].read_text(), **kwargs)


_PIECE_SVGS = {
    Stockfish.Piece.WHITE_KING: Path("chessgui/icons/Chess_klt45.svg"),
    Stockfish.Piece.WHITE_QUEEN: Path("chessgui/icons/Chess_qlt45.svg"),
    Stockfish.Piece.WHITE_ROOK: Path("chessgui/icons/Chess_rlt45.svg"),
    Stockfish.Piece.WHITE_BISHOP: Path("chessgui/icons/Chess_blt45.svg"),
    Stockfish.Piece.WHITE_KNIGHT: Path("chessgui/icons/Chess_nlt45.svg"),
    Stockfish.Piece.WHITE_PAWN: Path("chessgui/icons/Chess_plt45.svg"),
    Stockfish.Piece.BLACK_KING: Path("chessgui/icons/Chess_kdt45.svg"),
    Stockfish.Piece.BLACK_QUEEN: Path("chessgui/icons/Chess_qdt45.svg"),
    Stockfish.Piece.BLACK_ROOK: Path("chessgui/icons/Chess_rdt45.svg"),
    Stockfish.Piece.BLACK_BISHOP: Path("chessgui/icons/Chess_bdt45.svg"),
    Stockfish.Piece.BLACK_KNIGHT: Path("chessgui/icons/Chess_ndt45.svg"),
    Stockfish.Piece.BLACK_PAWN: Path("chessgui/icons/Chess_pdt45.svg"),
}

class Move:
    delivers_mate = False
    delivers_stale_mate = False
    is_capture = False
    is_legal = True
    is_castling = False
    is_promotion = False
    is_promotion_candidate = False


class ChessPiece:

    def __init__(self, piece: Stockfish.Piece):
        self._type = piece
        self._name = piece.name.split("_", maxsplit=2)[1].capitalize()
        self._is_white = piece.value == piece.value.upper()
        self._svg = load_svg(self._type)

    def to_svg(self, size: int):
        """SVG string for piece render"""
        self._svg = load_svg(self._type, scaletoheight=size)
        return self._svg

    @property
    def color(self):
        """Color of piece (white (w) or black (b)"""
        return "w" if self._is_white else "b"

    @property
    def type(self):
        """Type of piece"""
        return self._type

    @property
    def name(self):
        """Name of piece"""
        return self._name

    @property
    def short_name(self):
        """Name of piece"""
        return self._type.value

    def __repr__(self):
        return repr(self._type)
    
    def possible_moves_from(self, origin):

        def shift(a, b):
            return [(el_a[0] + b[0], el_a[1] + b[1]) for el_a in a]

        def is_on_board(i, j):
            if i < 0 or i >= 8 or j < 0 or j >= 8:
                return False
            return True

        return [
            candidate
            for candidate in shift(_BASE_MOVES[self._type], origin.to_index())
            if is_on_board(*candidate)
        ]


class PieceContainer(tk.Canvas):
    piece: ChessPiece | None = None
    svg_img: int | None = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind("<Configure>", self.resize)

    def place_piece(self, piece: Stockfish.Piece):
        """Place a piece on this square, removing any existing piece first"""
        if self.piece is not None:
            self.remove_piece()
        size = self.winfo_width()
        self.piece = ChessPiece(piece)
        self.svg_img = self.create_image(
            size / 2, size / 2, image=self.piece.to_svg(size)
        )

    def remove_piece(self):
        """Remove piece from this square"""
        self.svg_img = None
        self.piece = None
        self.delete("all")

    def resize(self, event):
        size = event.width
        if self.piece is not None:
            self.svg_img = self.create_image(
                size / 2, size / 2, image=self.piece.to_svg(size)
            )


class Square(PieceContainer):
    """This class implement a square on the chess board as a GUI element"""

    _color: str = "light"
    selected: bool = False
    last_move: bool = False

    def __init__(self, parent, rank, file):
        super().__init__(parent, highlightthickness=0)
        self.color = "light" if (rank + file) % 2 == 0 else "dark"
        self.grid(column=file, row=rank, sticky="nswe")

        self.font = Font(
            family="Roboto", size=int(0.1 * self.winfo_height()), weight="bold"
        )

        self.rank_label = None
        self.file_label = None
        self.add_label(
            rank=file if rank == 7 else None,
            file=rank if file == 0 else None,
        )

    @property
    def color(self):
        """Square color"""
        return self._color

    @color.setter
    def color(self, s: str):
        if s.lower() not in ["light", "dark"]:
            raise ValueError(f"Square: invalid color specifier: {s}")
        self._color = s.lower()
        self.refresh_color()

    def refresh_color(self):
        """Set background color"""
        if self.selected:
            hl_type = "selected"
        elif self.last_move:
            hl_type = "moved"
        else:
            hl_type = "none"

        self.configure(bg=_BG_COLORS[hl_type][self.color])

    def toggle_selected(self):
        """Toggle highlighting of selected square"""
        self.selected = not self.selected
        self.refresh_color()

    def toggle_moved(self):
        """Toggle highlighting of selected square"""
        self.last_move = not self.last_move
        self.refresh_color()

    def to_index(self):
        info = self.grid_info()
        return info["column"], info["row"]

    def to_algebraic(self):
        """Return algebraic notation for current square"""
        row, col = self.to_index()
        return "abcdefgh"[row] + str(8 - col)

    def resize(self, event):
        super().resize(event)
        size = event.width
        if self.rank_label is not None:
            self.moveto(self.rank_label, int(0.9 * size), int(0.83 * size))

        if self.file_label is not None:
            self.moveto(self.file_label, int(0.04 * size), int(0.04 * size))

    def add_label(self, rank: int | None = None, file: int | None = None):
        """Add rank of file label to this square"""
        size = self.winfo_width()
        if rank is not None:
            self.rank_label = self.create_text(
                int(0.96 * size),
                size,
                text="abcdefgh"[rank],
                font=self.font,
                anchor="se",
                fill=_FG_COLORS[self._color],
            )

        if file is not None:
            self.file_label = self.create_text(
                int(0.04 * size),
                int(0.04 * size),
                text=str(file + 1),
                font=self.font,
                anchor="nw",
                fill=_FG_COLORS[self._color],
            )


class EvalBar:
    def __init__(self, tk_frame, width):
        self.width = width // 2
        self.evaluation = {"type": "cp", "value": 0.0}

        self.frame = tk.Frame(tk_frame, padx=width // 4)
        self.frame.grid(row=0, column=8, rowspan=8, sticky="nsew")
        self.frame.update()
        self.height = self.frame.winfo_height()

        self.white_bar = tk.Canvas(
            self.frame,
            width=self.width,
            height=self.height,
            highlightthickness=0,
            bg=_BG_COLORS["none"]["light"],
        )
        self.white_bar.grid(row=0, column=0, sticky="nsew")

        self.black_bar = tk.Canvas(
            self.frame,
            width=self.width,
            height=self.height // 2,
            highlightthickness=0,
            bg=_BG_COLORS["none"]["dark"],
        )
        self.black_bar.grid(row=0, column=0, sticky="new")

        self.frame.update()

        fsize = int(0.2 * self.width)
        self.black_eval = self.black_bar.create_text(
            int(0.08 * self.width),
            int(0.08 * self.width),
            font=Font(family="Roboto", size=fsize, weight="bold"),
            fill=_PIECE_COLORS["light"],
            anchor="nw",
            text="Test",
        )
        self.white_eval = self.white_bar.create_text(
            int(0.08 * self.width),
            self.height - int(0.08 * self.width),
            font=Font(family="Roboto", size=fsize, weight="bold"),
            fill=_PIECE_COLORS["dark"],
            anchor="sw",
            text="Test",
        )

    def update_eval(self, evaluation):
        self.evaluation = evaluation
        if evaluation["type"] == "cp":
            eval_f = evaluation["value"]
            self.black_bar.configure(height=int(self.height * (0.5 - eval_f)))
            self.white_bar.configure(height=int(self.height * (0.5 - eval_f)))
            if eval_f > 0.1:
                # self.white_bar.
                pass
            elif eval_f < 0.1:
                pass
            else:
                pass

        else:
            # evaluation[type] == "mate"
            pass


class GameUI:

    def __init__(self, parent: tk.Frame):
        self.parent = parent
        self.parent.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)

        self.padding_frame = tk.Frame(parent, background="bisque")
        self.padding_frame.grid(row=0, column=0, sticky="nsew")
        self.padding_frame.rowconfigure(0, weight=1)
        self.padding_frame.columnconfigure(0, weight=1)
        self.padding_frame.bind("<Configure>", self.enforce_aspect_ratio)

        self.content_frame = tk.Frame(self.padding_frame, highlightthickness=0)
        self.content_frame.grid(row=0, column=0, sticky="nsew")
        self.content_frame.rowconfigure(0, weight=1)
        self.content_frame.columnconfigure(0, weight=1)

        self.board = ChessBoard(self)
        self.white_selector = PromotionSelector(self, (0, 1), True, False)
        self.black_selector = PromotionSelector(self, (8, 7), False, False)

    def enforce_aspect_ratio(self, event: tk.Event):
        """Enforce the correct aspect ration of the chess board, i.e. 1:1"""

        desired_size = min(event.width, event.height)

        # place the window, giving it an explicit size
        self.content_frame.place(
            in_=self.padding_frame, x=0, y=0, width=desired_size, height=desired_size
        )

        self.white_selector.resize(desired_size)
        self.black_selector.resize(desired_size)


class PromotionSelector:
    """This class implement the GUI element for selecting a piece for
    promotion
    """

    def __init__(
        self,
        gui: GameUI,
        position: tuple[int],
        color_is_white: bool = True,
        visible: bool = False,
    ):

        self.gui = gui
        self.position = position
        self.visible = visible
        self.callback = None

        self.options_frame = tk.Frame(self.gui.content_frame)
        self.cancel_button = tk.Canvas(self.gui.content_frame)

        self.resize(self.gui.content_frame.winfo_height())

        self.options = []
        self.options_frame.columnconfigure(0, weight=1)

        pieces = "QRBN" if color_is_white else "nbrq"
        for i, p in enumerate(pieces):
            self.options_frame.rowconfigure(i, weight=2)
            self.options.append(
                PieceContainer(
                    self.options_frame,
                    bg="red" if color_is_white else "blue",
                    highlightthickness=0,
                )
            )
            self.options[i].grid(row=i, column=0, sticky="nsew")
            self.options[i].place_piece(Stockfish.Piece(p))
            self.options[i].bind("<Button-1>", self.select)

        self.cancel_button.bind("<Button-1>", self.hide)

    def select(self, event):
        self.callback(event.widget.piece.short_name)
        self.hide()

    def resize(self, board_size):
        # place the window, giving it an explicit size
        if self.visible:
            width = (board_size + 7) // 8
            height = (board_size + 1) // 2

            posx = int((board_size * self.position[1] + 7) / 8)
            if self.position[0] < 4:
                options_posy = 0
                button_posy = height
            else:
                options_posy = board_size - height
                button_posy = board_size - width // 2 - height

            print(button_posy, options_posy, self.position[0])

            self.options_frame.place(
                in_=self.gui.content_frame,
                x=posx,
                y=options_posy,
                width=width,
                height=height,
            )
            self.cancel_button.place(
                in_=self.gui.content_frame,
                x=posx,
                y=button_posy,
                width=width,
                height=width // 2,
            )
            self.cross_svg = tksvg.SvgImage(
                data=Path("chessgui/icons/Cross.svg").read_text(),
                scaletoheight=max(1, width),
            )
            self.cancel_button.create_image(
                width // 2, width // 4, image=self.cross_svg
            )

    def hide(self, *args, **kwargs):
        if self.visible:
            self.visible = False
            self.callback = None
            self.options_frame.place_forget()
            self.cancel_button.place_forget()

    def show(self):
        self.visible = True
        self.resize(self.gui.content_frame.winfo_width())

    def show_at(self, position, callback):
        self.position = position
        self.callback = callback
        self.show()


class ChessBoard:
    """This class implements a chess board as a GUI element"""

    # TODO : move to GameState object
    white_active: bool = True
    castling: list[list[bool]] = [[False, False]] * 2
    engine: Stockfish = Stockfish(path=_stockfish_exe)
    selected_square: Square | None = None
    last_move: list[Square | None] = [None, None]
    pieces: list[ChessPiece] = []

    def __init__(self, gui: GameUI):
        self.gui = gui

        self.board_frame = tk.Frame(gui.content_frame, highlightthickness=0)
        self.board_frame.grid(row=0, column=0, sticky="nsew")

        self.squares = list(Square(self.board_frame, i // 8, i % 8) for i in range(64))
        for i in range(8):
            self.board_frame.rowconfigure(i, weight=1)
            self.board_frame.columnconfigure(i, weight=1)
            for j in range(8):
                self[i, j].bind("<Button-1>", self.on_click)

        self.load_fen_string(_STARTING_POS)
        print(self.engine.get_top_moves(3))

        # self.eval_bar = EvalBar(self.frame, width=self.square_size)

    def __getitem__(self, key):
        return self.squares[key[0] * 8 + key[1]]

    def __setitem__(self, key, val):
        self.squares[key[0] * 8 + key[1]] = val

    def load_fen_string(self, fen_str: str):
        """Load position froma FEN string"""

        self.engine.set_fen_position(fen_str)
        for i in range(8):
            for j in range(8):
                a_ind = "abcdefgh"[j] + str(8 - i)
                piece_name = self.engine.get_what_is_on_square(a_ind)
                if piece_name is not None:
                    self[i, j].place_piece(piece_name)
                elif self[i, j].piece is not None:
                    self[i, j].remove_piece()

    def on_click(self, event):
        """Callback event clicks on a give square"""
        if self.selected_square is None:
            self.toggle_hl_moves(event.widget)
        else:
            self.move_piece(self.selected_square, event.widget)

    def check_move_type(self, move_str):
        """Returns whether at move is possible and what type of move it is:
        capture, castling, normal
        """

        # Try to make a move, if the position doesn't change the move was invalid
        old_fen = self.engine.get_fen_position()
        self.engine.make_moves_from_current_position([move_str])
        new_fen = self.engine.get_fen_position()

        # Get best move and eval at depth 1 to detect game-ending moves and result
        depth = int(self.engine.depth)
        self.engine.set_depth(1)
        game_end = self.engine.get_best_move() is None
        evaluation = self.engine.get_evaluation()

        # Reset engine
        self.engine.set_fen_position(old_fen)
        self.engine.set_depth(depth)

        move = Move()
        if old_fen == new_fen:
            if move_str[-1].isdigit() and self.check_move_type(move_str + "q").is_legal:
                move.is_promotion_candidate = True
            else:
                move.is_legal = False

        # Check if game has ended
        if game_end:
            if evaluation["type"] == "cp":
                move.delivers_stale_mate = True
            else:
                move.delivers_mate = True

        # Check if move is a capture
        if self.engine.will_move_be_a_capture(move_str) != Stockfish.Capture.NO_CAPTURE:
            move.is_capture = True
        else:
            # Check if move is castling move
            active_color = old_fen.split(" ")[1]
            rank = 1 if active_color == "w" else 8
            s2 = new_fen.split(" ", maxsplit=1)[0].split("/")[8 - rank]
            s1 = old_fen.split(" ", maxsplit=1)[0].split("/")[8 - rank]
            if sum(1 for a, b in zip(s1, s2) if a != b) > 1:
                move.is_castling = True

        return move

    def move_piece(self, origin, destination, promote_to=""):
        """Move a piece from one square to another"""
        move_str = origin.to_algebraic()
        move_str += destination.to_algebraic()
        move_str += promote_to
        print(move_str)
        move = self.check_move_type(move_str)
        if move.is_legal:
            self.engine.make_moves_from_current_position([move_str])
            self.toggle_hl_moves(origin)

            if move.is_promotion_candidate:
                if self.white_active:
                    self.gui.white_selector.show_at(
                        destination.to_index(),
                        callback=partial(self.move_piece, origin, destination),
                    )
                else:
                    self.gui.black_selector.show_at(
                        destination.to_index(),
                        callback=partial(self.move_piece, origin, destination),
                    )
            else:
                self.load_fen_string(self.engine.get_fen_position())
        else:
            self.toggle_hl_moves(origin)
            self.toggle_hl_moves(destination)

    def toggle_hl_moves(self, square: Square):
        """Highlight all legal moves"""

        # Check if clicked square is occupied by a piece
        if square.piece is None:
            return
        # Check if selected piece belong to active color
        active_color = self.engine.get_fen_position().split(" ")[1]
        print(active_color)
        if square.piece.color == active_color:
            if self.selected_square is None:
                square.toggle_selected()
                self.selected_square = square
            else:
                self.selected_square.toggle_selected()
                if square is self.selected_square:
                    self.selected_square = None
                else:
                    square.toggle_selected()
                    self.selected_square = square
