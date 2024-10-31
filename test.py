import sys

from src.utils import *
from src.algorithms.bfs import *
from src.algorithms.dfs import *
from src.algorithms.ucs import *
from src.algorithms.astar import *

if __name__ == '__main__':
    layout, stone_weight, method = read_command(sys.argv[1:]).values()
    game_state = transfer_to_game_state(layout)

    if method == 'bfs':
        step_cnt, node_cnt, weight_total, duration, memory_usage, steps = execute_algorithm(game_state, stone_weight, breadth_first_search)
        print('BFS')
    elif method == 'dfs':
        step_cnt, node_cnt, weight_total, duration, memory_usage, steps = execute_algorithm(game_state, stone_weight, depth_first_search)
        print('DFS')
    elif method == 'ucs':
        step_cnt, node_cnt, weight_total, duration, memory_usage, steps = execute_algorithm(game_state, stone_weight, uniform_cost_search)
        print('UCS')
    elif method == 'astar':
        step_cnt, node_cnt, weight_total, duration, memory_usage, steps = execute_algorithm(game_state, stone_weight, a_star_search)
        print('A*')
    else:
        raise ValueError('Invalid method.')

    print('Steps: %d, Weight: %d, Node: %d, Time (ms): %.2f, Memory (MB): %.2f' %(step_cnt, weight_total, node_cnt, duration, memory_usage))
    for step in steps:
        print(step, end='')