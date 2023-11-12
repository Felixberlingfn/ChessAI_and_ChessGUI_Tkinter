import random
import chess
# import chess.polyglot
import datetime
import time
import inspect
# import timeit
from typing import Tuple
import evaluate_board
from evaluate_board import evaluate_board

"""
Sources:
https://www.geeksforgeeks.org/minimax-algorithm-in-game-theory-set-4-alpha-beta-pruning/
https://www.chessprogramming.org/Main_Page
"""

""" Constants """
INIT_DEPTH = 3  # initial depth for minimax
CAPTURE_EXTENSION = 2  # depth extension for Quiescence Search (integrated into minimax for simplicity)
CHECK_EXTENSION = 3
# DELTA = 50 not implemented

""" Counters for stats """
n_extensions: int = 0
n_evaluated_leaf_nodes: int = 0

""" Lists for improved move ordering"""
# Initialize the killer moves table with None. Each depth has two slots for killer moves.
# The length is depth + max depth extension + estimate for check extension
killer_moves = [[None, None] for _ in range(INIT_DEPTH + CAPTURE_EXTENSION + CHECK_EXTENSION)]

# Initialize the history table or previously successful moves (64x64 from to)
history_table = [[0 for _ in range(64)] for _ in range(64)]


def my_ai_0_new(board=None, time_limit=0) -> object:
    global n_extensions  # for stats
    n_extensions = 0  # reset
    """ This is the function that will be called to use this module with board as argument"""
    if not board:
        board = chess.Board()

    show_potential_last_capture(board)

    """ Find the Best Move with minimax """
    best_move_at_last_index: list
    if board.turn == chess.WHITE:
        best_move_at_last_index = minimax(board, INIT_DEPTH, True)
    else:
        best_move_at_last_index = minimax(board, INIT_DEPTH, False)

    """ Check if finding best move was successful """
    if best_move_at_last_index:
        print_results_and_stats(board, best_move_at_last_index)
        move_object = chess.Move.from_uci(best_move_at_last_index[-1])
        return move_object
    else:
        print("minimax search failed. Last resort: Use random move to avoid error")
        legal_moves = list(board.legal_moves)
        random_move = random.choice(legal_moves)
        if random_move:
            return random_move
        return False


def order_moves(board, moves, depth) -> list:
    """in contrast to the evaluate board this is BEFORE the move was made"""
    """Helper functions only needed for move ordering"""
    def mvv_lva_score(board, move):
        """ Most Valuable Victim - Least Valuable Attacker"""
        victim_value = get_piece_value(board.piece_at(move.to_square))
        aggressor_value = get_piece_value(board.piece_at(move.from_square))
        return victim_value - aggressor_value

    """Main Move Ordering"""
    try:
        killers = killer_moves[depth] if depth <= len(killer_moves) else []
        non_killer_moves = []
        confirmed_killer_moves = []
        """higher priority to killer moves"""
        for move in moves:
            if move in killers:
                confirmed_killer_moves.insert(0, move)  # Insert killer moves to the front
            else:
                non_killer_moves.append(move)
        """higher priority to capture moves"""
        captures_and_checks = [move for move in non_killer_moves if board.is_capture(move) or board.gives_check(move) or move.promotion]  # or board.gives_check(move) or move.promotion
        """ order captures_and_checks by most valuable victim """
        if len(captures_and_checks) > 1:
            captures_and_checks.sort(key=lambda m: mvv_lva_score(board, m), reverse=True)
        """ order quiet_moves by n in history table """
        quiet_moves = [move for move in non_killer_moves if not board.is_capture(move)]
        quiet_moves.sort(key=lambda m: history_table[m.from_square][m.to_square], reverse=True)
        """Now put everything together to make the final list"""
        ordered_moves = captures_and_checks + confirmed_killer_moves + quiet_moves
        return ordered_moves
    except Exception as error:
        print(f"{error} in order_moves.")
        return moves  # return unordered moves


