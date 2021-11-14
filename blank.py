from adversary import RandomAdversary
from board import Board, Direction, Rotation, Action, Shape
from constants import BOARD_WIDTH, BOARD_HEIGHT, DEFAULT_SEED, INTERVAL, \
    BLOCK_LIMIT
from exceptions import BlockLimitException
from player import Player, SelectedPlayer
import time, multiprocessing



def run(i):
    start = time.time()
    board = Board(BOARD_WIDTH, BOARD_HEIGHT)

    adversary = RandomAdversary(42, 400)

    player = SelectedPlayer()

    try:
        for move in board.run(player, adversary):
            p = board.score
    except BlockLimitException:
        pass     
    except:
        pass
    finally:
        end = time.time()
        print("Time="+str(end-start)+" Score=", str(board.score))
        #print("i="+str(i)+" Score=", str(board.score))
        return board.score


if __name__ == '__main__':
    run(41)
    '''
    p = multiprocessing.Pool(5)
    score = p.map(run, list(range(30)))
    print(score)
    print("Avg="+str(sum(score)/len(score)))
    '''
        
