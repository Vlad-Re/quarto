import random

import pytest

from quarto.bot.random_bot import random_bot
from quarto.model import (
    ALL_PIECES,
    LINES,
    Action,
    Cell,
    Draw,
    GameState,
    IllegalMove,
    Piece,
    Side,
    Win,
    check_invariants,
    give,
    new_game,
    outcome,
    place,
    shares_attribute,
)


def pieces(*values: int) -> tuple[Piece, ...]:
    return tuple(Piece(v) for v in values)


def test_new_game_starts_with_second_side_placing() -> None:
    state = new_game(Piece(0b0101))
    assert state.current == Piece(0b0101)
    assert state.side is Side.SECOND
    assert state.action is Action.PLACE
    assert len(state.available) == 15
    assert all(cell is None for cell in state.board)
    check_invariants(state)


def test_place_then_give_switches_side() -> None:
    placed = place(new_game(Piece(0)), Cell(5))
    assert placed.board[5] == Piece(0)
    assert placed.side is Side.SECOND and placed.action is Action.GIVE
    given = give(placed, Piece(7))
    assert given.side is Side.FIRST and given.action is Action.PLACE
    assert given.current == Piece(7) and Piece(7) not in given.available
    check_invariants(given)


def test_illegal_moves_raise() -> None:
    state = new_game(Piece(0))
    with pytest.raises(IllegalMove):
        give(state, Piece(1))  # wrong step
    placed = place(state, Cell(0))
    with pytest.raises(IllegalMove):
        place(placed, Cell(1))  # wrong step
    with pytest.raises(IllegalMove):
        give(placed, Piece(0))  # already on board
    given = give(placed, Piece(1))
    with pytest.raises(IllegalMove):
        place(given, Cell(0))  # occupied


def test_shares_attribute() -> None:
    assert shares_attribute(pieces(0b0001, 0b0011, 0b0101, 0b0111))  # common 1 in bit 0
    assert shares_attribute(pieces(0b0000, 0b0001, 0b0010, 0b0011))  # common 0 in bits 2, 3
    assert not shares_attribute(pieces(0b0000, 0b1111, 0b0101, 0b1010))


def test_lines_are_ten_distinct() -> None:
    assert len(LINES) == 10
    assert len(set(LINES)) == 10


def test_win_goes_to_the_side_that_placed() -> None:
    # SECOND fills row 0 with pieces sharing bit 0
    board = (Piece(0b0001), Piece(0b0011), Piece(0b0101), None) + (None,) * 12
    state = GameState(
        board=board,
        available=ALL_PIECES - {Piece(0b0001), Piece(0b0011), Piece(0b0101), Piece(0b0111)},
        current=Piece(0b0111),
        side=Side.SECOND,
        action=Action.PLACE,
    )
    result = outcome(place(state, Cell(3)))
    assert result == Win(side=Side.SECOND, line=LINES[0])


def test_game_over_blocks_moves() -> None:
    board = (Piece(0b0001), Piece(0b0011), Piece(0b0101), None) + (None,) * 12
    state = GameState(
        board=board,
        available=ALL_PIECES - {Piece(0b0001), Piece(0b0011), Piece(0b0101), Piece(0b0111)},
        current=Piece(0b0111),
        side=Side.SECOND,
        action=Action.PLACE,
    )
    won = place(state, Cell(3))
    with pytest.raises(IllegalMove):
        give(won, Piece(0b1000))


def test_random_games_keep_invariants_and_end() -> None:
    rng = random.Random(42)
    for _ in range(200):
        state = new_game(Piece(rng.randrange(16)))
        for _ in range(16):
            move = random_bot(state)
            state = place(state, move.cell)
            check_invariants(state)
            if outcome(state) is not None:
                break
            assert move.piece is not None
            state = give(state, move.piece)
            check_invariants(state)
        result = outcome(state)
        assert isinstance(result, Win | Draw)
