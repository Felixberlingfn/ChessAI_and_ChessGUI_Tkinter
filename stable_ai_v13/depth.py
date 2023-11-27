from chess import WHITE, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING
from typing import Tuple

from .CONSTANTS import (HORIZON_RISK_MULTIPLIER, CAPTURE, PROMOTION, EVAL_BASED_QUIESCENCE_START,
                        RELATIVE_QUIESCENCE_START, NEW_THRESHOLDS, REAL_QUIESCENCE_START,
                        DEGRADATION_IMPACT_RATIO, QUIESCENCE_DEPTH, MAX_EVALS_SHORTEN_QUIESCENCE)
from . import stats


def adjust_depth(move_tuple, depth, real_depth, op, turn) -> Tuple[int, float, int]:
    """
    param: board: chess.Board object
    param: move_tuple: move, move_type, material_balance, vv-aa, attacker_type, victim
    param: depth
    param: op
    description: NORMAL SEARCH IN POSITIVE DEPTH --- QUIESCENCE SEARCH IN NEGATIVE DEPTH
    """
    degradation = 1 - (real_depth / DEGRADATION_IMPACT_RATIO)
    move, move_type, material, _, attacker_type, attacker_value, moving_color, _ = move_tuple
    new_thresholds = NEW_THRESHOLDS

    def get_capture_risk() -> float:
        if moving_color == WHITE:  # same as attacking piece is white
            return attacker_value * HORIZON_RISK_MULTIPLIER  # bad for white
        else:
            return - attacker_value * HORIZON_RISK_MULTIPLIER  # bad for black

    def get_promotion_risk() -> float:
        if depth == - 1:  # 9 because new queen is at risk, already in material balance
            promotion_risk = attacker_value * HORIZON_RISK_MULTIPLIER if moving_color == WHITE else - attacker_value * HORIZON_RISK_MULTIPLIER
            return promotion_risk
        return 0.0

    def is_risk_higher_than_current_threshold() -> bool:
        """((-4, KNIGHT_THRESH), (-3, ROOK_THRESH), (-2, QUEEN_THRESH))"""
        for depth_for_threshold, threshold in new_thresholds:
            if depth < depth_for_threshold:
                if risk >= threshold or risk <= - threshold:  # 1=B/N 2=R 3=Q
                    return True

    """ default: depth - 1 """
    if depth > 0:
        if real_depth == 0:
            """'attacker_type' just means move by if not a capture'"""
            if attacker_type == QUEEN:
                depth += 1
                if op < 3:  # 5
                    depth += 1
            if attacker_type == KING:
                depth += 1  # 2

        """ 1) don't start quiescence start yet (by default 2)"""
        if real_depth < REAL_QUIESCENCE_START:  # real_depth < REAL_QUIESCENCE_START:
            return depth - 1, 0, 0  # Default

        """ it can either be 2 or 1 here, start if 1 or """
        if depth == 1 or stats.n_evaluated_leaf_nodes > EVAL_BASED_QUIESCENCE_START:
            if stats.n_evaluated_leaf_nodes < MAX_EVALS_SHORTEN_QUIESCENCE:
                depth = - QUIESCENCE_DEPTH  # currently - 11
            else:
                depth = - QUIESCENCE_DEPTH + 1
        else:
            return depth - 1, 0, 0

    """ default: depth + 1 """
    if depth < 0:

        if depth == - 1:  # quiescence search ends at - 1
            """ in this case always return depth 0 """
            if move_type == PROMOTION: return 0, get_promotion_risk() * degradation, - 1
            if move_type == CAPTURE: return 0, get_capture_risk() * degradation, - 1
            return 0, 0, - 1  # calm state, unless check

        """this has almost no effect or negative effect and I don't fully understand it
        if material > stats.starting_material_balance + 14 or material < stats.starting_material_balance - 14:
            return 0, 0, 0"""

        if move_type == PROMOTION:
            """ always continue - equivalent to queen risk """
            return depth + 1, get_promotion_risk() * degradation, 0

        elif move_type == CAPTURE:
            """ continue search """
            if depth < - 9: return depth + 1, 0, 0

            """ Continue based on risk """
            risk = get_capture_risk()
            if is_risk_higher_than_current_threshold():
                return depth + 1, 0, - 1
            else:
                """ threshold not met, stop"""
                return 0, risk * degradation, depth + 1  # "calm enough" state

        else:  # stop as we reached a calm state
            return 0, 0, depth + 1

    print(f"You fucked up. Depth: {depth} real depth: {real_depth}")


if __name__ == "__main__":
    """ implement something to test the function here """
    pass