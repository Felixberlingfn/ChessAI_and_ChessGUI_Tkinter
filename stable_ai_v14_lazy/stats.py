from chess import WHITE
from .CONSTANTS import MAXIMUM_REAL_DEPTH
from typing import List
import csv
from datetime import datetime

""" Counters for stats """
sum_of_all_pieces = 78
n_extensions: int = 0
n_early_end: int = 0
""" This one is actually used to determine depth"""
n_evaluated_leaf_nodes: int = 0

starting_material_balance = 0

""" Whole game stats"""
final_execution_times = []
final_evaluated_leaf_nodes = []
material_balance_over_time = []


top_moves: List[list] = []
distribution: list = [0 for _ in range(MAXIMUM_REAL_DEPTH)]
another_debugging_dict: dict = {i: 0 for i in range(MAXIMUM_REAL_DEPTH)}


def sort_top_moves(player_color) -> None:
    global top_moves
    if player_color == WHITE:
        top_moves.sort(key=lambda x: x[0], reverse=True)
    else:
        top_moves.sort(key=lambda x: x[0], reverse=False)


def get_rounded_top_moves():
    rounded_top_moves: List[list] = []
    for sub_list in top_moves:
        rounded_list = [round(item, 2) if isinstance(item, float) else item for item in sub_list]
        rounded_top_moves.append(rounded_list)
    return rounded_top_moves


def get_sorted_top_moves(player_color) -> list:
    if player_color == WHITE:
        sorted_top_moves: list = sorted(top_moves, key=lambda x: x[0], reverse=True)
    else:
        sorted_top_moves: list = sorted(top_moves, key=lambda x: x[0], reverse=False)
    return sorted_top_moves


def reset():
    global n_extensions, n_early_end, n_evaluated_leaf_nodes
    global top_moves, distribution, another_debugging_dict

    n_extensions = 0
    n_early_end = 0
    n_evaluated_leaf_nodes = 0
    top_moves = []
    distribution = [0 for _ in range(MAXIMUM_REAL_DEPTH)]
    another_debugging_dict = {i: 0 for i in range(MAXIMUM_REAL_DEPTH)}


def update_stats(execution_time):
    global final_execution_times, final_evaluated_leaf_nodes
    final_execution_times.append(execution_time)
    final_evaluated_leaf_nodes.append(n_evaluated_leaf_nodes)


def printf(player_color, move_id, execution_time):
    update_stats(execution_time)

    sort_top_moves(player_color)
    rounded_top_moves: List[list] = get_rounded_top_moves()

    print(f"nodes/depth: {distribution}")
    max_real_depth = sum(1 for item in distribution if item != 0)
    print(f"leaf nodes: {n_evaluated_leaf_nodes} maximum depth:{max_real_depth}")
    print(f"{move_id} moves:{rounded_top_moves[:2]}")
    reset()


def print_end_of_game_stats():
    global material_balance_over_time
    global final_execution_times
    global final_evaluated_leaf_nodes

    print(material_balance_over_time)

    directory = 'tournament_results'

    # Get current date and time and format it as a string
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y_%m_%d_%H_%M_%S")
    file_name = f"{formatted_time}.csv"
    file_path = f'{directory}/{file_name}'

    # Write data to a csv file
    headers = ["ply", "balance", "execution time", "leaf nodes"]
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for i, balance in enumerate(material_balance_over_time):
            writer.writerow([i, balance, final_execution_times[i], final_evaluated_leaf_nodes[i]])

    print(f"sum execution time: {sum(final_execution_times)}, nodes: {sum(final_evaluated_leaf_nodes)}")
    material_balance_over_time = []
    final_execution_times = []
    final_evaluated_leaf_nodes = []

