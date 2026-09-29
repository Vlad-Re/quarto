"""Bots: functions GameState -> Move"""

from collections.abc import Callable

from quarto.model import GameState, Move

type Bot = Callable[[GameState], Move]
