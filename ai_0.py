import random
import chess
import datetime
import time
import inspect
import history
import stats
from typing import Tuple
from typing import List
from evaluate_board import evaluate_board

"""
Sources:
https://www.geeksforgeeks.org/minimax-algorithm-in-game-theory-set-4-alpha-beta-pruning/
https://www.chessprogramming.org/Main_Page
"""

""" Constants """
INIT_DEPTH = 3  # initial depth for minimax
CAPTURE_EXTENSION = 3  # depth extension for captures and promotions aka quiescence search
CHECK_EXTENSION = 3  # depth extension for checks aka quiescence search

""" Lists for improved move ordering"""
# Initialize the killer moves table with None. Each depth has two slots for killer moves.
# The length is depth + max depth extension + estimate for check extension
killer_moves = [[None, None] for _ in range((INIT_DEPTH + CAPTURE_EXTENSION + CHECK_EXTENSION * 3) + 5)]


def my_ai_0(board=None, time_limit=0) -> object:
    """ The main function of the AI """
    stats.n_extensions = 0  # reset
    stats.n_evaluated_leaf_nodes = 0  # reset
    stats.max_real_depth = 0  # reset

    if not board:
        board = chess.Board()

    show_potential_last_capture(board)

    """ Find the Best Move with minimax """
    # get initial material balance - we can calculate relative material balance as it is faster
    init_material_balance = 0
    for piece in board.piece_map().values():
        value = get_piece_value(piece)  # piece_values.get(piece.piece_type, 0)
        if piece.color == chess.WHITE:
            init_material_balance += value
        else:
            init_material_balance -= value

    best_move_at_last_index: list
    if board.turn == chess.WHITE:
        best_move_at_last_index = minimax(board, INIT_DEPTH, True, float('-inf'), float('inf'),
                                          False, 0.0, 0, init_material_balance)
    else:
        best_move_at_last_index = minimax(board, INIT_DEPTH, False, float('-inf'), float('inf'),
                                          False, 0.0, 0, init_material_balance)

    """ Check if finding best move was successful """
    if best_move_at_last_index:
        print_results_and_stats(board, best_move_at_last_index)
        move_object = chess.Move.from_uci(best_move_at_last_index[-1])

        if move_object.promotion:
            """ otherwise it will promote to random """
            from_square = move_object.from_square
            to_square = move_object.to_square
            generated_queen_promotion = chess.Move(from_square, to_square, chess.QUEEN)
            return generated_queen_promotion
        return move_object
    else:
        print("minimax search failed. Last resort: Use random move to avoid error")
        legal_moves = list(board.legal_moves)
        random_move = random.choice(legal_moves)
        if random_move:
            return random_move
        return False


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
                difference = victim_value if victim.color == chess.BLACK else - victim_value
                new_material_balance = material + difference
                """ for mvv - lva score sorting """
                vv_minus_av = victim_value - aggressor_value
            else:
                # no victim on destination square but capture? Must be a pawn (en passant)!
                victim_value = 1
                aggressor = board.piece_at(move.from_square)
                victim_color = not aggressor.color
                aggressor_value = get_piece_value(aggressor)
                difference = victim_value if victim_color == chess.BLACK else - victim_value
                new_material_balance = material + difference
                vv_minus_av = victim_value - aggressor_value
            opportunities += victim_value
            captures.append((move, 1, new_material_balance, vv_minus_av))  # 1=capture, 2=promo, 3=check

        elif move.promotion:
            promoting_color = board.piece_at(move.from_square).color
            new_material_balance = material + 8 if promoting_color == chess.WHITE else material - 8
            opportunities += 9
            promotions.append((move, 2, new_material_balance, 0))  # 1=capture, 2=promo, 3=check

        elif move in killers:
            opportunities += 1
            quiet_killer_moves.append((move, 0, material, 0))

        else:
            opportunities += 1
            quiet_moves.append((move, 0, material, 0))  # 0=calm

    """elif board.gives_check(move):  # is expensive. not sure if worth - when I remove it I need to do is_check later
        opportunities += 1  # just 1 because gives_check is too expensive to calculate later for opponent
        checks.append((move, 3, material, 0))  # 1=capture, 2=promo, 3=check"""

    """ Third: Sorting """
    captures.sort(key=lambda a: a[3], reverse=True)
    quiet_moves.sort(key=lambda m: history.table[m[0].from_square][m[0].to_square], reverse=True)

    return (checks + promotions + captures + quiet_killer_moves + quiet_moves), opportunities


