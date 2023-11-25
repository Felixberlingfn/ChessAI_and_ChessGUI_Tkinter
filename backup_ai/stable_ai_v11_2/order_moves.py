from chess import BLACK, WHITE, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING
from typing import Tuple
from typing import List

from .tables_maximizer import history_table_max, killer_moves_max
from .tables_minimizer import history_table_min, killer_moves_min
from .CONSTANTS import CALM, CAPTURE, PROMOTION, DEGRADATION_IMPACT_RATIO


def order_moves(board, real_depth, material=0) -> Tuple[List[tuple], int]:
    """in contrast to the evaluate board this is BEFORE the move was made"""
    """def mvv_lva_score(m):
        # Most Valuable Victim - Least Valuable Attacker
        victim_value = get_piece_value(board.piece_at(m.to_square))
        aggressor_value = get_piece_value(board.piece_at(m.from_square))
        return victim_value - aggressor_value"""

    """ First: Initialization """
    moves = board.legal_moves
    if board.turn == BLACK:
        turn = BLACK
        killers = killer_moves_min[real_depth] if killer_moves_min[real_depth] is not None else []  # (depth <= len)
    else:
        turn = WHITE
        killers = killer_moves_max[real_depth] if killer_moves_max[real_depth] is not None else []

    captures: List[tuple] = []
    checks: List[tuple] = []
    promotions: List[tuple] = []
    quiet_moves: List[tuple] = []
    quiet_killer_moves: List[tuple] = []
    opportunities = 0

    if real_depth > 2:
        degradation = 1 - (real_depth / DEGRADATION_IMPACT_RATIO)
    else:
        degradation = 1

    """ Second: Separate captures, checks, killer moves and quiet moves"""
    for move in moves:
        if board.is_capture(move):
            """ We can already calculate material balance change, save time later"""
            victim = board.piece_at(move.to_square)
            if victim:
                victim_type = victim.piece_type
                victim_value = get_piece_value_from_type(victim_type)
                aggressor = board.piece_at(move.from_square)
                aggressor_type = aggressor.piece_type
                aggressor_value = get_piece_value(aggressor)
                difference = victim_value if victim.color == BLACK else - victim_value
                new_material_balance = material + (difference * degradation)
                """ for mvv - lva score sorting """
                vv_minus_av = victim_value - aggressor_value
            else:
                # no victim on destination square but capture? Must be a pawn (en passant)!
                victim_value = 1
                victim_type = False
                aggressor = board.piece_at(move.from_square)
                aggressor_type = aggressor.piece_type
                victim_color = not aggressor.color
                aggressor_value = get_piece_value_from_type(aggressor_type)
                difference = victim_value if victim_color == BLACK else - victim_value
                new_material_balance = material + (difference * degradation)
                vv_minus_av = victim_value - aggressor_value
            opportunities += victim_value
            captures.append((move, CAPTURE, new_material_balance, vv_minus_av, aggressor_type, victim_type))  # 1=capture, 2=promo, 3=check

        elif move.promotion:
            if move.promotion == QUEEN:  # ignore non queen promotions (maybe add knight?)
                promoting_color = board.piece_at(move.from_square).color
                new_material_balance = material + 8 if promoting_color == WHITE else material - 8
                opportunities += 9
                promotions.append((move, PROMOTION, new_material_balance, False, QUEEN, QUEEN))  # 1=capture, 2=promo, 3=check

        elif move in killers:
            opportunities += 1
            moving_piece = board.piece_at(move.from_square)
            moving_piece_type = moving_piece.piece_type
            # moving_piece_type = False if moving_piece_type != KING else KING
            quiet_killer_moves.append((move, CALM, material, False, moving_piece_type, False))

        else:
            opportunities += 1
            moving_piece = board.piece_at(move.from_square)
            moving_piece_type = moving_piece.piece_type
            quiet_moves.append((move, CALM, material, False, moving_piece_type, False))  # 0=calm

    """elif board.gives_check(move):  # is expensive. not sure if worth - when I remove it I need to do is_check later
        opportunities += 1  # just 1 because gives_check is too expensive to calculate later for opponent
        checks.append((move, 3, material, 0))  # 1=capture, 2=promo, 3=check"""

    """ Third: Sorting """
    captures.sort(key=lambda a: a[3], reverse=True)
    if turn == BLACK:
        quiet_moves.sort(key=lambda m: history_table_min[m[0].from_square][m[0].to_square], reverse=True)
    else:
        quiet_moves.sort(key=lambda m: history_table_max[m[0].from_square][m[0].to_square], reverse=True)

    return (checks + promotions + captures + quiet_killer_moves + quiet_moves), opportunities


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
