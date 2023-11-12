"""This is a concept"""

import chess
# from evaluate_board import evaluate_board


def minimax(board, depth, is_maximizing_player):
    if depth == 0 or board.is_game_over():
        return #evaluate_board(board)

    legal_moves = list(board.legal_moves)

    if is_maximizing_player:
        best_score = float('-inf')
        for move in legal_moves:
            board.push(move)
            score = minimax(board, depth - 1, False)
            board.pop()
            best_score = max(best_score, score)
        return best_score
    else:
        best_score = float('inf')
        for move in legal_moves:
            board.push(move)
            score = minimax(board, depth - 1, True)
            board.pop()
            best_score = min(best_score, score)
        return best_score


def minimax_find_best_move(board, depth):
    best_move = None
    best_score = float('-inf') if board.turn == chess.WHITE else float('inf')

    for move in board.legal_moves:
        board.push(move)
        score = minimax(board, depth - 1, board.turn == chess.BLACK)
        board.pop()

        if board.turn == chess.WHITE and score > best_score:
            best_score = score
            best_move = move
        elif board.turn == chess.BLACK and score < best_score:
            best_score = score
            best_move = move

    return best_move