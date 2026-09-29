"""Score shared by greedy and minimax"""

from quarto.config import THREAT_SCORE
from quarto.model import LINES, Board, Draw, GameState, Line, Side, Win, outcome, shares_attribute

WIN_SCORE = 1000


def evaluate(state: GameState, side: Side) -> int:
    result = outcome(state)
    match result:
        case Win():
            return WIN_SCORE if result.side is side else -WIN_SCORE
        case Draw():
            return 0
        case None:
            # threats hurt the side to move
            threat_score = THREAT_SCORE * count_threats(state.board)
            return -threat_score if state.side is side else threat_score


def count_threats(board: Board) -> int:
    return sum(1 for line in LINES if is_threat(board, line))


def is_threat(board: Board, line: Line) -> bool:
    # 3 piece with a common attribute + 1 empty
    pieces = tuple(piece for cell in line if (piece := board[cell]) is not None)
    return len(pieces) == 3 and shares_attribute(pieces)
