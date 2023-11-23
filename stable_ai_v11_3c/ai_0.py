""" from root: python -m stable_ai_YOUR_VERSION.ai_0 """
import chess
import random
import datetime
import time
import inspect

from .minimax import minimax
from . import stats
from .CONSTANTS import INIT_DEPTH
from .tables_maximizer import reset_history_max
from .tables_minimizer import reset_history_min


"""
Sources:
https://www.geeksforgeeks.org/minimax-algorithm-in-game-theory-set-4-alpha-beta-pruning/
https://www.chessprogramming.org/Main_Page
"""

# end_time = 0


def ai_0(board=None, time_limit=30) -> object:
    print(f"-------{chess.COLOR_NAMES[int(board.turn)]}-AI V11.3c ----------------------------")
    # global end_time
    # end_time = time.time() + time_limit

    start_time = time.time()

    """ The main function of the AI """
    stats.n_extensions = 0  # reset
    stats.n_evaluated_leaf_nodes = 0  # reset
    stats.max_real_depth = 0  # reset

    if not board:
        board = chess.Board()

    if board.ply() == 0:
        print("resetting history")
        reset_history_min()
        reset_history_max()

    show_potential_last_capture(board)

    """ Find the Best Move with minimax """
    # get initial material balance - we can calculate relative material balance as it is faster
    init_material_balance = 0
    for piece in board.piece_map().values():
        value = get_piece_value(piece)  # piece_values.get(piece.piece_type, 0)
        if piece.color == chess.WHITE:
            init_material_balance += value
        else:
            init_material_balance -= value

    stats.material_balance_over_time.append(init_material_balance)

    best_move_at_last_index: list
    if board.turn == chess.WHITE:
        best_move_at_last_index = minimax(board, INIT_DEPTH, True, float('-inf'), float('inf'),
                                          0.0, 0, init_material_balance)
    else:
        best_move_at_last_index = minimax(board, INIT_DEPTH, False, float('-inf'), float('inf'),
                                          0.0, 0, init_material_balance)

    end_time = time.time()
    execution_time = round((end_time - start_time) * 1000)
    readable_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print(f"Execution time: {execution_time} milliseconds --- {readable_time}")

    if best_move_at_last_index:
        """ This is some ugly error handling I know """
        if board.turn == chess.WHITE and best_move_at_last_index[0] == float("-inf"):
            return_move = generate_random_move(board)
            check_if_ends_game(board, return_move)
            return return_move
        if board.turn == chess.BLACK and best_move_at_last_index[0] == float("inf"):
            return_move = generate_random_move(board)
            check_if_ends_game(board, return_move)
            return return_move

        move_object = chess.Move.from_uci(best_move_at_last_index[-1])
        print_results_and_stats(board, move_object)

        if move_object.promotion:
            """ this is not necessary anymore, minimax only considers queen promotion """
            from_square = move_object.from_square
            to_square = move_object.to_square
            generated_queen_promotion = chess.Move(from_square, to_square, chess.QUEEN)
            check_if_ends_game(board, generated_queen_promotion)
            return generated_queen_promotion
        check_if_ends_game(board, move_object)
        return move_object
    else:
        return_move = generate_random_move(board)
        check_if_ends_game(board, return_move)
        return return_move


def check_if_ends_game(board: chess.Board, move):
    board.push(move)
    if board.is_game_over():
        stats.print_end_of_game_stats()
    board.pop()


"""def update_depth_stats(real_depth):
    if real_depth > stats.max_real_depth:
        stats.max_real_depth = real_depth  # just for stats
    stats.distribution[real_depth] += 1"""


def get_piece_value(piece) -> int:  # expects piece object not piece type
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
    }
    return piece_values.get(piece.piece_type, 0)


""" The rest: Printing stats etc. """


def print_results_and_stats(board, move_object):

    stats.printf(board.turn)

    move_id = len(board.move_stack) + 1

    if board.is_capture(move_object):
        print(f"Captured: {board.piece_at(move_object.to_square)}")


def show_potential_last_capture(board):
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
        print("")


def inspect_function_name() -> str:
    return inspect.currentframe().f_code.co_name


def generate_random_move(board):
    legal_moves = list(board.legal_moves)
    random_move = random.choice(legal_moves)
    if random_move:
        return random_move


if __name__ == "__main__":
    def test_board_moves():
        board = chess.Board()
        moves = ["e2e4", "c7c6", "f1c4", "d7d5", "e4d5", "c6d5", "c4b5", "c8d7", "d1e2", "e7e6",
                 "g1f3", "d7b5", "e2b5", "d8d7", "b5d3", "b8c6", "f3g5", "c6b4"]

        for uci in moves:
            move = chess.Move.from_uci(uci)
            board.push(move)

        return board

    ai_0(test_board_moves())
