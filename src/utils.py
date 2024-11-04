import os
from optparse import OptionParser
import numpy as np
import subprocess
import tracemalloc

from src.algorithms.bfs import *
from src.algorithms.dfs import *
from src.algorithms.ucs import *
from src.algorithms.astar import *

TEST_DIR = os.path.join("tests")
OUTPUT_DIR = os.path.join("outputs")

SPACE = " "
WALL = "#"
ARES = "@"
STONE = "$"
SWITCH = "."
STONE_ON_SWITCH = "*"
ARES_ON_SWITCH = "+"

def read_command(argv):
    """Read command arguments"""
    parser = OptionParser()
    parser.add_option('-l', '--level', dest='sokoban_levels', default='input-01.txt')
    parser.add_option('-m', '--method', dest='agent_method', default='bfs')
    
    options, _ = parser.parse_args(argv)
    args = dict()

    with open(os.path.join(TEST_DIR, options.sokoban_levels), "r") as f:
        weight_line = f.readline().strip()
        stone_weight = weight_line.split(' ')
        stone_weight = tuple(int(x) for x in stone_weight)
        
        layout = f.readlines()

    args['layout'] = layout
    args['stone_weight'] = stone_weight
    args['method'] = options.agent_method
    return args

def transfer_to_game_state(layout):
    """Transfer the layout to the initial game state"""
    layout = [x.replace('\n','') for x in layout]
    layout = [list(x) for x in layout]
    max_num_cols = max([len(x) for x in layout])
    for irow in range(len(layout)):
        for icol in range(len(layout[irow])):
            if layout[irow][icol] == SPACE: layout[irow][icol] = 0
            elif layout[irow][icol] == WALL: layout[irow][icol] = 1
            elif layout[irow][icol] == ARES: layout[irow][icol] = 2
            elif layout[irow][icol] == STONE: layout[irow][icol] = 3
            elif layout[irow][icol] == SWITCH: layout[irow][icol] = 4
            elif layout[irow][icol] == STONE_ON_SWITCH: layout[irow][icol] = 5
            elif layout[irow][icol] == ARES_ON_SWITCH: layout[irow][icol] = 6
        num_cols = len(layout[irow])
        if num_cols < max_num_cols:
            layout[irow].extend([-1 for _ in range(max_num_cols - num_cols)]) 
    
    for irow in range(len(layout)):
        for icol in range(len(layout[0])):
            if layout[irow][icol] > 0:
                break
            elif layout[irow][icol] == 0:
                layout[irow][icol] = -1

    for icol in range(len(layout[0])):
        for irow in range(len(layout)):
            if layout[irow][icol] > 0:
                break
            elif layout[irow][icol] == 0:
                layout[irow][icol] = -1
    
    for icol in range(len(layout[0])):
        for irow in range(len(layout) - 1, -1, -1):
            if layout[irow][icol] > 0:
                break
            elif layout[irow][icol] == 0:
                layout[irow][icol] = -1

    return np.array(layout)

def get_game_state(filename):
    """Get the initial game state from input file"""
    with open(os.path.join(TEST_DIR, filename), "r") as f:
        weight_line = f.readline().strip()
        stone_weight = weight_line.split(' ')
        stone_weight = tuple(int(x) for x in stone_weight)
        
        layout = f.readlines()

    game_state = transfer_to_game_state(layout)
    return game_state, stone_weight

def execute_algorithm(game_state, stone_weight, algorithm):
    """Get time and memory used by algorithm"""
    _, step_cnt, node_cnt, weight_total, duration, steps = algorithm(game_state, stone_weight)

    tracemalloc.start()
    algorithm(game_state, stone_weight)
    min_memory, max_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    memory_usage = (max_memory - min_memory) / (1024 ** 2)

    return step_cnt, node_cnt, weight_total, duration, memory_usage, steps

def write_search_output(game_state, stone_weight, algorithm, mode, filename):
    step_cnt, node_cnt, weight_total, duration, memory_usage, steps = execute_algorithm(game_state, stone_weight, algorithm)
    with open(os.path.join(OUTPUT_DIR, filename), "a") as f:
        f.write(mode + '\n')
        f.write('Steps: %d, Weight: %d, Node: %d, Time (ms): %.2f, Memory (MB): %.2f\n' %(step_cnt, weight_total, node_cnt, duration, memory_usage))
        for step in steps:
            f.write(step)
        f.write('\n')

def execute_search(dir, filename):
    script_path = os.path.join(dir, "script.py")
    subprocess.run(["python", script_path, filename])
    output_filename = "out" + filename[2:]
    return load_search(output_filename)

def load_search(filename):
    steps = dict()
    with open(os.path.join(OUTPUT_DIR, filename), "r") as f:
        for _ in range(4):
            algorithm = f.readline()[:-1]
            f.readline()
            step = f.readline()[:-1]
            steps[algorithm] = list(step)

    return steps