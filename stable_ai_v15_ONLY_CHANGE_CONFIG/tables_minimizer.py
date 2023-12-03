from chess import square_name
from .CONSTANTS import MAXIMUM_REAL_DEPTH


""" Lists for improved move ordering"""
killer_moves_min = [[None, None] for _ in range(MAXIMUM_REAL_DEPTH)]
history_table_min = [[0 for _ in range(64)] for _ in range(64)]
transposition_table_min = {}


def update_history_table(from_square, to_square, depth):
    history_table_min[from_square][to_square] += depth ** 2  # Weight by depth squared


def reset_history_min():
    global history_table_min
    global killer_moves_min
    """only reset history after whole match is over"""
    history_table_min = [[0 for _ in range(64)] for _ in range(64)]
    killer_moves_min = [[None, None] for _ in range(MAXIMUM_REAL_DEPTH)]


def add_to_killers_and_history(move, real_depth):
    """ Killer moves for move ordering """
    if move not in killer_moves_min[real_depth]:
        killer_moves_min[real_depth].insert(0, move)
        killer_moves_min[real_depth].pop()
    """ Update history table """
    update_history_table(move.from_square, move.to_square, real_depth)  # was depth


def print_top(top_n=10):
    move_scores = []
    for from_square in range(64):
        for to_square in range(64):
            score = history_table_min[from_square][to_square]
            if score > 0:
                move_scores.append(((from_square, to_square), score))

    # Sort the moves by score in descending order
    move_scores.sort(key=lambda x: x[1], reverse=True)

    # Print the top 'n' moves
    for i in range(min(top_n, len(move_scores))):
        from_sq = square_name(move_scores[i][0][0])
        to_sq = square_name(move_scores[i][0][1])
        print(f"{from_sq}{to_sq} has {move_scores[i][1]} Beta cutoffs")
