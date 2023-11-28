from chess import (WHITE, PAWN, KNIGHT, KNIGHT, BISHOP, ROOK,  QUEEN, KING,
                   square_rank, SQUARES, WHITE, square_name)

from .CONSTANTS import POS_BONUS_MULTIPLIER

"""
https://www.chessprogramming.org/Simplified_Evaluation_Function
https://www.chessprogramming.org/Tapered_Eval
"""

good_positions = (
        # MUSTER (index 0)
        (  # A  B   C   D   E   F   G   H
            0,  0,  0,  0,  0,  0,  0,  0,  # 8
            0,  0,  0,  0,  0,  0,  0,  0,  # 7
            0,  0,  0,  0,  0,  0,  0,  0,  # 6
            0,  0,  0,  0,  0,  0,  0,  0,  # 5
            0,  0,  0,  0,  0,  0,  0,  0,  # 4
            0,  0,  0,  0,  0,  0,  0,  0,  # 3
            0,  0,  0,  0,  0,  0,  0,  0,  # 2
            0,  0,  0,  0,  0,  0,  0,  0,  # 1
        ),
        # PAWN (index 1)
        (  # A     B    C    D    E    F    G    H
             0,    0,   0,   0,   0,   0,   0,   0,  # 8
             50,  50,  50,  50,  50,  50,  50,  50,  # 7 Promotion Preparation
             10,  10,  20,  30,  30,  20,  10,  10,  # 6 Promotion Preparation
             5,    5,  10,  25,  25,  10,   5,   5,  # 5 Central Control
             0,    0,   0,  20,  20,   0,   0,   0,  # 4 Central Control
             5,   -5, -10,   0,   0, -10,  -5,   5,  # 3 Protect Castled King
             5,   10,  10, -20, -20,  10,  10,   5,  # 2 Protect Castled King
             0,    0,   0,   0,   0,   0,   0,   0,  # 1
        ),
        # KNIGHT (index 2)
        (  # A    B     C    D    E    F    G    H
            -50, -40, -30, -30, -30, -30, -40,  -50,  # 8
            -40, -20,   0,   0,   0,   0, -20,  -40,  # 7
            -30,   0,  10,  15,  15,  10,   0,  -30,  # 6
            -30,   5,  15,  20,  20,  15,   5,  -30,  # 5
            -30,   0,  15,  20,  20,  15,   0,  -30,  # 4
            -30,   5,  10,  15,  15,  10,   5,  -30,  # 3
            -40, -20,   0,   5,   5,   0, -20,  -40,  # 2
            -50, -40, -30, -30, -30, -30, -40,  -50,  # 1
        ),
        # BISHOP (index 3)
        (  # A     B    C    D    E    F    G    H
            -20, -10, -10, -10, -10, -10, -10, -20,  # 8
            -10,   0,   0,   0,   0,   0,   0, -10,  # 7
            -10,   0,   5,  10,  10,   5,   0, -10,  # 6
            -10,   5,   5,  10,  10,   5,   5, -10,  # 5
            -10,   0,  10,  10,  10,  10,   0, -10,  # 4
            -10,  10,  10,  10,  10,  10,  10, -10,  # 3
            -10,   5,   0,   0,   0,   0,   5, -10,  # 2
            -20, -10, -10, -10, -10, -10, -10, -20,  # 1
        ),
        # ROOK (index 4)
        (  # A    B    C    D    E    F    G    H
             0,   0,   0,   0,   0,   0,   0,   0,  # 8
             5,  10,  10,  10,  10,  10,  10,   5,  # 7
            -5,   0,   0,   0,   0,   0,   0,  -5,  # 6
            -5,   0,   0,   0,   0,   0,   0,  -5,  # 5
            -5,   0,   0,   0,   0,   0,   0,  -5,  # 4
            -5,   0,   0,   0,   0,   0,   0,  -5,  # 3
            -5,   0,   0,   0,   0,   0,   0,  -5,  # 2
             0,   0,   0,   5,   5,   0,   0,   0,  # 1
        ),
        # QUEEN (index 5)
        (  # A    B    C    D    E    F    G    H
            -20, -10, -10, -5, -5, -10, -10, -20,  # 8
            -10,   0,   0,  0,  0,   0,   0, -10,  # 7
            -10,   0,   5,  5,  5,   5,   0, -10,  # 6
             -5,   0,   5,  5,  5,   5,   0,  -5,  # 5
              0,   0,   5,  5,  5,   5,   0,  -5,  # 4
            -10,   5,   5,  5,  5,   5,   0, -10,  # 3
            -10,   0,   5,  0,  0,   0,   0, -10,  # 2
            -20, -10, -10, -5, -5, -10, -10, -20,  # 1
        ),
        # KING (index 6)
        (   # A    B    C    D    E    F    G    H
            -30, -40, -40, -50, -50, -40, -40, -30,  # 8
            -30, -40, -40, -50, -50, -40, -40, -30,  # 7
            -30, -40, -40, -50, -50, -40, -40, -30,  # 6
            -30, -40, -40, -50, -50, -40, -40, -30,  # 5
            -20, -30, -30, -40, -40, -30, -30, -20,  # 4
            -10, -20, -20, -20, -20, -20, -20, -10,  # 3
             20,  20,   0,   0,   0,   0,  20,  20,  # 2
             20,  30,  10,   0,   0,  10,  30,  20,  # 1
        ),
    )

