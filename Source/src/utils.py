import os
from optparse import OptionParser
import numpy as np
import subprocess
import tracemalloc
import re

from src.algorithms.bfs import *
from src.algorithms.dfs import *
from src.algorithms.ucs import *
from src.algorithms.astar import *

# Config path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKING_DIR = os.path.dirname(CURRENT_DIR)

# Symbol for maze input
SPACE = " "
WALL = "#"
ARES = "@"
STONE = "$"
SWITCH = "."
STONE_ON_SWITCH = "*"
ARES_ON_SWITCH = "+"

# Command options for test.py
def read_command(argv):
    """Read command arguments"""
    parser = OptionParser()
    parser.add_option('-l', '--level', dest='sokoban_levels', default='input-01.txt')
    parser.add_option('-m', '--method', dest='agent_method', default='bfs')
    
    options, _ = parser.parse_args(argv)
    args = dict()

    with open(os.path.join(WORKING_DIR, options.sokoban_levels), "r") as f:
        weight_line = f.readline().strip()
        stone_weight = weight_line.split(' ')
        stone_weight = tuple(int(x) for x in stone_weight)
        layout = f.readlines()

    args['method'] = options.agent_method
    args['stone_weight'] = stone_weight
    args['layout'] = layout
    
    return args

def transfer_to_game_state(layout):
    """Transfer the layout to the initial game state"""
    layout = [x.replace('\n','') for x in layout]
    layout = [list(x) for x in layout]
    max_num_cols = max([len(x) for x in layout])

    # Change symbol to number
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
    
    # Cut the maze to its exact size
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
        for irow in range(len(layout))[::-1]:
            if layout[irow][icol] > 0:
                break
            elif layout[irow][icol] == 0:
                layout[irow][icol] = -1

    return np.array(layout)

def get_game_state(filename):
    """Get the initial game state from input file"""
    with open(filename, "r") as f:
        weight_line = f.readline().strip()
        stone_weight = weight_line.split(' ')
        stone_weight = tuple(int(x) for x in stone_weight)
        layout = f.readlines()

    game_state = transfer_to_game_state(layout)
    return game_state, stone_weight

# Wrap function to get memory usage
def execute_algorithm(game_state, stone_weight, algorithm):
    """Get time and memory used by algorithm"""
    _, step_cnt, node_cnt, weight_total, duration, steps = algorithm(game_state, stone_weight)

    tracemalloc.start()
    algorithm(game_state, stone_weight)
    min_memory, max_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    memory_usage = (max_memory - min_memory) / (1024 ** 2)

    return step_cnt, node_cnt, weight_total, duration, memory_usage, steps

def write_search_output(game_state, stone_weight, method, algorithm, f):
    step_cnt, node_cnt, weight_total, duration, memory_usage, steps = execute_algorithm(game_state, stone_weight, algorithm)
    f.write(method + '\n')
    f.write('Steps: %d, Weight: %d, Node: %d, Time (ms): %.2f, Memory (MB): %.2f\n' %(step_cnt, weight_total, node_cnt, duration, memory_usage))
    for step in steps:
        f.write(step)
    f.write('\n')

def load_search(filename):
    weights = dict()
    all_steps = dict()
    with open(filename, "r") as f:
        for _ in range(4):
            algorithm = f.readline()[:-1]
            statistics = f.readline()
            match = re.search(r"Weight:\s(\d+)", statistics)
            weights[algorithm] = match.group(1)
            steps = f.readline()[:-1]
            all_steps[algorithm] = list(steps)

    return all_steps, weights

def execute_search(filename):
    output_filename = "out" + filename[2:]
    output_filename = os.path.join(WORKING_DIR, output_filename)
    if not os.path.exists(output_filename):
        subprocess.run(["python", os.path.join(WORKING_DIR, "script.py"), filename])
    
    return load_search(output_filename)