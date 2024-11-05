import numpy as np
import heapq

class PriorityQueue:
    """A class for priority queue"""
    def  __init__(self):
        self.heap = []
        self.cnt = 0

    def push(self, item, priority):
        entry = (priority, self.cnt, item)
        heapq.heappush(self.heap, entry)
        self.cnt += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        return item

    def is_empty(self):
        return len(self.heap) == 0

def get_pos_of_player(game_state):
    """Return the position of agent"""
    return tuple(np.argwhere(game_state == 2)[0])

def get_pos_of_stones(game_state, stone_weight):
    """Return the positions of stones"""
    stones = tuple(tuple(x) for x in np.argwhere((game_state == 3) | (game_state == 5)))
    return tuple(a + (b,) for a, b in zip(stones, stone_weight))

def get_pos_of_walls(game_state):
    """Return the positions of walls"""
    return tuple(tuple(x) for x in np.argwhere(game_state == 1)) 

def get_pos_of_switches(game_state):
    """Return the positions of switches"""
    return tuple(tuple(x) for x in np.argwhere((game_state == 4) | (game_state == 5) | (game_state == 6)))

def is_end_state(pos_of_stones, pos_of_switches):
    """Check if all stones are on the switches"""
    return sorted(tuple(stone[0:2] for stone in pos_of_stones)) == sorted(pos_of_switches)

def is_legal_action(action, pos_of_player, pos_of_stones, pos_of_walls):
    """Check if the given action is legal"""
    x_player, y_player = pos_of_player
    if action[-1].isupper():
        x1, y1 = x_player + 2 * action[0], y_player + 2 * action[1]
    else:
        x1, y1 = x_player + action[0], y_player + action[1]
    return (x1, y1) not in tuple(stone[0:2] for stone in pos_of_stones) + pos_of_walls

def legal_actions(pos_of_player, pos_of_stones, pos_of_walls):
    """Return all legal actions for the agent in the current game state"""
    all_actions = [[-1, 0, 'u', 'U'], [0, 1, 'r', 'R'], [1, 0, 'd', 'D'], [0, -1, 'l', 'L']]
    x_player, y_player = pos_of_player
    legal_actions = []
    for action in all_actions:
        x1, y1 = x_player + action[0], y_player + action[1]
        if (x1, y1) in tuple(stone[0:2] for stone in pos_of_stones):
            action.pop(2)
        else:
            action.pop(3)
        if is_legal_action(action, pos_of_player, pos_of_stones, pos_of_walls):
            legal_actions.append(action)
    return tuple(tuple(x) for x in legal_actions)

def update_state(action, pos_of_player, pos_of_stones):
    """Return updated game state after an action is taken"""
    x_player, y_player = pos_of_player
    new_pos_of_player = [x_player + action[0], y_player + action[1]]
    weight_push = 0
    
    pos_of_stones = [list(x) for x in pos_of_stones]
    
    if action[-1].isupper():
        pos_of_stone_index = [i for i in range(len(pos_of_stones)) if pos_of_stones[i][0:2] == new_pos_of_player]
        pos_of_stone_index = pos_of_stone_index[0]
        pos_of_stones[pos_of_stone_index][0] = x_player + 2 * action[0]
        pos_of_stones[pos_of_stone_index][1] = y_player + 2 * action[1]
        weight_push = pos_of_stones[pos_of_stone_index][2]

    new_pos_of_player = tuple(new_pos_of_player) 
    new_pos_of_stones = tuple(tuple(x) for x in pos_of_stones)
    
    return new_pos_of_player, new_pos_of_stones, weight_push

def is_failed(stone, pos_of_stones, pos_of_switches, pos_of_walls):
    """Observe if the current game state is potentially failed, then prune the search"""
    pos_of_stones = tuple(stone[0:2] for stone in pos_of_stones)

    all_patterns = \
    [
        [0,1,2,3,4,5,6,7,8],
        [2,5,8,1,4,7,0,3,6],
        [0,1,2,3,4,5,6,7,8][::-1],
        [2,5,8,1,4,7,0,3,6][::-1],
        [2,1,0,5,4,3,8,7,6],
        [0,3,6,1,4,7,2,5,8],
        [2,1,0,5,4,3,8,7,6][::-1],
        [0,3,6,1,4,7,2,5,8][::-1]
    ]

    if stone not in pos_of_switches:
        board = \
        [
            (stone[0] - 1, stone[1] - 1), (stone[0] - 1, stone[1]), (stone[0] - 1, stone[1] + 1), 
            (stone[0], stone[1] - 1), (stone[0], stone[1]), (stone[0], stone[1] + 1), 
            (stone[0] + 1, stone[1] - 1), (stone[0] + 1, stone[1]), (stone[0] + 1, stone[1] + 1)
        ]
        for pattern in all_patterns:
            new_board = [board[i] for i in pattern]
            if new_board[1] in pos_of_walls and new_board[5] in pos_of_walls: 
                return True
            elif new_board[1] in pos_of_stones and new_board[2] in pos_of_walls and new_board[5] in pos_of_walls: 
                return True
            elif new_board[1] in pos_of_stones and new_board[2] in pos_of_walls and new_board[5] in pos_of_stones: 
                return True
            elif new_board[1] in pos_of_stones and new_board[2] in pos_of_stones and new_board[5] in pos_of_stones: 
                return True
            elif new_board[1] in pos_of_stones and new_board[2] in pos_of_walls and new_board[3] in pos_of_walls and new_board[8] in pos_of_walls: 
                return True
    
    return False

def cost(actions):
    """A cost function"""
    return len([x for x in actions if x.islower()])

def heuristic(pos_of_stones, pos_of_switches):
    """A heuristic function to calculate the overall distance between the remaining stones and the remaining switches"""
    pos_of_stones = set(tuple(pos[0:2] for pos in pos_of_stones))
    pos_of_switches = set(pos_of_switches)
    
    pos_of_stones_on_switches = pos_of_stones & pos_of_switches
    
    list_pos_of_stones = list(pos_of_stones - pos_of_stones_on_switches)
    list_pos_of_switches = list(pos_of_switches - pos_of_stones_on_switches)

    total_distance = 0
    
    for i in range(len(list_pos_of_stones)):
        total_distance += abs(list_pos_of_stones[i][0] - list_pos_of_switches[i][0]) + abs(list_pos_of_stones[i][1] - list_pos_of_switches[i][1])
        
    return total_distance