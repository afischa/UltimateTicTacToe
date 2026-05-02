import argparse
import random

from Game import EMPTY, UltimateTicTacToe


def make_headless_game(depth=2, ai_player="O"):
    game = UltimateTicTacToe.__new__(UltimateTicTacToe)
    game.ai_enabled = True
    game.ai_player = ai_player
    game.search_depth = depth
    game.current_player = "X"
    game.next_board = None
    game.ai_thinking = False
    game.game_over = False
    game.boards = [[[[EMPTY for _ in range(3)] for _ in range(3)]
                    for _ in range(3)] for _ in range(3)]
    game.big_wins = [[EMPTY for _ in range(3)] for _ in range(3)]
    return game


def play_headless_move(game, move, player):
    br, bc, r, c = move
    game.boards[br][bc][r][c] = player
    if game.big_wins[br][bc] == EMPTY and game.check_win(game.boards[br][bc]):
        game.big_wins[br][bc] = player
    game.next_board = game.resolve_next_board(r, c)


def game_result(game):
    if game.has_three_in_a_row(game.big_wins, "X"):
        return "X"
    if game.has_three_in_a_row(game.big_wins, "O"):
        return "O"
    if not game.get_valid_moves():
        return "draw"
    return None


def random_agent(game, player):
    """Baseline that knows only the rules: choose any legal move uniformly."""
    return random.choice(game.get_valid_moves())


def opponent(player):
    return "X" if player == "O" else "O"


def line_winning_move(game, moves, player):
    """
    Return an immediate winning move for player, if one exists.

    Global wins are checked before local-board wins because ending the whole game
    is strictly better than only claiming one local board.
    """
    for move in moves:
        undo = game.apply_simulated_move(move, player)
        won_local = game.big_wins[move[0]][move[1]] == player
        won_global = game.has_three_in_a_row(game.big_wins, player)
        game.undo_simulated_move(undo)
        if won_global:
            return move

    for move in moves:
        undo = game.apply_simulated_move(move, player)
        won_local = game.big_wins[move[0]][move[1]] == player
        game.undo_simulated_move(undo)
        if won_local:
            return move

    return None


def greedy_local_win_agent(game, player):
    """
    Greedy baseline:
    1. Take an immediate global win.
    2. Otherwise take an immediate local-board win.
    3. Otherwise choose a simple positional square.
    """
    moves = game.get_valid_moves()
    winning_move = line_winning_move(game, moves, player)
    if winning_move:
        return winning_move
    return prefer_positional_move(moves)


def blocker_agent(game, player):
    """
    Defensive baseline:
    1. Win immediately if possible.
    2. Otherwise block the opponent's immediate global/local win.
    3. Otherwise choose a simple positional square.
    """
    moves = game.get_valid_moves()
    winning_move = line_winning_move(game, moves, player)
    if winning_move:
        return winning_move

    block_move = line_winning_move(game, moves, opponent(player))
    if block_move:
        return block_move

    return prefer_positional_move(moves)


def older_ai_agent(game, player):
    """
    Lightweight scoring baseline modeled after the project's earlier AI idea.

    It does not recurse like minimax. It scores each legal move once:
    - +10000 for an immediate global win.
    - +100 for an immediate local-board win.
    - +50 if the same square would let the opponent win that local board, so it
      works as a basic block.
    - +10 for playing in the center local board.
    - +4 for playing the center cell inside a local board.
    """
    moves = game.get_valid_moves()
    scored_moves = []
    other = opponent(player)

    for move in moves:
        br, bc, r, c = move
        score = 0

        undo = game.apply_simulated_move(move, player)
        if game.has_three_in_a_row(game.big_wins, player):
            score += 10000
        elif game.big_wins[br][bc] == player:
            score += 100
        game.undo_simulated_move(undo)

        undo = game.apply_simulated_move(move, other)
        if game.big_wins[br][bc] == other:
            score += 50
        game.undo_simulated_move(undo)

        if (br, bc) == (1, 1):
            score += 10
        if (r, c) == (1, 1):
            score += 4

        scored_moves.append((score, move))

    best_score = max(score for score, _ in scored_moves)
    return random.choice([move for score, move in scored_moves if score == best_score])


def prefer_positional_move(moves):
    """Shared fallback that prefers center, then corners, over edge positions."""
    def score(move):
        br, bc, r, c = move
        value = 0
        if (br, bc) == (1, 1):
            value += 4
        if (r, c) == (1, 1):
            value += 3
        if (br, bc) in ((0, 0), (0, 2), (2, 0), (2, 2)):
            value += 2
        if (r, c) in ((0, 0), (0, 2), (2, 0), (2, 2)):
            value += 1
        return value

    best_score = max(score(move) for move in moves)
    return random.choice([move for move in moves if score(move) == best_score])


