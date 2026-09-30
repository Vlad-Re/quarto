"""Score shared by greedy and minimax"""

from quarto.config import UNSAFE_PIECE_SCORE
from quarto.model import (
    ALL_BITS,
    LINES,
    Board,
    Draw,
    GameState,
    Piece,
    Side,
    Win,
    outcome,
)

WIN_SCORE = 1000


def evaluate(state: GameState, side: Side) -> int:
    result = outcome(state)
    match result:
        case Win():
            return WIN_SCORE if result.side is side else -WIN_SCORE
        case Draw():
            return 0
        case None:
            # unsafe pieces hurt the side to move: it must give one of the rest (zugzwang)
            unsafe_score = UNSAFE_PIECE_SCORE * count_unsafe_pieces(state)
            return -unsafe_score if state.side is side else unsafe_score


def count_unsafe_pieces(state: GameState) -> int:
    # available pieces that would let the receiver complete a line right away
    masks = threat_masks(state.board)
    return sum(1 for piece in state.available if any(completes(piece, mask) for mask in masks))


def threat_masks(board: Board) -> tuple[tuple[int, int], ...]:
    # for each line with 3 pieces + 1 empty cell: (common ones, common zeros)
    masks: list[tuple[int, int]] = []
    for line in LINES:
        pieces = tuple(piece for cell in line if (piece := board[cell]) is not None)
        if len(pieces) != 3:
            continue
        ones = pieces[0] & pieces[1] & pieces[2]
        zeros = ~(pieces[0] | pieces[1] | pieces[2]) & ALL_BITS
        if ones | zeros:
            masks.append((ones, zeros))
    return tuple(masks)


def completes(piece: Piece, mask: tuple[int, int]) -> bool:
    ones, zeros = mask
    return bool(piece & ones) or bool(~piece & zeros)
