from .evaluate_board import evaluate_board
from .order_moves import order_moves
from . import stats, tables_maximizer, tables_minimizer, config
from .CONSTANTS import CALM, QUIESCENCE_DEPTH, PROMOTION


def search(board, alpha, beta, depth, is_maximizing, last_move_type, last_victim_value, last_op, last_material,
           real_depth, lost_castling):

    if board.is_game_over():
        """ evaluate immediately, skip op calculation """
        return evaluate_board(board, 0, 0, 0, real_depth, 0, 0)

    ordered_moves, op, max_gain = order_moves(board, real_depth, last_material)

    # 0) if absolute limit reached, end quiescence
    if real_depth > QUIESCENCE_DEPTH:
        return evaluate_board(board, 0, last_op, last_material, real_depth, lost_castling, op)

    always_continue_q = False
    if config.always_extend_high_value and (last_victim_value > config.high_value_bound or last_move_type == PROMOTION):
        always_continue_q = True
        last_victim_value = config.lower_the_bound_val  # new victims have to have higher value than that

    """if max_gain + config.victim_safety_margin < last_victim_value ... """
    if not always_continue_q:
        # 1) check if end q search because low gain
        if max_gain + config.victim_safety_margin <= last_victim_value and \
                (config.q_check_ext_deactivated or not board.is_check()):
            return evaluate_board(board, max_gain, last_op, last_material, real_depth, lost_castling, op)

        # 2) check if end q search because low last gain (was calm, doesn't have the same horizon risk)
        elif last_move_type == CALM and (config.q_check_ext_deactivated or not board.is_check()):
            return evaluate_board(board, 0, last_op, last_material, real_depth, lost_castling, op)

    if config.lower_last_victim_value and last_victim_value > config.lower_the_bound_val:
        last_victim_value = config.lower_the_bound_val

    """ I think I actually do need stand pat ?? I don't really understand this part """
    if config.stand_pat_active:
        stand_pat: list = evaluate_board(board, 0, last_op, last_material, real_depth, lost_castling, op, True)
        if stand_pat[0] >= beta:
            return stand_pat
        if stand_pat[0] > alpha:
            alpha = stand_pat[0]

    """ stats """
    stats.distribution[real_depth] += 1  # number of nodes at depth in general
    stats.quiescence_search_started += 1  # number of quiescence nodes

    """ let's implement the recursion """
    if is_maximizing:
        best = float('-inf')
        """ I need to test the effect of this I am not sure when or not to apply it """
        best_list: list = [best]

        for move_tuple in ordered_moves:
            """move, move_type, material, mvv_lva, aggr_type, aggr_value, aggr_color, lost_castling, vv"""
            move_type = move_tuple[1]
            victim_value = move_tuple[8]

            """ only promising captures with delta pruning """
            """if (last_material + victim_value + config.delta_safety_margin) * 100 >= beta:"""
            if victim_value + config.victim_safety_margin >= last_victim_value and \
                    (last_material + victim_value + config.delta_safety_margin) * 100 >= beta:
                move, material, move_lost_castling = move_tuple[0], move_tuple[2], move_tuple[7]
            else:
                continue  # skip

            move_lost_castling += lost_castling

            board.push(move)

            val_list = search(board, alpha, beta, depth, False, move_type, victim_value, op, material,
                              real_depth + 1, move_lost_castling)

            if val_list[0] >= best_list[0]:
                best_list = val_list
                best_list.append(last_material)
                best_list.append(board.uci(move))
            alpha = max(alpha, best_list[0])

            board.pop()

            """ Pruning """
            if beta < alpha:  # should be <=
                tables_maximizer.add_to_killers_and_history(move, real_depth)
                break

        if best_list[0] == float("-inf"):
            return evaluate_board(board, 0, last_op, last_material, real_depth, lost_castling, op)
        return best_list

    else:
        best = float('inf')
        best_list: list = [best]

        for move_tuple in ordered_moves:
            """move, move_type, material, mvv_lva, aggr_type, aggr_value, aggr_color, lost_castling, vv"""
            move_type = move_tuple[1]
            victim_value = move_tuple[8]

            # only promising captures with delta pruning
            """if (last_material - victim_value - config.delta_safety_margin) * 100 <= alpha:"""
            """ just a note: for check evasions all moves are searched."""
            if victim_value + config.victim_safety_margin >= last_victim_value and \
                    (last_material - victim_value - config.delta_safety_margin) * 100 <= alpha:
                move, material, move_lost_castling = move_tuple[0], move_tuple[2], move_tuple[7]
            else:
                continue  # skip

            move_lost_castling += lost_castling

            board.push(move)

            val_list = search(board, alpha, beta, depth, True, move_type, victim_value, op, material,
                              real_depth + 1, move_lost_castling)

            if val_list[0] <= best_list[0]:
                best_list = val_list
                best_list.append(last_material)
                best_list.append(board.uci(move))
            beta = min(beta, best_list[0])

            board.pop()

            # Pruning
            if beta < alpha:  # should be <=
                tables_minimizer.add_to_killers_and_history(move, real_depth)
                break

        if best_list[0] == float("inf"):
            return evaluate_board(board, 0, last_op, last_material, real_depth, lost_castling, op)
            # print("might be problematic")

        return best_list

