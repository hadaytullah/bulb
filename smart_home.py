
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
        #self.presence, self.bulbs = self.scenario.diagonal(self.width, self.height)
        #self.presence, self.bulbs = self.scenario.stripes(self.width, self.height)
        self.presence, self.bulbs = self.scenario.corners(self.width, self.height)

        self.init_deap()
        self.init_figures()
        
        

        
        self.pop = self.toolbox.population(n=1000)
    
    def init_figures(self):
        
        self.fig = plt.figure(figsize=(1, 3))
        
        self.fig.add_subplot(131)
        plt.imshow(self.presence, cmap='gray', interpolation='nearest', vmin=0, vmax=1)
        
        self.fig.add_subplot(132)
        plt.imshow(self.bulbs, cmap='gray', interpolation='nearest', vmin=-1, vmax=0)
        
        self.fig.add_subplot(133)
        self.im = plt.imshow(self.bulbs, cmap='gray', interpolation='bilinear', animated=True, vmin=0, vmax=1)
        
    def init_deap(self):
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
        self.toolbox.register("evaluate", self.evaluateInd4)
        self.toolbox.register("mutate", self.myMutation)

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
                    else:
                        match -= 1 #penalty
        match_percentage = match / (self.width * self.height) 
        return (float(match_percentage),)

    def evaluateInd3(self, individual):
        score = 0
        #for selected, bulbs in zip(individual, data):
            #if selected:
        for y in range(self.height): # top left is (X=0,Y=0)
            for x in range(self.width):
                
                if individual[y*self.width+x]>0:
                    #if self.presence_in_radius(1, x, y):
                    presence_score = self.presence_in_radius(1, x, y)
                    if self.bulbs[x,y] > -1 and presence_score > 0:
                        score += self.presence_in_radius(1, x, y)
                    else:
                        score -= 1 #penalty for using a broken bulb
        return (float(score),)
    
        #match_percentage = match / (self.width * self.height) 
        #return (float(match_percentage),)
    def presence_in_radius (self, radius, x, y):
        block = ((x-1, y-1), (x, y-1), (x+1,y-1), (x+1, y), (x+1, y+1), (x, y+1), (x-1, y+1), (x-1, y)) # starts from left top
        
        presence_count = 0
        for point in block:
            if point[0] in range(self.width):
                if point[1] in range(self.height): 
                    if self.presence[point[0], point[1]] > 0: #someone present
                        presence_count += 1
                
        return presence_count
 
    def evaluateInd4(self, individual):
        score = 0
        #for selected, bulbs in zip(individual, data):
            #if selected:
        for y in range(self.height): # top left is (X=0,Y=0)
            for x in range(self.width):
                
                if individual[y*self.width+x]>0:
                    #if self.presence_in_radius(1, x, y):
                    presence_score = self.presence_in_radius2(1, x, y, individual)
                    if self.bulbs[x,y] > -1 and presence_score > 0:
                        score += presence_score
                    else:
                        score -= 1 #penalty for using a broken bulb
        return (float(score),)
    
    def evaluateInd_table(self, individual):
        #bulb-state, luminosity, presence : reward sign
        logic_table = {
            '000':1,
            '001':-1,
            '010':-1,
            '011':1,
            '-100':1,
            '-101':1,
            '-110':-1,
            '-111':-1
        }

        score = 0
        #for selected, bulbs in zip(individual, data):
            #if selected:
        for y in range(self.height): # top left is (X=0,Y=0)
            for x in range(self.width):
                presence_score = self.presence_in_radius2(1, x, y, individual)
                key = ''
                key += str(int(self.bulbs[x,y]))
                key += str(int(individual[y*self.width+x])) #luninosity
                key += str(int(1 if presence_score>0 else 0)) # presence

                reward_sign = logic_table[key] #if logic_table[key] else 1
                score = score + (reward_sign * 1)

        return (float(score),)

    def presence_in_radius2 (self, radius, x, y, individual):
        block = ((x-1, y-1), (x, y-1), (x+1,y-1), (x+1, y), (x+1, y+1), (x, y+1), (x-1, y+1), (x-1, y)) # starts from left top
        
        presence_count = 0
        
        if self.presence[x,y] > 0:
            presence_count += 50 #award for presence under the bulb
            #print ('+50')
        
        for point in block:
            if point[0] in range(self.width):
                if point[1] in range(self.height): 
                    if self.presence[point[0], point[1]] > 0 and individual[point[1]*self.width+point[0]] < 1:#someone present in radius and that area is dark
                        presence_count += 1
                
        return presence_count
        
        
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
        bulbs = np.zeros((self.width,self.height))
        for y in range(self.height): # top left is (X=0,Y=0)
            for x in range(self.width):
                bulbs[x,y] = individual[y*self.width+x]
        return bulbs #np.reshape(individual, (-1, self.width))
 
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

    
    
    



