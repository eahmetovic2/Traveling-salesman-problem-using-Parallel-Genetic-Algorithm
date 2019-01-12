# -*- coding: utf-8 -*-
import random
import math
import matplotlib.pyplot as plt
import time
import multiprocessing as mp

def GenerisiGradove(numCities, width, height):
    x = []
    y = []
    for i in range(0,numCities):
        x.append(random.randint(0, width - 100) + 40)
        y.append(random.randint(0, height - 100) + 40)
    return (x, y)

class geneticOpt(object):
    def __init__(self, numIter, numCities, popSize, x, y, paralelno = False):
	# Initialize data
        self.generation = 0
        self.width = 1000
        self.height = 1000
        self.numIter = numIter
       	self.numCities = numCities
       	self.popSize = popSize
       	self.paralelno = paralelno
       	self.numThreads = 4
       	self.x = x
       	self.y = y 
       	self.population = [] #chromosome[]
       	#self.current = Chromosome(self.numCities, self)


	# Set up population
        for i in range(self.popSize):
            self.population.append(Chromosome(self.numCities, self))
            self.population[i].Mutate()
	

	# Pick out the strongest
        sorted(self.population, key=lambda c: c.cost)
        #self.Sort(self.population, self.population[0])
        self.current = self.population[0];
        
        start = time.time()
	# Loop through
        for i in range(self.numIter):
            self.Evolve(i)
            
        end = time.time()
        elapsed = end - start
        self.Plot(elapsed)

    def EvolveParallel(self, razmak):
        start = razmak[0]
        end = razmak[1]
        # Get midpoint
        n = len(self.population)/2
        for m in range(start, end, -1):
            i = random.randint(0,n)   
            j = random.randint(0,n)    
            while (i == j):
                j = random.randint(0,n)
                
            self.population[m].Crossover(self.population[i],self.population[j])
            self.population[m].Mutate()
        

    def Evolve(self, p):
        print("Iteracija broj: ", p+1)
        if self.paralelno:
            startEvolve = self.popSize - 1 #24
            endEvolve = (self.popSize - 1) - (self.popSize - 1)/self.numThreads
            razmaci = []
            for i in range(self.numThreads):
                if(i == self.numThreads -1):
                    endEvolve = -1
                else:
                    endEvolve = (self.popSize - 1) - (self.popSize - 1)*(i + 1)//self.numThreads + 1
                razmaci.append([startEvolve, endEvolve])
                startEvolve = endEvolve
                        
            pool = mp.Pool(processes=4)
            #result = [pool.apply(self.EvolveParallel, args=(razmak)) for razmak in razmaci]
            results = pool.map(self.EvolveParallel, razmaci)
            # Split up work, assign to threads
            #for i in range(self.numThreads):
            #    endEvolve = (self.popSize - 1) - (self.popSize - 1)*(i + 1)/self.numThreads + 1
                #tpool.execute(new evolveThread(startEvolve, endEvolve))
            #    startEvolve = endEvolve
	    
        else:
            # Select top half for breeding
            n = len(self.population)/2
        
            # CRITICAL SECTION
            for m in range(len(self.population)-1, 1, -1):
                i = random.randint(0,n)   
                j = random.randint(0,n)    
                while (i == j):
                    j = random.randint(0,n)
                    
                self.population[m].Crossover(self.population[i],self.population[j])
                self.population[m].Mutate()
            
        
        self.population[1].Crossover(self.population[0],self.population[1])
        self.population[1].Mutate()
        self.population[0].Mutate()
    
        # Pick out the strongest
        sorted(self.population, key=lambda c: c.cost)
        #self.Sort(self.population, self.population[0])
        self.current = self.population[0]
        self.generation += 1   


    def Distance(self, city1, city2):
        if (city1 >= self.numCities):
            city1 = 0
        if (city2 >= self.numCities):
            city2 = 0

        xdiff = self.x[city1] - self.x[city2]
        ydiff = self.y[city1] - self.y[city2]
        
        return math.sqrt(xdiff*xdiff + ydiff*ydiff)
        
    def Plot(self, vrijeme):
	# Fill in node graphic
        fig = plt.figure()
        fig.suptitle("Ukupna udaljenost: "+ str(round(self.current.cost, 2)))
        plt.plot(self.x, self.y, 'bo')
        plt.axis([0, self.width, 0, self.height])

	# Set up edges
        for i in range(self.numCities):
            icity = self.current.genes[i]
            if (i != 0):
                last = self.current.genes[i - 1]    
                plt.plot([self.x[icity], self.x[last]], [self.y[icity], self.y[last]], 'k-', lw=1)            
                
        plt.show()
        print("Vrijeme izvršenja: ", vrijeme)

