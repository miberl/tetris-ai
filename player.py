from random import Random
from board import Direction, Rotation, Action
from board import Shape

import time

lastScore = 0
lastHoles = 0
discards = 0
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
# Board.falling -> contains information about the currently falling block
# its shape (board.falling.shape) and the coordinates of its cells (board.falling.cells).
# The shape is an instance of the enum shape, whose definition can be found in board.py.


# Heuristics
# Bumpiness
# Holes
# Completed lines
# Aggregate height

# this should return the final board position, with the list of moves it took to accomplish it


# Returns a score for a board
def findHoles(sandbox):
    holes = 0
    for y in range(sandbox.height):
        for x in range(sandbox.width):
            if (x, y) not in sandbox.cells:
                for upperYs in range(0, y):
                    if (x, upperYs) in sandbox.cells:
                        holes += 1
                        break
    return holes


def findHeight(sandbox):
    highness = 0
    for x in range(sandbox.width):
        highness += columnHeight(sandbox, x)
    return highness ** 2


def columnHeight(sandbox, x):
    height = 0
    for y in range(0, sandbox.height):
        if (x, y) in sandbox.cells:
            height += (sandbox.height-y)
            break
    return height


# Maybe allow one bump of 4 blocks
def findBumps(sandbox):
    bumpy = 0
    diff = 0
    for x in range(sandbox.width-2):
        diff = abs(columnHeight(sandbox, x)-columnHeight(sandbox, x+1))
        bumpy += diff
    if diff > 3:
        bumpy *= 2
    return bumpy


def Tetris(sandbox, complines):
    global lastScore

    diffScore = sandbox.score - lastScore
    # We have a tetris
    if complines >= 4:
        return 1
    else:
        return 0

    '''
    if complines >= 1:
        # if complines >= 4:
        assert(False)
        return 1
    return 0
    '''


def realCompletedLines(sandbox):

    global lastScore
    diffScore = sandbox.score - lastScore

    if diffScore >= 1600:
        return 4
    elif diffScore >= 400:
        return 3
    elif diffScore >= 100:
        return 2
    elif diffScore >= 42:
        return 1
    else:
        return 0
    '''
        for y in range(sandbox.height):
        allComplete = True
        for x in range(sandbox.width):
            if (x, y) not in sandbox.cells:
                allComplete = False
                break
        if allComplete:
            linesCompleted += 1
    return linesCompleted
    '''


# Between 3 a


def completedLines(sandbox, complines):
    if complines < 4:
        return complines
    return 0

# Rightmost line should be free


def freeRightMostLine(sandbox):
    ch = columnHeight(sandbox, 9)
    if ch != 0:
        return 1
    return 0


def bigContinuousBlock(sandbox, holes, height):
    hol = holes
    if hol == 0 and height < 110:
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
    return gaps**2


def evalBoard(sandbox):
    # Function results
    holes = findHoles(sandbox)
    height = findHeight(sandbox)
    completedline = realCompletedLines(sandbox)
    onetothreelines = completedLines(sandbox, completedline)
    bumps = findBumps(sandbox)
    tetris = Tetris(sandbox, completedline)
    righMostLine = freeRightMostLine(sandbox)
    maximumColumnHeight = maxLineHeight(sandbox)
    gaps = bigGaps(sandbox)

 # Tetris Coefficients
    holeCoeff = -10.425848148861757
    heightCoeff = -0.0009293794396322049
    onetothreeCoeff = -2.5023832192570596
    # Changed from -0.05
    bumpsCoeff = -0.04355179063623546
    tetrisCoeff = 102.45373845404774
    rightMostCoeff = -0.45308411439364954
    gapsCoeff = -0.527280443244512
    maxColCoeff = 0

    # Old coefficients Coefficients

    if maximumColumnHeight > 13 or holes > 0:
        maxColCoeff = -1.2818902163686863
        heightCoeff = -0.008003913016549473
        onetothreeCoeff = 0.0012453808091311908
        bumpsCoeff = -0.1088077254081058
        gapsCoeff = -0.20168757364913825

    score = +holeCoeff*holes + heightCoeff * height + onetothreeCoeff * onetothreelines + bumpsCoeff*bumps + tetrisCoeff * \
        tetris + rightMostCoeff * righMostLine + maxColCoeff * \
        maximumColumnHeight + gapsCoeff*gaps

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
    bestSandbox = None
    if sandbox.falling is not None:
        leftmoves = distanceFrom0X(sandbox)
        rightmoves = 10-findPieceWidth(sandbox) - leftmoves

        for move in range(0, leftmoves):
            movedSandbox, moves = moveHorizontally(
                sandbox, previousMoves, Direction.Left, move)
            newSandboxScore = 0

            if sandbox.next is not None:
                newBoard = movedSandbox.clone()
                newSandboxScore += chooseBestMove(newBoard)[1]

            newSandboxScore += evalBoard(movedSandbox)
            if (newSandboxScore > bestScore):
                bestAction = moves.copy()
                bestScore = newSandboxScore
                bestSandbox = movedSandbox

        for move in range(0, rightmoves):
            movedSandbox, moves = moveHorizontally(
                sandbox, previousMoves, Direction.Right, move)
            newSandboxScore = 0

            if sandbox.next is not None:
                newBoard = movedSandbox.clone()
                newSandboxScore += chooseBestMove(newBoard)[1]

            newSandboxScore += evalBoard(movedSandbox)

            if (newSandboxScore > bestScore):
                bestAction = moves.copy()
                bestScore = newSandboxScore
                bestSandbox = movedSandbox
        # Neither right or lef, just drop centrally
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
            bestSandbox = movedSandbox
    return bestScore, bestAction, bestSandbox


def distanceFrom0X(sandbox):
    min = 100
    for pair in sandbox.falling.cells:
        if (pair[0] < min):
            min = pair[0]
    return min


def findPieceWidth(sandbox):
    min = 100
    max = -1
    for pair in sandbox.falling.cells:
        if (pair[0] > max):
            max = pair[0]
        if (pair[0] < min):
            min = pair[0]
    return (max-min+1)


def someDirection(list, move):
    l = list.copy()
    l.append(move)
    return l


def chooseBestMove(sandbox_original):
    bestScore = -1000000
    bestAction = []
    bestSandbox = None
    if sandbox_original.falling is not None:
        rots = 4
        if sandbox_original.falling.shape == Shape.O:
            rots = 1
        if sandbox_original.falling.shape == Shape.I:
            rots = 2
        for rotation in range(0, rots):
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

            score, totalActions, sandbox = findHorizontalMoves(
                sandbox, actions)
            if score > bestScore:
                bestAction = totalActions.copy()
                bestScore = score
                bestSandbox = sandbox
    return bestAction, bestScore, bestSandbox


def dropBomb(sandbox, position):
    tempsand = sandbox.clone()


class MichaelsPlayer(Player):
    def __init__(self, seed=None):
        # Could initialise parameters from here?
        self.random = Random(seed)
        self.test = True
        self.testtwo = False
        self.iterToTest = 1

    def choose_action(self, board):
        global lastHoles, lastScore, discards
        lastHoles = findHoles(board)
        lastScore = board.score

        bombedBoard = board.clone()

        bestMove = chooseBestMove(board)

        newHoles = findHoles(bestMove[2])

        if (newHoles > 0 and discards < 10):
            discards += 1
            return Action.Discard

        return bestMove[0]


SelectedPlayer = MichaelsPlayer
