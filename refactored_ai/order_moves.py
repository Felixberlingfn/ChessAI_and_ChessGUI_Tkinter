from chess import BLACK, WHITE, PAWN, KNIGHT, BISHOP, ROOK, QUEEN
from typing import Tuple
from typing import List

from refactored_ai import history
from refactored_ai.CONSTANTS import MAXIMUM_REAL_DEPTH

CALM = 0
CAPTURE = 1
PROMOTION = 2

""" Lists for improved move ordering"""
# Initialize the killer moves table with None. Each depth has two slots for killer moves.
# The length is depth + max depth extension + estimate for check extension
killer_moves = [[None, None] for _ in range(MAXIMUM_REAL_DEPTH)]


def order_moves(board, real_depth, material=0) -> Tuple[List[tuple], int]:
    """in contrast to the evaluate board this is BEFORE the move was made"""
    """def mvv_lva_score(m):
        # Most Valuable Victim - Least Valuable Attacker
        victim_value = get_piece_value(board.piece_at(m.to_square))
        aggressor_value = get_piece_value(board.piece_at(m.from_square))
        return victim_value - aggressor_value"""

    """ First: Initialization """
    moves = board.legal_moves
    killers: list = killer_moves[real_depth] if killer_moves[real_depth] is not None else []  # (depth <= len)
    captures: List[tuple] = []
    checks: List[tuple] = []
    promotions: List[tuple] = []
    quiet_moves: List[tuple] = []
    quiet_killer_moves: List[tuple] = []
    opportunities = 0

    """ Second: Separate captures, checks, killer moves and quiet moves"""
    for move in moves:
        if board.is_capture(move):
            """ We can already calculate material balance change, save time later"""
            victim = board.piece_at(move.to_square)
            if victim:
                victim_value = get_piece_value(victim)
                aggressor_value = get_piece_value(board.piece_at(move.from_square))
                difference = victim_value if victim.color == BLACK else - victim_value
                new_material_balance = material + difference
                """ for mvv - lva score sorting """
                vv_minus_av = victim_value - aggressor_value
            else:
                # no victim on destination square but capture? Must be a pawn (en passant)!
                victim_value = 1
                aggressor = board.piece_at(move.from_square)
                victim_color = not aggressor.color
                aggressor_value = get_piece_value(aggressor)
                difference = victim_value if victim_color == BLACK else - victim_value
                new_material_balance = material + difference
                vv_minus_av = victim_value - aggressor_value
            opportunities += victim_value
            captures.append((move, CAPTURE, new_material_balance, vv_minus_av))  # 1=capture, 2=promo, 3=check

        elif move.promotion:
            promoting_color = board.piece_at(move.from_square).color
            new_material_balance = material + 8 if promoting_color == WHITE else material - 8
            opportunities += 9
            promotions.append((move, PROMOTION, new_material_balance, 0))  # 1=capture, 2=promo, 3=check

        elif move in killers:
            opportunities += 1
            quiet_killer_moves.append((move, CALM, material, 0))

        else:
            opportunities += 1
            quiet_moves.append((move, CALM, material, 0))  # 0=calm

    """elif board.gives_check(move):  # is expensive. not sure if worth - when I remove it I need to do is_check later
        opportunities += 1  # just 1 because gives_check is too expensive to calculate later for opponent
        checks.append((move, 3, material, 0))  # 1=capture, 2=promo, 3=check"""

    """ Third: Sorting """
    captures.sort(key=lambda a: a[3], reverse=True)
    quiet_moves.sort(key=lambda m: history.table[m[0].from_square][m[0].to_square], reverse=True)

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
