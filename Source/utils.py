from optparse import OptionParser
import numpy as np
import heapq

WALL = "#"
SPACE = " "
STONE = "$"
ARES = "@"
SWITCH = "."
STONE_ON_SWITCH = "*"
ARES_ON_SWITCH = "+"

"""Read command"""
def readCommand(argv):

    parser = OptionParser()
    parser.add_option('-l', '--level', dest='sokobanLevels', default='input-01.txt')
    parser.add_option('-m', '--method', dest='agentMethod', default='bfs')
    
    options, _ = parser.parse_args(argv)
    args = dict()

    with open('./' + options.sokobanLevels,"r") as f:
        weightLine = f.readline()[0:-1]
        stoneWeight = weightLine.split(' ')
        stoneWeight = (int(x) for x in stoneWeight)
        
        layout = f.readlines()

    args['layout'] = layout
    args['stoneWeight'] = stoneWeight
    args['method'] = options.agentMethod
    return args

def transferToGameState(layout):
    """Transfer the layout of initial puzzle"""
    layout = [x.replace('\n','') for x in layout]
    layout = [','.join(x) for x in layout]
    layout = [x.split(',') for x in layout]
    maxColsNum = max([len(x) for x in layout])
    for irow in range(len(layout)):
        for icol in range(len(layout[irow])):
            if layout[irow][icol] == SPACE: layout[irow][icol] = 0   # free space
            elif layout[irow][icol] == WALL: layout[irow][icol] = 1 # wall
            elif layout[irow][icol] == ARES: layout[irow][icol] = 2 # player
            elif layout[irow][icol] == STONE: layout[irow][icol] = 3 # stone
            elif layout[irow][icol] == SWITCH: layout[irow][icol] = 4 # switch
            elif layout[irow][icol] == STONE_ON_SWITCH: layout[irow][icol] = 5 # stone on switch
        colsNum = len(layout[irow])
        if colsNum < maxColsNum:
            layout[irow].extend([1 for _ in range(maxColsNum-colsNum)]) 
            
    return np.array(layout)

# gameState
# [[0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1]
#  [1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
#  [1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1]
#  [1 0 3 0 3 0 0 0 0 0 0 0 0 0 0 0 1]
#  [1 4 0 2 0 0 0 0 0 0 0 0 0 0 0 4 1]
#  [1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1]]

def PosOfPlayer(gameState):
    """Return the position of agent"""
    return tuple(np.argwhere(gameState == 2)[0]) # e.g. (2, 2)

def PosOfStones(gameState, stoneWeight):
    """Return the positions of boxes"""
    stones = tuple(tuple(x) for x in np.argwhere((gameState == 3) | (gameState == 5))) # e.g. ((3, 2), (3, 4))
    return tuple(a + (b,) for a, b in zip(stones, stoneWeight)) # e.g. ((3, 2, 1), (3, 4, 99))

def PosOfWalls(gameState):
    """Return the positions of walls"""
    return tuple(tuple(x) for x in np.argwhere(gameState == 1)) 

def PosOfGoals(gameState):
    """Return the positions of goals"""
    return tuple(tuple(x) for x in np.argwhere((gameState == 4) | (gameState == 5))) 

def isEndState(posStone, posGoals):
    """Check if all boxes are on the goals (i.e. pass the game)"""
    return sorted(tuple(stone[0:2] for stone in posStone)) == sorted(posGoals)

def isLegalAction(action, posPlayer, posStone, posWalls):
    """Check if the given action is legal"""
    xPlayer, yPlayer = posPlayer
    if action[-1].isupper(): # the move was a push
        x1, y1 = xPlayer + 2 * action[0], yPlayer + 2 * action[1]
    else:
        x1, y1 = xPlayer + action[0], yPlayer + action[1]
    return (x1, y1) not in (tuple(stone[0:2] for stone in posStone)) + posWalls

