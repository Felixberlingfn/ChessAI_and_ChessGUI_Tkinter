from stable_ai_v2.CONSTANTS import MAXIMUM_REAL_DEPTH

""" Counters for stats """
n_extensions: int = 0
n_early_end: int = 0
n_evaluated_leaf_nodes: int = 0
max_real_depth: int = 0

distribution = [0 for _ in range(MAXIMUM_REAL_DEPTH)]

another_debugging_dict = {i: 0 for i in range(MAXIMUM_REAL_DEPTH)}

def printf():
    print(f"Leaf nodes: {n_evaluated_leaf_nodes} extensions: {n_extensions} maximum depth:{max_real_depth}")
    # print(distribution)
    # print(another_debugging_dict)
