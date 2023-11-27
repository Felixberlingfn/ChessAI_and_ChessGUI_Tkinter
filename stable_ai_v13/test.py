import chess

print(chess.QUEEN)

print(chess.D4, chess.E4)

board = chess.Board()

# print(board.piece_map())


for square, piece in board.piece_map().items():
    print(square)
    print(piece)
    print(piece.piece_type)