def legalActions(posPlayer, posStone, posWalls):
    """Return all legal actions for the agent in the current game state"""
    allActions = [[-1,0,'u','U'],[0,1,'r','R'], [1,0,'d','D'],[0,-1,'l','L']]
    xPlayer, yPlayer = posPlayer
    legalActions = []
    for action in allActions:
        x1, y1 = xPlayer + action[0], yPlayer + action[1]
        if (x1, y1) in (tuple(stone[0:2] for stone in posStone)): # the move was a push
            action.pop(2) # drop the little letter
        else:
            action.pop(3) # drop the upper letter
        if isLegalAction(action, posPlayer, posStone, posWalls):
            legalActions.append(action)
        else: 
            continue     
    return tuple(tuple(x) for x in legalActions) # e.g. ((0, -1, 'l'), (0, 1, 'R'))

def updateState(posPlayer, posStone, action):
    """Return updated game state after an action is taken"""
    
    xPlayer, yPlayer = posPlayer # the previous position of player
    newPosPlayer = [xPlayer + action[0], yPlayer + action[1]] # the current position of player
    weightPush = 0
    
    posStone = [list(x) for x in posStone]
    
    if action[-1].isupper(): # if pushing, update the position of stone
        curPosStone = [pos for pos in posStone if pos[0:2] == newPosPlayer]
        posStone.remove(curPosStone[0])
        weightPush = curPosStone[0][2]
        posStone.append([xPlayer + 2 * action[0], yPlayer + 2 * action[1], weightPush])
        
    newPosStone = tuple(tuple(x) for x in posStone)
    newPosPlayer = tuple(newPosPlayer)
    
    return newPosPlayer, newPosStone, weightPush

def isFailed(posStone, posGoals, posWalls):
    """This function used to observe if the state is potentially failed, then prune the search"""
    posStone = (tuple(stone[0:2] for stone in posStone))

    rotatePattern = [[0,1,2,3,4,5,6,7,8],
                    [2,5,8,1,4,7,0,3,6],
                    [0,1,2,3,4,5,6,7,8][::-1],
                    [2,5,8,1,4,7,0,3,6][::-1]]
    flipPattern = [[2,1,0,5,4,3,8,7,6],
                    [0,3,6,1,4,7,2,5,8],
                    [2,1,0,5,4,3,8,7,6][::-1],
                    [0,3,6,1,4,7,2,5,8][::-1]]
    allPattern = rotatePattern + flipPattern

    for stone in posStone:
        if stone not in posGoals:
            board = [(stone[0] - 1, stone[1] - 1), (stone[0] - 1, stone[1]), (stone[0] - 1, stone[1] + 1), 
                    (stone[0], stone[1] - 1), (stone[0], stone[1]), (stone[0], stone[1] + 1), 
                    (stone[0] + 1, stone[1] - 1), (stone[0] + 1, stone[1]), (stone[0] + 1, stone[1] + 1)]
            for pattern in allPattern:
                newBoard = [board[i] for i in pattern]
                if newBoard[1] in posWalls and newBoard[5] in posWalls: return True
                elif newBoard[1] in posStone and newBoard[2] in posWalls and newBoard[5] in posWalls: return True
                elif newBoard[1] in posStone and newBoard[2] in posWalls and newBoard[5] in posStone: return True
                elif newBoard[1] in posStone and newBoard[2] in posStone and newBoard[5] in posStone: return True
                elif newBoard[1] in posStone and newBoard[6] in posStone and newBoard[2] in posWalls and newBoard[3] in posWalls and newBoard[8] in posWalls: return True
    return False

def cost(actions):
    """A cost function"""
    return len([x for x in actions if x.islower()])

def heuristic(posPlayer, posStone, posGoals):
    """A heuristic function to calculate the overall distance between the else boxes and the else goals"""
    posStone = (tuple(stone[0:2] for stone in posStone))

    distance = 0
    completes = set(posGoals) & set(posStone)
    sortposStone = list(set(posStone).difference(completes))
    sortposGoals = list(set(posGoals).difference(completes))
    for i in range(len(sortposStone)):
        distance += (abs(sortposStone[i][0] - sortposGoals[i][0])) + (abs(sortposStone[i][1] - sortposGoals[i][1]))
    return distance

class PriorityQueue:
    """Define a PriorityQueue data structure that will be used"""
    def  __init__(self):
        self.Heap = []
        self.Count = 0

    def push(self, item, priority):
        entry = (priority, self.Count, item)
        heapq.heappush(self.Heap, entry)
        self.Count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.Heap)
        return item

    def isEmpty(self):
        return len(self.Heap) == 0