""" Counters for stats """
n_extensions: int = 0
n_evaluated_leaf_nodes: int = 0
max_real_depth: int = 0


def printf():
    print(f"Leaf nodes: {n_evaluated_leaf_nodes} extensions: {n_extensions} maximum depth:{max_real_depth}")
