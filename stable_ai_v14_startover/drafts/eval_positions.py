from chess import (PAWN, KNIGHT, KNIGHT, BISHOP, ROOK,  QUEEN, KING,
                   square_rank, SQUARES, WHITE, square_name,
                   E1, E8,)

from stable_ai_v14_lazy.CONSTANTS import POS_BONUS_MULTIPLIER

"""https://www.chessprogramming.org/Simplified_Evaluation_Function"""

good_positions = (
        # MUSTER (index 0)
        (
            # BLACK (index 0)
            (  # A   B   C   D   E   F   G   H
                -1, -1, -1, -1, -1, -1, -1, -1,  # 8
                -1, -1, -1, -1, -1, -1, -1, -1,  # 7
                -1, -1, -1, -1, -1, -1, -1, -1,  # 6
                -1, -1, -1, -1, -1, -1, -1, -1,  # 5
                -1, -1, -1, -1, -1, -1, -1, -1,  # 4
                -1, -1, -1, -1, -1, -1, -1, -1,  # 3
                -1, -1, -1, -1, -1, -1, -1, -1,  # 2
                -1, -1, -1, -1, -1, -1, -1, -1,  # 1
            ),
            # WHITE (index 1)
            (  # A   B   C   D   E   F   G   H
                 1,  1,  1,  1,  1,  1,  1,  1,  # 8
                 1,  1,  1,  1,  1,  1,  1,  1,  # 7
                 1,  1,  1,  1,  1,  1,  1,  1,  # 6
                 1,  1,  1,  1,  1,  1,  1,  1,  # 5
                 1,  1,  1,  1,  1,  1,  1,  1,  # 4
                 1,  1,  1,  1,  1,  1,  1,  1,  # 3
                 1,  1,  1,  1,  1,  1,  1,  1,  # 2
                 1,  1,  1,  1,  1,  1,  1,  1,  # 1
            ),
            # TEST (index 2)
            (  # A     B     C     D     E     F     G     H
                "A8", "B8", "C8", "D8", "E8", "F8", "G8", "H8",  # 8
                "G7", "B7", "C7", "D7", "E7", "F7", "G7", "H7",  # 7
                "G6", "B6", "C6", "D6", "E6", "F6", "G6", "H6",  # 6
                "G5", "B5", "C5", "D5", "E5", "F5", "G5", "H5",  # 5
                "G4", "B4", "C4", "D4", "E4", "F4", "G4", "H4",  # 4
                "G3", "B3", "C3", "D3", "E3", "F3", "G3", "H3",  # 3
                "G2", "B2", "C2", "D2", "E2", "F2", "G2", "H2",  # 2
                "G1", "B1", "C1", "D1", "E1", "F1", "G1", "H1",  # 1
            ),
        ),
        # PAWN (index 1)
        (
            # BLACK PAWN (index 0)
            (  # A    B    C    D    E    F    G   H
                 0,   0,   0,   0,   0,   0,   0,  0,  # 8
                -5, -10, -10,  20,  20, -10, -10, -5,  # 7 Protect Castled King
                -5,   5,  10,   0,   0,  10,   5, -5,  # 6 Protect Castled King
                 0,   0,   0, -20, -20,   0,   0,  0,  # 5 Central Control
                -5,  -5, -10, -25, -25, -10,  -5, -5,  # 4 Central Control
                -10,-10, -20, -30, -30, -20, -10,-10,  # 3 Promotion Preparation
                -50,-50, -50, -50, -50, -50, -50,-50,  # 2 Promotion Preparation
                 0,   0,   0,   0,   0,   0,   0,  0,  # 1
            ),
            # WHITE PAWN (index 1)
            (  # A    B   C   D   E   F   G   H
                 0,   0,  0,  0,  0,  0,  0,  0,  # 8
                 50, 50, 50, 50, 50, 50, 50, 50,  # 7 Promotion Preparation
                 10, 10, 20, 30, 30, 20, 10, 10,  # 6 Promotion Preparation
                 5,   5, 10, 25, 25, 10,  5,  5,  # 5 Central Control
                 0,   0,  0, 20, 20,  0,  0,  0,  # 4 Central Control
                 5,  -5,-10,  0,  0,-10, -5,  5,  # 3 Protect Castled King
                 5,  10, 10,-20,-20, 10, 10,  5,  # 2 Protect Castled King
                 0,   0,  0,  0,  0,  0,  0,  0,  # 1
            ),
            # PAWN (material value) (index 1)
            (  # A    B    C    D    E    F    G    H
                100, 100, 100, 100, 100, 100, 100, 100,  # 8
                150, 150, 150, 150, 150, 150, 150, 150,  # 7 Promotion Preparation
                110, 110, 120, 130, 130, 120, 110, 110,  # 6 Promotion Preparation
                105, 105, 110, 125, 125, 110, 105, 105,  # 5 Central Control
                100, 100, 100, 120, 120, 110, 110, 110,  # 4 Central Control
                105,  95,  90, 100, 100,  90,  95, 105,  # 3 Protect Castled King
                105, 110, 110,  80,  80, 110, 110, 105,  # 2 Protect Castled King
                100, 100, 100, 100, 100, 100, 100, 100,  # 1
            ),
        ),
        # KNIGHT (index 2)
        (
            # BLACK (index 0)
            (  # A   B   C   D   E   F   G   H
                -1, -1, -1, -1, -1, -1, -1, -1,  # 8
                -1, -1, -1, -1, -1, -1, -1, -1,  # 7
                -1, -1, -1, -1, -1, -1, -1, -1,  # 6
                -1, -1, -1, -1, -1, -1, -1, -1,  # 5
                -1, -1, -1, -1, -1, -1, -1, -1,  # 4
                -1, -1, -1, -1, -1, -1, -1, -1,  # 3
                -1, -1, -1, -1, -1, -1, -1, -1,  # 2
                -1, -1, -1, -1, -1, -1, -1, -1,  # 1
            ),
            # WHITE (index 1)
            (  # A   B   C   D   E   F   G   H
                 1,  1,  1,  1,  1,  1,  1,  1,  # 8
                 1,  1,  1,  1,  1,  1,  1,  1,  # 7
                 1,  1,  1,  1,  1,  1,  1,  1,  # 6
                 1,  1,  1,  1,  1,  1,  1,  1,  # 5
                 1,  1,  1,  1,  1,  1,  1,  1,  # 4
                 1,  1,  1,  1,  1,  1,  1,  1,  # 3
                 1,  1,  1,  1,  1,  1,  1,  1,  # 2
                 1,  1,  1,  1,  1,  1,  1,  1,  # 1
            ),
        ),
        # BISHOP (index 3)
        (
            # BLACK (index 0)
            (  # A   B   C   D   E   F   G   H
                -1, -1, -1, -1, -1, -1, -1, -1,  # 8
                -1, -1, -1, -1, -1, -1, -1, -1,  # 7
                -1, -1, -1, -1, -1, -1, -1, -1,  # 6
                -1, -1, -1, -1, -1, -1, -1, -1,  # 5
                -1, -1, -1, -1, -1, -1, -1, -1,  # 4
                -1, -1, -1, -1, -1, -1, -1, -1,  # 3
                -1, -1, -1, -1, -1, -1, -1, -1,  # 2
                -1, -1, -1, -1, -1, -1, -1, -1,  # 1
            ),
            # WHITE (index 1)
            (  # A   B   C   D   E   F   G   H
                 1,  1,  1,  1,  1,  1,  1,  1,  # 8
                 1,  1,  1,  1,  1,  1,  1,  1,  # 7
                 1,  1,  1,  1,  1,  1,  1,  1,  # 6
                 1,  1,  1,  1,  1,  1,  1,  1,  # 5
                 1,  1,  1,  1,  1,  1,  1,  1,  # 4
                 1,  1,  1,  1,  1,  1,  1,  1,  # 3
                 1,  1,  1,  1,  1,  1,  1,  1,  # 2
                 1,  1,  1,  1,  1,  1,  1,  1,  # 1
            ),
        ),
        # ROOK (index 4)
        (
            # BLACK (index 0)
            (  # A   B   C   D   E   F   G   H
                -1, -1, -1, -1, -1, -1, -1, -1,  # 8
                -1, -1, -1, -1, -1, -1, -1, -1,  # 7
                -1, -1, -1, -1, -1, -1, -1, -1,  # 6
                -1, -1, -1, -1, -1, -1, -1, -1,  # 5
                -1, -1, -1, -1, -1, -1, -1, -1,  # 4
                -1, -1, -1, -1, -1, -1, -1, -1,  # 3
                -1, -1, -1, -1, -1, -1, -1, -1,  # 2
                -1, -1, -1, -1, -1, -1, -1, -1,  # 1
            ),
            # WHITE (index 1)
            (  # A   B   C   D   E   F   G   H
                 1,  1,  1,  1,  1,  1,  1,  1,  # 8
                 1,  1,  1,  1,  1,  1,  1,  1,  # 7
                 1,  1,  1,  1,  1,  1,  1,  1,  # 6
                 1,  1,  1,  1,  1,  1,  1,  1,  # 5
                 1,  1,  1,  1,  1,  1,  1,  1,  # 4
                 1,  1,  1,  1,  1,  1,  1,  1,  # 3
                 1,  1,  1,  1,  1,  1,  1,  1,  # 2
                 1,  1,  1,  1,  1,  1,  1,  1,  # 1
            ),
        ),
        # QUEEN (index 5)
        (
            # BLACK (index 0)
            (  # A   B   C   D   E   F   G   H
                -1, -1, -1, -1, -1, -1, -1, -1,  # 8
                -1, -1, -1, -1, -1, -1, -1, -1,  # 7
                -1, -1, -1, -1, -1, -1, -1, -1,  # 6
                -1, -1, -1, -1, -1, -1, -1, -1,  # 5
                -1, -1, -1, -1, -1, -1, -1, -1,  # 4
                -1, -1, -1, -1, -1, -1, -1, -1,  # 3
                -1, -1, -1, -1, -1, -1, -1, -1,  # 2
                -1, -1, -1, -1, -1, -1, -1, -1,  # 1
            ),
            # WHITE (index 1)
            (  # A   B   C   D   E   F   G   H
                 1,  1,  1,  1,  1,  1,  1,  1,  # 8
                 1,  1,  1,  1,  1,  1,  1,  1,  # 7
                 1,  1,  1,  1,  1,  1,  1,  1,  # 6
                 1,  1,  1,  1,  1,  1,  1,  1,  # 5
                 1,  1,  1,  1,  1,  1,  1,  1,  # 4
                 1,  1,  1,  1,  1,  1,  1,  1,  # 3
                 1,  1,  1,  1,  1,  1,  1,  1,  # 2
                 1,  1,  1,  1,  1,  1,  1,  1,  # 1
            ),
        ),
        # KING (index 6)
        (
            # BLACK (index 0)
            (  # A   B   C   D   E   F   G   H
                -1, -1, -1, -1, -1, -1, -1, -1,  # 8
                -1, -1, -1, -1, -1, -1, -1, -1,  # 7
                -1, -1, -1, -1, -1, -1, -1, -1,  # 6
                -1, -1, -1, -1, -1, -1, -1, -1,  # 5
                -1, -1, -1, -1, -1, -1, -1, -1,  # 4
                -1, -1, -1, -1, -1, -1, -1, -1,  # 3
                -1, -1, -1, -1, -1, -1, -1, -1,  # 2
                -1, -1, -1, -1, -1, -1, -1, -1,  # 1
            ),
            # WHITE (index 1)
            (  # A   B   C   D   E   F   G   H
                 1,  1,  1,  1,  1,  1,  1,  1,  # 8
                 1,  1,  1,  1,  1,  1,  1,  1,  # 7
                 1,  1,  1,  1,  1,  1,  1,  1,  # 6
                 1,  1,  1,  1,  1,  1,  1,  1,  # 5
                 1,  1,  1,  1,  1,  1,  1,  1,  # 4
                 1,  1,  1,  1,  1,  1,  1,  1,  # 3
                 1,  1,  1,  1,  1,  1,  1,  1,  # 2
                 1,  1,  1,  1,  1,  1,  1,  1,  # 1
            ),
        ),
    )