def minimax(board, depth, max_player, alpha=float('-inf'), beta=float('inf'), quiescence_x=False,
            horizon_risk=0.0, opportunities=0, material=0, real_depth=0) -> list:
    """ Minimax returns optimal value for current player """

    if real_depth > stats.max_real_depth:
        stats.max_real_depth = real_depth  # just for stats

    """ We do Check Extension Check here (is_check is cheaper than gives_check) """
    if depth == 0 and quiescence_x < 5 and board.is_check():
        stats.n_extensions += CHECK_EXTENSION  # just for stats
        depth = 1  # extend the search
        quiescence_x += 1  # False becomes 1, then 2 etc. = number of extensions

    if depth == 0 or board.is_game_over():
        """ Final Node reached. Do the Evaluation of the board """
        final_val_list = evaluate_board(board, horizon_risk, opportunities, material)
        stats.n_evaluated_leaf_nodes += 1
        return final_val_list

    ordered_moves, opportunities = order_moves(board, real_depth, material)
    # number_of_moves = len(ordered_moves)  # now using opportunities

    """ MAXIMIZING """
    if max_player:
        best = float('-inf')
        best_list: list = [best]
        """ Loop through moves """
        for move, move_type, material_balance, _ in ordered_moves:
            next_depth, new_quiescence, next_horizon_risk = get_next_depth(board, move, depth, quiescence_x,
                                                                           move_type, )
            """ Chess  move"""
            board.push(move)
            """ Recursive Call and Value Updating """
            val_list: list = minimax(board, next_depth, False, alpha, beta, new_quiescence,
                                     next_horizon_risk, opportunities, material_balance, real_depth + 1)
            if val_list[0] >= best_list[0]:
                best_list = val_list  # use the evaluation list as the new best list
                best_list.append(board.uci(move))   # append the move history
            alpha = max(alpha, best_list[0])
            """ Undo Chess  move """
            board.pop()
            """ Alpha Beta Pruning """
            if beta <= alpha:
                """ Killer moves for move ordering """
                if move not in killer_moves[real_depth]:
                    killer_moves[real_depth].insert(0, move)
                    killer_moves[real_depth].pop()
                """ Update history table """
                history.update(move.from_square, move.to_square, depth)
                break
        return best_list

    # minimizing
    else:
        best = float('inf')
        best_list: list = [best]
        # loop through moves
        for move, move_type, material_balance, _ in ordered_moves:
            next_depth, new_quiescence, next_horizon_risk = get_next_depth(board, move, depth, quiescence_x,
                                                                           move_type)
            # Chess  move"""
            board.push(move)
            # Recursive Call and Value Updating"""
            val_list: list = minimax(board, next_depth, True, alpha, beta, new_quiescence,
                                     next_horizon_risk, opportunities, material_balance, real_depth + 1)
            if val_list[0] <= best_list[0]:
                best_list = val_list
                best_list.append(board.uci(move))  # append the move history
            beta = min(beta, best_list[0])
            # Undo Chess  move"""
            board.pop()
            # Alpha Beta Pruning"""
            if beta <= alpha:
                # Killer moves for move ordering
                if move not in killer_moves[real_depth]:
                    killer_moves[real_depth].insert(0, move)
                    killer_moves[real_depth].pop()
                # Update history table
                history.update(move.from_square, move.to_square, depth)
                break
        return best_list


