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
from order_moves import order_moves
from horizon import get_next_depth
from CONSTANTS import INIT_DEPTH, CAPTURE_EXTENSION, CHECK_EXTENSION
from order_moves import killer_moves

"""
Sources:
https://www.geeksforgeeks.org/minimax-algorithm-in-game-theory-set-4-alpha-beta-pruning/
https://www.chessprogramming.org/Main_Page
"""

end_time = 0

def ai_0(board=None, time_limit=0) -> object:
    global end_time

    end_time = time.time() + 30

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


def minimax(board, depth, max_player, alpha=float('-inf'), beta=float('inf'), quiescence_x=False,
            horizon_risk=0.0, opportunities=0, material=0, real_depth=0) -> list:
    """ Minimax returns optimal value for current player """

    if real_depth > stats.max_real_depth:
        stats.max_real_depth = real_depth  # just for stats
    stats.distribution[real_depth] += 1

    """ We do Check Extension Check here (is_check is cheaper than gives_check) """
    if depth == 0 and quiescence_x < 6 and board.is_check():
        stats.n_extensions += CHECK_EXTENSION  # just for stats
        depth = 1  # extend the search
        quiescence_x += 1  # False becomes 1, then 2 etc. = number of extensions

    if depth == 0 or board.is_game_over() or time.time() > end_time:
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
    ai_0(test_board_moves())
    end_time = time.time()
    execution_time = round((end_time - start_time) * 1000)
    print(f"Execution time: {execution_time} milliseconds")
