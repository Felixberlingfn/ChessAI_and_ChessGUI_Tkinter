from chess import WHITE
from .CONSTANTS import MAXIMUM_REAL_DEPTH
from typing import List
import csv
from datetime import datetime

""" Counters for stats """
n_extensions: int = 0
n_early_end: int = 0
n_evaluated_leaf_nodes: int = 0

top_moves: List[list] = []

distribution: list = [0 for _ in range(MAXIMUM_REAL_DEPTH)]
another_debugging_dict: dict = {i: 0 for i in range(MAXIMUM_REAL_DEPTH)}

material_balance_over_time = []


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


def printf(player_color):
    sort_top_moves(player_color)
    rounded_top_moves: List[list] = get_rounded_top_moves()

    print(f"visualize this distribution: {distribution}")
    max_real_depth = sum(1 for item in distribution if item != 0)
    print(f"Leaf nodes: {n_evaluated_leaf_nodes} maximum depth:{max_real_depth}")
    print(f"top 2:{rounded_top_moves[:2]}")
    reset()


def print_end_of_game_stats():
    global material_balance_over_time
    print(material_balance_over_time)

    directory = 'tournament_results'

    # Get current date and time and format it as a string
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y_%m_%d_%H_%M_%S")
    file_name = f"{formatted_time}.csv"
    file_path = f'{directory}/{file_name}'

    # Write data to a csv file
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        for balance in material_balance_over_time:
            writer.writerow([balance])

    material_balance_over_time = []

