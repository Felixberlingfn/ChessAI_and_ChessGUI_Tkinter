from chess import WHITE, PAWN, KNIGHT, BISHOP, ROOK, QUEEN
from typing import Tuple

from .CONSTANTS import (HORIZON_RISK_MULTIPLIER, CAPTURE, PROMOTION, EVAL_BASED_QUIESCENCE_START,
                        REAL_DEPTH_AND_THRESHOLDS, REAL_QUIESCENCE_START)
from . import stats


def adjust_depth(board, move, depth: int, real_depth: int = 0, move_type: int = 0,) -> Tuple[int, float, int]:
    # adjusts the current depth based on if the last move was capture, promotion, or gave check

    # real_depth_and_qx = ((7, 1), (8, 2), (9, 3))

    """if quiescence_x == 5:
        print(f"{real_depth} : {quiescence_x} : {depth}")  # {check_x} : {make_up_difference}"""

    def calculate_horizon_risk() -> float:
        # because of horizon uncertainty let's not overvalue the capture
        attacker_piece = board.piece_at(move.from_square)  # victim already in material balance
        if attacker_piece.color == WHITE:
            horizon_risk: float = get_piece_value(attacker_piece) * HORIZON_RISK_MULTIPLIER  # bad for white
        else:
            horizon_risk: float = - get_piece_value(attacker_piece) * HORIZON_RISK_MULTIPLIER  # bad for black
        return horizon_risk

    def add_risk_based_extension():
        if real_depth > REAL_DEPTH_AND_THRESHOLDS[2][0]:  # already too many extensions
            return False
        # risk threshold based on how many extensions already added
        for real_depth_limit, threshold in REAL_DEPTH_AND_THRESHOLDS:
            if real_depth < real_depth_limit:
                if risk >= threshold or risk <= - threshold:  # 1=B/N 2=R 3=Q
                    return True

    """ 1) default 
    using a number of evals based quiescence start, and we should at least start quiescence at depth 2"""
    if depth > 2 and stats.n_evaluated_leaf_nodes < EVAL_BASED_QUIESCENCE_START:
        return depth - 1, 0, 0

    """ 2) end search early checks """
    if depth > 1:
        if move_type in [CAPTURE, PROMOTION] or real_depth < REAL_QUIESCENCE_START:  # minimum depth
            return depth - 1, 0, 0
        else:
            difference = depth - 2
            # print(f"{real_depth}: {difference}")
            return 0, 0, difference

    """ 3) extra quiescence extensions """
    """ depth == 1 """
    # type capture
    if move_type == CAPTURE:
        risk = calculate_horizon_risk()
        if add_risk_based_extension():
            return 1, 0, 0
        else:
            return 0, risk, 0

    # type promotion
    if move_type == PROMOTION:
        if real_depth < 10:
            return 1, 0, 0
        else:
            promotion_risk = HORIZON_RISK_MULTIPLIER if board.turn == WHITE else - HORIZON_RISK_MULTIPLIER
            return 0, promotion_risk, 0

    """ 4) Default Fallback """
    return depth - 1, 0, 0


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

