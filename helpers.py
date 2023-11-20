from chess import WHITE


def determine_winner(result, version_a, version_b):
    if "White wins" in result:
        return version_a
    elif "Black wins" in result:
        return version_b
    elif "Draw" in result:
        return "draw"
    else:
        return None


def game_status(board):
    if board.is_checkmate():
        if board.turn == WHITE:
            return "Black wins by checkmate"
        else:
            return "White wins by checkmate"
    elif board.is_stalemate():
        return "Draw by stalemate"
    elif board.is_insufficient_material():
        return "Draw due to insufficient material"
    elif board.can_claim_draw():
        return "Draw can be claimed"
    elif board.is_seventyfive_moves():
        return "Draw by 75-move rule"
    elif board.is_fivefold_repetition():
        return "Draw by fivefold repetition"
    else:
        return "Game is not over"
