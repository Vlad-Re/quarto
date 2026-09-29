"""Acceptance criterion: win when possible, never give a winning piece if a safe one exists."""

import random

import pytest

from quarto.bot import Bot
from quarto.bot.greedy import greedy_bot, opponent_can_win
from quarto.bot.minimax import minimax_bot
from quarto.bot.random_bot import random_bot
from quarto.model import (
    Draw,
    GameState,
    Piece,
    Win,
    empty_cells,
    give,
    new_game,
    outcome,
    place,
    sorted_available,
)

BOTS = [greedy_bot, minimax_bot]


def random_positions(count: int, seed: int) -> list[GameState]:
    # bot's PLACE step positions from random games, only unfinished ones
    rng = random.Random(seed)
    positions: list[GameState] = []
    while len(positions) < count:
        state = new_game(Piece(rng.randrange(16)))
        steps = rng.randrange(2, 12)
        for _ in range(steps):
            move = random_bot(state)
            placed = place(state, move.cell)
            if outcome(placed) is not None or move.piece is None:
                break
            state = give(placed, move.piece)
        else:
            positions.append(state)
    return positions


def can_win_now(state: GameState) -> bool:
    return any(isinstance(outcome(place(state, c)), Win) for c in empty_cells(state))


def safe_move_exists(state: GameState) -> bool:
    for cell in empty_cells(state):
        placed = place(state, cell)
        if isinstance(outcome(placed), Draw):
            return True
        for piece in sorted_available(placed):
            if not opponent_can_win(give(placed, piece)):
                return True
    return False


@pytest.mark.parametrize("bot", BOTS)
def test_bot_wins_when_possible(bot: Bot) -> None:
    for state in random_positions(40, seed=1):
        if can_win_now(state):
            move = bot(state)
            assert isinstance(outcome(place(state, move.cell)), Win)


@pytest.mark.parametrize("bot", BOTS)
def test_bot_never_gives_winning_piece_when_safe_one_exists(bot: Bot) -> None:
    for state in random_positions(40, seed=2):
        if can_win_now(state) or not safe_move_exists(state):
            continue
        move = bot(state)
        placed = place(state, move.cell)
        if outcome(placed) is not None:
            continue
        assert move.piece is not None
        assert not opponent_can_win(give(placed, move.piece))


@pytest.mark.parametrize("bot", BOTS)
def test_bot_is_reproducible(bot: Bot) -> None:
    for state in random_positions(10, seed=3):
        assert bot(state) == bot(state)
