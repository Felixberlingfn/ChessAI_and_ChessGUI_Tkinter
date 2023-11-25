from . import stats
from . import tables_maximizer
from . import tables_minimizer
from .evaluate_board import evaluate_board
from .order_moves import order_moves
from .depth import adjust_depth
from .CONSTANTS import CHECK_X_LIMITER, PREFERENCE_DEEP


"""
Sources:
https://www.geeksforgeeks.org/minimax-algorithm-in-game-theory-set-4-alpha-beta-pruning/
https://www.chessprogramming.org/Main_Page
"""


def minimax(board, depth, max_player, alpha=float('-inf'), beta=float('inf'), horizon_risk=0.0,
            op=0, material=0, real_depth=0, make_up_difference=1) -> list:
    """ Minimax returns optimal value for current player """

    """ DEPTH EXTENSIONS """
    if depth == 0 and real_depth < CHECK_X_LIMITER and board.is_check():
        depth = make_up_difference  # increase depth by (at least) 1

    """ CHECK AND END THE RECURSION: """
    if depth == 0 or board.is_game_over():  # or time.time() > end_time:
        final_val_list = evaluate_board(board, horizon_risk, op, material, real_depth)
        stats.n_evaluated_leaf_nodes += 1
        return final_val_list

    ordered_moves, op = order_moves(board, real_depth, material)

    if real_depth == 0 and op < 10:
        print("very few available moves, extend search")
        depth += 1
    if depth > 0 and op < 3 and real_depth < CHECK_X_LIMITER:
        depth += 1

    """ MAXIMIZING """
    if max_player:
        best = float('-inf')
        best_list: list = [best]
        """ Loop through moves """
        for move_tuple in ordered_moves:
            """move_tuple: move, move_type, material_balance, _, aggressor, victim"""
            move, material = move_tuple[0], move_tuple[2]

            stats.distribution[real_depth] += 1

            n_depth, risk, diff = adjust_depth(board, move_tuple, depth, real_depth, op)

            """ Chess  move """
            board.push(move)
            if real_depth == 0 and op > 1 and board.is_repetition(2):
                board.pop()
                continue

            """ Recursive Call and Value Updating """
            val_list: list = minimax(board, n_depth, False, alpha, beta,
                                     risk, op, material, real_depth + 1, diff)

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
                tables_maximizer.add_to_killers_and_history(move, real_depth)
                break

        return best_list

    # minimizing
    else:
        best = float('inf')
        best_list: list = [best]
        # loop through moves
        for move_tuple in ordered_moves:
            """move_tuple: move, move_type, material_balance, _, aggressor, victim"""
            move, material = move_tuple[0], move_tuple[2]

            stats.distribution[real_depth] += 1

            n_depth, risk, diff = adjust_depth(board, move_tuple, depth, real_depth, op)

            # Chess  move
            board.push(move)
            if real_depth == 0 and op > 1 and board.is_repetition(2):
                board.pop()
                continue

            # Recursive Call and Value Updating
            val_list: list = minimax(board, n_depth, True, alpha, beta,
                                     risk, op, material, real_depth + 1, diff)

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
                tables_minimizer.add_to_killers_and_history(move, real_depth)
                break
        return best_list


if __name__ == "__main__":
    pass
