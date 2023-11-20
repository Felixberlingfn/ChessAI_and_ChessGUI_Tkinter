def determine_winner(result, version_a, version_b):
    if "White wins" in result:
        return version_a
    elif "Black wins" in result:
        return version_b
    elif "Draw" in result:
        return "draw"
    else:
        return None
