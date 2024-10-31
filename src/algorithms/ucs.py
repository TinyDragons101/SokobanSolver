from src.algorithms.utils import *

def uniform_cost_search(game_state, stone_weight):
    begin_player = get_pos_of_player(game_state)
    begin_stones = get_pos_of_stones(game_state, stone_weight)
    pos_of_walls = get_pos_of_walls(game_state)
    pos_of_switches = get_pos_of_switches(game_state)
    
    step_cnt = 0    
    total_weight = 0
    node_cnt = 0
    steps = []

    begin_state = (begin_player, begin_stones)
    
    # Initialize priority queues for states, actions, and weights
    states = PriorityQueue()
    states.push([begin_state], 0)  # Priority is the total cost (0 for start)
    actions = PriorityQueue()
    actions.push([], 0)
    weights = PriorityQueue()
    weights.push(0, 0)
    
    explored_set = set()
    
    while states:
        node = states.pop()
        node_action = actions.pop()
        node_weight = weights.pop()
        
        if is_end_state(node[-1][1], pos_of_switches):
            steps = node_action
            step_cnt = len(node_action)
            total_weight = node_weight
            break
        
        if node[-1] not in explored_set:
            explored_set.add(node[-1])
            
            # Explore all possible actions from current state
            for action in legal_actions(node[-1][0], node[-1][1], pos_of_walls):
                new_pos_of_player, new_pos_of_stones, weight_push = update_state(action, node[-1][0], node[-1][1])
                
                # Skip if the new state leads to a failed position
                if is_failed(new_pos_of_stones, pos_of_switches, pos_of_walls):
                    continue
                    
                node_cnt += 1
                
                # Calculate new total cost (weight + steps)
                new_total_cost = node_weight + weight_push + 1  # +1 for the step cost
                
                # Add new states to priority queues with their total cost as priority
                states.push(node + [(new_pos_of_player, new_pos_of_stones)], new_total_cost)
                actions.push(node_action + [action[-1]], new_total_cost)
                weights.push(node_weight + weight_push, new_total_cost)
    
    return step_cnt, node_cnt, total_weight, steps