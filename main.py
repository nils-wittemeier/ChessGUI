""" A GUI for tracking multiple games"""
from pathlib import Path
import tkinter as tk
from tkinter import ttk
import tksvg
import os
from functools import partial

from chessgui.chessboard import GameUI

# def enforce_aspect_ratio(pad_frame, content_frame, event):
#     '''Modify padding when window is resized.'''
#     # when the pad window resizes, fit the content into it,
#     # either by fixing the width or the height and then
#     # adjusting the height or width based on the aspect ratio.

#     width, height = pad_frame.winfo_width(), pad_frame.winfo_height()
#     width, height = event.width, event.height
#     if width > height:
#         desired_size = height
#     else:
#         desired_size = width

#     # place the window, giving it an explicit size
#     content_frame.place(in_=pad_frame, x=0, y=0, 
#         width=desired_size, height=desired_size)

#     print('Pad    ', pad_frame.winfo_height(), pad_frame.winfo_width())
#     print('Content', content_frame.winfo_height(),content_frame.winfo_width())
#     print('Desired', desired_size, desired_size)

class ChessGUI():
    """ A GUI for tracking multiple games"""

    tk_gui = None
    tk_tab_control = None
    boards = {}

    def __init__(self):
        self.tk_gui = tk.Tk()
        self.tk_gui.title("Chess Tracker")
        self.tk_gui.geometry("1200x1000")

        self.tk_tab_control = ttk.Notebook(self.tk_gui)

        add_game_button = ttk.Button(self.tk_gui, text="+", command=self.add_game_tab)

        add_game_button.pack(side="left")

        self.tk_tab_control.pack(expand=1, fill="both", side="bottom")

        # self.padding_frame = tk.Frame(self.tk_tab_control, background="bisque",width=200, height=200)
        # self.padding_frame.grid(row=0, column=0, sticky='nsew')

        # self.content_frame = tk.Frame(self.padding_frame, bg='green')
        # self.content_frame.grid(row=0, column=0, sticky='nsew')
        # for i in range(2):
        #     for j in range(2):
        #         test_canvas = tk.Canvas(self.content_frame)
        #         test_canvas.grid(row=i, column=j, sticky='nsew')
        #         test_canvas.configure(bg='red' if (i+j)%2==0 else 'blue')

        # for i in range(2):
        #     self.content_frame.rowconfigure(i, weight=1)
        #     self.content_frame.columnconfigure(i, weight=1)

        # # tk.Label(self.content_frame,text='content').pack()
        # self.padding_frame.bind('<Configure>', partial(enforce_aspect_ratio, self.padding_frame, self.content_frame))
        
        # self.tk_tab_control.rowconfigure(0, weight=1)
        # self.tk_tab_control.columnconfigure(0, weight=1)
        # self.padding_frame.rowconfigure(0, weight=1)
        # self.padding_frame.columnconfigure(0, weight=1)
        
        # self.tk_gui.update()
        # print(self.padding_frame.winfo_height(), self.padding_frame.winfo_width())
        # print(self.content_frame.winfo_height(), self.content_frame.winfo_width())

        self.add_game_tab()

    def add_game_tab(self):
        """ Create a new game tab"""

        idx = len(self.tk_tab_control.children)
        tab = ttk.Frame(self.tk_tab_control, padding=(10, 10, 0, 0))
        tab.pack(expand=1, fill="both", side="bottom")
        self.tk_tab_control.add(tab, text=f"Game {idx}")
        self.boards[idx] = GameUI(tab)

    def mainloop(self):
        """ Enter mainloop """
        self.tk_gui.mainloop()


if __name__ == "__main__":
    gui = ChessGUI()
    gui.mainloop()
