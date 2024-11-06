import os
import sys

from src.utils import *
from src.algorithms.bfs import *
from src.algorithms.dfs import *
from src.algorithms.ucs import *
from src.algorithms.astar import *

if __name__ == '__main__':
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    game_state, stone_weight = get_game_state(os.path.join(CURRENT_DIR, sys.argv[1]))
    output_file = "out" + sys.argv[1][2:]
    with open(os.path.join(CURRENT_DIR, output_file), "w") as f:
        write_search_output(game_state, stone_weight, 'BFS', breadth_first_search, f)
        write_search_output(game_state, stone_weight, 'DFS', depth_first_search, f)
        write_search_output(game_state, stone_weight, 'UCS', uniform_cost_search, f)
        write_search_output(game_state, stone_weight, 'A*', a_star_search, f)