from chess import BLACK, WHITE, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING
from typing import Tuple, List

from .tables_maximizer import history_table_max, killer_moves_max
from .tables_minimizer import history_table_min, killer_moves_min
from .CONSTANTS import CALM, CAPTURE, PROMOTION, DEGRADATION_IMPACT_RATIO
from .piece_sq_pesto import score_piece_positive


def order_moves(board, real_depth, material=0) -> Tuple[List[tuple], int]:
    """in contrast to the evaluate board this is BEFORE the move was made"""
    """ First: Initialization """
    pawn, knight, bishop, rook, queen, king = PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING
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
    def op_victim_value(victim_piece, victim_color, piece_square_64) -> float:
        """ has a side effect on op """
        nonlocal op
        if not victim_piece:  # en passant if capture but no piece currently at to square
            v_piece_type = 1
        else:
            v_piece_type = victim_piece.piece_type
        piece_value = score_piece_positive(v_piece_type, victim_color, piece_square_64)
        op += piece_value + 1  # 1 is just being a move and victim value on top
        return piece_value

    def op_attacker_value(piece_type, aggr_color, from_square) -> float:
        """ has a side effect on op """
        nonlocal op
        value = score_piece_positive(piece_type, aggr_color, from_square)
        op -= (value / 20)  # at most remove 1 from opportunities when attacking with king
        return value

    def op_promotion_value(p_move, promoting_color, square_64) -> float:
        """ has a side effect on op """
        nonlocal op
        # piece_values = {pawn: 1, knight: 3, bishop: 3.33, rook: 5.63, queen: 9.5}
        promotion_type = p_move.promotion

        value = score_piece_positive(promotion_type, promoting_color, square_64)
        op += value
        return value

    def get_material_and_position(moving_piece_type=0, from_square=0, to_square=0, promotion_value=None,
                                  victim_value=None, aggr_value=None, victim_color=None):
        """ currently needs from outer scope: material, turn - no side effects """
        new_material = material

        if victim_value and aggr_value:  # only for captures
            """ degradation: capturing / loosing pieces far in the future is worth less (e.g. 96%)"""
            new_material += ((-victim_value if victim_color == WHITE else victim_value) * degradation)
            value_at_old_position = aggr_value
            value_at_new_position = score_piece_positive(moving_piece_type, turn, to_square)
        elif promotion_value:
            value_at_old_position = score_piece_positive(1, turn, from_square)
            value_at_new_position = promotion_value  # this is either our new queen or new knight
        else:
            value_at_old_position = score_piece_positive(moving_piece_type, turn, from_square)
            value_at_new_position = score_piece_positive(moving_piece_type, turn, to_square)

        """degradation: position improvement far in the future is worth less (e.g. 96%)"""
        position_improvement = (value_at_new_position - value_at_old_position) * degradation
        final_material = new_material + (position_improvement if turn == WHITE else -position_improvement)
        return round(final_material, 2)

    def generate_capture_move_tuples(d_captures) -> List[tuple]:
        """ currently needs access to board, turn from outer scope and has an indirect side effect on op """
        return [
            (
                capture_move,
                capture,
                new_material_and_position,
                victim_value - aggr_value,
                aggr_type,
                aggr_value,
                turn,
                False,
            )
            for capture_move in d_captures
            for from_square in [capture_move.from_square]
            for to_square in [capture_move.to_square]
            for aggressor in [board.piece_at(capture_move.from_square)]
            for aggr_type in [aggressor.piece_type]
            # for aggr_color in [aggressor.color] we know the turn so that is the attacker
            for aggr_value in [op_attacker_value(aggr_type, turn, from_square)]
            for victim in [board.piece_at(to_square)]
            for victim_color in [not turn]
            for victim_value in [op_victim_value(victim, victim_color, to_square)]
            for new_material_and_position in [get_material_and_position(aggr_type, from_square, to_square, 0,
                                                                        victim_value, aggr_value, victim_color)]
        ]

    def generate_promotion_move_tuples(d_promotions) -> List[tuple]:
        """ currently needs access to turn from outer scope, has an indirect side effect on op """
        return [
            (
                promotion_move,
                promotion,
                new_material_and_position,
                False,
                queen,
                promotion_value,
                turn,
                False,
            )
            for promotion_move in d_promotions
            for to_square in [promotion_move.to_square]
            for from_square in [promotion_move.from_square]
            for promotion_value in [op_promotion_value(promotion_move, turn, to_square)]
            for new_material_and_position in [get_material_and_position(1, from_square, to_square,
                                                                        promotion_value)]
        ]

    def op_update_quiet(moving_piece, quiet_move) -> int:
        """ has a side effect on op """
        nonlocal op
        """ check if move might cause loosing castling rights"""
        if moving_piece != king and moving_piece != rook:
            op += 1
            return False
        lost_castling = False
        if board.is_castling(quiet_move):
            op += 2
            """ this is not really loosing castling, we give a tiny reward"""
            lost_castling = 10 if turn == WHITE else - 10  # still needed?
            return lost_castling
        elif board.has_castling_rights(turn):
            op += 1
            """lost castling right, some punishment"""
            lost_castling = 40 if turn == BLACK else - 40  # still needed?
            return lost_castling
        op += 1
        return lost_castling

    def generate_quiet_move_tuples(moves_list, is_king_move=False) -> List[tuple]:
        """ currently needs access to turn and has an indirect side effect on op"""
        return [
            (
                quiet_move,
                calm,
                new_material_and_position,
                False,
                moving_piece,
                None,
                turn,
                lost_castling,
            )
            for quiet_move in moves_list
            for from_square in [quiet_move.from_square]
            for to_square in [quiet_move.to_square]
            for moving_piece in [board.piece_at(quiet_move.from_square).piece_type]
            for lost_castling in [op_update_quiet(moving_piece, quiet_move)]
            for new_material_and_position in [get_material_and_position(moving_piece, from_square, to_square)]
        ]

    d_captures, d_checks, d_promotions, d_killers, d_quiet, d_king = [], [], [], [], [], []

    """ Second: Divide captures, checks, killer moves and quiet moves"""
    for move in moves:
        if board.is_capture(move):
            d_captures.append(move)
        elif move.promotion:  # DO NOT COMBINE THE FOLLOWING CHECKS HERE!
            if move.promotion == queen or move.promotion == knight:
                d_promotions.append(move)  # append only queen and knight promotions, ignore others
        elif move in killers:
            d_killers.append(move)
        else:
            d_quiet.append(move)

    """if board.piece_at(move.from_square).piece_type == king:
            d_king.append(move)"""

    """ add details with list comprehension """
    captures: List[tuple] = generate_capture_move_tuples(d_captures)
    promotions: List[tuple] = generate_promotion_move_tuples(d_promotions)
    quiet_killer_moves: List[tuple] = generate_quiet_move_tuples(d_killers)
    quiet_moves: List[tuple] = generate_quiet_move_tuples(d_quiet)
    checks: List[tuple] = []
    king_moves: List[tuple] = generate_quiet_move_tuples(d_king)

    """ Third: Sorting """
    captures.sort(key=lambda a: a[3], reverse=True)
    if turn == BLACK:
        quiet_moves.sort(key=lambda m: history_table_min[m[0].from_square][m[0].to_square], reverse=True)
    else:
        quiet_moves.sort(key=lambda m: history_table_max[m[0].from_square][m[0].to_square], reverse=True)

    return (checks + promotions + captures + quiet_killer_moves + quiet_moves + king_moves), round(op, 2)


if __name__ == "__main__":
    from chess import Board

    test_board = Board()

    print(order_moves(test_board, 0, 0))