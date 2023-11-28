# import chess
from . import stats
from . import tables_maximizer
from . import tables_minimizer
from .evaluate_board import evaluate_board
from .order_moves import order_moves
from .depth import adjust_depth
from .CONSTANTS import CHECK_X_LIMITER


"""
Sources:
https://www.geeksforgeeks.org/minimax-algorithm-in-game-theory-set-4-alpha-beta-pruning/
https://www.chessprogramming.org/Main_Page
"""

""" I will need to increment the number of pieces to switch from start to endgame"""


def sum_of_pieces(board):
    """not counting the king - side effect on stats.sum_of_all_pieces"""
    piece_values = {1: 1, 2: 3, 3: 3.33, 4: 5.63, 5: 9.5, 6: 0}
    sum_of_all_pieces = 0
    for square_64, piece in board.piece_map().items():
        sum_of_all_pieces += piece_values.get(piece.piece_type, 0)

    stats.sum_of_all_pieces = sum_of_all_pieces
    return sum_of_all_pieces


def minimax(board, depth, max_player, alpha=float('-inf'), beta=float('inf'), horizon_risk=0.0,
            op=0, material=0, real_depth=0, make_up_difference=1, lost_castling=False) -> list:
    """ Minimax returns optimal value for current player """

    material = round(material, 2)
    horizon_risk = round(horizon_risk, 2)

    """ DEPTH EXTENSIONS """
    if depth == 0 and real_depth < CHECK_X_LIMITER and board.is_check():
        depth = make_up_difference  # increase depth by (at least) 1

    """ CHECK AND END THE RECURSION: """
    if depth == 0 or board.is_game_over() or real_depth == CHECK_X_LIMITER:  # or time.time() > end_time:
        final_val_list = evaluate_board(board, horizon_risk, op, material, real_depth, lost_castling)
        stats.n_evaluated_leaf_nodes += 1
        return final_val_list

    ordered_moves, op = order_moves(board, real_depth, material)
    # op_total = op_total + op if board.turn == chess.WHITE else op_total - op

    if real_depth == 0:
        if op < 10:
            print("very few available moves, extend search")
            depth += 1
        if sum_of_pieces(board) < 20:  # less than two queens
            print("very few pieces on the board, extend search")
            depth += 1
    if depth > 0 and op < 3 and real_depth < CHECK_X_LIMITER:
        depth += 1

    """ MAXIMIZING """
    if max_player:
        best = float('-inf')
        best_list: list = [best]
        """ Loop through moves """
        for move_tuple in ordered_moves:
            """move_tuple: move, move_type, material, mvva, aggr_type, aggr_value, aggr_color, lost_castling"""
            move, material, move_lost_castling = move_tuple[0], move_tuple[2], move_tuple[7]
            move_lost_castling += lost_castling
            stats.distribution[real_depth] += 1

            n_depth, risk, diff = adjust_depth(move_tuple, depth, real_depth, op, board.turn)

            """ somewhere I should skip moves
            with delta pruning after lazy evaluation or similar? we have the needed information
            https://www.chessprogramming.org/Futility_Pruning
            https://www.chessprogramming.org/Delta_Pruning
            https://www.chessprogramming.org/Razoring
            """

            """ Chess  move """
            board.push(move)
            if real_depth == 0 and op > 1 and board.is_repetition(2):
                board.pop()
                continue

            """ Recursive Call and Value Updating """
            val_list: list = minimax(board, n_depth, False, alpha, beta,
                                     risk, op, material, real_depth + 1, diff, move_lost_castling)

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
            """move_tuple: move, move_type, material, _, aggr_type, aggr_value, aggr_color, lost_castling"""
            move, material, move_lost_castling = move_tuple[0], move_tuple[2], move_tuple[7]
            move_lost_castling += lost_castling

            stats.distribution[real_depth] += 1

            n_depth, risk, diff = adjust_depth(move_tuple, depth, real_depth, op, board.turn)

            # Chess  move
            board.push(move)
            if real_depth == 0 and op > 1 and board.is_repetition(2):
                board.pop()
                continue

            # Recursive Call and Value Updating
            val_list: list = minimax(board, n_depth, True, alpha, beta,
                                     risk, op, material, real_depth + 1, diff, move_lost_castling)

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
    """ implement something to test the function here """
    pass
