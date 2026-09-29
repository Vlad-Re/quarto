"""Tkinter window. Draws what the presenter tells it, filters clicks, forwards the rest."""

import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto
from tkinter import messagebox

from quarto.model import ALL_PIECES, COLOR, HOLE, SHAPE, SIZE, Cell, Line, Piece

# colors
BG = "#1E1E1E"
CELL_BG = "#2D2D30"
CELL_BORDER = "#3E3E42"
LIGHT_PIECE = "#E0E0E0"
DARK_PIECE = "#121212"
LIGHT_OUTLINE = "#000000"
DARK_OUTLINE = "#BDBDBD"
ACCENT = "#4CAF50"
TEXT = "#E0E0E0"

# layout, px
MARGIN = 20
CELL = 80  # board cell
SLOT = 50  # available piece slot
BOARD_SIZE = 4 * CELL
PANEL_X = MARGIN + BOARD_SIZE + 40
CURRENT_Y = MARGIN + 20
AVAILABLE_Y = CURRENT_Y + CELL + 40
CANVAS_W = PANEL_X + 4 * SLOT + MARGIN
CANVAS_H = MARGIN + BOARD_SIZE + MARGIN


class InputMode(Enum):
    NONE = auto()  # bot's turn or game over: ignore everything
    PLACE = auto()  # player clicks an empty cell
    GIVE = auto()  # player clicks an available piece


@dataclass(frozen=True, slots=True)
class Screen:
    # everything the window needs for one redraw
    board: tuple[Piece | None, ...]
    available: frozenset[Piece]
    current: Piece | None
    selected: Piece | None  # frame after first click
    status: str
    mode: InputMode
    highlight: Line | None  # winning line


class QuartoView(tk.Frame):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, bg=BG)
        self._screen: Screen | None = None
        self._hover: Cell | None = None
        self._on_cell: Callable[[Cell], None] = lambda _cell: None
        self._on_piece: Callable[[Piece | None], None] = lambda _piece: None
        self._on_reset: Callable[[], None] = lambda: None

        self._status = tk.Label(self, text="", bg=BG, fg=TEXT, font=("Segoe UI", 14))
        self._status.pack(pady=(MARGIN, 0))
        self._canvas = tk.Canvas(self, width=CANVAS_W, height=CANVAS_H, bg=BG, highlightthickness=0)
        self._canvas.pack()
        self._reset_button = tk.Button(
            self,
            text="Reset",
            command=self._reset_clicked,
            bg=CELL_BG,
            fg=TEXT,
            activebackground=CELL_BORDER,
            activeforeground=TEXT,
            relief=tk.FLAT,
            padx=16,
            pady=4,
        )
        self._reset_button.pack(pady=(0, MARGIN))

        self._canvas.bind("<Button-1>", self._clicked)
        self._canvas.bind("<Motion>", self._moved)
        self._canvas.bind("<Leave>", self._left)

    # --- called by presenter ---

    def set_handlers(
        self,
        on_cell: Callable[[Cell], None],
        on_piece: Callable[[Piece | None], None],  # None = click outside the pieces
        on_reset: Callable[[], None],
    ) -> None:
        self._on_cell = on_cell
        self._on_piece = on_piece
        self._on_reset = on_reset

    def show(self, screen: Screen) -> None:
        self._screen = screen
        self._status.config(text=screen.status)
        self._redraw()
        self.update_idletasks()  # paint now, before a long bot computation

    def schedule(self, ms: int, callback: Callable[[], None]) -> None:
        self.after(ms, callback)

    # --- events ---

    def _reset_clicked(self) -> None:
        if messagebox.askyesno("Reset", "Start a new game?", parent=self):
            self._on_reset()

    def _clicked(self, event: "tk.Event[tk.Canvas]") -> None:
        screen = self._screen
        if screen is None:
            return
        match screen.mode:
            case InputMode.PLACE:
                cell = _cell_at(event.x, event.y)
                if cell is not None and screen.board[cell] is None:
                    self._on_cell(cell)
            case InputMode.GIVE:
                piece = _piece_at(event.x, event.y)
                if piece is not None and piece in screen.available:
                    self._on_piece(piece)
                else:
                    self._on_piece(None)
            case InputMode.NONE:
                pass

    def _moved(self, event: "tk.Event[tk.Canvas]") -> None:
        cell = _cell_at(event.x, event.y)
        if cell != self._hover:
            self._hover = cell
            self._redraw()

    def _left(self, _event: "tk.Event[tk.Canvas]") -> None:
        if self._hover is not None:
            self._hover = None
            self._redraw()

    # --- drawing ---

    def _redraw(self) -> None:
        screen = self._screen
        canvas = self._canvas
        canvas.delete("all")
        if screen is None:
            return

        # board
        for index in range(16):
            x0, y0 = _cell_origin(index)
            canvas.create_rectangle(x0, y0, x0 + CELL, y0 + CELL, fill=CELL_BG, outline=CELL_BORDER)
            piece = screen.board[index]
            if piece is not None:
                _draw_piece(canvas, piece, x0 + CELL / 2, y0 + CELL / 2, CELL, CELL_BG)

        # hover over a free cell while placing
        hover = self._hover
        if screen.mode is InputMode.PLACE and hover is not None and screen.board[hover] is None:
            x0, y0 = _cell_origin(hover)
            canvas.create_rectangle(
                x0 + 2, y0 + 2, x0 + CELL - 2, y0 + CELL - 2, outline=ACCENT, width=2
            )

        # winning line
        if screen.highlight is not None:
            for cell in screen.highlight:
                x0, y0 = _cell_origin(cell)
                canvas.create_rectangle(
                    x0 + 2, y0 + 2, x0 + CELL - 2, y0 + CELL - 2, outline=ACCENT, width=4
                )

        # current piece
        canvas.create_text(PANEL_X, CURRENT_Y - 8, text="Current piece", fill=TEXT, anchor=tk.W)
        canvas.create_rectangle(
            PANEL_X,
            CURRENT_Y,
            PANEL_X + CELL,
            CURRENT_Y + CELL,
            fill=CELL_BG,
            outline=CELL_BORDER,
        )
        if screen.current is not None:
            _draw_piece(
                canvas, screen.current, PANEL_X + CELL / 2, CURRENT_Y + CELL / 2, CELL, CELL_BG
            )

        # available pieces: fixed slot per piece, empty slot once used
        canvas.create_text(
            PANEL_X, AVAILABLE_Y - 8, text="Available pieces", fill=TEXT, anchor=tk.W
        )
        for piece in sorted(ALL_PIECES):
            x0, y0 = _slot_origin(piece)
            canvas.create_rectangle(x0, y0, x0 + SLOT, y0 + SLOT, fill=CELL_BG, outline=CELL_BORDER)
            if piece in screen.available:
                _draw_piece(canvas, piece, x0 + SLOT / 2, y0 + SLOT / 2, SLOT, CELL_BG)
            if piece == screen.selected:
                canvas.create_rectangle(
                    x0 + 1, y0 + 1, x0 + SLOT - 1, y0 + SLOT - 1, outline=ACCENT, width=3
                )