class Chromosome(object):
    def __init__(self, numCities, gen):
        self.gen = gen
        self.numCities = numCities
        self.genes = []
        self.b = BitSet(numCities)
        
        for i in range(self.numCities):
            self.genes.append(i)
    
        self.cost = self.Cost()
    
    
    def Cost(self):
        d = 0
        for i in range(1, len(self.genes)):
            d += self.gen.Distance(self.genes[i], self.genes[i - 1])
        return d
    
    
    def Mutate(self):
        for k in range(self.numCities-1, -1, -1):
            i1 = random.randint(0, self.numCities-2)
            j1 = random.randint(0, self.numCities-2)
            
            while(j1 == i1): 
                j1 = random.randint(0, self.numCities-2)
            old = self.gen.Distance(self.genes[i1], self.genes[i1 + 1]) + self.gen.Distance(self.genes[j1], self.genes[j1 + 1])
            guess = self.gen.Distance(self.genes[i1], self.genes[j1]) + self.gen.Distance(self.genes[i1 + 1], self.genes[j1 + 1])
            
            if guess >= old:
                continue
            
            self.cost -= old - guess
            
            if j1 < i1:
                k1 = i1 
                i1 = j1 
                j1 = k1            
            
            while j1 > i1:
                i2 = self.genes[i1 + 1];
                self.genes[i1 + 1] = self.genes[j1];
                self.genes[j1] = i2;
                j1 = j1 -1
                i1 = i1 +1
                
        self.cost = self.Cost()
             
    
    def Crossover(self, dad, mom):
        i = random.randint(0, self.numCities)
    
        while (i < self.numCities - 1):
            child = self.gen.Distance(dad.genes[i], mom.genes[i+1]);
            
            if (child < self.gen.Distance(dad.genes[i], dad.genes[i+1]) and child < self.gen.Distance(mom.genes[i], mom.genes[i+1])):
                self.Mate(dad, mom, i)
                break            
            
            i += 1
        
       
    def Mate(self, dad, mom, i):
        self.b.Clear();
    
        if (self == mom):
            temp = mom
            mom = dad
            dad = temp
            
        for j in range(0, i + 1):
            self.genes[j] = dad.genes[j];
            self.b.Set(self.genes[j]);
        
        k = i + 1
        
        for j in range(i+1, len(self.genes)):
            if (self.b.Get(mom.genes[j])):
                continue
            self.genes[k] = mom.genes[j];
            self.b.Set(self.genes[k]);
            k += 1
        
    
        j = 0
    
        while (k < len(self.genes)):
            while (self.b.Get(mom.genes[j])):
                j += 1
            self.genes[k] = mom.genes[j]
            k += 1
            j += 1        
    
        self.cost = self.Cost()

class BitSet(object):
    def __init__(self, duzina):
        self.niz = []
        for i in range(duzina):
            self.niz.append(False)
    
    def Clear(self):
        for i in range(len(self.niz)):
            self.niz[i] = False
            
    def Set(self, index):
        self.niz[index] = True
        
    def Get(self, index):
        return self.niz[index]
    

def main():
    numIter = 5
    numCities = 5
    popSize = 100*numCities//2
    gradovi = GenerisiGradove(numCities, 1000, 1000)
    k = geneticOpt(numIter, numCities, popSize, gradovi[0], gradovi[1])
    if __name__ == '__main__':
        __spec__ = "ModuleSpec(name='builtins', loader=<class '_frozen_importlib.BuiltinImporter'>)"
        k = geneticOpt(numIter, numCities, popSize, gradovi[0], gradovi[1], True)
    
main()