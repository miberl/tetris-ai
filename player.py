from random import Random
from board import Direction, Rotation, Action
from board import Shape



shape_to_cells = {
    Shape.I: {
        (0, 0),
        (0, 1),
        (0, 2),
        (0, 3),
    },
    Shape.J: {
                (1, 0),
                (1, 1),
        (0, 2), (1, 2), # noqa
    },
    Shape.L: {
        (0, 0),
        (0, 1),
        (0, 2), (1, 2),
    },
    Shape.O: {
        (0, 0), (1, 0),
        (0, 1), (1, 1),
    },
    Shape.S: {
                (1, 0), (2, 0),
        (0, 1), (1, 1),
    },
    Shape.T: {
        (0, 0), (1, 0), (2, 0),
                (1, 1),
    },
    Shape.Z: {
        (0, 0), (1, 0),
                (1, 1), (2, 1),
    },
    Shape.B: { (0,0)}
}


class Player:
    def choose_action(self, board):
        raise NotImplementedError



class RandomPlayer(Player):
    def __init__(self, seed=None):
        self.random = Random(seed)

    def choose_action(self, board):
        if self.random.random() > 0.97:
            # 3% chance we'll discard or drop a bomb
            return self.random.choice([
                Action.Discard,
                Action.Bomb,
            ])
        else:
            # 97% chance we'll make a normal move
            return self.random.choice([
                Direction.Left,
                Direction.Right,
                Direction.Down,
                Rotation.Anticlockwise,
                Rotation.Clockwise,
            ])
#Board.falling -> contains information about the currently falling block
#its shape (board.falling.shape) and the coordinates of its cells (board.falling.cells). 
# The shape is an instance of the enum shape, whose definition can be found in board.py.


#Heuristics
#Bumpiness
#Holes
#Completed lines 
#Aggregate height

#this should return the final board position, with the list of moves it took to accomplish it 





#Returns a score for a board
def hisHolyness(sandbox):
    holes = 0
    for y in range (sandbox.height):
        for x in range (sandbox.width):
            if (x,y) not in sandbox.cells:
                for upperYs in range(0,y):
                    if (x, upperYs) in sandbox.cells:
                        holes+=1
                        break
    return holes

def hisHighNess(sandbox):
    highness = 0
    for x in range (sandbox.width):
        highness+=columnHeight(sandbox, x)
    return highness

def columnHeight(sandbox, x):
    height = 0
    for y in range (0, sandbox.height):
        if (x,y) in sandbox.cells:
            height += (sandbox.height-y)
            break
    return height


#Maybe only over 3?
def hisBumpiness(sandbox):
    bumpy = 0
    for x in range(sandbox.width-1):
        bumpy += abs(columnHeight(sandbox, x)-columnHeight(sandbox, x+1))
    return bumpy


def completedLines(sandbox):
    linesCompleted = 0
    for y in range (sandbox.height):
        allComplete = True
        for x in range (sandbox.width):
            if (x,y) not in sandbox.cells:
                allComplete = False
                break
        if allComplete:
            linesCompleted +=1
    return linesCompleted
#Heuristics taken from https://codemyroad.wordpress.com/2013/04/14/tetris-ai-the-near-perfect-player/

def evalBoard(sandbox):
    score = -0.35663*hisHolyness(sandbox) - 0.510066* hisHighNess(sandbox) +0.760666 * completedLines(sandbox) -0.184483*hisBumpiness(sandbox)
    return score




def moveHorizontally(sandbox, previousMoves, direction, shifts):

    moves = previousMoves.copy()
    newSandbox = sandbox.clone()
    ret = None
    for shift in range(0, shifts+1):
        ret = newSandbox.move(direction)
        moves.append(direction)
        if ret:
            break
    
    if not ret:
        newSandbox.move(Direction.Drop)
        moves.append(Direction.Drop)
    
    return newSandbox, moves

def addShapeToBoard(secondSandbox, shape):
    secondSandbox.falling = True
    secondSandbox.falling.shape = shape
    secondSandbox.falling.cells = shape_to_cells[shape]
    return secondSandbox.clone()

def findHorizontalMoves(sandbox, previousMoves):
    
    leftmoves = distanceFrom0X(sandbox)
    rightmoves = 10-findPieceWidth(sandbox) - leftmoves
    
    bestAction = []
    bestScore = -1000000

    for move in range(0, leftmoves):
        movedSandbox, moves = moveHorizontally(sandbox, previousMoves, Direction.Left, move)
        newSandboxScore = 0
        
        if sandbox.next is not None:
            newBoard = movedSandbox.clone()
            newSandboxScore += chooseBestMove(newBoard)[1]
 
        newSandboxScore += evalBoard(movedSandbox)
        if (newSandboxScore > bestScore):
            bestAction = moves.copy()
            bestScore = newSandboxScore

    for move in range(0,rightmoves):
        movedSandbox, moves = moveHorizontally(sandbox, previousMoves, Direction.Right, move)
        newSandboxScore = 0
        
        if sandbox.next is not None:
            newBoard = movedSandbox.clone()
            newSandboxScore += chooseBestMove(newBoard)[1]

        newSandboxScore += evalBoard(movedSandbox)

        if (newSandboxScore > bestScore):
            bestAction = moves.copy()
            bestScore = newSandboxScore

    ##Neither right or lef, just drop centrally
    moves = previousMoves.copy()
    movedSandbox = sandbox.clone()
    newSandboxScore = 0
    if movedSandbox.falling:
        movedSandbox.move(Direction.Drop)
        moves.append(Direction.Drop)
    
    if sandbox.next is not None:
        newBoard = movedSandbox.clone()
        newSandboxScore += chooseBestMove(newBoard)[1]
    
    newSandboxScore += evalBoard(movedSandbox)
    if (newSandboxScore > bestScore):
        bestAction = moves.copy()
        bestScore = newSandboxScore

    return bestScore, bestAction

def distanceFrom0X(sandbox):
    min =100 
    for pair in sandbox.falling.cells:
        if (pair[0]<min):
            min = pair[0]
    return min

def findPieceWidth(sandbox):
    min = 100
    max = -1
    for pair in sandbox.falling.cells:
        if (pair[0]>max):
            max = pair[0]
        if (pair[0]<min):
            min = pair[0]
    return (max-min+1)

def someDirection(list, move):
    l = list.copy()
    l.append(move)
    return l

def chooseBestMove(sandbox_original):
    bestScore = -1000000
    bestAction = []
    
    for rotation in range(0,4):
        sandbox = sandbox_original.clone()
        
        actions = []
        if rotation == 1:
            sandbox.rotate(Rotation.Clockwise)
            actions.append(Rotation.Clockwise)
        if rotation == 2:
            sandbox.rotate(Rotation.Clockwise)
            sandbox.rotate(Rotation.Clockwise)
            actions.append(Rotation.Clockwise)
            actions.append(Rotation.Clockwise)
        if rotation == 3:
            sandbox.rotate(Rotation.Anticlockwise)
            actions.append(Rotation.Anticlockwise)
        
        score, totalActions = findHorizontalMoves(sandbox, actions)
        if score > bestScore:
            bestAction = totalActions.copy()
            bestScore = score
    return bestAction, bestScore

class MichaelsPlayer(Player):

    def __init__(self, seed=None):
        self.random = Random(seed)
    
    def choose_action(self, board):
        bestMove = chooseBestMove(board)[0]
        
        return bestMove
        

        
        
SelectedPlayer = MichaelsPlayer
