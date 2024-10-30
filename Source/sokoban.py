import sys
import time
from utils import *
from bfs import breadthFirstSearch
from dfs import depthFirstSearch
from ucs import uniformCostSearch
from astar import aStarSearch


if __name__ == '__main__':
    time_start = time.time()
    layout, stoneWeight, method = readCommand(sys.argv[1:]).values()
    gameState = transferToGameState(layout)
    
    if method == 'astar':
        aStarSearch(gameState)
    elif method == 'dfs':
        step_cnt, node_cnt, weight_total = depthFirstSearch(gameState, stoneWeight)
    elif method == 'bfs':
        step_cnt, node_cnt, weight_total = breadthFirstSearch(gameState, stoneWeight)
    elif method == 'ucs':
        uniformCostSearch(gameState)
    else:
        raise ValueError('Invalid method.')
    time_end=time.time()
    print('%d steps - %d nodes - %d weights' %(step_cnt, node_cnt, weight_total))
    print('Runtime of %s: %.2f second.' %(method, time_end-time_start))