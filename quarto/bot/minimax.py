"""Minimax with alpha-beta pruning. Depth unit = half-action (one place or one give)."""

from collections.abc import Iterator

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

INF = 10**9


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
    best_score = -INF
    for cell in empty_cells(state):
        placed = place(state, cell)
        if outcome(placed) is not None:  # draw
            return Move(cell=cell, piece=None)
        for piece in sorted_available(placed):
            given = give(placed, piece)
            # best_score as alpha
            score = search(given, depth - 2, best_score, INF, me)
            if best_move is None or score > best_score:
                best_move = Move(cell=cell, piece=piece)
                best_score = score

    assert best_move is not None, "bot called on a finished game"
    return best_move


def search(state: GameState, depth: int, alpha: int, beta: int, me: Side) -> int:
    # side maximizes -> max, max, min, min
    if depth <= 0 or outcome(state) is not None:
        return evaluate(state, me)
    maximizing = state.side is me
    for child in _children(state):
        score = search(child, depth - 1, alpha, beta, me)
        if maximizing:
            alpha = max(alpha, score)
        else:
            beta = min(beta, score)
        if alpha >= beta:
            break  # cutoff
    return alpha if maximizing else beta


def _children(state: GameState) -> Iterator[GameState]:
    # lazy: after a cutoff never built
    if state.action is Action.PLACE:
        return (place(state, cell) for cell in empty_cells(state))
    return (give(state, piece) for piece in sorted_available(state))
