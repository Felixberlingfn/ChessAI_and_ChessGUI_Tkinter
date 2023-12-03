from . import stats, config, tables_maximizer, tables_minimizer, quiescence
from .order_moves import order_moves
from .CONSTANTS import CHECK_X_LIMITER


"""
Sources:
https://www.geeksforgeeks.org/minimax-algorithm-in-game-theory-set-4-alpha-beta-pruning/
https://www.chessprogramming.org/Main_Page
"""

""" I will need to increment the number of pieces to switch from start to endgame"""


def sum_of_pieces(board):
    """not counting the king - side effect on stats.sum_of_all_pieces"""
    piece_values = {1: 1, 2: 3, 3: 3, 4: 5, 5: 9, 6: 0}
    sum_of_all_pieces = 0
    for square_64, piece in board.piece_map().items():
        sum_of_all_pieces += piece_values.get(piece.piece_type, 0)

    stats.sum_of_all_pieces = sum_of_all_pieces
    return sum_of_all_pieces


def minimax(board, depth, max_player, alpha=float('-inf'), beta=float('inf'), op=0, material=0, real_depth=0,
            lost_castling=False, last_move_type=0, last_victim_value=0) -> list:
    """ Minimax returns optimal value for current player """

    material = round(material, 2)

    """ DEPTH EXTENSIONS """
    if depth == 0 and config.check_extension_minimax_active:
        if real_depth < CHECK_X_LIMITER and board.is_check():
            stats.n_check_extensions += 1
            depth += 1

    """ CHECK AND END THE RECURSION: """
    if depth == 0 or board.is_game_over() or real_depth == CHECK_X_LIMITER:  # or time.time() > end_time:
        """if last_move_type == CALM:
            return evaluate_board(board, horizon_risk, op, material, real_depth, lost_castling)"""
        return quiescence.search(board, alpha, beta, 0, max_player, last_move_type, last_victim_value, op,
                                 material, real_depth, lost_castling)

    ordered_moves, op, max_gain = order_moves(board, real_depth, material)

    if real_depth == 0:
        sum_of_pieces(board)
        """if op < 10:
            print("very few available moves, extend search")
            depth += 1
        if sum_of_pieces(board) < 20:  # less than two queens
            print("very few pieces on the board, extend search")
            depth += 1"""
    """if depth > 0 and op < 3 and real_depth < CHECK_X_LIMITER:
        depth += 1"""

    """ MAXIMIZING """
    if max_player:
        best = float('-inf')
        best_list: list = [best]
        """ Loop through moves """
        for move_tuple in ordered_moves:
            """move_tuple: move, move_type, material, mvva, aggr_type, aggr_value, aggr_color, lost_castling, vv"""
            move, move_type, material, move_lost_castling, victim_value = (move_tuple[0], move_tuple[1], move_tuple[2],
                                                                           move_tuple[7], move_tuple[8])
            move_lost_castling += lost_castling
            stats.distribution[real_depth] += 1

            """ Chess  move """
            board.push(move)
            if real_depth == 0 and op > 1 and board.is_repetition(config.max_repetitions):
                board.pop()
                continue

            """ Recursive Call and Value Updating """
            val_list: list = minimax(board, depth - 1, False, alpha, beta, op, material,
                                     real_depth + 1, move_lost_castling, move_type, victim_value)

            # if real_depth == 0: val_list[0] = val_list[0] + ((len(val_list) - 4) * PREFERENCE_DEEP)

            if val_list[0] > best_list[0] or (val_list[0] == best_list[0] and len(val_list) >= len(best_list)):
                # if real_depth == 0: print(f"{val_list[0]} >= {best_list[0]}")
                best_list = val_list
                best_list.append(material)
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
            move, move_type, material, move_lost_castling, victim_value = (move_tuple[0], move_tuple[1], move_tuple[2],
                                                                           move_tuple[7], move_tuple[8])
            move_lost_castling += lost_castling

            stats.distribution[real_depth] += 1

            # Chess  move
            board.push(move)
            if real_depth == 0 and op > 1 and board.is_repetition(config.max_repetitions):
                board.pop()
                continue

            # Recursive Call and Value Updating
            val_list: list = minimax(board, depth - 1, True, alpha, beta, op, material,
                                     real_depth + 1, move_lost_castling, move_type, victim_value)

            # if real_depth == 0: val_list[0] = val_list[0] - ((len(val_list) - 4) * PREFERENCE_DEEP)

            if val_list[0] < best_list[0] or (val_list[0] == best_list[0] and len(val_list) >= len(best_list)):
                # if real_depth == 0: print(f"{val_list[0]} <= {best_list[0]}")
                best_list = val_list
                best_list.append(material)
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