def minimax(board, depth, max_player, alpha=float('-inf'), beta=float('inf'),
            quiet_search=False, horizon_risk=0) -> list:

    """Minimax returns optimal value for current player """
    global n_evaluated_leaf_nodes
    global n_extensions
    """ checking board for depth extension"""
    if depth == 0 and board.is_check():
        depth = CHECK_EXTENSION
        n_extensions += CHECK_EXTENSION
        horizon_risk = 0
        quiet_search = True
    if depth == 0 or board.is_game_over():
        """ Final Node reached. Do the Evaluation of the board"""
        final_val_list = evaluate_board(board, horizon_risk)
        n_evaluated_leaf_nodes += 1
        return final_val_list

    # here we could implement looking up a hash

    """ MAXIMIZING """
    if max_player:
        best = float('-inf')
        best_list: list = [best]
        """ Loop through moves """
        for move in order_moves(board, board.legal_moves, depth):
            next_depth, quiet_search, horizon_risk = get_next_depth(board, move, depth, quiet_search)
            """ Chess  move"""
            board.push(move)
            """ Recursive Call and Value Updating """
            val_list: list = minimax(board, next_depth, False, alpha, beta, quiet_search, horizon_risk)
            if val_list[0] >= best_list[0]:
                best_list = val_list  # use the evaluation list as the new best list
                best_list.append(board.uci(move))   # append the move history
            alpha = max(alpha, best_list[0])
            """ Undo Chess  move """
            board.pop()
            """ Alpha Beta Pruning """
            if beta <= alpha:
                """ Killer moves for move ordering """
                try:
                    if move not in killer_moves[depth]:
                        killer_moves[depth].insert(0, move)
                        killer_moves[depth].pop()
                except Exception as error:
                    print(f"{error} killer moves list too short. that's ok")
                """ Update history table """
                update_history_table(move, depth)
                break
        # maybe zobrist hash the board fen?
        return best_list

    # minimizing
    else:
        best = float('inf')
        best_list: list = [best]
        # loop through moves
        for move in order_moves(board, board.legal_moves, depth):
            next_depth, quiet_search, horizon_risk = get_next_depth(board, move, depth, quiet_search)
            # Chess  move"""
            board.push(move)
            # Recursive Call and Value Updating"""
            val_list: list = minimax(board, next_depth, True, alpha, beta, quiet_search, horizon_risk)
            if val_list[0] <= best_list[0]:
                best_list = val_list
                best_list.append(board.uci(move))  # append the move history
            beta = min(beta, best_list[0])
            # Undo Chess  move"""
            board.pop()
            # Alpha Beta Pruning"""
            if beta <= alpha:
                # Killer moves for move ordering
                try:
                    if move not in killer_moves[depth]:
                        killer_moves[depth].insert(0, move)
                        killer_moves[depth].pop()
                except Exception as error:
                    print(f"{error} killer moves list too short. that's ok")
                # Update history table
                update_history_table(move, depth)
                break
        # maybe zobrist hash the board fen?
        return best_list


def get_next_depth(board, move, depth: int, quiet_search: bool = False) -> Tuple[int, bool, float]:
    # gets the depth of the next minimax recursion
    # taking into account depth extension, quiescence and a horizon risk
    global n_extensions
    end_quiescence_checks = True
    start_quiescence_checks = True  # means it only starts on checks
    use_horizon_risk = True

    def calculate_horizon_risk() -> float:
        # because of horizon uncertainty let's not overvalue the capture/loss
        attacker_piece = board.piece_at(move.from_square)  # victim already in material balance
        if attacker_piece.color == chess.WHITE:
            horizon_risk: float = get_piece_value(attacker_piece) * 0.5  # bad for white when subst. later
        else:
            horizon_risk: float = - get_piece_value(attacker_piece) * 0.5  # bad for black when subst. later
        return horizon_risk

    def has_threats() -> bool:
        # Get the position of high value pieces
        critical_sqs_white: set = board.pieces(chess.QUEEN, chess.WHITE) | board.pieces(chess.ROOK, chess.WHITE)
        critical_sqs_black: set = board.pieces(chess.QUEEN, chess.BLACK) | board.pieces(chess.ROOK, chess.BLACK)

        for critical_sq_w in critical_sqs_white:
            if board.is_attacked_by(chess.BLACK, critical_sq_w):
                return True
        for critical_sq_b in critical_sqs_black:
            if board.is_attacked_by(chess.WHITE, critical_sq_b):
                return True
        return False

    # default
    if not quiet_search and depth != 1:
        # we are not doing quiescence search yet and have not yet reached final move
        return depth - 1, False, 0  # quiet_search=False

    if start_quiescence_checks:
        # we have reached the final move - check if we should start quiescence search
        if not quiet_search and depth == 1:
            # we are reaching final node and are not yet performing quiescence search
            if board.is_capture(move) or move.promotion:
                # we are in a critical situation and should do a quiescence extension
                n_extensions += CAPTURE_EXTENSION  # just for stats
                return (depth + CAPTURE_EXTENSION), True, 0  # quiet_search=True

    if end_quiescence_checks:
        # check if we should end quiescence search
        if quiet_search and depth != 1:
            if board.is_capture(move) or move.promotion:
                return depth - 1, True, 0  # continue quiet_search
            else:
                return 0, True, 0  # quiet stage reach - end quiescence search early

    if use_horizon_risk:
        if depth == 1 and quiet_search:
            # quiet search extension limit reached
            if board.is_capture(move):
                risk = calculate_horizon_risk()
                if risk > 8 or risk < -8:
                    n_extensions += 1  # just for stats
                    return 1, True, 0  # queen risk extension
                return 0, True, risk
            return 0, True, 0

    # quiescence default
    return depth-1, True, 0 # quiet_search=True


