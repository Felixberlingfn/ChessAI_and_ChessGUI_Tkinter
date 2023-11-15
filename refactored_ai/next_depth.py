from chess import WHITE, PAWN, KNIGHT, BISHOP, ROOK, QUEEN
from typing import Tuple

from refactored_ai.CONSTANTS import CAPTURE_EXTENSION
from refactored_ai import stats
from refactored_ai.CONSTANTS import QUIESCENCE_START, CAPTURE, PROMOTION


def get_next_depth(board, move, depth: int, quiescence_x: any = False, move_type: int = 0) -> Tuple[int, any, float]:
    # gets the next depth of the minimax recursion, based on quiescence and risk

    def calculate_horizon_risk() -> float:
        # because of horizon uncertainty let's not overvalue the capture
        attacker_piece = board.piece_at(move.from_square)  # victim already in material balance
        if attacker_piece.color == WHITE:
            horizon_risk: float = get_piece_value(attacker_piece) * 0.5  # bad for white when subst. later
        else:
            horizon_risk: float = - get_piece_value(attacker_piece) * 0.5  # bad for black when subst. later
        return horizon_risk

    def add_risk_based_extension():
        if quiescence_x > 3:  # already too many extensions
            return False
        # risk threshold based on how many extensions already added
        for i in range(1, 4):
            if quiescence_x == i:
                if risk > i or risk < - i:  # 1=B/N 2=R 3=Q
                    stats.n_extensions += 1
                    return True

    """ 1) default """
    if depth > QUIESCENCE_START:
        return depth - 1, False, 0

    """ 2) end search early checks """
    if depth <= QUIESCENCE_START and depth != 1:
        if move_type in [CAPTURE, PROMOTION]:
            return depth - 1, True, 0
        else:
            stats.n_early_end += 1
            return 0, True, 0

    """ 3) extra quiescence extensions """
    if depth == 1:
        # type capture
        if move_type == CAPTURE:
            risk = calculate_horizon_risk()
            if add_risk_based_extension():
                return 1, quiescence_x + 1, 0
            else:
                return 0, quiescence_x, risk

        # type promotion
        if move_type == PROMOTION and quiescence_x < 5:  # 2 = promotion
            stats.n_extensions += 1
            promotion_risk: float = 0.5 if board.turn == WHITE else -0.5
            return 2, quiescence_x + 1, promotion_risk

        # type calm or gives_check
        return 0, quiescence_x, 0

    """ 4) Default Fallback """
    return depth - 1, quiescence_x, 0


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

