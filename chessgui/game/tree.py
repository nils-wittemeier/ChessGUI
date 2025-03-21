from typing import Optional, Self, Iterable

from .moves import Move
from .state import GameState


# Node:
#
#   previous : parent node
#   state
#   { next_moves : child_node }
#
#
class GameTreeNode:
    def __init__(
        self,
        depth: int,
        parent: Optional[Self] = None,
        move: Optional[Move] = None,
        tag: Optional[str] = "",
        fen: Optional[str] = "",
    ):
        self.parent = parent
        self.depth = depth
        self.value = move
        self.tag = tag
        self.fen = fen
        self.children = {}

    def add_child(self, move: Move, tag: str, fen: str):
        """Add a child node resulting from applying an action."""
        if move in self.children:
            return self.children[move]  # Avoid duplicate states under the same parent

        child_node = GameTreeNode(parent=self, depth=self.depth+1, move=move, tag=tag, fen=fen)
        self.children[move] = child_node
        return child_node

    def get_path(self):
        """Reconstructs the path from the root to this node."""
        path = []
        node = self
        while node.parent is not None:
            path.append(node.value)
            node = node.parent
        path.reverse()
        return path

    def __repr__(self):
        return f"GameTreeNode(value={self.value}, children={list(self.children.keys())})"


class GameTree:
    def __init__(self, root_state: GameState):
        """Initialize a tree with a root state."""
        self.root_state = root_state
        self.root = GameTreeNode(0, fen=root_state.to_fen_string())
        self.pointer = self.root
        self.tip = self.root

    def make_move(self, move: Move, tag: str, fen: str):
        self.pointer = self.pointer.add_child(move, tag, fen)
        if len(self.pointer.children) == 0:
            self.tip = self.pointer

    def undo_move(self):
        self.pointer = self.pointer.parent

    def get_node(self, moves: Iterable[Move]):
        """Retrieve a node by state, if it exists."""
        node = self.root
        for move in moves:
            node = node.children[move]
        return node

    def get_state(self, node: Optional[Self] = None):
        _node = node if node is not None else self.pointer
        path = _node.get_path()
        state = self.root_state
        for move in path:
            state = state.make_move(move)

        return state

    def __repr__(self):
        return f"Tree(root={self.root})"

    def print_tree(self):
        """Perform a depth-first traversal and print the tree structure."""

        def dfs(node: GameTree, depth: Optional[int] = 0):
            indent = "  " * depth
            move_str = f" (Move: {node.move})" if node.move is not None else ""
            print(f"{indent}- {move_str}")
            for _, child in node.children.items():
                dfs(child, depth + 1)

        dfs(self.root)
