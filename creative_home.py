
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
        self.width_bound = [1, w-2]
        self.height_bound = [1, h-2]
        #self.presence, self.bulbs = self.scenario.diagonal(self.width, self.height)
        self.presence, self.bulbs = self.scenario.stripes(self.width, self.height)
        #self.presence, self.bulbs = self.scenario.corners(self.width, self.height)

        self.init_deap()
        self.init_figures()






    def init_figures(self):

        self.fig = plt.figure(figsize=(1, 3))

        self.fig.add_subplot(131)
        plt.imshow(self.presence, cmap='gray', interpolation='nearest', vmin=0, vmax=1)

        self.fig.add_subplot(132)
        plt.imshow(self.bulbs, cmap='gray', interpolation='nearest', vmin=-1, vmax=0)

        self.fig.add_subplot(133)
        self.im = plt.imshow(self.bulbs, cmap='gray', interpolation='bilinear', animated=True, vmin=0, vmax=1)

    def generate_individual(self,icls):
        luminosity = np.zeros((self.width,self.height))

        for x in range(self.width_bound[0], self.width_bound[1]):
            for y in range(self.height_bound[0], self.height_bound[1]):
                luminosity[x,y] = random.choice([0,1])
                #print ('mutating')

        genome = self.encode(luminosity)
        return icls(genome)

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
            self.generate_individual,
            #tools.initRepeat,
            creator.Individual

            #self.toolbox.random_num,
            #n=self.DIM
            )

        print (self.toolbox.individual())

        self.toolbox.register("population",
                           tools.initRepeat,
                           list,
                           self.toolbox.individual)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("select", tools.selBest)
        self.toolbox.register("evaluate", self.fitness)
        self.toolbox.register("mutate", self.mutate)
        self.pop = self.toolbox.population(n=100)

#    def fitness_(self, individual, data):
#        print (data)
#        print (individual)
#        match = 0
#        #for selected, bulbs in zip(individual, data):
#            #if selected:
#        for x in range(self.width):
#            for y in range(self.height):
#                if self.presence[x,y]>0 and individual[x,y]>0:
#                    match += 1
#        match_percentage = match / self.width * self.height
#        return match_percentage


