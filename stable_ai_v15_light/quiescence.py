from .evaluate_board import evaluate_board
from .order_moves import order_moves
from . import stats, tables_maximizer, tables_minimizer
from .CONSTANTS import CHECK_X_LIMITER, CALM, CAPTURE, PROMOTION, CHECK, QUIESCENCE_DEPTH


def search(board, depth, is_maximizing, last_move_type, last_victim_value, horizon_risk=0, last_op=0, last_material=0,
           real_depth=0, lost_castling=0, alpha=float('-inf'), beta=float('inf')):
    ordered_moves, op, max_gain = order_moves(board, real_depth, last_material)

    """I can also use current op in evaluation, skipping it in evaluate board """

    if max_gain <= last_victim_value or real_depth > QUIESCENCE_DEPTH:
        return evaluate_board(board, max_gain, last_op, last_material, real_depth, lost_castling, op)
    elif last_move_type == CALM:
        return evaluate_board(board, 0, last_op, last_material, real_depth, lost_castling, op)

    """ only now the real quiescence search starts """
    stats.quiescence_search_started += 1

    """ I think I actually do need stand pat ?? I don't really understand this part """
    stand_pat = evaluate_board(board, 0, last_op, last_material, real_depth, lost_castling, op, True)

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

            val_list = search(board, depth, False, move_type, victim_value, horizon_risk, op, material,
                              real_depth + 1, move_lost_castling, alpha, beta)

            if val_list[0] >= best_list[0]:
                best_list = val_list
                # best_list.append("max")
                # best_list.append(material)
                # best_list.append(last_victim_value)
                # best_list.append(max_gain)
                best_list.append(last_material)  # does this affect anything?
                best_list.append(board.uci(move))
                alpha = max(alpha, best_list[0])

            board.pop()

            """ Pruning """
            if beta <= alpha:  # should be <=
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

            val_list = search(board, depth, True, move_type, victim_value, horizon_risk, op, material,
                              real_depth + 1, move_lost_castling, alpha, beta)

            if val_list[0] <= best_list[0]:
                best_list = val_list
                # best_list.append("min")
                # best_list.append(material)
                # best_list.append(last_victim_value)
                # best_list.append(max_gain)
                best_list.append(last_material)
                best_list.append(board.uci(move))
                beta = min(beta, best_list[0])

            board.pop()

            # Pruning
            if beta <= alpha:  # should be <=
                tables_minimizer.add_to_killers_and_history(move, real_depth)
                break

        return best_list

