import collections

from utils import *

def breadthFirstSearch(gameState):
    """Implement breadthFirstSearch approach"""
    beginBox = PosOfBoxes(gameState)
    beginPlayer = PosOfPlayer(gameState)
    posWalls = PosOfWalls(gameState)
    posGoals = PosOfGoals(gameState)

    startState = (beginPlayer, beginBox) # e.g. ((2, 2), ((2, 3), (3, 4), (4, 4), (6, 1), (6, 4), (6, 5)))
    frontier = collections.deque([[startState]]) # store states
    actions = collections.deque([[0]]) # store actions
    exploredSet = set()
    while frontier:
        node = frontier.popleft()
        node_action = actions.popleft() 
        if isEndState(posBox=node[-1][-1], posGoals=posGoals):
            print(','.join(node_action[1:]).replace(',',''))
            break
        if node[-1] not in exploredSet:
            exploredSet.add(node[-1])
            for action in legalActions(posPlayer=node[-1][0], posBox=node[-1][1], posWalls=posWalls):
                newPosPlayer, newPosBox = updateState(node[-1][0], node[-1][1], action)
                if isFailed(posBox=newPosBox, posGoals=posGoals, posWalls=posWalls):
                    continue
                frontier.append(node + [(newPosPlayer, newPosBox)])
                actions.append(node_action + [action[-1]])