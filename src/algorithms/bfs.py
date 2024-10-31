from collections import deque

from src.algorithms.utils import *

def breadth_first_search(game_state, stone_weight):
    begin_player = get_pos_of_player(game_state)
    begin_stones = get_pos_of_stones(game_state, stone_weight)
    pos_of_walls = get_pos_of_walls(game_state)
    pos_of_switches = get_pos_of_switches(game_state)
    
    step_cnt = 0    
    total_weight = 0
    node_cnt = 0
    steps = []

    begin_state = (begin_player, begin_stones)
    states = deque([[begin_state]])
    actions = deque([[]])
    weights = deque([0])
    explored_set = set()
    
    while states:
        node = states.popleft()
        node_action = actions.popleft()
        node_weight = weights.popleft()

        if is_end_state(node[-1][1], pos_of_switches):
            node_cnt += 1
            steps = node_action
            step_cnt = len(node_action)
            total_weight = node_weight
            break

        if node[-1] not in explored_set:
            node_cnt += 1
            explored_set.add(node[-1])
            for action in legal_actions(node[-1][0], node[-1][1], pos_of_walls):
                new_pos_of_player, new_pos_of_stones, weight_push = update_state(action, node[-1][0], node[-1][1])
                if is_failed(new_pos_of_stones, pos_of_switches, pos_of_walls):
                    continue
                states.append(node + [(new_pos_of_player, new_pos_of_stones)])
                actions.append(node_action + [action[-1]])
                weights.append(node_weight + weight_push)
                
    return step_cnt, node_cnt, total_weight, steps
