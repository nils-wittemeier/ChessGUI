from functools import partial
import tkinter as tk
from tkinter.font import Font

from ..files import get_icon
from .svg import SVGContainer
from ..game.tree import GameTree, GameTreeNode


class SecondSideBar:

    def __init__(self, parent: tk.Frame, move_tree: GameTree, goto_state_callback):
        self.parent = parent
        self.move_tree = move_tree
        self.goto_state_callback = goto_state_callback

        # Add control elements
        self.controls_canvas = tk.Canvas(self.parent, height=25, bg='#cccccc', highlightthickness=0)
        self.controls_canvas.pack(side=tk.BOTTOM, fill=tk.X, expand=False)
        #
        self.first_button = tk.Canvas(self.controls_canvas, height=25, bg='#cccccc', highlightthickness=0)
        self.first_button.grid(row=0, column=0, sticky=tk.NSEW)
        self.controls_canvas.columnconfigure(0, weight=1)
        self.first_svg = SVGContainer(get_icon('First'), self.first_button, posx=0, posy=0, scale=(1,0.8), centered=True)
        self.first_button.bind("<Button-1>", self.goto_first_pos)
        #
        self.prev_button = tk.Canvas(self.controls_canvas, height=25, bg='#cccccc', highlightthickness=0)
        self.prev_button.grid(row=0, column=1, sticky=tk.NSEW)
        self.controls_canvas.columnconfigure(1, weight=1)
        self.prev_svg = SVGContainer(get_icon('Prev'), self.prev_button, posx=0, posy=0, scale=(1,0.8), centered=True)
        self.prev_button.bind("<Button-1>", self.goto_prev_pos)
        #
        self.next_button = tk.Canvas(self.controls_canvas, height=25, bg='#cccccc', highlightthickness=0)
        self.next_button.grid(row=0, column=2, sticky=tk.NSEW)
        self.controls_canvas.columnconfigure(2, weight=1)
        self.next_svg = SVGContainer(get_icon('Next'), self.next_button, posx=0, posy=0, scale=(1,0.8), centered=True)
        self.next_button.bind("<Button-1>", self.goto_next_pos)
        #
        self.last_button = tk.Canvas(self.controls_canvas, height=25, bg='#cccccc', highlightthickness=0)
        self.last_button.grid(row=0, column=3, sticky=tk.NSEW)
        self.controls_canvas.columnconfigure(3, weight=1)
        self.last_svg = SVGContainer(get_icon('Last'), self.last_button, posx=0, posy=0, scale=(1,0.8), centered=True)
        self.last_button.bind("<Button-1>", self.goto_last_pos)

        # Create a canvas object and a vertical scrollbar for scrolling it.
        self.vscrollbar = tk.Scrollbar(self.parent, orient=tk.VERTICAL)
        self.vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=False)
        self.moves_canvas = tk.Canvas(
            self.parent,
            highlightthickness=0,
            width=200,
            height=300,
            yscrollcommand=self.vscrollbar.set,
        )
        self.moves_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        self.vscrollbar.config(command=self.moves_canvas.yview)
        
        # Reset the view
        self.moves_canvas.xview_moveto(0)
        self.moves_canvas.yview_moveto(0)

        # Create frames inside the canvas which will be scrolled with it.
        self.num_col = tk.Frame(self.moves_canvas)
        self.white_col = tk.Frame(self.moves_canvas)
        self.black_col = tk.Frame(self.moves_canvas)
        self.num_id = self.moves_canvas.create_window(10, 10, window=self.num_col, anchor=tk.NW)
        self.white_id = self.moves_canvas.create_window(10, 10, window=self.white_col, anchor=tk.NW)
        self.black_id = self.moves_canvas.create_window(10, 10, window=self.black_col, anchor=tk.NW)

        self.parent.bind("<Configure>", self._configure_parent, add=True)
        self.num_col.bind("<Configure>", self._configure_interior)


        self.font = Font()

        self.half_move = 0

    def reload_moves(self):

        self.half_move = 0
        node = self.move_tree.root
        for col1, col2, col3 in zip(
            self.num_col.winfo_children(),
            self.white_col.winfo_children(),
            self.black_col.winfo_children(),
        ):
            col1.destroy()
            col2.destroy()
            col3.destroy()
        while True:
            try:
                node = list(node.children.values())[0]
            except IndexError:
                break
            self.half_move += 1
            if self.half_move % 2 == 1:
                num_col = tk.Label(
                    self.num_col, text=f"{self.half_move//2+1:d}", font=self.font, bg="#dddddd"
                )
                num_col.pack(expand=True, fill=tk.X)

                white_move = tk.Label(
                    self.white_col, text=node.tag, font=self.font, justify="left", bg="#ffffff"
                )
                white_move.pack(expand=True, fill=tk.X)
                white_move.bind("<Button-1>", partial(self.select, node, self.half_move))

                black_move = tk.Label(
                    self.black_col, text="", font=self.font, justify="left", bg="#ffffff"
                )
                black_move.pack(expand=True, fill=tk.X)
            else:
                black_move.configure(text=node.tag)
                black_move.bind("<Button-1>", partial(self.select, node, self.half_move))

        if self.half_move % 2 == 1:
            white_move.configure(bg="lightblue")
        else:
            black_move.configure(bg="lightblue")

    def make_move(self, node: GameTreeNode):
        # Add move to tree
        # Add move to UI
        self.half_move += 1
        if self.half_move % 2 == 1:
            num_col = tk.Label(
                self.num_col, text=f"{self.half_move//2+1:d}", font=self.font, bg="#dddddd"
            )
            num_col.pack(expand=True, fill=tk.X)

            white_move = tk.Label(
                self.white_col, text=node.tag, font=self.font, justify="left", bg="lightblue"
            )
            white_move.pack(expand=True, fill=tk.X)
            white_move.bind("<Button-1>", partial(self.select, node, self.half_move))

            try:
                black_move = list(self.black_col.children.values())[-1]
                black_move.configure(bg="#ffffff")
            except IndexError:
                pass

            black_move = tk.Label(
                self.black_col, text="", font=self.font, justify="left", bg="#ffffff"
            )
            black_move.pack(expand=True, fill=tk.X)
        else:
            white_move = list(self.white_col.children.values())[-1]
            white_move.configure(bg="#ffffff")
            black_move = list(self.black_col.children.values())[-1]
            black_move.configure(text=node.tag, bg="lightblue")
            black_move.bind("<Button-1>", partial(self.select, node, self.half_move))

    def _configure_interior(self, event):
        # Update the scrollbars to match the size of the inner frame.
        size = (self.num_col.winfo_reqwidth(), self.num_col.winfo_reqheight())
        self.moves_canvas.config(scrollregion=(0, 0, size[0], size[1]))

    def _configure_parent(self, event):
        interior_width = min(400, event.width - self.vscrollbar.winfo_reqwidth())
        self.moves_canvas.configure(width=interior_width)
        self.moves_canvas.moveto(self.num_id, 10, 10)
        self.moves_canvas.itemconfigure(self.num_id, width=int(interior_width / 5))
        self.moves_canvas.moveto(self.white_id, 10 + int(interior_width / 5), 10)
        self.moves_canvas.itemconfigure(self.white_id, width=int(2 * interior_width / 5))
        self.moves_canvas.moveto(self.black_id, 10 + 3 * int(interior_width / 5), 10)
        self.moves_canvas.itemconfigure(self.black_id, width=int(2 * interior_width / 5))

    def select(self, node: GameTreeNode, half_move : int, event: tk.Event):
        for w in self.white_col.children.values():
            w.configure(bg="#ffffff")
        for w in self.black_col.children.values():
            w.configure(bg="#ffffff")

        self.half_move = half_move
        event.widget.configure(bg="lightblue")
        self.goto_state_callback(node)

    def goto_first_pos(self, event):
        for w in self.white_col.children.values():
            w.configure(bg="#ffffff")
        for w in self.black_col.children.values():
            w.configure(bg="#ffffff")

        self.half_move = 0
        self.goto_state_callback(self.move_tree.root)
    
    def goto_prev_pos(self, event):
        if self.move_tree.pointer.parent is not None:
            for w in self.white_col.children.values():
                w.configure(bg="#ffffff")
            for w in self.black_col.children.values():
                w.configure(bg="#ffffff")

            self.half_move -= 1
            if self.half_move % 2 == 1:
                list(self.white_col.children.values())[self.half_move//2].configure(bg="lightblue")
            else:
                list(self.black_col.children.values())[self.half_move//2-1].configure(bg="lightblue")
            self.goto_state_callback(self.move_tree.pointer.parent)
    
    def goto_next_pos(self, event):
        if len(self.move_tree.pointer.children) > 0:
            for w in self.white_col.children.values():
                w.configure(bg="#ffffff")
            for w in self.black_col.children.values():
                w.configure(bg="#ffffff")

            self.half_move += 1
            if self.half_move % 2 == 1:
                list(self.white_col.children.values())[self.half_move//2].configure(bg="lightblue")
            else:
                list(self.black_col.children.values())[self.half_move//2-1].configure(bg="lightblue")
            self.goto_state_callback(list(self.move_tree.pointer.children.values())[0])
    
    def goto_last_pos(self, event):
        for w in self.white_col.children.values():
            w.configure(bg="#ffffff")
        for w in self.black_col.children.values():
            w.configure(bg="#ffffff")

        self.half_move = self.move_tree.tip.depth
        if self.half_move % 2 == 1:
            list(self.white_col.children.values())[self.half_move//2].configure(bg="lightblue")
        else:
            list(self.black_col.children.values())[self.half_move//2-1].configure(bg="lightblue")
        self.goto_state_callback(self.move_tree.tip)
