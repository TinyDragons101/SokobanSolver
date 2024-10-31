import sys

from src.utils import *
from src.algorithms.bfs import *
from src.algorithms.dfs import *
from src.algorithms.ucs import *
from src.algorithms.astar import *

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(CURRENT_DIR, "outputs")

if __name__ == '__main__':
    game_state, stone_weight = get_game_state(sys.argv[1])
    output_file = "out" + sys.argv[1][2:]
    with open(os.path.join(OUTPUT_DIR, output_file), "w") as f:
        write_search_output(game_state, stone_weight, breadth_first_search, 'BFS', output_file)
        write_search_output(game_state, stone_weight, depth_first_search, 'DFS', output_file)
        write_search_output(game_state, stone_weight, uniform_cost_search, 'UCS', output_file)
        write_search_output(game_state, stone_weight, a_star_search, 'A*', output_file)