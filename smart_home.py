
# Scenarios: 
#   use windows, use doors
#   failed bulb- use others
#   intensity vs cost- turn few bulb on with higher intensity instead of turning all on- saving cost by using one high intensity bulb

# MAPE will have a GA with f.f Cost, Keep it lit for occupants
#      GA: mutations turn ON, Turn off
#           ON= costs 10 units per step, OFF= zero units

# Awareness
#   Goal: Add to f.f. reduce polution, some bulb type create more polution than others
#   Context: roof and wall window control system awareness, linked to resource awareness
#       Resoruce: Amount and location of Wall and roof top windows
#
import numpy as np
from deap import base, creator, algorithms, benchmarks, tools
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math 

import random
from scenario import Scenario
from home import Home

#----- Mape

class SmartHome(Home):
    
    def __init__(self, w, h):
        super().__init__(w,h)
        self.scenario = Scenario()
        self.presence, self.bulbs = self.scenario.diagonal(self.width, self.height)
        
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        self.toolbox = base.Toolbox()

        self.toolbox.register(
           "random_num",
           random.choice,
           [0,1]) 
        self.DIM = self.width * self.height

        self.toolbox.register(
            "individual",
            tools.initRepeat,
            creator.Individual,
            self.toolbox.random_num,
            n=self.DIM)

        print (self.toolbox.individual())

        self.toolbox.register("population",
                           tools.initRepeat,
                           list,
                           self.toolbox.individual)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("select", tools.selBest)
        self.toolbox.register("evaluate", self.evaluateInd2)
        self.toolbox.register("mutate", self.myMutation)

        self.fig = plt.figure(figsize=(1, 2))

        self.fig.add_subplot(121)
        plt.imshow(self.presence, cmap='gray', interpolation='nearest', vmin=0, vmax=1)

        self.fig.add_subplot(122)
        self.im = plt.imshow(self.bulbs, cmap='gray', interpolation='bilinear', animated=True, vmin=0, vmax=1)
        
        self.pop = self.toolbox.population(n=1000)
        
    def fitness(self, individual, data):
        print (data)
        print (individual)
        match = 0
        #for selected, bulbs in zip(individual, data):
            #if selected:
        for x in range(self.width):
            for y in range(self.height):
                if self.presence[x,y]>0 and individual[x,y]>0:
                    match += 1
        match_percentage = match / self.width * self.height 
        return match_percentage

    def evaluateInd(self, individual):
        match = 0
        #for selected, bulbs in zip(individual, data):
            #if selected:
        for y in range(self.height): # top left is (X=0,Y=0)
            for x in range(self.width):
                if individual[y*self.width+x]>0 and self.presence[x,y]>0:
                    match += 1
        match_percentage = match / (self.width * self.height) 
        return (float(match_percentage),)

    def evaluateInd2(self, individual):
        match = 0
        #for selected, bulbs in zip(individual, data):
            #if selected:
        for y in range(self.height): # top left is (X=0,Y=0)
            for x in range(self.width):
                
                if individual[y*self.width+x] == self.presence[x,y]:
                    if self.bulbs[x,y] > -1:
                        match += 1
        match_percentage = match / (self.width * self.height) 
        return (float(match_percentage),)

    def myMutation(self, individual):
        luminosity = self.decode(individual)
        
        for i in range(self.width):
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)

            if(self.bulbs[x,y] > -1):
                luminosity[x,y] = random.choice([0,1])
        
        #luminosity = self.encode (luminosity)
        self.update_individual(individual, luminosity)
        #for i in range(self.width):
        #    individual[random.randint(0,len(individual)-1)] = random.choice([0,1])
        return (individual,)
    
    def update_individual (self, individual, data):
        for y in range(self.height):
            for x in range(self.width):
                individual[y*self.width+x] = data[x,y]
            
    def encode(self, luminosity):
        return luminosity.flatten()
        
    def decode(self, individual):
#        bulbs = np.zeros((self.width,self.height))
#        for y in range(self.height): # top left is (X=0,Y=0)
#            for x in range(self.width):
#                bulbs[x,y] = individual[y*self.width+x]
        return np.reshape(individual, (-1, self.width))
 
    def updatefig(self, *args):
        algorithms.eaMuPlusLambda (
                self.pop, self.toolbox, 
                400, 100, #parents, children
                0.8, 0.2, #probabilities
                1) #iterations

        top = sorted(self.pop, key=lambda x:x.fitness.values[0])[-1]
        fit = top.fitness.values[0]
        print ('fitness-: {}'.format(fit))

        self.im.set_data(self.decode(top))
        #im.set_cmap("gray")
        #im.update()
        return self.im,
    
    def run(self):
        ani = animation.FuncAnimation(self.fig, self.updatefig, interval=50, blit=True)
        plt.show()

    
    
    