def get_next_depth(board, move, depth: int, quiescence_x: any = False, move_type: int = 0) -> Tuple[int, any, float]:
    # gets the depth of the next minimax recursion
    # taking into account depth extension, quiescence and a horizon risk

    def calculate_horizon_risk(promotion=False) -> float:
        if not promotion:
            # because of horizon uncertainty let's not overvalue the capture/loss
            attacker_piece = board.piece_at(move.from_square)  # victim already in material balance
            if attacker_piece.color == chess.WHITE:
                horizon_risk: float = get_piece_value(attacker_piece) * 0.5  # bad for white when subst. later
            else:
                horizon_risk: float = - get_piece_value(attacker_piece) * 0.5  # bad for black when subst. later
            return horizon_risk
        else:
            if board.turn == chess.WHITE:  # white is promoting
                horizon_risk: float = 0.5
            else:
                horizon_risk: float = -0.5
            return horizon_risk

    def has_threats() -> bool:
        # Get the position of high value pieces
        critical_sqs_white: set = board.pieces(chess.QUEEN, chess.WHITE) | board.pieces(chess.ROOK, chess.WHITE)
        critical_sqs_black: set = board.pieces(chess.QUEEN, chess.BLACK) | board.pieces(chess.ROOK, chess.BLACK)

        for critical_sq_w in critical_sqs_white:
            if board.is_attacked_by(chess.BLACK, critical_sq_w):
                return True
        for critical_sq_b in critical_sqs_black:
            if board.is_attacked_by(chess.WHITE, critical_sq_b):
                return True
        return False

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
            return (depth + CAPTURE_EXTENSION), True, 0  # quiet_search=True
        else:
            return 0, False, 0

    """ end quiescence search early """
    # check if we should end quiescence search
    if quiescence_x and depth != 1:
        # I know gives_check is expensive but here it is checked less often
        if move_type in [1, 2]:    # 1=capture, 2=promo, 3=check
            # we don't need board.gives_check(move) because otherwise we extend with is_check
            return depth - 1, True, 0  # continue quiet_search
        else:
            """ unless this causes a check this ends quiescence search """
            return 0, quiescence_x, 0

    """ final quiescence extensions called only when first search reaches end """
    if depth == 1 and quiescence_x:

        " extend high value captures "
        if move_type == 1 and quiescence_x < 6:    # 1=capture, 2=promo, 3=check
            risk = calculate_horizon_risk()

            if quiescence_x < 2 and (risk > 1 or risk < -1):  # > 1 = bishop/horse
                """ extra (second) quiescence extension when more than bishop capture"""
                stats.n_extensions += 1
                return 1, quiescence_x + 1, 0

            elif quiescence_x < 3 and (risk > 2 or risk < -2):    # > 2 = rook
                """ extra (third) quiescence extension when more than rook capture """
                stats.n_extensions += 1
                return 1, quiescence_x + 1, 0

            elif quiescence_x < 4 and (risk > 4 or risk < -4):  # > 4 = queen
                """ extra (fourth) quiescence extension when queen capture """
                stats.n_extensions += 1
                return 1, quiescence_x + 1, 0

            """ too many extensions, evaluate with horizon risk value (50% of attacker value) """
            return 0, quiescence_x, risk

        """ extend promotions too """
        if move_type == 2 and quiescence_x < 4:  # 2 = promotion
            stats.n_extensions += 1
            return 1, quiescence_x + 1, 0

        """ unless this causes a check this ends quiescence search """
        return 0, quiescence_x, 0

    # quiescence default
    return depth-1, quiescence_x, 0  # quiet_search=True


def get_piece_value(piece) -> int:  # expects piece object not piece type
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
    }
    if not piece:
        return 0
    return piece_values.get(piece.piece_type, 0)


""" The rest: Printing stats etc. """


def print_results_and_stats(board, best_move_at_index_depth):
    # print history
    history.print_top(1)

    stats.printf()

    rounded_list = [round(item, 2) if isinstance(item, float) else item for item in best_move_at_index_depth]

    print("first move last:", rounded_list)

    readable_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

    move_id = len(board.move_stack) + 1

    print(f"Move # {move_id}: {best_move_at_index_depth[-1]}. [Sum, Pos., ..., ..., Path... ] - {readable_time}")

    move_object = chess.Move.from_uci(best_move_at_index_depth[-1])

    if board.is_capture(move_object):
        print(f"Captured: {board.piece_at(move_object.to_square)}")

    # print(killer_moves)


def show_potential_last_capture(board):
    if board.move_stack:  # Check if there are any moves made
        last_move = board.peek()
        if last_move and board.is_capture(last_move):
            # Undo the last move to see what was at the to_square
            board.pop()
            captured_piece = board.piece_at(last_move.to_square)
            # Redo the move
            board.push(last_move)
            if captured_piece:
                print(f"Lost: {captured_piece}")
    else:
        print("")


def inspect_function_name() -> str:
    return inspect.currentframe().f_code.co_name


if __name__ == "__main__":
    def test_board_moves():
        board = chess.Board()
        moves = ["e2e4", "c7c6", "f1c4", "d7d5", "e4d5", "c6d5", "c4b5", "c8d7", "d1e2", "e7e6",
                 "g1f3", "d7b5", "e2b5", "d8d7", "b5d3", "b8c6", "f3g5", "c6b4"]

        for uci in moves:
            move = chess.Move.from_uci(uci)
            board.push(move)

        return board

    start_time = time.time()
    my_ai_0(test_board_moves())
    end_time = time.time()
    execution_time = round((end_time - start_time) * 1000)
    print(f"Execution time: {execution_time} milliseconds")
