from .evaluate_board import evaluate_board
from .order_moves import order_moves
from . import stats
from .CONSTANTS import CHECK_X_LIMITER, CALM, CAPTURE, PROMOTION, CHECK

""" placeholder for now """


def search(board, depth, is_maximizing, last_move_type, last_victim_value, horizon_risk=0, last_op=0, last_material=0,
           real_depth=0, lost_castling=0):
    """placeholder"""
    ordered_moves, op, max_gain = order_moves(board, real_depth, last_material)

    """I can also use current op in evaluation, skipping it in evaluate board """

    """ I should also look at who the capture is done with. if it is a high value piece or not"""
    if max_gain <= last_victim_value:
        """ this might be flawed or it might work"""
        # if max_gain > 0: print(f"{max_gain} <= {last_victim_value}")
        stats.n_evaluated_leaf_nodes += 1
        return evaluate_board(board, max_gain, last_op, last_material, real_depth, lost_castling, op)
    elif last_move_type == CALM:
        # not go in quiescence if last move was no capture?
        # I mean every gain would be higher.
        # though maybe that is ok, we will still see if anything is higher after that
        stats.n_evaluated_leaf_nodes += 1
        return evaluate_board(board, 0, last_op, last_material, real_depth, lost_castling, op)

        pass
        # print(f"{max_gain} > {last_victim_value}")
        """# for now, if there is a more valuable response return as if capture did not happen
        search_1(ordered_moves, is_maximizing)
        stats.n_evaluated_leaf_nodes += 1
        return evaluate_board(board, last_victim_value, last_op, last_material, real_depth, lost_castling)"""

    stats.quiescence_search_started += 1

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
                              real_depth + 1, move_lost_castling)

            if val_list[0] >= best_list[0]:
                best_list = val_list
                best_list.append("max")
                best_list.append(material)
                best_list.append(last_victim_value)
                best_list.append(max_gain)
                best_list.append(board.uci(move))

            board.pop()

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
                              real_depth + 1, move_lost_castling)

            if val_list[0] <= best_list[0]:
                best_list = val_list
                best_list.append("min")
                best_list.append(material)
                best_list.append(last_victim_value)
                best_list.append(max_gain)
                best_list.append(board.uci(move))

            board.pop()

        return best_list









""" for testing I could also not make it recursive """


def search_1(ordered_moves, is_maximizing):
    pass


def search_2():
    pass

