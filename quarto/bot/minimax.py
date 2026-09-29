"""Draft minimax. Depth unit = half-action (one place or one give). No pruning yet."""

from quarto.bot.evaluation import evaluate
from quarto.config import MINIMAX_DEPTH
from quarto.model import (
    Action,
    GameState,
    Move,
    Side,
    Win,
    empty_cells,
    give,
    outcome,
    place,
    sorted_available,
)


def minimax_bot(state: GameState) -> Move:
    return minimax_move(state, MINIMAX_DEPTH)


def minimax_move(state: GameState, depth: int) -> Move:
    me = state.side

    # base: immediate win
    for cell in empty_cells(state):
        placed = place(state, cell)
        if isinstance(outcome(placed), Win):
            return Move(cell=cell, piece=None)

    best_move: Move | None = None
    best_score = 0
    for cell in empty_cells(state):
        placed = place(state, cell)
        if outcome(placed) is not None:  # draw
            return Move(cell=cell, piece=None)
        for piece in sorted_available(placed):
            given = give(placed, piece)
            score = search(given, depth - 2, me)
            if best_move is None or score > best_score:  # first wins on ties
                best_move = Move(cell=cell, piece=piece)
                best_score = score

    assert best_move is not None, "bot called on a finished game"
    return best_move


def search(state: GameState, depth: int, me: Side) -> int:
    # act side maximizes -> max, max, min, min
    if depth <= 0 or outcome(state) is not None:
        return evaluate(state, me)
    children = (
        [place(state, cell) for cell in empty_cells(state)]
        if state.action is Action.PLACE
        else [give(state, piece) for piece in sorted_available(state)]
    )
    scores = [search(child, depth - 1, me) for child in children]
    return max(scores) if state.side is me else min(scores)
