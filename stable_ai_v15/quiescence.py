from .evaluate_board import evaluate_board
from .order_moves import order_moves
from . import stats, tables_maximizer, tables_minimizer
from .CONSTANTS import CHECK_X_LIMITER, CALM, CAPTURE, PROMOTION, CHECK

""" placeholder for now """


def search(board, alpha, beta, depth, is_maximizing, last_move_type, last_victim_value, last_op, last_material,
           real_depth, lost_castling):
    """placeholder"""
    ordered_moves, op, max_gain = order_moves(board, real_depth, last_material)

    """I can also use current op in evaluation, skipping it in evaluate board """

    """ I should also look at who the capture is done with. if it is a high value piece or not"""
    higher_value_capture_possible = False
    board_is_in_check = False
    move_giving_check_is_possible = False

    if max_gain <= last_victim_value:
        if not (board.is_check() and real_depth < CHECK_X_LIMITER):
            stats.n_evaluated_leaf_nodes += 1
            return evaluate_board(board, max_gain, last_op, last_material, real_depth, lost_castling, op)
    elif last_move_type == CALM:
        if not (board.is_check() and real_depth < CHECK_X_LIMITER):
            stats.n_evaluated_leaf_nodes += 1
            return evaluate_board(board, 0, last_op, last_material, real_depth, lost_castling, op)

    """ only now the real quiescence search starts """
    stats.quiescence_search_started += 1  # number of quiescence nodes

    """ let's implement the recursion """
    if is_maximizing:
        best = float('-inf')
        best_list: list = [best]

        for move_tuple in ordered_moves:
            """move, move_type, material, mvv_lva, aggr_type, aggr_value, aggr_color, lost_castling, vv"""
            move_type = move_tuple[1]
            victim_value = move_tuple[8]

            if victim_value > last_victim_value:
                stats.distribution[real_depth] += 1
                move, material, move_lost_castling = move_tuple[0], move_tuple[2], move_tuple[7]
            else:
                continue  # skip

            move_lost_castling += lost_castling

            board.push(move)

            val_list = search(board, alpha, beta, depth, False, move_type, victim_value, op, material,
                              real_depth + 1, move_lost_castling)

            if val_list[0] >= best_list[0]:
                best_list = val_list
                best_list.append("max")
                best_list.append(material)
                best_list.append(last_victim_value)
                best_list.append(max_gain)
                best_list.append(board.uci(move))
            alpha = max(alpha, best_list[0])

            board.pop()

            """ Pruning """
            if beta <= alpha:
                tables_maximizer.add_to_killers_and_history(move, real_depth)
                break

        return best_list

    else:
        best = float('inf')
        best_list: list = [best]

        for move_tuple in ordered_moves:
            """move, move_type, material, mvv_lva, aggr_type, aggr_value, aggr_color, lost_castling, vv"""
            move_type = move_tuple[1]
            victim_value = move_tuple[8]

            if victim_value > last_victim_value:
                stats.distribution[real_depth] += 1
                move, material, move_lost_castling = move_tuple[0], move_tuple[2], move_tuple[7]
            else:
                continue  # skip

            move_lost_castling += lost_castling

            board.push(move)

            val_list = search(board, alpha, beta, depth, True, move_type, victim_value, op, material,
                              real_depth + 1, move_lost_castling)

            if val_list[0] <= best_list[0]:
                best_list = val_list
                best_list.append("min")
                best_list.append(material)
                best_list.append(last_victim_value)
                best_list.append(max_gain)
                best_list.append(board.uci(move))
            beta = min(beta, best_list[0])

            board.pop()

            # Pruning
            if beta <= alpha:
                tables_minimizer.add_to_killers_and_history(move, real_depth)
                break

        return best_list









""" for testing I could also not make it recursive """


def search_1(ordered_moves, is_maximizing):
    pass


def search_2():
    pass

