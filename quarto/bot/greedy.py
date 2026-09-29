"""Greedy bot: win now if possible, never hand over a winning piece."""

from quarto.bot.evaluation import evaluate
from quarto.model import (
    GameState,
    Move,
    Win,
    empty_cells,
    give,
    outcome,
    place,
    sorted_available,
)


def greedy_bot(state: GameState) -> Move:
    me = state.side

    # base: immediate win
    for cell in empty_cells(state):
        placed = place(state, cell)
        if _is_win(placed):
            return Move(cell=cell, piece=None)

    # best safe (cell, piece)
    best_move: Move | None = None
    best_score = 0
    fallback: Move | None = None
    for cell in empty_cells(state):
        placed = place(state, cell)
        if outcome(placed) is not None:  # draw TODO: refactor
            return Move(cell=cell, piece=None)
        for piece in sorted_available(placed):
            given = give(placed, piece)
            move = Move(cell=cell, piece=piece)
            if fallback is None:
                fallback = move
            if opponent_can_win(given):
                continue
            score = evaluate(given, me)
            if best_move is None or score > best_score:  # strict: first wins on ties
                best_move = move
                best_score = score

    if best_move is not None:
        return best_move
    assert fallback is not None, "bot called on a finished game"
    return fallback


def opponent_can_win(state: GameState) -> bool:
    # state: opponent's PLACE step
    return any(_is_win(place(state, cell)) for cell in empty_cells(state))


def _is_win(state: GameState) -> bool:
    return isinstance(outcome(state), Win)
