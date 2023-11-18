from chess import WHITE, PAWN, KNIGHT, BISHOP, ROOK, QUEEN
from typing import Tuple

from .CONSTANTS import (HORIZON_RISK_MULTIPLIER, CAPTURE, PROMOTION, EVAL_BASED_QUIESCENCE_START,
                        NEW_THRESHOLDS, REAL_QUIESCENCE_START)
from . import stats


def adjust_depth(board, move, depth: int, real_depth: int = 0, move_type: int = 0,) -> Tuple[int, float, int]:
    """ NORMAL SEARCH IN POSITIVE DEPTH --- QUIESCENCE SEARCH IN NEGATIVE DEPTH """

    def get_capture_risk() -> float:
        attacker_piece = board.piece_at(move.from_square)  # victim already in material balance
        if attacker_piece.color == WHITE:
            return get_piece_value(attacker_piece) * HORIZON_RISK_MULTIPLIER  # bad for white
        else:
            return - get_piece_value(attacker_piece) * HORIZON_RISK_MULTIPLIER  # bad for black

    def get_promotion_risk() -> float:
        if depth == - 1:  # 9 because new queen is at risk, already in material balance
            promotion_risk = 9 * HORIZON_RISK_MULTIPLIER if board.turn == WHITE else - 9 * HORIZON_RISK_MULTIPLIER
            return promotion_risk
        return 0.0

    def is_risk_higher_than_current_threshold():
        """((-4, KNIGHT_THRESH), (-3, ROOK_THRESH), (-2, QUEEN_THRESH))"""
        for depth_for_threshold, threshold in NEW_THRESHOLDS:
            if depth < depth_for_threshold:
                if risk >= threshold or risk <= - threshold:  # 1=B/N 2=R 3=Q
                    return True

    """ default: depth - 1 """
    if depth > 0:
        """ 1) # never start quiescence before this"""
        if real_depth < REAL_QUIESCENCE_START:
            return depth - 1, 0, 0  # Default

        if depth == 1 or stats.n_evaluated_leaf_nodes > EVAL_BASED_QUIESCENCE_START:
            depth = - 11  # Start Quiescence
        else:
            return depth - 1, 0, 0  # Default

    """ default: depth + 1 """
    if depth < 0:

        if depth == - 1:  # quiescence search ends at - 1
            """ in this case always return depth 0 """
            if move_type == PROMOTION: return 0, get_promotion_risk(), - 1
            if move_type == CAPTURE: return 0, get_capture_risk(), - 1
            return 0, 0, - 1  # calm state, unless check

        if move_type == PROMOTION:
            """ always continue - equivalent to queen risk """
            return depth + 1, get_promotion_risk(), 0

        elif move_type == CAPTURE:
            """ continue search """
            if depth < - 9: return depth + 1, 0, 0

            """ Continue based on risk """
            risk = get_capture_risk()
            if is_risk_higher_than_current_threshold():
                return depth + 1, 0, - 1
            else:
                """ threshold not met, stop"""
                return 0, risk, depth + 1  # "calm enough" state

        else:  # stop as we reached a calm state
            return 0, 0, depth + 1

    print(f"Depth: {depth} real depth: {real_depth}  End of adjust depth - if this is printed something is wrong.")


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
