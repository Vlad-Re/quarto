"""Game model: immutable state + pure rule functions"""

from dataclasses import dataclass, replace
from enum import Enum, auto
from typing import NewType

# 4 bits: shape, color, size, hole
Piece = NewType("Piece", int)
# cell 0..15, cell = row * 4 + col
Cell = NewType("Cell", int)

SHAPE = 0b0001  # circle/square
COLOR = 0b0010  # white/black
SIZE = 0b0100  # small/big
HOLE = 0b1000  # solid/hollow
ALL_BITS = 0b1111

ALL_PIECES: frozenset[Piece] = frozenset(Piece(i) for i in range(16))
ALL_CELLS: tuple[Cell, ...] = tuple(Cell(i) for i in range(16))

type Board = tuple[Piece | None, ...]
type Line = tuple[Cell, Cell, Cell, Cell]


def _line(a: int, b: int, c: int, d: int) -> Line:
    return (Cell(a), Cell(b), Cell(c), Cell(d))


LINES: tuple[Line, ...] = (
    # rows
    _line(0, 1, 2, 3),
    _line(4, 5, 6, 7),
    _line(8, 9, 10, 11),
    _line(12, 13, 14, 15),
    # columns
    _line(0, 4, 8, 12),
    _line(1, 5, 9, 13),
    _line(2, 6, 10, 14),
    _line(3, 7, 11, 15),
    # diagonals
    _line(0, 5, 10, 15),
    _line(3, 6, 9, 12),
)


class Side(Enum):
    # FIRST chooses piece, SECOND places first
    FIRST = auto()
    SECOND = auto()

    def other(self) -> Side:
        return Side.SECOND if self is Side.FIRST else Side.FIRST


class Action(Enum):
    PLACE = auto()
    GIVE = auto()


@dataclass(frozen=True, slots=True)
class GameState:
    board: Board
    available: frozenset[Piece]
    current: Piece | None
    side: Side
    action: Action


@dataclass(frozen=True, slots=True)
class Move:
    # full bot turn
    cell: Cell
    piece: Piece | None  # end


@dataclass(frozen=True, slots=True)
class Win:
    side: Side
    line: Line


@dataclass(frozen=True, slots=True)
class Draw:
    """Board full, no winning line."""


type Outcome = Win | Draw | None


class IllegalMove(Exception):
    """Rule violation. Bug in view/presenter."""


# CREATING STATES
def new_game(first_piece: Piece) -> GameState:
    return GameState(
        board=(None,) * 16,
        available=ALL_PIECES - {first_piece},
        current=first_piece,
        side=Side.SECOND,
        action=Action.PLACE,
    )


def place(state: GameState, cell: Cell) -> GameState:
    if outcome(state) is not None:
        raise IllegalMove("game over")
    if state.action is not Action.PLACE or state.current is None:
        raise IllegalMove("not a place step")
    if not 0 <= cell < 16 or state.board[cell] is not None:
        raise IllegalMove(f"cell {cell} is not free")
    new_board = state.board[:cell] + (state.current,) + state.board[cell + 1 :]
    return replace(state, board=new_board, current=None, action=Action.GIVE)


def give(state: GameState, piece: Piece) -> GameState:
    if outcome(state) is not None:
        raise IllegalMove("game is over")
    if state.action is not Action.GIVE:
        raise IllegalMove("not a give step")
    if piece not in state.available:
        raise IllegalMove(f"piece {piece:04b} is not available")
    return replace(
        state,
        available=state.available - {piece},
        current=piece,
        side=state.side.other(),
        action=Action.PLACE,
    )


# READING STATES
def outcome(state: GameState) -> Outcome:
    # side don't change between place and give
    for line in LINES:
        if line_wins(state.board, line):
            return Win(side=state.side, line=line)
    if board_full(state.board):
        return Draw()
    return None


def line_wins(board: Board, line: Line) -> bool:
    pieces = pieces_on_line(board, line)
    if pieces is None:
        return False
    return shares_attribute(pieces)


def pieces_on_line(board: Board, line: Line) -> tuple[Piece, ...] | None:
    pieces: list[Piece] = []
    for cell in line:
        piece = board[cell]
        if piece is None:
            return None
        else:
            pieces.append(piece)
    return tuple(pieces)


def shares_attribute(pieces: tuple[Piece, ...]) -> bool:
    common_ones = ALL_BITS
    common_zeros = ALL_BITS
    for piece in pieces:
        common_ones &= piece
        common_zeros &= ~piece & ALL_BITS
    return (common_ones | common_zeros) != 0


def board_full(board: Board) -> bool:
    return all(piece is not None for piece in board)


def empty_cells(state: GameState) -> tuple[Cell, ...]:
    # oredered
    return tuple(cell for cell in ALL_CELLS if state.board[cell] is None)


def sorted_available(state: GameState) -> tuple[Piece, ...]:
    return tuple(sorted(state.available))


# for tests. AI
def check_invariants(state: GameState) -> None:
    assert len(state.board) == 16
    on_board = [piece for piece in state.board if piece is not None]
    in_hand = [] if state.current is None else [state.current]
    everything = on_board + in_hand + list(state.available)
    assert len(everything) == len(set(everything)), "piece in two places"
    assert set(everything) <= ALL_PIECES
    if state.action is Action.PLACE and outcome(state) is None:
        assert state.current is not None, "nothing to place"
    if state.action is Action.GIVE:
        assert state.current is None, "piece in hand while giving"
