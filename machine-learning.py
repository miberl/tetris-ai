from constants import BOARD_WIDTH, BOARD_HEIGHT, DEFAULT_SEED, INTERVAL, BLOCK_LIMIT
from board import Board, Direction, Rotation, Action, Shape
from exceptions import BlockLimitException
from machinePlayer import Player, SelectedPlayer
from adversary import RandomAdversary
import math, time, multiprocessing, operator
from random import seed 
import numpy as np


class Candidate:
    def __init__(self, candidateDict):
        self.Holes = candidateDict['Holes']
        self.AggrHeight = candidateDict['AggrHeight']
        self.CompletedLines = candidateDict['CompletedLines']
        self.Bumpiness = candidateDict['Bumpiness']
        self.Tetris = candidateDict['Tetris']
        self.RightMost = candidateDict['RightMost']
        self.Gaps =  candidateDict['Gaps']
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
        #Max mutation delta between -0.05 and +0.05
        mutRate = 0.1
        self.Holes = self.mutateElement(self.Holes, mutRate)
        self.AggrHeight = self.mutateElement(self.AggrHeight, mutRate)
        self.CompletedLines = self.mutateElement(self.CompletedLines, mutRate)
        self.Bumpiness = self.mutateElement(self.Bumpiness, mutRate)
        self.Tetris = self.mutateElement(self.Tetris, mutRate)
        self.RightMost = self.mutateElement(self.RightMost, mutRate)
        self.Gaps =  self.mutateElement(self.Gaps, mutRate)
        self.after8MaxCol = self.mutateElement(self.after8MaxCol, mutRate)
        self.after8CompletedLines =  self.mutateElement(self.after8CompletedLines, mutRate)
        self.after8Bumpiness =  self.mutateElement(self.after8Bumpiness, mutRate)
        self.after8Gaps =  self.mutateElement(self.after8Gaps, mutRate)

    def addFitness(self, fitnessScore):
        self.Fitness = fitnessScore
    
    def clone(self):
        return self
        
    def __repr__(self):
        return 'Candidate( Holes: '+ str(self.Holes) + ' AggrHeight: '+ str(self.AggrHeight) + ' CompletedLines: '+ str(self.CompletedLines) + ' Bumpiness: '+ str(self.Bumpiness) + ' Tetris: '+ str(self.Tetris) + ' RightMost: '+ str(self.RightMost)+' Gaps: '+ str(self.Gaps)+' after8MaxCol: '+str(self.after8MaxCol)+' after8CompletedLines: '+str(self.after8CompletedLines)+' after8Bumpiness: '+str(self.after8Bumpiness)+' after8Gaps: '+str(self.after8Gaps)+' )'
class Population:
    def __init__(self):
        self.candidates = []
        self.rounds = 10
        self.latestTotalFitness = 0
    
    def addCandidate(self, candidate):
        self.candidates.append(candidate)

    def computeFitnesses(self):
        totFitness = 0
        p = multiprocessing.Pool(8)
        lst = list(range(len(self.candidates)))
        results = p.map(self.computeMProc, lst)
        for tupl in results:
            self.candidates[tupl[0]].Fitness = tupl[1]
            totFitness += tupl[1]
        self.sortByFitness()
        self.latestTotalFitness = totFitness

    #It is passed an index of the candidate in the list, it returns a tuple containing (index, fitnessscore)
    def computeMProc(self, candidateIndex):
        totScore = 0
        seeds = [23,32,38,42,100,101,123,150,223,250]
        for rnd in range(self.rounds):
            board = Board(BOARD_WIDTH, BOARD_HEIGHT)
            block_limit = 400
            adversary = RandomAdversary(seeds[rnd], block_limit)
            player = SelectedPlayer(self.candidates[candidateIndex])
            try:
                for move in board.run(player, adversary):
                    i = board.score     
            except:
                pass
            finally:
                score = board.score
                if board.alive is False:
                    score = int(score*0.5)
                totScore += score
        return (candidateIndex, totScore)

    def sortByFitness(self):
        self.candidates = sorted(self.candidates, key=operator.attrgetter("Fitness"), reverse=True)

    def naturalSelection(self):
        newCandidates = []
        self.sortByFitness()
        parent = self.candidates[0]
        child = parent.clone()
        
        newCandidates.append(child)
        mutatedchild = child.clone().mutate()
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
            sum+= cand.Fitness 
            if sum > rand:
                return cand
        return None


    def getLength(self):
        return len(self.candidates)

def percentageDelta(value):
    variance = value*0.05
    return value + np.random.random(1)[0]*2*variance - variance
    


#this could be an initial element of population
def generateRandomCandidate():
    # Generating random values between -0.5 and 0.5 for each characteristic 

    #Not truly random, starting from known heuristics

    randCandidate = {   'Holes':  -4.9,
                    'AggrHeight': -0.001, 
                    'CompletedLines' :-0.4,
                    'Bumpiness' : -0.01,
                    'Tetris' : 1000,
                    'RightMost' : -0.4,
                    'Gaps': -0.2,
                    'after8MaxCol':-1,
                    'after8CompletedLines': 0.01,
                    'after8Bumpiness':-0.15,
                    'after8Gaps': -0.1
                    }

    return randCandidate

    


def startLearning():
    popSize = 16
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

    #best performing candidate

    
    print('Average Fitness: ', pop.latestTotalFitness//pop.getLength())
    print('Highest Fitness: ', pop.candidates[0].Fitness)
    print('Fittest candidate values: ', pop.candidates[0])
    print('Highest AVG round Fitness:',pop.candidates[0].Fitness//pop.rounds )
    

    
    
    
    while True:

        pop.naturalSelection()

        generation+=1
        print('Checking fitness of new candidates, gen=',generation)

        pop.computeFitnesses()
        pop.sortByFitness()
        
    
        print('Average Fitness: ', pop.latestTotalFitness//pop.getLength())
        print('Highest Fitness: ', pop.candidates[0].Fitness)
        print('Fittest candidate values: ', pop.candidates[0])
        print('Highest AVG round Fitness:',pop.candidates[0].Fitness//pop.rounds)

        
    
if __name__ == '__main__':
    startLearning()
