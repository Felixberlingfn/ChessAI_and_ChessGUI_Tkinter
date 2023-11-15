from chess import WHITE, PAWN, KNIGHT, BISHOP, ROOK, QUEEN
from typing import Tuple

from stable_ai.CONSTANTS import CAPTURE_EXTENSION
from stable_ai import stats


def get_next_depth(board, move, depth: int, quiescence_x: any = False, move_type: int = 0) -> Tuple[int, any, float]:
    # gets the depth of the next minimax recursion
    # taking into account depth extension, quiescence and a horizon risk

    def calculate_horizon_risk(promotion=False) -> float:
        if not promotion:
            # because of horizon uncertainty let's not overvalue the capture/loss
            attacker_piece = board.piece_at(move.from_square)  # victim already in material balance
            if attacker_piece.color == WHITE:
                horizon_risk: float = get_piece_value(attacker_piece) * 0.5  # bad for white when subst. later
            else:
                horizon_risk: float = - get_piece_value(attacker_piece) * 0.5  # bad for black when subst. later
            return horizon_risk
        else:
            if board.turn == WHITE:  # white is promoting
                horizon_risk: float = 0.5
            else:
                horizon_risk: float = -0.5
            return horizon_risk

    # default
    if not quiescence_x and depth != 1:
        # we are not doing quiescence search yet and have not yet reached final move
        return depth - 1, False, 0  # quiet_search=False

    """ start quiescence search """
    """ maybe I should switch to 2 so that if you loose a piece the search is also extended
    (might not be so bad in the long run)"""
    # we have reached the final move - check if we should start quiescence search
    if not quiescence_x and depth == 1:
        # we are reaching final node and are not yet performing quiescence search
        if move_type in [1, 2]:  # 1=capture, 2=promo, 3=check is tested by is_check
            stats.n_extensions += CAPTURE_EXTENSION  # just for stats
            return (depth + CAPTURE_EXTENSION), True, 0  # quiet_search=True starts quiescence search
        else:
            return 0, False, 0

    """ end quiescence search early """
    # check if we should end quiescence search
    if quiescence_x and depth != 1:
        # I know gives_check is expensive but here it is checked less often
        if move_type in [1, 2]:    # 1=capture, 2=promo, 3=check
            # we don't need board.gives_check(move) because otherwise we extend with is_check
            return depth - 1, quiescence_x, 0  # continue quiet_search
        else:
            """ unless this causes a check this ends quiescence search """
            return 0, quiescence_x, 0

    """ final quiescence extensions called only when first search reaches end """
    if depth == 1 and quiescence_x:

        " extend high value captures "
        if move_type == 1 and quiescence_x < 6:    # 1=capture, 2=promo, 3=check
            risk = calculate_horizon_risk()

            """if quiescence_x < 2 and (risk == 0.5 or risk == -0.5):  # > 0.5 = pawn
                stats.n_extensions += 1
                return 1, quiescence_x + 1, 0"""

            if quiescence_x < 3 and (risk > 1 or risk < -1):  # > 1 = bishop/horse
                """ extra (second) quiescence extension when more than bishop capture"""
                stats.n_extensions += 1
                return 1, quiescence_x + 1, 0

            elif quiescence_x < 4 and (risk > 2 or risk < -2):    # > 2 = rook
                """ extra (third) quiescence extension when more than rook capture """
                stats.n_extensions += 1
                return 1, quiescence_x + 1, 0

            elif quiescence_x < 5 and (risk > 4 or risk < -4):  # > 4 = queen
                """ extra (fourth) quiescence extension when queen capture """
                stats.n_extensions += 1
                return 1, quiescence_x + 1, 0

            """ too many extensions, evaluate with horizon risk value (50% of attacker value) """
            return 0, quiescence_x, risk

        """ extend promotions too """
        if move_type == 2 and quiescence_x < 5:  # 2 = promotion
            stats.n_extensions += 1
            return 2, quiescence_x + 1, 0

        """ unless this causes a check this ends quiescence search """
        return 0, quiescence_x, 0

    # quiescence default
    return depth-1, quiescence_x, 0  # quiet_search=True


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


"""def has_threats() -> bool:
    # Get the position of high value pieces
    critical_sqs_white: set = board.pieces(QUEEN, WHITE) | board.pieces(ROOK, WHITE)
    critical_sqs_black: set = board.pieces(QUEEN, BLACK) | board.pieces(ROOK, BLACK)

    for critical_sq_w in critical_sqs_white:
        if board.is_attacked_by(BLACK, critical_sq_w):
            return True
    for critical_sq_b in critical_sqs_black:
        if board.is_attacked_by(WHITE, critical_sq_b):
            return True
    return False"""


# print(PAWN)
# print(KNIGHT)
# print(BISHOP)
# print(ROOK)
# print(QUEEN)
