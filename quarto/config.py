"""Tunable settings in one place."""

from typing import Literal

BOT_NAME: Literal["random", "greedy", "minimax"] = "minimax"
BOT_MOVE_DELAY = 800
MINIMAX_DEPTH = 8
UNSAFE_PIECE_SCORE = 7
