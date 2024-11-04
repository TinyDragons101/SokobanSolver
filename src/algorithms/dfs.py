from collections import deque
import time

from src.algorithms.utils import *

def depth_first_search(game_state, stone_weight):
    begin_time = time.time()
    begin_player = get_pos_of_player(game_state)
    begin_stones = get_pos_of_stones(game_state, stone_weight)
    pos_of_walls = get_pos_of_walls(game_state)
    pos_of_switches = get_pos_of_switches(game_state)

    step_cnt = 0
    node_cnt = 0  
    total_weight = 0
    steps = []

    begin_state = (begin_player, begin_stones)
    if is_end_state(begin_stones, pos_of_switches):
        end_time = time.time()
        duration = (end_time - begin_time) * 1000

        return True, step_cnt, node_cnt, total_weight, duration, steps       

    states = deque([begin_state])
    weights = deque([0])
    actions = deque([[]])
    explored_set = set([])

    while states:
        node = states.pop()
        node_weight = weights.pop()
        node_action = actions.pop()

        if node not in explored_set:
            explored_set.add(node) 

            for action in legal_actions(node[0], node[1], pos_of_walls):
                new_pos_of_player, new_pos_of_stones, weight_push = update_state(action, node[0], node[1])
                new_state = (new_pos_of_player, new_pos_of_stones)
                
                if new_state not in explored_set:
                
                    if action[-1].isupper():
                        stone = (new_pos_of_player[0] + action[0], new_pos_of_player[1] + action[1])
                        if is_failed(stone, new_pos_of_stones, pos_of_switches, pos_of_walls):
                            continue
                    
                    node_cnt += 1
                    
                    if is_end_state(new_state[1], pos_of_switches):
                        step_cnt = len(node_action) + 1
                        total_weight = node_weight + weight_push
                        steps = node_action + [action[-1]]
                        
                        end_time = time.time()
                        duration = (end_time - begin_time) * 1000

                        return True, step_cnt, node_cnt, total_weight, duration, steps
                    
                    states.append(new_state)
                    weights.append(node_weight + weight_push)
                    actions.append(node_action + [action[-1]])

    end_time = time.time()
    duration = (end_time - begin_time) * 1000

    return False, step_cnt, node_cnt, total_weight, duration, steps