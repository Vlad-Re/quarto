"""Presenter: game flow. Calls model and bot, tells the view what to show."""

import random
import time

from quarto.bot import Bot
from quarto.bot.greedy import greedy_bot
from quarto.bot.minimax import minimax_bot
from quarto.bot.random_bot import random_bot
from quarto.model import (
    ALL_PIECES,
    Action,
    Cell,
    Draw,
    GameState,
    IllegalMove,
    Piece,
    Side,
    Win,
    give,
    new_game,
    outcome,
    place,
)
from quarto.view import InputMode, QuartoView, Screen

BOTS: dict[str, Bot] = {
    "random": random_bot,
    "greedy": greedy_bot,
    "minimax": minimax_bot,
}
BOT: Bot = BOTS["greedy"]
BOT_MOVE_DELAY = 800  # ms

BOT_SIDE = Side.FIRST  # gives piece
PLAYER_SIDE = Side.SECOND  # places


class Presenter:
    def __init__(self, view: QuartoView) -> None:
        self._view = view
        self._state = new_game(Piece(0))  # rand
        self._selected: Piece | None = None
        self._game_id = 0  # stale bot callbacks after reset are dropped by this

    def start(self) -> None:
        self._game_id += 1
        first_piece = random.choice(sorted(ALL_PIECES))
        self._state = new_game(first_piece)
        self._selected = None
        self._render()

    # VIEW EVENTS

    def on_reset(self) -> None:
        self.start()

    def on_cell_click(self, cell: Cell) -> None:
        if not self._player_step(Action.PLACE):
            return
        self._state = place(self._state, cell)
        self._render()

    def on_piece_click(self, piece: Piece | None) -> None:
        if not self._player_step(Action.GIVE):
            return
        if piece is None or piece != self._selected:
            self._selected = piece  # first click: frame (None: remove frame)
            self._render()
            return
        self._selected = None
        self._state = give(self._state, piece)
        self._render()
        game_id = self._game_id
        self._view.schedule(1, lambda: self._bot_turn(game_id))  # let the window repaint first

    # --- bot ---

    def _bot_turn(self, game_id: int) -> None:
        if game_id != self._game_id:
            return
        started = time.perf_counter()
        move = BOT(self._state)
        spent = (time.perf_counter() - started) * 1000
        print(f"{BOT.__name__}: {spent:.1f} ms")
        wait_ms = max(1, BOT_MOVE_DELAY - int(spent))
        self._view.schedule(wait_ms, lambda: self._apply_bot_move(game_id, move.cell, move.piece))

    def _apply_bot_move(self, game_id: int, cell: Cell, piece: Piece | None) -> None:
        if game_id != self._game_id:
            return
        placed = place(self._state, cell)
        if outcome(placed) is not None:
            self._state = placed
        elif piece is None:
            raise IllegalMove("bot did not give a piece")
        else:
            self._state = give(placed, piece)
        self._render()

    # --- helpers ---

    def _player_step(self, action: Action) -> bool:
        state = self._state
        return outcome(state) is None and state.side is PLAYER_SIDE and state.action is action

    def _render(self) -> None:
        self._view.show(_screen_for(self._state, self._selected))


def _screen_for(state: GameState, selected: Piece | None) -> Screen:
    result = outcome(state)
    highlight = None
    mode = InputMode.NONE
    match result:
        case Win():
            highlight = result.line
            status = "Player's win" if result.side is PLAYER_SIDE else "Bot's win"
        case Draw():
            status = "Draw"
        case None:
            if state.side is BOT_SIDE:
                status = "Bot's turn"
            elif state.action is Action.PLACE:
                status = "Player's turn: place the piece"
                mode = InputMode.PLACE
            else:
                status = "Player's turn: choose a piece for the bot"
                mode = InputMode.GIVE
    return Screen(
        board=state.board,
        available=state.available,
        current=state.current,
        selected=selected,
        status=status,
        mode=mode,
        highlight=highlight,
    )
