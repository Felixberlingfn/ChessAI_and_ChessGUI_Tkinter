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
            stats.distribution[real_depth] += 1

            n_depth, nhr, ndiff = adjust_depth(board, move, depth, real_depth, move_type)

            """ Chess  move """
            board.push(move)
            if real_depth == 0 and board.is_repetition(2): board.pop(); continue  # skips repetitive move

            """ Recursive Call and Value Updating """
            val_list: list = minimax(board, n_depth, False, alpha, beta,
                                     nhr, opportunities, material_balance, real_depth + 1, ndiff)

            if real_depth == 0: val_list[0] = val_list[0] + ((len(val_list) - 5) * 0.1)

            if val_list[0] >= best_list[0]:
                # if real_depth == 0: print(f"{val_list[0]} >= {best_list[0]}")
                best_list = val_list
                best_list.append(board.uci(move))
                if real_depth == 0: stats.top_moves.append(val_list)
            alpha = max(alpha, best_list[0])

            """ Undo Chess  move """
            board.pop()

            """ Alpha Beta Pruning """
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
            stats.distribution[real_depth] += 1

            n_depth, nhr, ndiff = adjust_depth(board, move, depth, real_depth, move_type)

            # Chess  move
            board.push(move)
            if real_depth == 0 and board.is_repetition(2): board.pop(); continue  # skips repetitive move

            # Recursive Call and Value Updating
            val_list: list = minimax(board, n_depth, True, alpha, beta,
                                     nhr, opportunities, material_balance, real_depth + 1, ndiff)

            if real_depth == 0: val_list[0] = val_list[0] - ((len(val_list) - 5) * 0.1)

            if val_list[0] <= best_list[0]:
                # if real_depth == 0: print(f"{val_list[0]} <= {best_list[0]}")
                best_list = val_list
                best_list.append(board.uci(move))  # append the move history
                if real_depth == 0: stats.top_moves.append(val_list)
            beta = min(beta, best_list[0])

            # Undo Chess  move
            board.pop()

            # Alpha Beta Pruning
            if beta <= alpha:
                add_to_killers_and_history(move, real_depth)
                break
        return best_list


""" The rest: Printing stats etc. """


if __name__ == "__main__":
    start_time = time.time()
    end_time = time.time()
    execution_time = round((end_time - start_time) * 1000)
    print(f"Execution time: {execution_time} milliseconds")
