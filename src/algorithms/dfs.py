import collections

from src.algorithms.utils import *

def depthFirstSearch(gameState, stoneWeight):
    """Implement depthFirstSearch approach"""
    beginStone = PosOfStones(gameState, stoneWeight)
    beginPlayer = PosOfPlayer(gameState)
    posWalls = PosOfWalls(gameState)
    posGoals = PosOfGoals(gameState)
    
    step_cnt = 0    
    node_cnt = 0
    weight_total = 0
    
    startState = (beginPlayer, beginStone)
    frontier = [[startState]]
    weights = [0]
    actions = [[0]]
    exploredSet = set()
     
    while frontier:
        node = frontier.pop()
        node_action = actions.pop()
        node_weight = weights.pop()
        
        if isEndState(posStone=node[-1][1], posGoals=posGoals):
            print(','.join(node_action[1:]).replace(',',''))
            node_cnt = len(node)
            step_cnt = len(node_action)
            weight_total = node_weight
            break
        if node[-1] not in exploredSet:
            exploredSet.add(node[-1])
            for action in legalActions(posPlayer=node[-1][0], posStone=node[-1][1], posWalls=posWalls):
                newPosPlayer, newPosStone, weightPush = updateState(node[-1][0], node[-1][1], action)
                if isFailed(posStone=newPosStone, posGoals=posGoals, posWalls=posWalls):
                    continue
                frontier.append(node + [(newPosPlayer, newPosStone)])
                actions.append(node_action + [action[-1]])
                weights.append(node_weight + weightPush)

    return step_cnt - 1, node_cnt, weight_total
