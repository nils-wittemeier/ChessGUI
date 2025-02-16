from .piece import ChessPiece


class Move:

    def __init__(
        self,
        piece: ChessPiece,
        origin: tuple[int],
        target: tuple[int],
        piece_on_target: ChessPiece,
        is_promotion: bool = False,
    ) -> None:
        self._piece = piece
        self._origin = origin
        self._target = target
        self._piece_on_target = piece_on_target

    def __repr__(self):
        s = f"<{self.__class__.__name__}: {self._piece.name} from {self._origin} to {self._target}"
        for attr in dir(self):
            if attr.startswith("is") and getattr(self, attr):
                s += f", {attr}"
        return s + ">"

    def __eq__(self, value):
        return (
            self.piece == value.piece
            and self.origin == value.origin
            and self.target == value.target
            and self._piece_on_target == value._piece_on_target
        )

    @property
    def piece(self):
        return self._piece

    @property
    def origin(self):
        return self._origin

    @property
    def target(self):
        return self._target

    @property
    def is_capture(self):
        return self._piece_on_target is not None

    @property
    def is_promotion(self):
        is_pawn = self._piece.name == "Pawn"
        reached_end = (
            self._target[1] == 0 if self._piece.is_white else self._target[1] == 7
        )
        return is_pawn and reached_end
