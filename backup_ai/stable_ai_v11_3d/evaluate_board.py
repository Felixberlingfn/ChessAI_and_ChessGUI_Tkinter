import chess
import inspect
import timeit

from .CONSTANTS import OPPORTUNITY_MULTIPLIER, GOOD_POS_BONUS, BAD_POS_PUNISH

def run(board, testing=False) -> list:
    """ wrapper for evaluate_board() - runs when not imported as module """
    if testing:
        move = chess.Move.from_uci("e2e4")
        board.push(move)
    return evaluate_board(board)


def evaluate_board(board, horizon_risk=0.0, opportunities=0, material=None, real_depth=1) -> list:
    """ Simplistic but most important: Material Balance + White - Black"""
    material_balance = material if material else get_material_balance(board)

    final_val: list = [material_balance * 100]  # Using centi-pawns instead of pawns because it is convention
    """ endgame check """
    try_to_win_soon = real_depth if real_depth > 0 else 1
    # without try_to_win_soon it will essentially do random moves when the opponent has only a king left
    # if unlucky it might even miss that the opponent can force a 50 move rule stalemate
    if board.is_checkmate():
        if board.turn == chess.WHITE:  # is turn dependent
            """great for black"""
            final_val[0] = - 1.7976931348623150e308 / try_to_win_soon
        else:
            """great for white"""
            final_val[0] = 1.7976931348623150e308 / try_to_win_soon

    """ adding extra values to simple material balance """
    pos = get_position_score(board) * 100  # centi-pawns is convention
    mob = get_opportunity_score(board, opportunities) * 100  # centi-pawns is convention

    final_val[0] += pos
    final_val[0] += mob  # is turn dependent
    final_val[0] -= horizon_risk * 100  # centi-pawns is convention

    """ append details to list for stats """
    final_val.append(pos)
    final_val.append(mob)
    final_val.append(- horizon_risk * 100)

    return final_val


def get_material_balance(board) -> int:
    material_balance = 0
    for piece in board.piece_map().values():
        value = get_piece_value(piece)
        if piece.color == chess.WHITE:
            material_balance += value
        else:
            material_balance -= value
    return material_balance


def get_pins_score(board):
    """
    TAKES TOO MUCH COMPUTE - MAYBE NOT WORTH IT
    :param board: chess.Board object
    :return: score representing pinned pieces
    """
    pin_value = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.WHITE:
                if board.is_pinned(chess.WHITE, square):
                    pin_value -= get_piece_value(piece) * 0.2
            if piece.color == chess.BLACK:
                if board.is_pinned(chess.BLACK, square):
                    pin_value += get_piece_value(piece) * 0.2

    return pin_value * 100



def get_position_score(board) -> float:
    """PLUS MEANS GOOD FOR WHITE"""
    score = 0

    """WHITE"""
    """good_pawn_positions_white"""
    good_pawn_positions_white = [chess.D4, chess.E4,  # chess.C4, chess.F4,
                                 chess.A7, chess.B7, chess.C7, chess.D7,  # Promotion Preparation
                                 chess.E7, chess.F7, chess.G7, chess.H7  # Promotion Preparation
                                 ]
    for square in good_pawn_positions_white:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.WHITE:
                score += GOOD_POS_BONUS
    bad_pawn_positions_white = [chess.D2, chess.E2]
    for square in bad_pawn_positions_white:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.WHITE:
                score -= BAD_POS_PUNISH
    """good_knight_positions_white"""
    good_knight_positions_white = [chess.F3, chess.C3, chess.G5, chess.F5, chess.D5, chess.E5]
    for square in good_knight_positions_white:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.WHITE and piece.piece_type == chess.KNIGHT:
                score += GOOD_POS_BONUS
    bad_knight_positions_white = [chess.A3, chess.H3, chess.A5, chess.H5]
    for square in bad_knight_positions_white:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.WHITE and piece.piece_type == chess.KNIGHT:
                score -= BAD_POS_PUNISH
    """good_bishop_positions_white"""
    good_bishop_positions_white = [chess.C4, chess.F4, chess.G2, chess.B2, chess.D3, chess.E3]
    for square in good_bishop_positions_white:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.WHITE and piece.piece_type == chess.BISHOP:
                score += GOOD_POS_BONUS
    bad_bishop_positions_white = [chess.F1] # should be cleared for castling
    for square in bad_bishop_positions_white:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.WHITE and piece.piece_type == chess.BISHOP:
                score -= BAD_POS_PUNISH
    """good_rook_positions_white"""
    good_rook_positions_white = [chess.D1, chess.E1, chess.D2, chess.E2, chess.F1, chess.A4, chess.H4]  # chess.C1,
    for square in good_rook_positions_white:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.WHITE and piece.piece_type == chess.ROOK:
                score += GOOD_POS_BONUS

    """good_queen_positions_white"""
    good_queen_positions_white = [chess.D1, chess.E2, chess.D2, chess.C2, chess.D3, chess.E3, chess.F3]
    for square in good_queen_positions_white:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.WHITE and piece.piece_type == chess.QUEEN:
                score += GOOD_POS_BONUS
    """good_king_positions_white"""
    good_king_positions_white = [chess.G1, chess.B1]
    for square in good_king_positions_white:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.WHITE and piece.piece_type == chess.KING:
                score += GOOD_POS_BONUS

    # BLACK
    # Evaluate good pawn positions for black
    good_pawn_positions_black = [chess.D5, chess.E5,  # chess.C5, chess.F5,
                                 chess.A2, chess.B2, chess.C2, chess.D2,  # promotion preparation
                                 chess.E2, chess.F2, chess.G2, chess.H2  # promotion preparation
                                 ]
    for square in good_pawn_positions_black:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.BLACK:
                score -= GOOD_POS_BONUS
    # Evaluate good knight positions for black
    good_knight_positions_black = [chess.F6, chess.C6, chess.D7, chess.E7, chess.G4, chess.F4, chess.D4, chess.E4]
    for square in good_knight_positions_black:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.BLACK and piece.piece_type == chess.KNIGHT:
                score -= GOOD_POS_BONUS
    # Evaluate good bishop positions for black
    good_bishop_positions_black = [chess.C5, chess.G7, chess.B7, chess.D6, chess.E6, chess.A6, chess.H6]
    for square in good_bishop_positions_black:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.BLACK and piece.piece_type == chess.BISHOP:
                score -= GOOD_POS_BONUS
    # Evaluate good rook positions for black
    good_rook_positions_black = [chess.D8, chess.E8, chess.D7, chess.E7, chess.F8, chess.C8, chess.A5, chess.H5]
    for square in good_rook_positions_black:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.BLACK and piece.piece_type == chess.ROOK:
                score -= GOOD_POS_BONUS
    # Evaluate good queen positions for black
    good_queen_positions_black = [chess.D8, chess.E7, chess.D7, chess.C7, chess.D6, chess.E6, chess.F6]
    for square in good_queen_positions_black:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.BLACK and piece.piece_type == chess.QUEEN:
                score -= GOOD_POS_BONUS
    # good_king_positions_black
    good_king_positions_black = [chess.G8]  # Typical castling squares for black king
    for square in good_king_positions_black:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.BLACK and piece.piece_type == chess.KING:
                score -= GOOD_POS_BONUS
    return score


