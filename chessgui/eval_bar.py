""" This module implements the graphical interface for an evaluation bar"""
import tkinter as tk
from tkinter.font import Font

from .colors import _COLORS

_PIECE_COLORS = {"light": "#FFFFFF", "dark": "#272932"}

class EvalBar:
    """ The graphical interface for an evaluation bar"""
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
            bg=_COLORS["evalbar"]["background"]["light"],
        )
        self.white_bar.grid(row=0, column=0, sticky="nsew")

        self.black_bar = tk.Canvas(
            self.frame,
            width=self.width,
            height=self.height // 2,
            highlightthickness=0,
            bg=_COLORS["evalbar"]["background"]["dark"],
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

    def update_eval(self, evaluation: dict) -> None:
        """ Update evaluation displayed'
        
        This function changes the height of the bars and alters the text displayed
        withing
        
        Args:
            evaluation (dict) : A dictionary of the current advantage with 
                                "type" as "cp" (centipawns) or "mate" (checkmate in).

        """
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
