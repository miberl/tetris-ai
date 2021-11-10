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

        self.Fitness = None

    def mutate(self):
        #Max mutation delta between -0.2 and +0.2
        for i in range(1, np.random.randint(3, size=1)[0]):
            randomGeneToMutate = np.random.randint(6, size=1)[0]
            if randomGeneToMutate == 0:
                self.Holes = percentageDelta(self.Holes)
            elif randomGeneToMutate == 1:
                self.AggrHeight = percentageDelta(self.AggrHeight)
            elif randomGeneToMutate == 2:
                self.CompletedLines = percentageDelta(self.CompletedLines)
            elif randomGeneToMutate == 3:
                self.Bumpiness = percentageDelta(self.Bumpiness)
            elif randomGeneToMutate == 4:
                self.Tetris+= percentageDelta(self.Tetris)
            else:
                self.RightMost += percentageDelta(self.RightMost)

    def addFitness(self, fitnessScore):
        self.Fitness = fitnessScore
    
    def normaliseValues(self):
        norm = 0
        norm += (self.Holes ** 2)
        norm += (self.AggrHeight ** 2)
        norm += (self.CompletedLines ** 2)
        norm += (self.Bumpiness ** 2)
        norm += (self.Tetris ** 2)
        norm += (self.RightMost ** 2)
        norm = math.sqrt(norm)
        
        self.Holes /= norm
        self.AggrHeight /= norm
        self.CompletedLines /= norm
        self.Bumpiness /= norm
        self.Tetris /= norm
        self.RightMost /= norm

    def __repr__(self):
        return 'Candidate( Holes: '+ str(self.Holes) + ' AggrHeight: '+ str(self.AggrHeight) + ' CompletedLines: '+ str(self.CompletedLines) + ' Bumpiness: '+ str(self.Bumpiness) + ' Tetris: '+ str(self.Tetris) + ' RightMost: '+ str(self.RightMost)+' )'
class Population:
    def __init__(self):
        self.candidates = []
        self.rounds = 1
    
    def addCandidate(self, candidate):
        self.candidates.append(candidate)

    def computeFitnesses(self):
        p = multiprocessing.Pool(8)
        lst = list(range(len(self.candidates)))
        results = p.map(self.computeMProc, lst)
        for tupl in results:
            self.candidates[tupl[0]].Fitness = tupl[1]
        self.sortByFitness()
        

    #It is passed an index of the candidate in the list, it returns a tuple containing (index, fitnessscore)
    def computeMProc(self, candidateIndex):
        totScore = 0
        #seeds = [3,7,23,48,76,92,99,123,200,324]
        seeds = [42]
        for rnd in range(self.rounds):
            board = Board(BOARD_WIDTH, BOARD_HEIGHT)
            #RANDOM SEED
            #random_seed = np.random.randint(200, size=1)[0]
            block_limit = 200
            adversary = RandomAdversary(seeds[rnd], block_limit)
            player = SelectedPlayer(self.candidates[candidateIndex])
            try:
                for move in board.run(player, adversary):
                    i = board.score     
            except:
                pass
            finally:
                score = board.score
                #if board.alive is False:
                    #score = int(score*0.5)
                totScore += score
        return (candidateIndex, totScore)

    def sortByFitness(self):
        self.candidates = sorted(self.candidates, key=operator.attrgetter("Fitness"), reverse=True)

    #Removes the n last population candidates (based on their fitness) and swaps them with the passed n candidates
    def swapLastPopulationcandidates(self, them):
        self.sortByFitness()
        for newCand in them:
            self.candidates.pop()
        for newCand in them:
            self.addCandidate(newCand)

    #The probability of being selected is based on the fitness 
    def selectRandomPair(self):
        fittestCand1 = None
        fittestCand2 = None
        randomPairIterations = self.getLength()//10+2 #self.getLength()//10 + 1
        for it in range(randomPairIterations):
            candidatesLen = len(self.candidates)
            randInd = np.random.randint(candidatesLen, size=1)[0]
            if fittestCand1 is None or self.candidates[randInd].Fitness > self.candidates[fittestCand1].Fitness:
                fittestCand2 = fittestCand1
                fittestCand1 = randInd
            elif fittestCand2 is None or self.candidates[randInd].Fitness > self.candidates[fittestCand2].Fitness:
                fittestCand2 = randInd
        return self.candidates[fittestCand1], self.candidates[fittestCand2]

    def getLength(self):
        return len(self.candidates)

