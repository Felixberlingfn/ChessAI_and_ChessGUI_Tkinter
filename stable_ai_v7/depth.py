from chess import BLACK, WHITE, PAWN, KNIGHT, BISHOP, ROOK, QUEEN
from typing import Tuple

from .CONSTANTS import (HORIZON_RISK_MULTIPLIER, CAPTURE, PROMOTION, EVAL_BASED_QUIESCENCE_START,
                        REAL_DEPTH_AND_THRESHOLDS, REAL_QUIESCENCE_START, CHECK_X_LIMITER,
                        KNIGHT_THRESH)
from . import stats


def adjust_depth(board, move, depth: int, real_depth: int = 0, move_type: int = 0,) -> Tuple[int, float, int]:
    # adjusts the current depth based on if the last move was capture, promotion, or gave check

    # real_depth_and_qx = ((7, 1), (8, 2), (9, 3))

    """ CHANGE ALL THIS TO MAKE NORMAL SEARCH IN POSITIVE DEPTH; THEN QUIESCENCE SEARCH
    IN NEGATIVE DEPTH, THAT WILL MAKE THE WHOLE LOGIC EASIER. WHEN STARTING QUIESCENCE
    SIMPLY SET THE DEPTH TO FOR EXAMPLE -7 AND IN QUIESCEN COUNT UP INSTEAD OF DOWN"""


    def calculate_horizon_risk() -> float:
        # because of horizon uncertainty let's not overvalue the capture
        attacker_piece = board.piece_at(move.from_square)  # victim already in material balance
        if attacker_piece.color == WHITE:
            horizon_risk: float = get_piece_value(attacker_piece) * HORIZON_RISK_MULTIPLIER  # bad for white
        else:
            horizon_risk: float = - get_piece_value(attacker_piece) * HORIZON_RISK_MULTIPLIER  # bad for black
        return horizon_risk

    def add_risk_based_extension():
        """REAL_DEPTH_AND_THRESHOLDS =
        ((7 + 0, KNIGHT_THRESH), (7 + 2, ROOK_THRESH), (7 + 4, QUEEN_THRESH))

        INSTEAD OF REAL DEPTH: QUIESCENCE STARTS IN NEGATIVE DEPTH
        E.G.:
        ((-7, NO_THRESH),(-7, KNIGHT_THRESH), (-7 + 2, ROOK_THRESH), (-7 + 4, QUEEN_THRESH))
"""
        new_thresholds = ((-7, 0), (-7, KNIGHT_THRESH), (-7 + 2, ROOK_THRESH), (-7 + 4, QUEEN_THRESH))
        if real_depth > REAL_DEPTH_AND_THRESHOLDS[2][0]:  # already too many extensions
            return False
        # risk threshold based on how many extensions already added
        for real_depth_limit, threshold in REAL_DEPTH_AND_THRESHOLDS:
            if real_depth < real_depth_limit:
                if risk >= threshold or risk <= - threshold:  # 1=B/N 2=R 3=Q
                    return True

    """ 1) # never start quiescence before this"""
    if real_depth < REAL_QUIESCENCE_START:
        return depth - 1, 0, 1

    """ 1 B) Start quiescence if limit of nodes reached or when we reach X"""
    if depth > 3 and stats.n_evaluated_leaf_nodes < EVAL_BASED_QUIESCENCE_START:
        return depth - 1, 0, 1

    """ 2) end search early checks (simple quiescence without risk, just continue if capture or promotion)"""
    if depth > 1:
        if move_type in [CAPTURE, PROMOTION]:
            return depth - 1, 0, 1
        else:
            return 0, 0, depth - 1

    """ 2 B)"""
    """if depth == 1 and real_depth < CHECK_X_LIMITER and stats.n_evaluated_leaf_nodes < EVAL_BASED_QUIESCENCE_START:
        if move_type in [CAPTURE, PROMOTION]:
            return 1, 0, 1"""

    """ 3) extra quiescence extensions """
    """ depth == 1 """
    # type capture
    if move_type == CAPTURE:
        risk = calculate_horizon_risk()
        if add_risk_based_extension():
            return 1, 0, 1
        else:
            return 0, risk, 1

    # type promotion
    if move_type == PROMOTION:
        if real_depth < 14:
            return 1, 0, 1
        else:
            promotion_risk = HORIZON_RISK_MULTIPLIER if board.turn == WHITE else - HORIZON_RISK_MULTIPLIER
            return 0, promotion_risk, 1

    """ 4) Default Fallback """
    return depth - 1, 0, 1


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