endgame_good_positions = (
        # MUSTER (index 0)
        (  # A  B   C   D   E   F   G   H
            0,  0,  0,  0,  0,  0,  0,  0,  # 8
            0,  0,  0,  0,  0,  0,  0,  0,  # 7
            0,  0,  0,  0,  0,  0,  0,  0,  # 6
            0,  0,  0,  0,  0,  0,  0,  0,  # 5
            0,  0,  0,  0,  0,  0,  0,  0,  # 4
            0,  0,  0,  0,  0,  0,  0,  0,  # 3
            0,  0,  0,  0,  0,  0,  0,  0,  # 2
            0,  0,  0,  0,  0,  0,  0,  0,  # 1
        ),
        # PAWN (index 1)
        (   # A    B    C    D    E    F    G    H
            100, 100, 100, 100, 100, 100, 100, 100,  # 8
            150, 150, 150, 150, 150, 150, 150, 150,  # 7 Promotion Preparation
            110, 110, 120, 130, 130, 120, 110, 110,  # 6 Promotion Preparation
            105, 105, 110, 125, 125, 110, 105, 105,  # 5 Central Control
            100, 100, 100, 120, 120, 110, 110, 110,  # 4 Central Control
            105,  95,  90, 100, 100,  90,  95, 105,  # 3 Protect Castled King
            105, 110, 110,  80,  80, 110, 110, 105,  # 2 Protect Castled King
            100, 100, 100, 100, 100, 100, 100, 100,  # 1
        ),
        # KNIGHT (index 2)
        (   # A    B    C    D    E    F    G    H
            100, 100, 100, 100, 100, 100, 100, 100,  # 8
            150, 150, 150, 150, 150, 150, 150, 150,  # 7
            110, 110, 120, 130, 130, 120, 110, 110,  # 6
            105, 105, 110, 125, 125, 110, 105, 105,  # 5
            100, 100, 100, 120, 120, 110, 110, 110,  # 4
            105,  95,  90, 100, 100,  90,  95, 105,  # 3
            105, 110, 110,  80,  80, 110, 110, 105,  # 2
            100, 100, 100, 100, 100, 100, 100, 100,  # 1
        ),
        # BISHOP (index 3)
        (   # A    B    C    D    E    F    G    H
            100, 100, 100, 100, 100, 100, 100, 100,  # 8
            150, 150, 150, 150, 150, 150, 150, 150,  # 7
            110, 110, 120, 130, 130, 120, 110, 110,  # 6
            105, 105, 110, 125, 125, 110, 105, 105,  # 5
            100, 100, 100, 120, 120, 110, 110, 110,  # 4
            105,  95,  90, 100, 100,  90,  95, 105,  # 3
            105, 110, 110,  80,  80, 110, 110, 105,  # 2
            100, 100, 100, 100, 100, 100, 100, 100,  # 1
        ),
        # ROOK (index 4)
        (   # A    B    C    D    E    F    G    H
            100, 100, 100, 100, 100, 100, 100, 100,  # 8
            150, 150, 150, 150, 150, 150, 150, 150,  # 7
            110, 110, 120, 130, 130, 120, 110, 110,  # 6
            105, 105, 110, 125, 125, 110, 105, 105,  # 5
            100, 100, 100, 120, 120, 110, 110, 110,  # 4
            105,  95,  90, 100, 100,  90,  95, 105,  # 3
            105, 110, 110,  80,  80, 110, 110, 105,  # 2
            100, 100, 100, 100, 100, 100, 100, 100,  # 1
        ),
        # QUEEN (index 5)
        (   # A    B    C    D    E    F    G    H
            100, 100, 100, 100, 100, 100, 100, 100,  # 8
            150, 150, 150, 150, 150, 150, 150, 150,  # 7
            110, 110, 120, 130, 130, 120, 110, 110,  # 6
            105, 105, 110, 125, 125, 110, 105, 105,  # 5
            100, 100, 100, 120, 120, 110, 110, 110,  # 4
            105,  95,  90, 100, 100,  90,  95, 105,  # 3
            105, 110, 110,  80,  80, 110, 110, 105,  # 2
            100, 100, 100, 100, 100, 100, 100, 100,  # 1
        ),
        # KING (index 6)
        (   # A    B    C    D    E    F    G    H
            -50, -40, -30, -20, -20, -30, -40, -50,  # 8
            -30, -20, -10,   0,   0, -10, -20, -30,  # 7
            -30, -10,  20,  30,  30,  20, -10, -30,  # 6
            -30, -10,  30,  40,  40,  30, -10, -30,  # 5
            -30, -10,  30,  40,  40,  30, -10, -30,  # 4
            -30, -10,  20,  30,  30,  20, -10, -30,  # 3
            -30, -30,   0,   0,   0,   0, -30, -30,  # 2
            -50, -30, -30, -30, -30, -30, -30, -50,  # 1
        ),
    )

