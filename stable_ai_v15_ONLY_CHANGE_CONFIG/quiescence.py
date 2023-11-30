from .evaluate_board import evaluate_board
from .order_moves import order_moves
from . import stats, tables_maximizer, tables_minimizer, config
from .CONSTANTS import CHECK_X_LIMITER, CALM, CAPTURE, PROMOTION, CHECK


def search(board, alpha, beta, depth, is_maximizing, last_move_type, last_victim_value, last_op, last_material,
           real_depth, lost_castling):

    ordered_moves, op, max_gain = order_moves(board, real_depth, last_material)

    # continue_quiescence, gain_high, last_capt_promo, is_check, gives_check = False, False, False, False, False

    # 1) no higher capture available + also not currently in check
    if max_gain + 1 < last_victim_value and \
            (config.q_check_ext_deactivated or not (board.is_check() and real_depth < CHECK_X_LIMITER)):
        stats.n_evaluated_leaf_nodes += 1
        return evaluate_board(board, max_gain, last_op, last_material, real_depth, lost_castling, op)

    # 2) higher capture available but there was no capture + also not currently in check
    elif last_move_type == CALM and \
            (config.q_check_ext_deactivated or not (board.is_check() and real_depth < CHECK_X_LIMITER)):
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

            """ only promising captures with delta pruning """
            if victim_value + config.delta_safety_margin >= last_victim_value and \
                    (last_material + victim_value + config.delta_safety_margin) * 100 >= beta:
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
                best_list.append(last_material)
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

            # only promising captures with delta pruning
            if victim_value + config.delta_safety_margin >= last_victim_value and \
                    (last_material - victim_value - config.delta_safety_margin) * 100 <= alpha:
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
                best_list.append(last_material)
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

