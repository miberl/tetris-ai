from constants import BOARD_WIDTH, BOARD_HEIGHT, DEFAULT_SEED, INTERVAL, BLOCK_LIMIT
from board import Board, Direction, Rotation, Action, Shape
from exceptions import BlockLimitException
from machinePlayer import Player, SelectedPlayer
from adversary import RandomAdversary
import math
import time
import multiprocessing
import operator
from random import seed
import numpy as np
import copy


class Candidate:
    def __init__(self, candidateDict):
        self.Holes = candidateDict['Holes']
        self.AggrHeight = candidateDict['AggrHeight']
        self.CompletedLines = candidateDict['CompletedLines']
        self.Bumpiness = candidateDict['Bumpiness']
        self.Tetris = candidateDict['Tetris']
        self.RightMost = candidateDict['RightMost']
        self.Gaps = candidateDict['Gaps']
        self.after8AggrHeight = candidateDict['after8AggrHeight']
        self.after8MaxCol = candidateDict['after8MaxCol']
        self.after8CompletedLines = candidateDict['after8CompletedLines']
        self.after8Bumpiness = candidateDict['after8Bumpiness']
        self.after8Gaps = candidateDict['after8Gaps']

        self.Fitness = None

    def mutateElement(self, value, mutationrate):
        if np.random.random(1)[0] < mutationrate:
            return percentageDelta(value)
        return value

    def mutate(self):
        # Max mutation delta between -0.05 and +0.05
        mutRate = 0.12
        self.Holes = self.mutateElement(self.Holes, mutRate)
        self.AggrHeight = self.mutateElement(self.AggrHeight, mutRate)
        self.CompletedLines = self.mutateElement(self.CompletedLines, mutRate)
        self.Bumpiness = self.mutateElement(self.Bumpiness, mutRate)
        self.Tetris = self.mutateElement(self.Tetris, mutRate)
        self.RightMost = self.mutateElement(self.RightMost, mutRate)
        self.Gaps = self.mutateElement(self.Gaps, mutRate)
        self.after8AggrHeight = self.mutateElement(
            self.after8AggrHeight, mutRate)
        self.after8MaxCol = self.mutateElement(self.after8MaxCol, mutRate)
        self.after8CompletedLines = self.mutateElement(
            self.after8CompletedLines, mutRate)
        self.after8Bumpiness = self.mutateElement(
            self.after8Bumpiness, mutRate)
        self.after8Gaps = self.mutateElement(self.after8Gaps, mutRate)

    def addFitness(self, fitnessScore):
        self.Fitness = fitnessScore

    def clone(self):
        return copy.deepcopy(self)

    def __repr__(self):
        return 'Candidate( Holes: ' + str(self.Holes) + ' AggrHeight: ' + str(self.AggrHeight) + ' CompletedLines: ' + str(self.CompletedLines) + ' Bumpiness: ' + str(self.Bumpiness) + ' Tetris: ' + str(self.Tetris) + ' RightMost: ' + str(self.RightMost)+' Gaps: ' + str(self.Gaps)+' after8AggrHeight: '+str(self.after8AggrHeight)+' after8MaxCol: '+str(self.after8MaxCol)+' after8CompletedLines: '+str(self.after8CompletedLines)+' after8Bumpiness: '+str(self.after8Bumpiness)+' after8Gaps: '+str(self.after8Gaps)+' )'


class Population:
    def __init__(self):
        self.candidates = []
        self.rounds = 10
        self.latestTotalFitness = 0
        self.currentCandidate = None

    def addCandidate(self, candidate):
        self.candidates.append(candidate)

    def computeFitnesses(self):
        totFitness = 0
        seeds = [8, 100, 22, 122, 612, 222, 127, 329, 431, 174]

        for cand in self.candidates:
            totScore = 0
            self.currentCandidate = cand
            p = multiprocessing.Pool(10)
            results = p.map(self.computeSProc, seeds)
            for seed, score in results:
                totScore += score
            cand.Fitness = totScore

        self.sortByFitness()
        self.latestTotalFitness = totFitness

    def computeSProc(self, seed):
        board = Board(BOARD_WIDTH, BOARD_HEIGHT)
        block_limit = 400
        adversary = RandomAdversary(seed, block_limit)
        #player = SelectedPlayer(self.candidates[candidateIndex])
        player = SelectedPlayer(self.currentCandidate)
        try:
            for move in board.run(player, adversary):
                i = board.score
        except:
            pass
        finally:
            score = board.score
            print(seed, score)
        return (seed, score)

    def sortByFitness(self):
        self.candidates = sorted(
            self.candidates, key=operator.attrgetter("Fitness"), reverse=True)

    def naturalSelection(self):
        newCandidates = []
        self.sortByFitness()
        parent = self.candidates[0]
        child = parent.clone()
        newCandidates.append(child)

        mutatedchild = child.clone()
        mutatedchild.mutate()

        newCandidates.append(mutatedchild)

        while len(newCandidates) < len(self.candidates):
            randomParent = self.selectCandidate()
            child = randomParent.clone()
            child.mutate()
            newCandidates.append(child)

        self.candidates = newCandidates

    def selectCandidate(self):
        rand = np.random.random(1)[0]*self.latestTotalFitness
        sum = 0
        for cand in self.candidates:
            sum += cand.Fitness
            if sum > rand:
                return cand
        return None

    def getLength(self):
        return len(self.candidates)

# Variance between 0.95 and 1.05


def percentageDelta(value):
    variance = value*0.2
    #variance = value*0.05
    return value + np.random.random(1)[0]*2*variance - variance


# this could be an initial element of population
def generateRandomCandidate():
    # Generating random values between -0.5 and 0.5 for each characteristic

    # Not truly random, starting from known heuristics

    randCandidate = {'Holes': -10.425848148861757,
                     'AggrHeight': -0.0009293794396322049,
                     'CompletedLines': -2.5023832192570596,
                     'Bumpiness': -0.04355179063623546,
                     'Tetris': 102.45373845404774,
                     'RightMost': -0.45308411439364954,
                     'Gaps': -0.527280443244512,
                     'after8AggrHeight': -0.008003913016549473,
                     'after8MaxCol': -1.2818902163686863,
                     'after8CompletedLines': 0.0012453808091311908,
                     'after8Bumpiness': -0.1088077254081058,
                     'after8Gaps': -0.20168757364913825
                     }

    return randCandidate


def startLearning():
    popSize = 10
    pop = Population()
    c = Candidate(generateRandomCandidate())
    pop.addCandidate(c)
    for i in range(popSize-1):
        c = Candidate(generateRandomCandidate())
        c.mutate()
        pop.addCandidate(c)

    generation = 0

    print('Calculating fitness for gen=0 (random) population')
    pop.computeFitnesses()
    pop.sortByFitness()

    # best performing candidate

    print('Average Fitness: ', pop.latestTotalFitness//pop.getLength())
    print('Highest Fitness: ', pop.candidates[0].Fitness)
    print('Fittest candidate values: ', pop.candidates[0])
    print('Highest AVG round Fitness:', pop.candidates[0].Fitness//pop.rounds)

    while True:

        pop.naturalSelection()

        generation += 1
        print('Checking fitness of new candidates, gen=', generation)

        pop.computeFitnesses()
        pop.sortByFitness()

        print('Average Fitness: ', pop.latestTotalFitness//pop.getLength())
        print('Highest Fitness: ', pop.candidates[0].Fitness)
        print('Fittest candidate values: ', pop.candidates[0])
        print('Highest AVG round Fitness:',
              pop.candidates[0].Fitness//pop.rounds)


if __name__ == '__main__':
    startLearning()
