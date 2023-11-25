from . import stats
from .tables_maximizer import add_to_killers_and_history
from .evaluate_board import evaluate_board
from .order_moves import order_moves
from .depth import adjust_depth
from .CONSTANTS import CHECK_X_LIMITER

"""
Sources:
https://www.geeksforgeeks.org/minimax-algorithm-in-game-theory-set-4-alpha-beta-pruning/
https://www.chessprogramming.org/Main_Page


future: https://python-chess.readthedocs.io/en/latest/polyglot.html
"""


def minimax(board, depth, max_player, alpha=float('-inf'), beta=float('inf'), horizon_risk=0.0,
            opportunities=0, material=0, real_depth=0, make_up_difference=1) -> list:
    """ Minimax returns optimal value for current player """

    """ DEPTH EXTENSIONS """
    if depth == 0 and real_depth < CHECK_X_LIMITER and board.is_check():
        depth = make_up_difference

    """ CHECK AND END THE RECURSION: """
    if depth == 0 or board.is_game_over():  # or time.time() > end_time:
        final_val_list = evaluate_board(board, horizon_risk, opportunities, material, real_depth)
        stats.n_evaluated_leaf_nodes += 1
        return final_val_list

    ordered_moves, opportunities = order_moves(board, real_depth, material)

    if real_depth < 2 and opportunities < 15:
        print("very few available moves, extend search")
        depth += 1

    """ MAXIMIZING """
    if max_player:
        best = float('-inf')
        best_list: list = [best]
        """ Loop through moves """
        for move, move_type, material_balance, _, aggressor, victim in ordered_moves:
            stats.distribution[real_depth] += 1

            n_depth, nhr, ndiff = adjust_depth(board, move, depth, real_depth, move_type, aggressor, victim)

            """ Chess  move """
            board.push(move)
            if real_depth == 0 and opportunities > 1 and board.is_repetition(2):
                board.pop(); continue

            """ Recursive Call and Value Updating """
            val_list: list = minimax(board, n_depth, False, alpha, beta,
                                     nhr, opportunities, material_balance, real_depth + 1, ndiff)

            # if real_depth == 0: val_list[0] = val_list[0] + ((len(val_list) - 4) * PREFERENCE_DEEP)

            if val_list[0] > best_list[0] or (val_list[0] == best_list[0] and len(val_list) >= len(best_list)):
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

        """ I need to handle the case when this returns float(inf). but I want to know why
        anyways it is usually when all is lost so choosing a random move might be ok"""
        return best_list

    # minimizing
    else:
        best = float('inf')
        best_list: list = [best]
        # loop through moves
        for move, move_type, material_balance, _, aggressor, victim in ordered_moves:
            stats.distribution[real_depth] += 1

            n_depth, nhr, ndiff = adjust_depth(board, move, depth, real_depth, move_type, aggressor, victim)

            # Chess  move
            board.push(move)
            if real_depth == 0 and opportunities > 1 and board.is_repetition(2):
                board.pop(); continue

            # Recursive Call and Value Updating
            val_list: list = minimax(board, n_depth, True, alpha, beta,
                                     nhr, opportunities, material_balance, real_depth + 1, ndiff)

            # if real_depth == 0: val_list[0] = val_list[0] - ((len(val_list) - 4) * PREFERENCE_DEEP)

            if val_list[0] < best_list[0] or (val_list[0] == best_list[0] and len(val_list) >= len(best_list)):
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
    pass
