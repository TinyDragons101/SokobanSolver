import numpy as np

from src.algorithms.utils import *

def a_star_search(game_state, stone_weight):
    begin_player = get_pos_of_player(game_state)
    begin_stones = get_pos_of_stones(game_state, stone_weight)
    pos_of_walls = get_pos_of_walls(game_state)
    pos_of_switches = get_pos_of_switches(game_state)
    
    step_cnt = 0    
    total_weight = 0
    node_cnt = 0
    steps = []

    begin_state = (begin_player, begin_stones)
    states = PriorityQueue()
    states.push([begin_state], heuristic(begin_stones, pos_of_switches))
    actions = PriorityQueue()
    actions.push([0], heuristic(begin_stones, pos_of_switches))
    weights = PriorityQueue()
    weights.push(0, heuristic(begin_stones, pos_of_switches))
    exploredSet = set()

    while states:
        node = states.pop()
        node_action = actions.pop()
        node_weight = weights.pop()
        
        if is_end_state(node[-1][-1], pos_of_switches):
            steps = node_action
            step_cnt = len(node_action)
            total_weight = node_weight
            break
        
        if node[-1] not in exploredSet:
            exploredSet.add(node[-1])
            Cost = cost(node_action[1:])
            for action in legal_actions(node[-1][0], node[-1][1], pos_of_walls):
                new_pos_of_player, new_pos_of_stones, weight_push = update_state(action, node[-1][0], node[-1][1])
                if is_failed(new_pos_of_stones, pos_of_switches, pos_of_walls):
                    continue
                node_cnt += 1
                Heuristic = heuristic(new_pos_of_stones, pos_of_switches)
                states.push(node + [(new_pos_of_player, new_pos_of_stones)], Heuristic + Cost) 
                actions.push(node_action + [action[-1]], Heuristic + Cost)
                weights.push(node_weight + weight_push, Heuristic + Cost)
    
    return step_cnt, node_cnt, total_weight, steps

