import chess
import inspect
import timeit

from . import config


def run(board, testing=False) -> list:
    """ wrapper for evaluate_board() - runs when not imported as module """
    if testing:
        move = chess.Move.from_uci("e2e4")
        board.push(move)
    return evaluate_board(board)


def evaluate_board(board, horizon_risk=0.0, opportunities=0, material=None, real_depth=1,
                   lost_castling=False, now_op=0) -> list:
    """
    :param board: chess.Board object
    :param horizon_risk
    :param opportunities
    :param material
    :param real_depth
    :param lost_castling
    :return: score representing material balance
    """

    turn = board.turn

    """ get material balance from material change """
    material_balance = material  # if material else get_material_balance(board)

    final_val: list = [material_balance * 100]  # Using centi-pawns instead of pawns because it is convention
    """ endgame check """
    try_to_win_soon = real_depth if real_depth > 0 else 1
    if board.is_checkmate():
        if turn == chess.WHITE:  # is turn dependent
            """really bad for white - great for black - we are evaluating for black - current turn is white"""
            final_val[0] = - 1.7976931348623150e308 / try_to_win_soon
        else:
            """really bad for black - great for white - we are evaluating for white - current turn is black"""
            final_val[0] = 1.7976931348623150e308 / try_to_win_soon

    """ adding extra values to simple material balance """
    # pos = get_position_score(board) * 100  # centi-pawns is convention
    # mob = get_opportunity_score(board, opportunities) * 100  # centi-pawns is convention

    # for the player we evaluate for it is a risk, for the current turn player it is a potential gain
    risk = - horizon_risk if turn == chess.BLACK else horizon_risk

    op_score = (now_op - opportunities) if turn == chess.WHITE else (-now_op + opportunities)

    risk_in_centipawns = round(risk * 100, 2)
    # final_val[0] += pos
    if config.opportunity_score_activated:
        final_val[0] += (op_score * config.opportunity_score_weight)
    if config.lost_castling_activated:
        final_val[0] += lost_castling
    if config.horizon_risk_activated:
        final_val[0] += (risk_in_centipawns * config.horizon_risk_weight)  # centi-pawns is convention

    """ append details to list for stats """
    final_val.append(risk_in_centipawns)
    final_val.append(0)
    final_val.append(0)
    final_val.append(- horizon_risk * 100)

    final_val[0] = round(final_val[0], 2)

    return final_val


def get_material_balance(board) -> int:
    """
    :param board: chess.Board object
    :return: score representing material balance
    """
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
    for square, piece in board.piece_map().items():
        if piece.color == chess.WHITE:
            if board.is_pinned(chess.WHITE, square):
                pin_value -= get_piece_value(piece) * 0.2
        if piece.color == chess.BLACK:
            if board.is_pinned(chess.BLACK, square):
                pin_value += get_piece_value(piece) * 0.2

    return pin_value * 100


def get_opportunity_score(board, opportunity_score) -> float:
    """
    :param board: chess.Board object
    :param opportunity_score
    """
    def get_opportunities() -> int:
        moves = board.legal_moves
        opportunities = 0

        for move in moves:
            if board.is_capture(move):
                """ We can already calculate material balance change, save time later"""
                victim = board.piece_at(move.to_square)
                if victim:
                    victim_value = get_piece_value(victim)  # this still uses the old method !!!!!
                    opportunities += 1 + victim_value
                else:
                    opportunities += 2  # en passant
            elif move.promotion:
                opportunities += 9.5
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
    """
    :param piece (not piece type!)
    :return: integer representing the piece value
    """
    # Assign values to the pieces for the purpose of MVV-LVA scoring
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3.33,
        chess.ROOK: 5.63,
        chess.QUEEN: 9.5,
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