piece_values = {PAWN: 1, KNIGHT: 3, BISHOP: 3.33, ROOK: 5.63, QUEEN: 9.5}
piece_values_with_king = {PAWN: 1, KNIGHT: 3, BISHOP: 3.33, ROOK: 5.63, QUEEN: 9.5, KING: 10}


def piece_value(piece_type):
    piece_values.get(piece_type, 0)


def index_from_64(chess_square):
    # return chess_square - 56 + 16 * (7 - (chess_square // 8))
    # return chess_square - 56 + 16 * (7 - square_rank(chess_square))
    # return chess_square + 56 - 16 * (chess_square // 8)
    return chess_square + 56 - 16 * square_rank(chess_square)


indexes = [index_from_64(sq) for sq in SQUARES]


def score_board(board) -> float:
    """
    :param board: chess.Board object
    """
    score = 0

    for square_64, piece in board.piece_map().items():
        piece_type: int = piece.piece_type

        if piece.color == WHITE:
            index: int = indexes[square_64]
            piece_position_score = good_positions[piece_type][index] + piece_value(piece_type)
            score -= piece_position_score
        else:
            piece_position_score = good_positions[piece_type][square_64] + piece_value(piece_type)
            score += piece_position_score

    return score


def score_piece(piece_type, piece_color, piece_square) -> float:
    """ get the positional score for a specific piece
    :param piece_type
    :param piece_color
    :param piece_square
    """
    # if not piece: return 0 piece_type = piece.piece_type

    if not piece_type:
        return 0

    if piece_color == WHITE:
        index: int = indexes[piece_square]
        return good_positions[piece_type][index]
    else:
        return good_positions[piece_type][piece_square]


if __name__ == "__main__":

    for square in SQUARES:
        # print(square, square_name(square), index_from_64(square))
        # print(square, square_name(square), indexes[square])
        print("WHITE:", good_positions[0][indexes[square]], good_positions[1][indexes[square]] )
        print("BLACK:", good_positions[0][square], good_positions[1][indexes[square]])