""" Move Ordering Helper Functions """


def update_history_table(move, depth):
    from_square = move.from_square
    to_square = move.to_square
    history_table[from_square][to_square] += depth ** 2  # Weight by depth squared


def get_piece_value(piece) -> int:  # expects piece object not piece type
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
    }
    if not piece:
        return 0
    return piece_values.get(piece.piece_type, 0)


""" The rest: Printing stats etc. """


def print_results_and_stats(board, best_move_at_index_depth):
    try:
        # print stats
        # print_top_history_moves(history_table, top_n=3)
        print(f"Leaf nodes evaluated: {n_evaluated_leaf_nodes} with {n_extensions} extensions")
        # print results
        rounded_list = [round(item, 2) if isinstance(item, float) else item for item in best_move_at_index_depth]
        print("first move last:", rounded_list)
        readable_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        move_id = len(board.move_stack) + 1
        print(f"Move # {move_id}: {best_move_at_index_depth[-1]}. [Sum, Pos., ..., ..., Path... ]"
              f" - {readable_time}")
        move_object = chess.Move.from_uci(best_move_at_index_depth[-1])
        if board.is_capture(move_object):
            print(f"Captured: {board.piece_at(move_object.to_square)}")
    except Exception as error:
        print(f"{error} in {inspect_function_name()}")


def print_top_history_moves(history_table, top_n=10):
    move_scores = []
    for from_square in range(64):
        for to_square in range(64):
            score = history_table[from_square][to_square]
            if score > 0:
                move_scores.append(((from_square, to_square), score))

    # Sort the moves by score in descending order
    move_scores.sort(key=lambda x: x[1], reverse=True)

    # Print the top 'n' moves
    for i in range(min(top_n, len(move_scores))):
        from_sq = chess.square_name(move_scores[i][0][0])
        to_sq = chess.square_name(move_scores[i][0][1])
        print(f"{from_sq}{to_sq} has {move_scores[i][1]} Beta cutoffs")


def show_potential_last_capture(board):
    try:
        if board.move_stack:  # Check if there are any moves made
            last_move = board.peek()
            if last_move and board.is_capture(last_move):
                # Undo the last move to see what was at the to_square
                board.pop()
                captured_piece = board.piece_at(last_move.to_square)
                # Redo the move
                board.push(last_move)
                if captured_piece:
                    print(f"Lost: {captured_piece}")
        else:
            print("")  # just starting the game, make a newline
    except Exception as error:
        print(f"{error} in {inspect_function_name()}")

def inspect_function_name() -> str:
    return inspect.currentframe().f_code.co_name


if __name__ == "__main__":
    def test_board_moves():
        board = chess.Board()
        moves = ["e2e4", "d7d5", "f1c4", "g8f6", "g1f3", "e7e6", "b1c3", "f8e7", "d1e2", "c8g4"]

        for uci in moves:
            move = chess.Move.from_uci(uci)
            board.push(move)

        return board

    start_time = time.time()
    my_ai_0_new(test_board_moves())
    end_time = time.time()
    execution_time = round((end_time - start_time) * 1000)
    print(f"Execution time: {execution_time} milliseconds")