def minimax_agent(depth):
    def choose(game, player):
        old_ai_player = game.ai_player
        old_depth = game.search_depth
        game.ai_player = player
        game.search_depth = depth
        move = game.choose_ai_move(depth)
        game.ai_player = old_ai_player
        game.search_depth = old_depth
        return move

    return choose


BASELINE_AGENTS = {
    "random": random_agent,
    "greedy": greedy_local_win_agent,
    "blocker": blocker_agent,
    "older": older_ai_agent,
}


def play_match(x_agent, o_agent, seed=None):
    if seed is not None:
        random.seed(seed)

    game = make_headless_game()
    current = "X"

    while game_result(game) is None:
        move = x_agent(game, current) if current == "X" else o_agent(game, current)
        if move not in game.get_valid_moves():
            raise AssertionError(f"{current} selected illegal move: {move}")
        play_headless_move(game, move, current)
        current = "O" if current == "X" else "X"

    return game_result(game)


def test_completed_target_board_allows_anywhere():
    game = make_headless_game()
    game.big_wins[1][1] = "X"
    game.next_board = (1, 1)

    moves = game.get_valid_moves()

    assert moves, "AI should have legal moves when target board is already won"
    assert all((br, bc) != (1, 1) for br, bc, _, _ in moves)
    assert len(moves) == 72, f"Expected all open cells outside won board, got {len(moves)}"


def test_ai_takes_local_board_win():
    game = make_headless_game(depth=2, ai_player="O")
    game.next_board = (0, 0)
    game.boards[0][0][0][0] = "O"
    game.boards[0][0][0][1] = "O"
    game.boards[0][0][1][1] = "X"

    assert game.choose_ai_move(depth=2) == (0, 0, 0, 2)


def test_ai_takes_global_win():
    game = make_headless_game(depth=2, ai_player="O")
    game.big_wins[0][0] = "O"
    game.big_wins[0][1] = "O"
    game.next_board = (0, 2)
    game.boards[0][2][2][0] = "O"
    game.boards[0][2][2][1] = "O"
    game.boards[0][2][1][1] = "X"

    assert game.choose_ai_move(depth=2) == (0, 2, 2, 2)


def test_greedy_local_win_agent_takes_board():
    game = make_headless_game()
    game.next_board = (0, 0)
    game.boards[0][0][1][0] = "X"
    game.boards[0][0][1][1] = "X"

    assert greedy_local_win_agent(game, "X") == (0, 0, 1, 2)


def test_blocker_agent_blocks_local_win():
    game = make_headless_game()
    game.next_board = (2, 2)
    game.boards[2][2][0][0] = "O"
    game.boards[2][2][0][1] = "O"

    assert blocker_agent(game, "X") == (2, 2, 0, 2)


def test_random_agent_returns_legal_move_on_forced_board():
    random.seed(7)
    game = make_headless_game()
    game.next_board = (1, 2)
    game.boards[1][2][0][0] = "X"
    game.boards[1][2][0][1] = "O"

    move = random_agent(game, "X")

    assert move in game.get_valid_moves()
    assert move[:2] == (1, 2)


def test_greedy_agent_prefers_global_win_over_local_win():
    game = make_headless_game()
    game.big_wins[0][0] = "X"
    game.big_wins[0][1] = "X"
    game.next_board = None
    game.boards[0][2][2][0] = "X"
    game.boards[0][2][2][1] = "X"
    game.boards[1][1][0][0] = "X"
    game.boards[1][1][0][1] = "X"

    assert greedy_local_win_agent(game, "X") == (0, 2, 2, 2)


def test_blocker_agent_wins_before_blocking():
    game = make_headless_game()
    game.next_board = None
    game.boards[0][0][1][0] = "X"
    game.boards[0][0][1][1] = "X"
    game.boards[2][2][0][0] = "O"
    game.boards[2][2][0][1] = "O"

    assert blocker_agent(game, "X") == (0, 0, 1, 2)


def test_older_agent_prefers_center_board_and_cell():
    game = make_headless_game()
    game.next_board = None

    assert older_ai_agent(game, "X") == (1, 1, 1, 1)


def test_forced_full_board_allows_anywhere_else():
    game = make_headless_game()
    game.next_board = (0, 0)
    game.boards[0][0] = [
        ["X", "O", "X"],
        ["O", "X", "O"],
        ["O", "X", "O"],
    ]

    moves = game.get_valid_moves()

    assert moves
    assert all(move[:2] != (0, 0) for move in moves)
    assert len(moves) == 72