def index_from_64(chess_square):
    # return chess_square - 56 + 16 * (7 - (chess_square // 8))
    # return chess_square - 56 + 16 * (7 - square_rank(chess_square))
    # return chess_square + 56 - 16 * (chess_square // 8)
    return chess_square + 56 - 16 * square_rank(chess_square)


indexes = [index_from_64(sq) for sq in SQUARES]


def get_position_score_board(board) -> float:
    """
    :param board: chess.Board object
    """
    score = 0
    # new easier maybe faster
    score_new = 0

    for square_64, piece in board.piece_map().items():
        piece_type: int = piece.piece_type
        color_index: int = int(piece.color)
        index: int = indexes[square_64]
        score_new += good_positions[piece_type][color_index][index]

    return score * POS_BONUS_MULTIPLIER


def get_position_score_piece(piece_type, piece_color, piece_square) -> float:
    """ get the positional score for a specific piece
    :param piece_type
    :param piece_color
    :param piece_square
    """

    if not piece_type:
        return 0

    if piece_color == WHITE:
        index: int = indexes[piece_square]
        return good_positions[piece_type][1][index]
    else:
        return good_positions[piece_type][1][piece_square]


def get_positional_piece_value(piece_type, piece_color, piece_square) -> float:
    """ get the positional score for a specific piece
    :param piece_type
    :param piece_color
    :param piece_square
    """
    piece_value_positional = 0

    index: int = indexes[piece_square]

    if piece_color == WHITE:
        piece_value_positional += good_positions[piece_type][2][index]
    else:
        piece_value_positional -= good_positions[piece_type][2][piece_square]

    return piece_value_positional

if __name__ == "__main__":

    print("WHITE:", good_positions[0][2][indexes[E1]])
    print("BLACK:", good_positions[0][2][E8])

    """for square in SQUARES:
        # print(square, square_name(square), index_from_64(square))
        # print(square, square_name(square), indexes[square])
        print("WHITE:", good_positions[0][2][indexes[square]], good_positions[1][1][indexes[square]] )
        print("BLACK:", good_positions[0][2][square], good_positions[1][1][indexes[square]])"""

