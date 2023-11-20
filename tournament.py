

def run_round_robin_tournament(ai_versions, chess_board, app, injected_function):
    app.display_message("tournament started", "label2")
    print("tournament started")

    results = {ai: {"wins": 0, "draws": 0, "losses": 0} for ai in ai_versions}

    for i, ai1 in enumerate(ai_versions):
        for ai2 in ai_versions[i+1:]:
            winner = play_match(ai1, ai2, chess_board, injected_function)
            update_results(results, winner, ai1, ai2)

    return rank_ais(results)


def play_match(ai1, ai2, chess_board, injected_function):
    chess_board.reset()

    winner = injected_function(chess_board, ai1, ai2, 30, 30)
    # Use version_vs_version or similar function to play the match
    # Return the result: winner AI, 'draw', or 'none' if the match couldn't be completed
    return winner


def update_results(results, winner, ai1, ai2):
    if winner == ai1:
        results[ai1]["wins"] += 1
        results[ai2]["losses"] += 1
    elif winner == ai2:
        results[ai2]["wins"] += 1
        results[ai1]["losses"] += 1
    else:  # Draw
        results[ai1]["draws"] += 1
        results[ai2]["draws"] += 1


def rank_ais(results):
    # Sort AI based on wins, draws
    sorted_ais = sorted(results.items(), key=lambda x: (x[1]['wins'], x[1]['draws']), reverse=True)
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