def test_simulated_move_undo_restores_state():
    game = make_headless_game()
    game.next_board = (0, 0)
    game.boards[0][0][0][0] = "O"
    game.boards[0][0][0][1] = "O"

    undo = game.apply_simulated_move((0, 0, 0, 2), "O")
    assert game.big_wins[0][0] == "O"
    assert game.next_board == (0, 2)

    game.undo_simulated_move(undo)

    assert game.boards[0][0][0][2] == EMPTY
    assert game.big_wins[0][0] == EMPTY
    assert game.next_board == (0, 0)


UNIT_TESTS = (
    ("completed target board allows anywhere", test_completed_target_board_allows_anywhere),
    ("forced full target board allows anywhere else", test_forced_full_board_allows_anywhere_else),
    ("simulated move undo restores state", test_simulated_move_undo_restores_state),
    ("main AI takes immediate local board win", test_ai_takes_local_board_win),
    ("main AI takes immediate global win", test_ai_takes_global_win),
    ("random baseline returns a legal forced-board move", test_random_agent_returns_legal_move_on_forced_board),
    ("greedy baseline takes immediate local board win", test_greedy_local_win_agent_takes_board),
    ("greedy baseline prefers global win over local win", test_greedy_agent_prefers_global_win_over_local_win),
    ("blocker baseline blocks immediate local board win", test_blocker_agent_blocks_local_win),
    ("blocker baseline wins before blocking", test_blocker_agent_wins_before_blocking),
    ("older baseline prefers center board and center cell", test_older_agent_prefers_center_board_and_cell),
)


def run_unit_tests():
    print("Unit tests")
    for name, test in UNIT_TESTS:
        test()
        print(f"  PASS - {name}")
    print(f"Unit tests passed: {len(UNIT_TESTS)}/{len(UNIT_TESTS)}")


def run_benchmark(games, depth, seed, opponent_name):
    random.seed(seed)
    results = {"X": 0, "O": 0, "draw": 0}
    ai_results = {"win": 0, "loss": 0, "draw": 0}
    opponent_agent = BASELINE_AGENTS[opponent_name]

    for i in range(games):
        if i % 2 == 0:
            result = play_match(opponent_agent, minimax_agent(depth), seed + i)
            ai_player = "O"
        else:
            result = play_match(minimax_agent(depth), opponent_agent, seed + i)
            ai_player = "X"
        results[result] += 1
        if result == "draw":
            ai_results["draw"] += 1
        elif result == ai_player:
            ai_results["win"] += 1
        else:
            ai_results["loss"] += 1

    return {
        "opponent": opponent_name,
        "games": games,
        "depth": depth,
        "seed": seed,
        "x_wins": results["X"],
        "o_wins": results["O"],
        "ai_wins": ai_results["win"],
        "ai_losses": ai_results["loss"],
        "draws": ai_results["draw"],
    }


def print_benchmark_report(rows):
    if not rows:
        return

    print()
    print("Benchmarks")
    print("Opponent | Games | Depth | AI Wins | AI Losses | Draws | X Wins | O Wins")
    print("-" * 74)
    for row in rows:
        print(
            f"{row['opponent']:<8} | "
            f"{row['games']:>5} | "
            f"{row['depth']:>5} | "
            f"{row['ai_wins']:>7} | "
            f"{row['ai_losses']:>9} | "
            f"{row['draws']:>5} | "
            f"{row['x_wins']:>6} | "
            f"{row['o_wins']:>6}"
        )
    print()
    print("AI wins/losses/draws are from the minimax AI perspective.")
    print("X/O wins show raw first-symbol results while the benchmark alternates who starts.")


def main():
    parser = argparse.ArgumentParser(description="Headless checks for the Ultimate Tic Tac Toe AI.")
    parser.add_argument(
        "--games",
        type=int,
        default=10,
        help="Games to play against each selected baseline opponent.",
    )
    parser.add_argument(
        "--benchmark",
        type=int,
        default=None,
        help="Deprecated alias for --games. If supplied, it overrides --games.",
    )
    parser.add_argument("--depth", type=int, default=2, help="Search depth for benchmark games.")
    parser.add_argument(
        "--opponent",
        choices=["all"] + sorted(BASELINE_AGENTS),
        default="all",
        help="Baseline agent for benchmark games, or all to run every baseline.",
    )
    parser.add_argument("--skip-benchmarks", action="store_true", help="Only run unit tests.")
    parser.add_argument("--seed", type=int, default=440, help="Random seed for reproducible results.")
    args = parser.parse_args()

    games = args.benchmark if args.benchmark is not None else args.games
    if games < 1:
        raise ValueError("--games must be at least 1")

    run_unit_tests()
    if not args.skip_benchmarks:
        opponents = sorted(BASELINE_AGENTS) if args.opponent == "all" else [args.opponent]
        rows = [
            run_benchmark(games, args.depth, args.seed + index * games, opponent_name)
            for index, opponent_name in enumerate(opponents)
        ]
        print_benchmark_report(rows)


if __name__ == "__main__":
    main()