def normalise(candidateDict):
    norm = 0
    for key, value in candidateDict.items():
        if key not in 'Fitness':
            norm += (value ** 2)
    norm = math.sqrt(norm)
    normCand = candidateDict.copy()
    for key, value in normCand.items():
        if key not in 'Fitness':
            normCand[key] /= norm 
    return normCand

#Returns new candidate that is a crossover of the 2 
def crossOver2Candidates(cand1, cand2):
    COCandidate = {  'Holes':  cand1.Fitness *cand1.Holes + cand2.Fitness *cand2.Holes,
                    'AggrHeight': cand1.Fitness *cand1.AggrHeight + cand2.Fitness *cand2.AggrHeight, 
                    'CompletedLines' : cand1.Fitness *cand1.CompletedLines + cand2.Fitness *cand2.CompletedLines,
                    'Bumpiness' : cand1.Fitness *cand1.Bumpiness + cand2.Fitness *cand2.Bumpiness,
                    'Tetris' : cand1.Fitness *cand1.Tetris + cand2.Fitness *cand2.Tetris,
                    'RightMost' : cand1.Fitness *cand1.RightMost + cand2.Fitness *cand2.RightMost
                }
    COCand = Candidate(COCandidate)
    COCand.normaliseValues()
    return COCand

def percentageDelta(value):
    variance = value*0.2
    return value + np.random.random(1)[0]*2*variance - variance
    

#this could be an initial element of population
def generateRandomCandidate():
    # Generating random values between -0.5 and 0.5 for each characteristic 

    #Not truly random, starting from known heuristics
    '''
    randCandidate = {   'Holes':  np.random.random(1)[0] - 0.5,
                    'AggrHeight': np.random.random(1)[0] - 0.5, 
                    'CompletedLines' : np.random.random(1)[0] - 0.5,
                    'Bumpiness' : np.random.random(1)[0] - 0.5,
                    'Tetris' : np.random.random(1)[0] - 0.5,
                    'RightMost' : np.random.random(1)[0] - 0.5
                }
    
    
    randCandidate = {   'Holes':  percentageDelta(-4.9),
                    'AggrHeight': percentageDelta(-0.001), 
                    'CompletedLines' :percentageDelta(-0.4),
                    'Bumpiness' : percentageDelta(-0.05),
                    'Tetris' : percentageDelta(1000),
                    'RightMost' : percentageDelta(-0.4)
                }
    '''
    randCandidate = {   'Holes':  -4.9,
                    'AggrHeight': -0.001, 
                    'CompletedLines' :-0.4,
                    'Bumpiness' : -0.01,
                    'Tetris' : 1000,
                    'RightMost' : -0.4
                }
    #normalisedCand = normalise(randCandidate)
    #return normalisedCand
    return randCandidate

    


def startLearning():
    #popSize = 400
    popSize = 4
    pop = Population()
    for i in range(popSize):
        c = Candidate(generateRandomCandidate())
        pop.addCandidate(c)
    
    print('Calculating fitness for gen=0 (random) population')
    pop.computeFitnesses()
    pop.sortByFitness()
    totFitness = 0
    for cand in pop.candidates:
        totFitness+= cand.Fitness
    print('Average Fitness: ', totFitness//pop.getLength())
    print('Highest Fitness: ', pop.candidates[0].Fitness)
    print('Fittest candidate values: ', pop.candidates[0])
    print('Highrest AVG round Fitness:',pop.candidates[0].Fitness//pop.rounds )
    '''
    generation = 1
    mutationRate = 0.1
    
    while True:
        newCands = []
        #Approx 1/3 of population
        for iteration in range(pop.getLength()//4):
            cand1, cand2 = pop.selectRandomPair()
            cand = crossOver2Candidates(cand1, cand2)
            if np.random.random(1)[0] < mutationRate:
                cand.mutate()
            cand.normaliseValues()
            newCands.append(cand)
        
        print('Checking fitness of new candidates, gen=',generation)
        subPopulation = Population()
        for cand in newCands:
            subPopulation.addCandidate(cand)
        subPopulation.computeFitnesses()

        pop.swapLastPopulationcandidates(subPopulation.candidates)
        pop.sortByFitness()
        totFitness = 0
        for cand in pop.candidates:
            totFitness+= cand.Fitness
        
    
        print('Average Fitness: ', totFitness//pop.getLength())
        print('Highest Fitness: ', pop.candidates[0].Fitness)
        print('Fittest candidate values: ', pop.candidates[0])
        print('Highrest AVG round Fitness:',pop.candidates[0].Fitness//pop.rounds)

        generation += 1
    '''
if __name__ == '__main__':
    startLearning()
