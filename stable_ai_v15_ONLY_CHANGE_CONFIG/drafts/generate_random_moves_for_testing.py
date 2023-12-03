import chess
import random

board = chess.Board()

for i in range(27):
    random_moves = list(board.legal_moves)
    random_move = random.choice(random_moves)
    board.push(random_move)

for move in board.move_stack:
    print(f'"{move.uci()}", ', end="")