""" Stock fish interface """
from pathlib import Path

from stockfish import Stockfish

stockfish_root = Path("/Users/Juijan/stockfish")
stockfish_exe = stockfish_root / "stockfish-windows-x86-64-avx2.exe"
stockfish = Stockfish(path=stockfish_exe)
print(stockfish.get_best_move())
