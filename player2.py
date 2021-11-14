from random import Random
from board import Direction, Rotation, Action
from board import Shape

import time


run = 0

class Player:
    def choose_action(self, board):
        raise NotImplementedError



class RandomPlayer(Player):
    def __init__(self, seed=None):
        self.random = Random(1)

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


#Maybe allow one bump of 4 blocks 
def hisBumpiness(sandbox):
    bumpy = 0
    diff = 0
    for x in range(sandbox.width-2):
        diff = abs(columnHeight(sandbox, x)-columnHeight(sandbox, x+1))
        bumpy += diff
    if diff > 3:
        bumpy *= 2
    return bumpy


def Tetris(sandbox, complines):
    if complines >= 4:
        return 1 
    return 0



def realCompletedLines(sandbox):
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

##Between 3 a
def completedLines(sandbox, complines):
    if complines < 4:
        return complines
    return 0 

#Rightmost line should be free 
def freeRightMostLine(sandbox):
    ch = columnHeight(sandbox, 9)
    if ch != 0:
        return 1
    else: 
        return 0
def bigContinuousBlock(sandbox, holes, height):
    hol = holes
    if hol == 0 and height< 110:
        return 1
    return 0

def maxLineHeight(sandbox):
    maxHeight = 0
    for x in range(sandbox.width):
        hx = columnHeight(sandbox, x)
        if hx > maxHeight:
            maxHeight = hx
    return maxHeight

def bigGaps(sandbox):
    gaps = 0
    for column in range(1, sandbox.width):
        chLeft = columnHeight(sandbox, column-1)
        chCurrentColumn = columnHeight(sandbox, column)
        deltaH = chCurrentColumn - chLeft
        if deltaH > 0:
            gaps += deltaH
    return gaps


def evalBoard(sandbox):
    #Function results 
    holes = hisHolyness(sandbox)
    height = hisHighNess(sandbox)
    completedline = realCompletedLines(sandbox)
    onetothreelines = completedLines(sandbox, completedline)
    bumps = hisBumpiness(sandbox)
    tetris = Tetris(sandbox, completedline)
    righMostLine = freeRightMostLine(sandbox)
    bigBlock = bigContinuousBlock(sandbox, holes, height)
    maximumColumnHeight = maxLineHeight(sandbox)
    gaps = bigGaps(sandbox)


    #Tetris Coefficients 
    holeCoeff = -4.9
    heightCoeff = -0.01
    onetothreeCoeff = -0.4
    #Changed from -0.05
    bumpsCoeff = -0.05
    tetrisCoeff = 1
    rightMostCoeff = -0.4
    gapsCoeff = -0.2
    maxColCoeff = 0
    
    #Old coefficients Coefficients 

    if maximumColumnHeight > 8 or holes >0:
        maxColCoeff = -1
        onetothreeCoeff = 0
        bumpsCoeff = -0.15
        gapsCoeff = -0.2
        #return -0.35663*hisHolyness(sandbox) - 0.510066* hisHighNess(sandbox) +tetris*100+0.760666 * realCompletedLines(sandbox) -0.184483*hisBumpiness(sandbox)


    score = +holeCoeff*holes +heightCoeff* height +onetothreeCoeff* onetothreelines +bumpsCoeff*bumps +tetrisCoeff*tetris +rightMostCoeff* righMostLine + maxColCoeff*maximumColumnHeight + gapsCoeff*gaps #+ 0.99* bigBlock

    #score = -0.35663*hisHolyness(sandbox) - 0.510066* hisHighNess(sandbox) +0.760666 * ((completedLines(sandbox))*(4**(completedLines(sandbox)-1))) -0.184483*hisBumpiness(sandbox) 
    #print(score)
    
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


def findHorizontalMoves(sandbox, previousMoves):
    bestAction = []
    bestScore = -1000000

    if sandbox.falling is not None:
        leftmoves = distanceFrom0X(sandbox)
        rightmoves = 10-findPieceWidth(sandbox) - leftmoves
        
        

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
    
    if sandbox_original.falling is not None:
        rots = 4
        if sandbox_original.falling.shape == Shape.O:
            rots = 1
        if sandbox_original.falling.shape == Shape.I:
            rots = 2
        for rotation in range(0,rots):
            sandbox = sandbox_original.clone()
            if sandbox.falling is not None:
                actions = []
                if rotation == 1:
                    try:
                        sandbox.rotate(Rotation.Clockwise)
                    except:
                        pass
                    actions.append(Rotation.Clockwise)
                if rotation == 2:
                    try:
                        sandbox.rotate(Rotation.Clockwise)
                        sandbox.rotate(Rotation.Clockwise)
                    except:
                        pass
                    actions.append(Rotation.Clockwise)
                    actions.append(Rotation.Clockwise)
                if rotation == 3:
                    try:
                        sandbox.rotate(Rotation.Anticlockwise)
                    except:
                        pass
                    actions.append(Rotation.Anticlockwise)
            
            score, totalActions = findHorizontalMoves(sandbox, actions)
            if score > bestScore:
                bestAction = totalActions.copy()
                bestScore = score
    return bestAction, bestScore


class MichaelsPlayer(Player):
    def __init__(self, seed=None):
        #Could initialise parameters from here?
        self.random = Random(seed)
        self.test = True 
        self.testtwo = False
        
    def choose_action(self, board):
        
        bestMove = chooseBestMove(board)[0]

        return bestMove
        

    
        
SelectedPlayer = MichaelsPlayer