# --- geometry helpers ---


def _cell_origin(cell: int) -> tuple[int, int]:
    return MARGIN + (cell % 4) * CELL, MARGIN + (cell // 4) * CELL


def _slot_origin(piece: int) -> tuple[int, int]:
    return PANEL_X + (piece % 4) * SLOT, AVAILABLE_Y + (piece // 4) * SLOT


def _cell_at(x: int, y: int) -> Cell | None:
    col = (x - MARGIN) // CELL
    row = (y - MARGIN) // CELL
    if 0 <= col < 4 and 0 <= row < 4 and x >= MARGIN and y >= MARGIN:
        return Cell(row * 4 + col)
    return None


def _piece_at(x: int, y: int) -> Piece | None:
    col = (x - PANEL_X) // SLOT
    row = (y - AVAILABLE_Y) // SLOT
    if 0 <= col < 4 and 0 <= row < 4 and x >= PANEL_X and y >= AVAILABLE_Y:
        return Piece(row * 4 + col)
    return None


def _draw_piece(
    canvas: tk.Canvas, piece: Piece, cx: float, cy: float, box: int, background: str
) -> None:
    # shape bit: circle/square; color bit: light/dark; size bit: 50%/90%; hole bit: small circle
    ratio = 0.9 if piece & SIZE else 0.5
    half = box * ratio / 2
    dark = bool(piece & COLOR)
    fill = DARK_PIECE if dark else LIGHT_PIECE
    outline = DARK_OUTLINE if dark else LIGHT_OUTLINE
    if piece & SHAPE:
        canvas.create_rectangle(
            cx - half, cy - half, cx + half, cy + half, fill=fill, outline=outline, width=2
        )
    else:
        canvas.create_oval(
            cx - half, cy - half, cx + half, cy + half, fill=fill, outline=outline, width=2
        )
    if piece & HOLE:
        hole = half * 0.4
        canvas.create_oval(
            cx - hole, cy - hole, cx + hole, cy + hole, fill=background, outline=outline, width=2
        )
