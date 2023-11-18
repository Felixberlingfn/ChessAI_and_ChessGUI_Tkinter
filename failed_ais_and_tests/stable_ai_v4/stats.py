from .CONSTANTS import MAXIMUM_REAL_DEPTH

""" Counters for stats """
n_extensions: int = 0
n_early_end: int = 0
n_evaluated_leaf_nodes: int = 0
max_real_depth: int = 0

distribution = [0 for _ in range(MAXIMUM_REAL_DEPTH)]

top_moves = []

another_debugging_dict = {i: 0 for i in range(MAXIMUM_REAL_DEPTH)}


def printf():
    global top_moves
    print(f"Leaf nodes: {n_evaluated_leaf_nodes} maximum depth:{max_real_depth}")  # extensions: {n_extensions}
    sorted_top_moves = sorted(top_moves, key=lambda x: x[0], reverse=True)
    print(f"top 5:{sorted_top_moves[:5]}")
    top_moves = []

    print(f"visualize this distribution: {distribution}")
    # print(another_debugging_dict)
