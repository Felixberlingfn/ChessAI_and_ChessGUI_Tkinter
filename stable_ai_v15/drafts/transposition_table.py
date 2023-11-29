"""from chatgpt but probably all wrong, need to find proper examples:

just a concept for now"""


import random
import chess

def init_zobrist_keys():
    """
    Initializes Zobrist keys for each piece type on each square,
    and other game state properties like castling rights and en passant.
    """
    keys = {}
    for square in range(64):
        keys[square] = {}
        for piece in chess.PIECE_TYPES:
            for color in chess.COLORS:
                keys[square][chess.Piece(piece, color)] = random.getrandbits(64)
    keys['castling'] = {side: random.getrandbits(64) for side in chess.COLORS}
    keys['ep'] = {square: random.getrandbits(64) for square in chess.SQUARES}
    return keys

zobrist_keys = init_zobrist_keys()

def get_hash_key(board):
    """
    Generates a Zobrist hash for the given board state.
    """
    h = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            h ^= zobrist_keys[square][piece]
    if board.has_queenside_castling_rights(chess.WHITE):
        h ^= zobrist_keys['castling'][chess.WHITE]
    if board.has_kingside_castling_rights(chess.WHITE):
        h ^= zobrist_keys['castling'][chess.WHITE]
    if board.has_queenside_castling_rights(chess.BLACK):
        h ^= zobrist_keys['castling'][chess.BLACK]
    if board.has_kingside_castling_rights(chess.BLACK):
        h ^= zobrist_keys['castling'][chess.BLACK]
    ep_square = board.ep_square
    if ep_square is not None:
        h ^= zobrist_keys['ep'][ep_square]
    return h
