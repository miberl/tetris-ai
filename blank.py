from adversary import RandomAdversary
from board import Board, Direction, Rotation, Action, Shape
from constants import BOARD_WIDTH, BOARD_HEIGHT, DEFAULT_SEED, INTERVAL, \
    BLOCK_LIMIT
from exceptions import BlockLimitException
from player import Player, SelectedPlayer
import time

def run():
    start = time.time()
    board = Board(BOARD_WIDTH, BOARD_HEIGHT)

    adversary = RandomAdversary(DEFAULT_SEED, BLOCK_LIMIT)

    player = SelectedPlayer()

    try:
        for move in board.run(player, adversary):
            i = board.score
    except BlockLimitException:
        print("Out of blocks")
        pass     
    except:
        pass
    finally:
        end = time.time()
        print("Score=", board.score)
        print("Time=", end - start)
if __name__ == '__main__':

    run()

        
