from chess import BLACK, WHITE, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING
from typing import Tuple
from typing import List

from .tables_maximizer import history_table_max, killer_moves_max
from .tables_minimizer import history_table_min, killer_moves_min
from .CONSTANTS import CALM, CAPTURE, PROMOTION, DEGRADATION_IMPACT_RATIO

import chess.engine  # testing

STOCKFISH_PATH = "./stockfish/stockfish-windows-x86-64-avx2.exe"  # testing


def stockfish_static(board, real_depth):
    if real_depth > 1:
        return 0
    """ this is for testing a concept where you do a static evaluation or very
    shallow search during move ordering to inform what move to investigate first"""

    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

    """ Do a depth 1 search, essentially giving the best move based on static eval"""
    """ This is just to test the effect this might have on move ordering"""
    result = engine.play(board, chess.engine.Limit(depth=1))

    engine.quit()
    """ this is a placeholder before I would implement my own"""

    return result.move


def order_moves(board, real_depth, material=0) -> Tuple[List[tuple], int]:
    """in contrast to the evaluate board this is BEFORE the move was made"""

    """ First: Initialization """
    moves = board.legal_moves
    if board.turn == BLACK:
        turn = BLACK
        killers = killer_moves_min[real_depth] if killer_moves_min[real_depth] is not None else []  # (depth <= len)
    else:
        turn = WHITE
        killers = killer_moves_max[real_depth] if killer_moves_max[real_depth] is not None else []

    captures: List[tuple] = []
    fish: List[tuple] = []
    promotions: List[tuple] = []
    quiet_moves: List[tuple] = []
    quiet_killer_moves: List[tuple] = []
    opportunities = 0

    if real_depth > 2:
        degradation = 1 - (real_depth / DEGRADATION_IMPACT_RATIO)
    else:
        degradation = 1

    best_static_fish = stockfish_static(board, real_depth)

    """ Second: Separate captures, checks, killer moves and quiet moves"""
    for move in moves:
        if board.is_capture(move):
            """ get aggressor and victim details """
            aggressor = board.piece_at(move.from_square)
            aggr_type = aggressor.piece_type
            aggr_value = get_piece_value_from_type(aggr_type)
            victim = board.piece_at(move.to_square)
            if victim:  # not en passant
                victim_type, victim_color = victim.piece_type, victim.color
                victim_value = get_piece_value_from_type(victim_type)
            else:  # en passant (victim is not at to_square)
                victim_type, victim_value, victim_color = PAWN, 1, not aggressor.color

            """ calculate potential material gain """
            vv_minus_av = victim_value - aggr_value
            difference = victim_value if victim_color == BLACK else - victim_value
            new_material_balance = material + (difference * degradation)

            """ add capture to list and update opportunity score"""
            opportunities += victim_value
            if move == best_static_fish:
                fish.append((move, CAPTURE, new_material_balance, vv_minus_av, aggr_type, victim_type))
            else:
                captures.append((move, CAPTURE, new_material_balance, vv_minus_av, aggr_type, victim_type))

        elif move.promotion:
            if move.promotion == QUEEN:
                promoting_color = board.piece_at(move.from_square).color
                new_material_balance = material + 8 if promoting_color == WHITE else material - 8

                """ add promotion to list and update opportunity score"""
                opportunities += 9
                if move == best_static_fish:
                    fish.append((move, PROMOTION, new_material_balance, False, QUEEN, QUEEN))
                else:
                    promotions.append((move, PROMOTION, new_material_balance, False, QUEEN, QUEEN))

        elif move in killers:
            moving_piece = board.piece_at(move.from_square)
            moving_piece_type = moving_piece.piece_type

            """ add killer move to list and update opportunity score"""
            opportunities += 1
            if move == best_static_fish:
                fish.append((move, CALM, material, False, moving_piece_type, False))
            else:
                quiet_killer_moves.append((move, CALM, material, False, moving_piece_type, False))

        else:
            moving_piece = board.piece_at(move.from_square)
            moving_piece_type = moving_piece.piece_type

            """ add calm move to list and update opportunity score"""
            opportunities += 1
            if move == best_static_fish:
                fish.append((move, CALM, material, False, moving_piece_type, False))
            else:
                quiet_moves.append((move, CALM, material, False, moving_piece_type, False))  # 0=calm

    """ Third: Sorting """
    captures.sort(key=lambda a: a[3], reverse=True)
    if turn == BLACK:
        quiet_moves.sort(key=lambda m: history_table_min[m[0].from_square][m[0].to_square], reverse=True)
    else:
        quiet_moves.sort(key=lambda m: history_table_max[m[0].from_square][m[0].to_square], reverse=True)

    return (fish + promotions + captures + quiet_killer_moves + quiet_moves), opportunities


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
