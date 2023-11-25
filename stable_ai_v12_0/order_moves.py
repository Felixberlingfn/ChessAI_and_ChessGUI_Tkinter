from chess import BLACK, WHITE, PAWN, KNIGHT, BISHOP, ROOK, QUEEN
from typing import Tuple, List

from .tables_maximizer import history_table_max, killer_moves_max
from .tables_minimizer import history_table_min, killer_moves_min
from .CONSTANTS import CALM, CAPTURE, PROMOTION, DEGRADATION_IMPACT_RATIO


def order_moves(board, real_depth, material=0) -> Tuple[List[tuple], int]:
    """in contrast to the evaluate board this is BEFORE the move was made"""
    """ First: Initialization """
    moves = board.legal_moves
    if board.turn == BLACK:
        turn = BLACK
        killers = killer_moves_min[real_depth] if killer_moves_min[real_depth] is not None else []  # (depth <= len)
    else:
        turn = WHITE
        killers = killer_moves_max[real_depth] if killer_moves_max[real_depth] is not None else []

    """ op = opportunity score"""
    op = 0

    """calculate material gain/loss degradation (lower probability of future moves)"""
    degradation = 1 - (real_depth / DEGRADATION_IMPACT_RATIO) if real_depth > 2 else 1

    """ Generate move tuples and update opportunity score """
    def op_victim_value_and_update(piece) -> int:
        nonlocal op
        if not piece:  # en passant if capture but nor piece at to square
            op += 1
            return 1
        piece_values = {PAWN: 1, KNIGHT: 3, BISHOP: 3, ROOK: 5, QUEEN: 9}
        piece_value = piece_values.get(piece.piece_type, 0)
        op += piece_value
        return piece_value

    def generate_capture_move_tuples():
        return [
            (
                capture_move,
                CAPTURE,
                material + ((victim_value if victim_color == BLACK else -victim_value) * degradation),
                victim_value - aggr_value,
                aggr_type,
                aggr_value
            )
            for capture_move in d_captures
            for aggressor in [board.piece_at(capture_move.from_square)]
            for aggr_type in [aggressor.piece_type]
            for aggr_value in [get_piece_value_from_type(aggr_type)]
            for victim in [board.piece_at(capture_move.to_square)]
            for victim_color in [not aggressor.color]
            for victim_value in [op_victim_value_and_update(victim)]
        ]

    def op_update_promotion() -> int:
        nonlocal op
        op += 9
        return 9

    def generate_promotion_move_tuples():
        return [
            (
                promotion_move,
                PROMOTION,
                material + 8 if board.piece_at(promotion_move.from_square).color == WHITE else material - 8,
                False,
                QUEEN,
                op_update_promotion()
            )
            for promotion_move in d_promotions
        ]

    def op_update_quiet():
        nonlocal op
        op += 1

    def generate_quiet_move_tuples(passed_moves):
        return [
            (
                quiet_move,
                CALM,
                material,
                False,
                board.piece_at(quiet_move.from_square).piece_type,  # moving_piece
                op_update_quiet()  # mostly just for updating op
            )
            for quiet_move in passed_moves
        ]

    d_captures, d_checks, d_promotions, d_killers, d_quiet = [], [], [], [], []

    """ Second: Divide captures, checks, killer moves and quiet moves"""
    for move in moves:
        if board.is_capture(move):
            d_captures.append(move)
        elif move.promotion and move.promotion == QUEEN:  # ignore other promotions
            d_promotions.append(move)
        elif move in killers:
            d_killers.append(move)
        else:
            d_quiet.append(move)

    """ add details with list comprehension """
    captures: List[tuple] = generate_capture_move_tuples()
    promotions: List[tuple] = generate_promotion_move_tuples()
    quiet_killer_moves: List[tuple] = generate_quiet_move_tuples(d_killers)
    quiet_moves: List[tuple] = generate_quiet_move_tuples(d_quiet)
    checks: List[tuple] = []

    """ Third: Sorting """
    captures.sort(key=lambda a: a[3], reverse=True)
    if turn == BLACK:
        quiet_moves.sort(key=lambda m: history_table_min[m[0].from_square][m[0].to_square], reverse=True)
    else:
        quiet_moves.sort(key=lambda m: history_table_max[m[0].from_square][m[0].to_square], reverse=True)

    return (checks + promotions + captures + quiet_killer_moves + quiet_moves), op


def get_piece_value(piece) -> int:  # expects piece object not piece type
    piece_values = {
        PAWN: 1,
        KNIGHT: 3,
        BISHOP: 3,
        ROOK: 5,
        QUEEN: 9,
    }
    if not piece:
        return 0
    return piece_values.get(piece.piece_type, 0)


def get_piece_value_from_type(piece_type) -> int:  # expects piece object not piece type
    piece_values = {
        PAWN: 1,
        KNIGHT: 3,
        BISHOP: 3,
        ROOK: 5,
        QUEEN: 9,
    }
    return piece_values.get(piece_type, 0)


if __name__ == "__main__":
    from chess import Board

    test_board = Board()

    print(order_moves(test_board, 0, 0))