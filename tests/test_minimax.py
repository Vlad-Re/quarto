"""Alpha-beta must pick exactly the same move as plain minimax."""

import random

import pytest

from quarto.bot.evaluation import evaluate
from quarto.bot.minimax import minimax_move
from quarto.model import (
    Action,
    GameState,
    Move,
    Piece,
    Side,
    Win,
    empty_cells,
    give,
    new_game,
    outcome,
    place,
    sorted_available,
)


def plain_move(state: GameState, depth: int) -> Move:
    # old minimax without pruning, reference only
    me = state.side
    for cell in empty_cells(state):
        if isinstance(outcome(place(state, cell)), Win):
            return Move(cell=cell, piece=None)
    best_move: Move | None = None
    best_score = 0
    for cell in empty_cells(state):
        placed = place(state, cell)
        if outcome(placed) is not None:
            return Move(cell=cell, piece=None)
        for piece in sorted_available(placed):
            score = plain_search(give(placed, piece), depth - 2, me)
            if best_move is None or score > best_score:
                best_move = Move(cell=cell, piece=piece)
                best_score = score
    assert best_move is not None
    return best_move


def plain_search(state: GameState, depth: int, me: Side) -> int:
    if depth <= 0 or outcome(state) is not None:
        return evaluate(state, me)
    children = (
        [place(state, cell) for cell in empty_cells(state)]
        if state.action is Action.PLACE
        else [give(state, piece) for piece in sorted_available(state)]
    )
    scores = [plain_search(child, depth - 1, me) for child in children]
    return max(scores) if state.side is me else min(scores)


def random_position(seed: int, placed_count: int) -> GameState:
    # bot's PLACE step after `placed_count` random placements, game not over
    rng = random.Random(seed)
    state = new_game(Piece(rng.randrange(16)))
    while True:
        cell = rng.choice(empty_cells(state))
        placed = place(state, cell)
        if outcome(placed) is not None:
            return random_position(seed + 1000, placed_count)
        state = give(placed, rng.choice(sorted_available(placed)))
        if 16 - len(empty_cells(state)) >= placed_count:
            return state


@pytest.mark.parametrize("seed", range(20))
@pytest.mark.parametrize("placed_count", [6, 8, 10])
def test_same_move_as_plain_minimax(seed: int, placed_count: int) -> None:
    state = random_position(seed, placed_count)
    assert minimax_move(state, 4) == plain_move(state, 4)
