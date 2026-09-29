# pyright: basic
# matplotlib is only partly typed, strict mode stays on for the game code
"""Minimax time vs depth on the bot's 1st and 2nd move. Run: python -m tools.bench_depth

Stops a series when one move takes longer than --limit seconds.
Saves CSV + PNG into benchmarks/.
"""

import argparse
import csv
import time
from pathlib import Path

from matplotlib.figure import Figure  # Figure without pyplot: no window, just files

from quarto.bot.greedy import greedy_bot
from quarto.bot.minimax import minimax_move
from quarto.model import GameState, Piece, give, new_game, place

OUT_DIR = Path("benchmarks")
REQUIREMENT_S = 3.5


def play_turn(state: GameState) -> GameState:
    # one full turn by greedy: deterministic, so positions are always the same
    move = greedy_bot(state)
    placed = place(state, move.cell)
    assert move.piece is not None, "game ended too early for a benchmark"
    return give(placed, move.piece)


def bot_positions() -> dict[str, GameState]:
    # bot = FIRST side; player (SECOND) places first
    # first piece does not matter: all pieces are equivalent on an empty board
    start = new_game(Piece(0))
    bot_move_1 = play_turn(start)  # after player's first turn
    bot_move_2 = play_turn(play_turn(bot_move_1))  # after bot + player turns
    return {"bot move 1": bot_move_1, "bot move 2": bot_move_2}


def measure(state: GameState, depth: int) -> float:
    started = time.perf_counter()
    minimax_move(state, depth)
    return time.perf_counter() - started


def run(limit_s: float) -> dict[str, list[tuple[int, float]]]:
    results: dict[str, list[tuple[int, float]]] = {}
    for name, state in bot_positions().items():
        series: list[tuple[int, float]] = []
        depth = 2
        while True:
            print(f"{name}, depth {depth} ...", end=" ", flush=True)
            spent = measure(state, depth)
            print(f"{spent:.3f} s")
            series.append((depth, spent))
            if spent > limit_s:
                break
            depth += 1
        results[name] = series
    return results


def save(results: dict[str, list[tuple[int, float]]]) -> None:
    OUT_DIR.mkdir(exist_ok=True)
    csv_path = OUT_DIR / "minimax_depth.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["position", "depth_half_actions", "seconds"])
        for name, series in results.items():
            for depth, spent in series:
                writer.writerow([name, depth, f"{spent:.4f}"])

    figure = Figure(figsize=(8, 5))
    axes = figure.subplots()
    for (name, series), color in zip(results.items(), ["#4CAF50", "#E0A030"], strict=False):
        depths = [depth for depth, _ in series]
        seconds = [spent for _, spent in series]
        axes.plot(depths, seconds, marker="o", color=color, label=name)
    axes.axhline(REQUIREMENT_S, color="gray", linestyle="--", label="requirement 3.5 s")
    all_depths = sorted({depth for series in results.values() for depth, _ in series})
    axes.set_xticks(all_depths)
    axes.set_yscale("log")
    axes.set_xlabel("depth, half-actions")
    axes.set_ylabel("time per move, s (log scale)")
    axes.set_title("Minimax (no pruning, eval = 0): time vs depth")
    axes.grid(True, which="both", alpha=0.3)
    axes.legend()
    png_path = OUT_DIR / "minimax_depth.png"
    figure.savefig(png_path, dpi=120, bbox_inches="tight")
    print(f"saved {csv_path} and {png_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=float, default=120.0, help="stop above this, seconds")
    args = parser.parse_args()
    limit_s: float = args.limit
    save(run(limit_s))


if __name__ == "__main__":
    main()
