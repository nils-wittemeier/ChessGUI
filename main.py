"""A GUI for tracking multiple games"""

import tkinter as tk
from tkinter import ttk
from tkinter.font import Font

from chessgui import GameUI


class ChessGUI:
    """A GUI for tracking multiple games"""

    tk_gui = None
    tk_tab_control = None
    boards = {}

    def __init__(self):
        self.tk_gui = tk.Tk()

        defaultFont = Font(root=self.tk_gui, name="TkDefaultFont", exists=True)
        defaultFont.configure(family="Roboto")
        self.tk_gui.title("Chess Tracker")
        self.tk_gui.geometry("1200x1000")

        self.tk_tab_control = ttk.Notebook(self.tk_gui)

        add_game_button = ttk.Button(self.tk_gui, text="+", command=self.add_game_tab)

        add_game_button.pack(side="top")

        self.tk_tab_control.pack(expand=1, fill="both", side="bottom")

        self.add_game_tab()

    def add_game_tab(self):
        """Create a new game tab"""

        idx = len(self.tk_tab_control.children)
        tab = ttk.Frame(self.tk_tab_control, padding=(10, 10, 0, 0))
        tab.pack(expand=1, fill="both", side="bottom")
        self.tk_tab_control.add(tab, text=f"Game {idx}")
        self.boards[idx] = GameUI(tab)

    def mainloop(self):
        """Enter mainloop"""
        self.tk_gui.mainloop()


if __name__ == "__main__":
    gui = ChessGUI()
    gui.mainloop()
