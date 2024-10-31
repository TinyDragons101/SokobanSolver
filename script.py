import sys

from src.utils import *
from src.algorithms.bfs import *
from src.algorithms.dfs import *
from src.algorithms.ucs import *
from src.algorithms.astar import *

if __name__ == '__main__':
    game_state, stone_weight = get_game_state(sys.argv[1])
    id = sys.argv[1][-6:-4]
    output_file = "output-" + id + ".txt"
    with open("./outputs/" + output_file, "w") as f:
        write_search_output(game_state, stone_weight, breadth_first_search, 'BFS', output_file)
        write_search_output(game_state, stone_weight, depth_first_search, 'DFS', output_file)
        write_search_output(game_state, stone_weight, uniform_cost_search, 'UCS', output_file)
        write_search_output(game_state, stone_weight, a_star_search, 'A*', output_file)