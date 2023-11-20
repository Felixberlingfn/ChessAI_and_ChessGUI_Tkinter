"""
Implements a round-robin tournament for chess AI players. Each AI competes twice against
every other AI, once as white and once as black, providing a balanced assessment of each
AI's strategy.

Functions:
    run_round_robin_tournament: Conducts the tournament among AI versions.
    play_match: Plays a match between two AIs.
    update_results: Updates tournament standings based on match results.
    rank_ais: Sorts AIs based on performance metrics.
    determine_winner: Identifies the winner based on the match outcome.

Usage:
    Call run_round_robin_tournament with AI versions, a chess board, the GUI app, and the function for playing matches.
    The final standings are printed, showing each AI's performance.
"""


results: dict = {}


def run_round_robin_tournament(ai_versions, chess_board, app, injected_function):
    global results

    app.display_message("tournament started", "label2")
    print("tournament started")

    results = {ai: {"points": 0, "wins": 0, "draws": 0, "losses": 0} for ai in ai_versions}

    for i, ai1 in enumerate(ai_versions):
        for ai2 in ai_versions[i+1:]:
            """ ai1 as white and ai2 as black """
            winner = play_match(ai1, ai2, chess_board, injected_function)
            update_results(winner, ai1, ai2)

            """ ai2 as white and ai1 as black """
            winner_reverse = play_match(ai2, ai1, chess_board, injected_function)
            update_results(winner_reverse, ai1, ai2)

    return rank_ais()


def play_match(ai1, ai2, chess_board, injected_function):
    chess_board.reset()

    """ use the dependency injected version_vs_version function"""
    winner = injected_function(chess_board, ai1, ai2, 30, 30)
    # Return the result: winner AI, 'draw', or 'none' if the match couldn't be completed
    return winner


def update_results(winner, ai1, ai2):
    global results

    if winner == ai1:
        results[ai1]["points"] += 2
        results[ai2]["points"] += 0

        results[ai1]["wins"] += 1
        results[ai2]["losses"] += 1
    elif winner == ai2:
        results[ai1]["points"] += 0
        results[ai2]["points"] += 2

        results[ai2]["wins"] += 1
        results[ai1]["losses"] += 1
    else:  # Draw
        results[ai1]["points"] += 1
        results[ai2]["points"] += 1

        results[ai1]["draws"] += 1
        results[ai2]["draws"] += 1


def rank_ais():
    global results

    # Sort AI based on points
    sorted_ais = sorted(results.items(), key=lambda x: (x[1]['points']), reverse=True)
    return sorted_ais


def determine_winner(result, version_a, version_b):
    if "White wins" in result:
        return version_a
    elif "Black wins" in result:
        return version_b
    elif "Draw" in result:
        return "draw"
    else:
        return None


if __name__ == "__main__":
    """ai_versions = []
    chess_board = ""
    app = ""
    # Run the tournament
    tournament_results = run_round_robin_tournament(ai_versions, chess_board, app)
    for ai, result in tournament_results:
        print(f"AI {ai.__name__}: Wins: {result['wins']}, Draws: {result['draws']}, Losses: {result['losses']}")
"""