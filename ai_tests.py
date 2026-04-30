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
    return random.choice(game.get_valid_moves())


def opponent(player):
    return "X" if player == "O" else "O"


def line_winning_move(game, moves, player):
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
    moves = game.get_valid_moves()
    winning_move = line_winning_move(game, moves, player)
    if winning_move:
        return winning_move
    return prefer_positional_move(moves)


def blocker_agent(game, player):
    moves = game.get_valid_moves()
    winning_move = line_winning_move(game, moves, player)
    if winning_move:
        return winning_move

    block_move = line_winning_move(game, moves, opponent(player))
    if block_move:
        return block_move

    return prefer_positional_move(moves)


def older_ai_agent(game, player):
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


def run_unit_tests():
    test_completed_target_board_allows_anywhere()
    test_ai_takes_local_board_win()
    test_ai_takes_global_win()
    test_greedy_local_win_agent_takes_board()
    test_blocker_agent_blocks_local_win()
    print("Unit tests passed.")


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

    print(
        f"Played {games} games with minimax depth {depth} against "
        f"{opponent_name} baseline, alternating first player."
    )
    print(f"Raw results: X={results['X']} O={results['O']} draws={results['draw']}")
    print(
        "AI results: "
        f"wins={ai_results['win']} losses={ai_results['loss']} draws={ai_results['draw']}"
    )
    print("Use this as a regression trend, not a proof of optimal play.")


def main():
    parser = argparse.ArgumentParser(description="Headless checks for the Ultimate Tic Tac Toe AI.")
    parser.add_argument("--benchmark", type=int, default=0, help="Run this many minimax-vs-random games.")
    parser.add_argument("--depth", type=int, default=2, help="Search depth for benchmark games.")
    parser.add_argument(
        "--opponent",
        choices=sorted(BASELINE_AGENTS),
        default="random",
        help="Baseline agent for benchmark games.",
    )
    parser.add_argument("--seed", type=int, default=440, help="Random seed for reproducible results.")
    args = parser.parse_args()

    run_unit_tests()
    if args.benchmark:
        run_benchmark(args.benchmark, args.depth, args.seed, args.opponent)


if __name__ == "__main__":
    main()
