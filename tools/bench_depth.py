# pyright: basic
# matplotlib is only partly typed, strict mode stays on for the game code
"""Minimax time vs depth on the bot's first moves. Run: python -m tools.bench_depth

A series stops when one move takes longer than --limit seconds or at --max-depth.
Ctrl+C skips the current position; results are saved at the end anyway.
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
POSITIONS = 4  # bot moves 1..4; the slow ones are in the middle

type Results = dict[str, list[tuple[int, float]]]


def play_turn(state: GameState) -> GameState:
    # one full turn by greedy: deterministic, so positions are always the same
    move = greedy_bot(state)
    placed = place(state, move.cell)
    assert move.piece is not None, "game ended too early for a benchmark"
    return give(placed, move.piece)


def bot_positions(count: int) -> dict[str, GameState]:
    # bot = FIRST side; player (SECOND) places first
    # first piece does not matter: all pieces are equivalent on an empty board
    positions: dict[str, GameState] = {}
    state = play_turn(new_game(Piece(0)))  # after player's first turn
    for number in range(1, count + 1):
        positions[f"bot move {number}"] = state
        state = play_turn(play_turn(state))  # bot turn, then player turn
    return positions


def measure(state: GameState, depth: int) -> float:
    started = time.perf_counter()
    minimax_move(state, depth)
    return time.perf_counter() - started


def run(limit_s: float, max_depth: int) -> Results:
    results: Results = {}
    for name, state in bot_positions(POSITIONS).items():
        series: list[tuple[int, float]] = []
        results[name] = series  # filled in place, so Ctrl+C keeps what was measured
        try:
            for depth in range(2, max_depth + 1):
                print(f"{name}, depth {depth} ...", end=" ", flush=True)
                spent = measure(state, depth)
                print(f"{spent:.3f} s")
                series.append((depth, spent))
                if spent > limit_s:
                    break
        except KeyboardInterrupt:
            print("\nskipped, going to the next position")
    return results


def save(results: Results) -> None:
    OUT_DIR.mkdir(exist_ok=True)
    csv_path = OUT_DIR / "alpha_beta_depth.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["position", "depth_half_actions", "seconds"])
        for name, series in results.items():
            for depth, spent in series:
                writer.writerow([name, depth, f"{spent:.4f}"])

    figure = Figure(figsize=(8, 5))
    axes = figure.subplots()
    for name, series in results.items():
        if not series:
            continue  # position skipped before the first measurement
        depths = [depth for depth, _ in series]
        seconds = [spent for _, spent in series]
        axes.plot(depths, seconds, marker="o", label=name)
    axes.axhline(REQUIREMENT_S, color="gray", linestyle="--", label="requirement 3.5 s")
    all_depths = sorted({depth for series in results.values() for depth, _ in series})
    axes.set_xticks(all_depths)
    axes.set_yscale("log")
    axes.set_xlabel("depth, half-actions")
    axes.set_ylabel("time per move, s (log scale)")
    axes.set_title("Alpha-Beta (unsafe-pieces eval): time vs depth")
    axes.grid(True, which="both", alpha=0.3)
    axes.legend()
    png_path = OUT_DIR / "alpha_beta_depth.png"
    figure.savefig(png_path, dpi=120, bbox_inches="tight")
    print(f"saved {csv_path} and {png_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=float, default=10.0, help="stop above this, seconds")
    parser.add_argument("--max-depth", type=int, default=10, help="deepest depth to try")
    args = parser.parse_args()
    limit_s: float = args.limit
    max_depth: int = args.max_depth
    save(run(limit_s, max_depth))


if __name__ == "__main__":
    main()
