"""Entry point: python -m quarto"""

import tkinter as tk

from quarto.presenter import Presenter
from quarto.view import BG, QuartoView


def main() -> None:
    root = tk.Tk()
    root.title("Quarto")
    root.configure(bg=BG)
    root.resizable(False, False)

    view = QuartoView(root)
    view.pack(padx=20)
    presenter = Presenter(view)
    view.set_handlers(
        on_cell=presenter.on_cell_click,
        on_piece=presenter.on_piece_click,
        on_reset=presenter.on_reset,
    )

    presenter.start()
    root.mainloop()


if __name__ == "__main__":
    main()
