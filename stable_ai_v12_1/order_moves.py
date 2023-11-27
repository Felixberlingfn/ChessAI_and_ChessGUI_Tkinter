from chess import BLACK, WHITE, PAWN, KNIGHT, BISHOP, ROOK, QUEEN
from typing import Tuple, List

from .tables_maximizer import history_table_max, killer_moves_max
from .tables_minimizer import history_table_min, killer_moves_min
from .CONSTANTS import CALM, CAPTURE, PROMOTION, DEGRADATION_IMPACT_RATIO


def order_moves(board, real_depth, material=0) -> Tuple[List[tuple], int]:
    """in contrast to the evaluate board this is BEFORE the move was made"""
    """ First: Initialization """
    pawn, knight, bishop, rook, queen = PAWN, KNIGHT, BISHOP, ROOK, QUEEN
    capture, calm, promotion = CAPTURE, CALM, PROMOTION

    moves = board.legal_moves
    if board.turn == BLACK:
        turn = BLACK
        killers = killer_moves_min[real_depth] if killer_moves_min[real_depth] is not None else []  # (depth <= len)
    else:
        turn = WHITE
        killers = killer_moves_max[real_depth] if killer_moves_max[real_depth] is not None else []

    """ op = opportunity score"""
    op = 0

    #  op_mutable = [0]  # this would allow me to put the functions outside the scope

    """calculate material gain/loss degradation (lower probability of future moves)"""
    degradation = 1 - (real_depth / DEGRADATION_IMPACT_RATIO) if real_depth > 2 else 1

    """ Generate move tuples and update opportunity score """
    def op_victim_value(piece) -> float:
        nonlocal op
        if not piece:  # en passant if capture but no piece at to square
            op += 2  # 1 is just being a move and victim value on top
            return 1
        piece_values = {pawn: 1, knight: 3, bishop: 3.33, rook: 5.63, queen: 9.5}
        piece_value = piece_values.get(piece.piece_type, 0)
        op += piece_value + 1  # 1 is just being a move and victim value on top
        return piece_value

    def op_attacker_value(piece_type) -> float:  # expects piece type
        nonlocal op
        piece_values = {pawn: 1, knight: 3, bishop: 3.33, rook: 5.63, queen: 9.5}
        value = piece_values.get(piece_type, 0)
        op -= value / 9.5  # at most remove 1 from opportunities when attacking with queen
        return value

    def op_promotion_value(p_move) -> float:
        nonlocal op
        piece_values = {pawn: 1, knight: 3, bishop: 3.33, rook: 5.63, queen: 9.5}
        value = piece_values.get(p_move.promotion, 0)
        op += value
        return value - 1  # you loose the promoting pawn

    def generate_capture_move_tuples(d_captures) -> List[tuple]:
        return [
            (
                capture_move,
                capture,
                material + ((victim_value if victim_color == BLACK else -victim_value) * degradation),
                victim_value - aggr_value,
                aggr_type,
                aggr_value
            )
            for capture_move in d_captures
            for aggressor in [board.piece_at(capture_move.from_square)]
            for aggr_type in [aggressor.piece_type]
            for aggr_value in [op_attacker_value(aggr_type)]
            for victim in [board.piece_at(capture_move.to_square)]
            for victim_color in [not aggressor.color]
            for victim_value in [op_victim_value(victim)]
        ]

    def generate_promotion_move_tuples() -> List[tuple]:
        return [
            (
                promotion_move,
                promotion,
                material + promotion_value if promoting_color == WHITE else material - promotion_value,
                False,
                queen,
                promotion_value
            )
            for promotion_move in d_promotions
            for promotion_value in [op_promotion_value(promotion_move)]
            for promoting_color in [board.piece_at(promotion_move.from_square).color]
        ]

    def op_update_quiet() -> None:
        nonlocal op
        op += 1

    def generate_quiet_move_tuples(passed_moves) -> List[tuple]:
        return [
            (
                quiet_move,
                calm,
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
        elif move.promotion:
            if move.promotion == queen or move.promotion == knight:
                d_promotions.append(move)
        elif move in killers:
            d_killers.append(move)
        else:
            d_quiet.append(move)

    """ add details with list comprehension """
    captures: List[tuple] = generate_capture_move_tuples(d_captures)
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

    return (checks + promotions + captures + quiet_killer_moves + quiet_moves), round(op, 2)


if __name__ == "__main__":
    from chess import Board

    test_board = Board()

    print(order_moves(test_board, 0, 0))