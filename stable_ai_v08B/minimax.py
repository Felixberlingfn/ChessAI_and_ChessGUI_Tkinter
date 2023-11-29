""" from root: python -m stable_ai_YOUR_VERSION.ai_0 """
import chess
import random
import datetime
import time
import inspect

from . import stats
from .tables import add_to_killers_and_history
from .evaluate_board import evaluate_board
from .order_moves import order_moves
from .depth import adjust_depth
from .CONSTANTS import INIT_DEPTH, CHECK_X_LIMITER


"""
Sources:
https://www.geeksforgeeks.org/minimax-algorithm-in-game-theory-set-4-alpha-beta-pruning/
https://www.chessprogramming.org/Main_Page
"""


def update_depth_stats(real_depth):
    if real_depth > stats.max_real_depth:
        stats.max_real_depth = real_depth  # just for stats
    stats.distribution[real_depth] += 1


def minimax(board, depth, max_player, alpha=float('-inf'), beta=float('inf'), horizon_risk=0.0,
            opportunities=0, material=0, real_depth=0, make_up_difference=1) -> list:
    """ Minimax returns optimal value for current player """

    """ We do Check Extension Check here (is_check is cheaper than gives_check) """
    if depth == 0 and real_depth < CHECK_X_LIMITER and board.is_check():
        depth = make_up_difference

    if depth == 0 or board.is_game_over():  # or time.time() > end_time:
        """ Final Node reached. Do the Evaluation of the board """
        final_val_list = evaluate_board(board, horizon_risk, opportunities, material)
        stats.n_evaluated_leaf_nodes += 1
        return final_val_list

    ordered_moves, opportunities = order_moves(board, real_depth, material)

    # board.__hash__() # might come soon

    """ MAXIMIZING """
    if max_player:
        best = float('-inf')
        best_list: list = [best]
        """ Loop through moves """
        for move, move_type, material_balance, _ in ordered_moves:
            update_depth_stats(real_depth)

            n_depth, nhr, ndiff = adjust_depth(board, move, depth, real_depth, move_type)

            """ Chess  move """
            board.push(move)
            if real_depth == 0 and board.is_repetition(2): board.pop(); continue  # skips repetitive move

            """ Recursive Call and Value Updating """
            val_list: list = minimax(board, n_depth, False, alpha, beta,
                                     nhr, opportunities, material_balance, real_depth + 1, ndiff)
            if val_list[0] >= best_list[0]:
                best_list = val_list  # use the evaluation list as the new best list
                best_list.append(board.uci(move))   # append the move history
            alpha = max(alpha, best_list[0])

            """ Undo Chess  move """
            board.pop()

            """ Alpha Beta Pruning """
            if real_depth == 0: stats.top_moves.append(val_list)
            if beta <= alpha:
                add_to_killers_and_history(move, real_depth)
                break
        return best_list

    # minimizing
    else:
        best = float('inf')
        best_list: list = [best]
        # loop through moves
        for move, move_type, material_balance, _ in ordered_moves:
            update_depth_stats(real_depth)
            n_depth, nhr, ndiff = adjust_depth(board, move, depth, real_depth, move_type)
            # Chess  move"""
            board.push(move)
            if real_depth == 0 and board.is_repetition(2): board.pop(); continue  # skips repetitive move
            # Recursive Call and Value Updating"""
            val_list: list = minimax(board, n_depth, True, alpha, beta,
                                     nhr, opportunities, material_balance, real_depth + 1, ndiff)
            if val_list[0] <= best_list[0]:
                best_list = val_list
                best_list.append(board.uci(move))  # append the move history
            beta = min(beta, best_list[0])
            # Undo Chess  move"""
            board.pop()
            # Alpha Beta Pruning"""
            if real_depth == 0: stats.top_moves.append(val_list)
            if beta <= alpha:
                add_to_killers_and_history(move, real_depth)
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

    stats.printf()

    rounded_list = [round(item, 2) if isinstance(item, float) else item for item in best_move_at_index_depth]

    print("first move last:", rounded_list)

    readable_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

    move_id = len(board.move_stack) + 1

    print(f"Move # {move_id}: {best_move_at_index_depth[-1]}. [Sum, Pos., ..., ..., Path... ] - {readable_time}")

    move_object = chess.Move.from_uci(best_move_at_index_depth[-1])

    if board.is_capture(move_object):
        print(f"Captured: {board.piece_at(move_object.to_square)}")

    print(stats.top_moves)

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
    end_time = time.time()
    execution_time = round((end_time - start_time) * 1000)
    print(f"Execution time: {execution_time} milliseconds")