#    def fitness(self, individual):#evalInd4
#        score = 0
#        #for selected, bulbs in zip(individual, data):
#            #if selected:
#        for y in range(self.height): # top left is (X=0,Y=0)
#            for x in range(self.width):
#
#                if individual[y*self.width+x]>0:
#                    #if self.presence_in_radius(1, x, y):
#                    presence_score = self.presence_in_radius2(1, x, y, individual)
#                    if self.bulbs[x,y] > -1 and presence_score > 0:
#                        score += presence_score
#                    else:
#                        score -= 1 #penalty for using a broken bulb
#        return (float(score),)

    def fitness(self, individual):#evalInd4
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


    def presence_in_radius2 (self, radius, x, y, individual):
        block = ((x-1, y-1), (x, y-1), (x+1,y-1), (x+1, y), (x+1, y+1), (x, y+1), (x-1, y+1), (x-1, y)) # starts from left top

        presence_count = 0

        if self.presence[x,y] > 0:
            presence_count += 10 #award for presence under the bulb
            #print ('+50')

        for point in block:
            if point[0] in range(self.width):
                if point[1] in range(self.height):
                    if self.presence[point[0], point[1]] > 0 and individual[point[1]*self.width+point[0]] < 1:#someone present in radius and that area is dark
                        presence_count += 1

        return presence_count


    def mutate(self, individual):
        #print('Mutating')
        luminosity = self.decode(individual)

        for i in range(self.width):
            x = random.randint(self.width_bound[0], self.width_bound[1])
            y = random.randint(self.height_bound[0], self.height_bound[1])

            if(self.bulbs[x,y] > -1):
                luminosity[x,y] = random.choice([1,1])

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

    #------------------ simulation loop ----------------
    def updatefig(self, *args):
        algorithms.eaMuPlusLambda (
                self.pop, self.toolbox,
                400, 100, #parents, children
                0.5, 0.5, #probabilities
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
    #---------------------- awareness ---------------------
    def awareness_step(self):
        # context: interaction with windows controller
        # resource: luminosity sensors, bulbs broken/working, bulb intensity high/low = radius
        # domain: windows are source of light
        # goal : power saving + luminosity
        # probe: luminosity sensors
        # strategy,
        # enactor
        # time,
        # hypothesis
        pass

class CreativeHome(SmartHome):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.evaluation_unit = 1

        self.goal_aware = True
        self.resource_aware = True
        self.context_aware = True
        self.domain_aware = True

        self.goals = {
            'luminosity':{
                'enabled': True,
                'maximize': True,
                'evaluate': self.evaluate_luminosity
            },
            'cost':{
                'enabled':True,
                'maximize':False,
                'evaluate': self.evaluate_cost
            }
        }


    #------------------ goal awareness stuff starts -----------------
    def evaluate_luminosity(self, individual):
        score = 0
        #for selected, bulbs in zip(individual, data):
            #if selected:
        for y in range(self.height): # top left is (X=0,Y=0)
            for x in range(self.width):

                if individual[y*self.width+x]>0:
                    #if self.presence_in_radius(1, x, y):
                    presence_score = self.presence_in_radius2(1, x, y, individual)
                    #if self.bulbs[x,y] > -1 and presence_score > 0:
                    #if presence_score > 0:
                    score += presence_score
                    #else:
                    #    score -= 1 #penalty for using a broken bulb
        return score


    def evaluate_cost(self, individual):
        score = 0
        #for selected, bulbs in zip(individual, data):
            #if selected:
        for y in range(self.height): # top left is (X=0,Y=0)
            for x in range(self.width):
                if individual[y*self.width+x]>0 and self.bulbs[x,y] > -1:
                    presence_score = self.presence_in_radius2(1, x, y, individual)
                    if presence_score < 1:
                        score += 3 * self.evaluation_unit
        return score
    # ------- main fitness function -------

    def fitness(self, individual):
        #print('goal based fitness')
        fitness = 0

        if self.goal_aware:
            for goal_name, goal in self.goals.items():
                if goal['enabled']:
                    if goal['maximize']:
                        fitness = fitness + goal['evaluate'](individual)
                    else:
                        fitness = fitness - goal['evaluate'](individual)
        #else:
        #    fitness += super().fitness(individual)[0]

        if self.resource_aware:
            fitness += self.evaluate_resource(individual)

        if self.domain_aware and self.context_aware:
            fitness += self.evaluate_domain_context (individual)


        return (float(fitness),)


    #------- resoruce awareness
    def evaluate_resource(self, individual):
        # probe: luminosity sensors are resources too, may be merge prob-aw into resources. lumisity array is kind of probes
        score = 0
        #for selected, bulbs in zip(individual, data):
            #if selected:
        for y in range(self.height): # top left is (X=0,Y=0)
            for x in range(self.width):
                if individual[y*self.width+x]>0 and self.bulbs[x,y] == -1:
                    score += (10 * self.evaluation_unit)
        #penalty, -1 makes it reduce the fitness of individuals using broken bulbs
        return -1*score

    #------- domain and context, access window control, use windows --------------

    def evaluate_domain_context(self, individual):
        #domain: windows are source of light
        #context: windows can be controlled for light
        # assumption: one quarter of the space can be lit with windows there, left-top here
        score = 0
        for y in range(self.height): # top left is (X=0,Y=0)
            for x in range(self.width):
                if x < 0.5*self.width and y < 0.5*self.height: #left-top area
                    if individual[y*self.width+x]>0:
                        score += 1*self.evaluation_unit

        #penalty for using bulbs in already lit area
        return -1*score

    # --- probe and enactors are kind of resources, does not make sense, drop them, see evaluate_resource function for explanation

    #

#class CreativeHome_(object):
#    def __init__(self, width, height):
#        self.wrapped_class = SmartHome(width, height)
#
#    def __getattr__(self,attr):
#        orig_attr = self.wrapped_class.__getattribute__(attr)
#        if callable(orig_attr):
#            def hooked(*args, **kwargs):
#                self.pre()
#                result = orig_attr(*args, **kwargs)
#                # prevent wrapped_class from becoming unwrapped
#                if result == self.wrapped_class:
#                    return self
#                self.post()
#                return result
#            return hooked
#        else:
#            return orig_attr
#
#    def pre(self):
#        print (">> pre")
#
#    def post(self):
#        print ("<< post")
