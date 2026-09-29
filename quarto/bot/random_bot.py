"""Random bot"""

import random

from quarto.model import GameState, Move, empty_cells, outcome, place, sorted_available

_rng = random.Random()


def random_bot(state: GameState) -> Move:
    cell = _rng.choice(empty_cells(state))
    placed = place(state, cell)
    if outcome(placed) is not None:
        return Move(cell=cell, piece=None)
    return Move(cell=cell, piece=_rng.choice(sorted_available(placed)))