def get_opportunity_score(board, opportunity_score) -> float:
    def get_opportunities() -> int:
        moves = board.legal_moves
        opportunities = 0

        for move in moves:
            if board.is_capture(move):
                """ We can already calculate material balance change, save time later"""
                victim = board.piece_at(move.to_square)
                if victim:
                    victim_value = get_piece_value(victim)
                    opportunities += 1 + victim_value
                else:
                    opportunities += 2  # en passant
            elif move.promotion:
                opportunities += 9
            else:
                opportunities += 1
        return opportunities

    """PLUS MEANS GOOD FOR WHITE"""
    opportunity_score_white = 0
    opportunity_score_black = 0

    if board.turn == chess.WHITE:
        opportunity_score_white = get_opportunities() * OPPORTUNITY_MULTIPLIER
        opportunity_score_black = opportunity_score * OPPORTUNITY_MULTIPLIER
    if board.turn == chess.BLACK:
        opportunity_score_black = get_opportunities() * OPPORTUNITY_MULTIPLIER
        opportunity_score_white = opportunity_score * OPPORTUNITY_MULTIPLIER

    # approximating this from previous move saves time
    # null move would also just be an approximation
    """board.push(chess.Move.null())
    if board.turn == chess.WHITE:
        mobility_white = len(list(board.legal_moves)) * MOBILITY_MULTIPLIER
    if board.turn == chess.BLACK:
        mobility_black = len(list(board.legal_moves)) * MOBILITY_MULTIPLIER
    board.pop()"""

    return opportunity_score_white - opportunity_score_black


def get_piece_value(piece) -> int:
    # Assign values to the pieces for the purpose of MVV-LVA scoring
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
    }
    if piece is None:
        return 0  # Return 0 if there's no piece
    return piece_values.get(piece.piece_type, 0)


def inspect_function_name() -> str:
    return inspect.currentframe().f_code.co_name


if __name__ == "__main__":

    """ test with timeit """
    setup = '''
from __main__ import run, chess, evaluate_board, get_piece_value, inspect_function_name, get_opportunity_score, get_position_score
'''
    statement = '''
test_board = chess.Board()
run(test_board, True)
'''
    runs = 10000
    time = timeit.timeit(stmt=statement, setup=setup, number=runs)
    print(f"{runs} runs: {round(time * 1000)} milliseconds")

    """ regular test """
    test_board = chess.Board()

    print_evaluation = run(test_board, True)
    move_id = len(test_board.move_stack) + 1
    print(f"Move # {move_id}: {print_evaluation}.")
    print("[Sum, Pos., Mobil., Check, Threat_Def, ... ]")
    # print(f"{n_evaluated_leaf_nodes}")
