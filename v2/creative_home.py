
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
from v2.adaptive_home import AdaptiveHome
#from v2.home import Home

class CreativeHome(AdaptiveHome):

    def __init__(self, w, h):
        super().__init__(w,h)
        self.scenario = Scenario()
        self.width_bound = [1, w-1]
        self.height_bound = [1, h-1]
        self.evaluation_unit = 10

        #Enables/Disables EA
        self.strategy_aware = True

        self.goal_aware = True # each goal can be seperately turned on/off
        self.resource_aware = True #awareness of broken bulbs

        #awarenss of window and its control system
        self.context_aware = True #window controls system
        self.domain_aware = True #window gives light



        # time awareness: Pattern detected --> the mid section is always empty
        # Mid section should be ignore in initial population and mutations, it will lead to more efficient strategy generation. it worked! mutate() and generate_individuals() have been updated to reflect this.
        self.time_aware = True
        self.time_aware_width_bound = [0, self.width]
        self.time_aware_height_bound = [int(self.height*0.35), int(self.width*0.65)]

        # hypothesis:?

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

        self.weight = {
            'present':6.0, #luminosity
            'cost':4.0,
            'penalty_broken_bulb':12.0,
            'context':3.5
            #time:

        }
        #self.presence, self.bulbs = self.scenario.diagonal(self.width, self.height)
        #self.presence, self.bulbs = self.scenario.stripes(self.width, self.height)
        #self.presence, self.bulbs = self.scenario.corners(self.width, self.height)
        self.presence, self.bulbs = self.scenario.corners2(self.width, self.height)
        #self.presence, self.bulbs = self.scenario.extreme(self.width, self.height)

        if self.strategy_aware:
            self.init_deap()
        #self.init_figures()

    #----- Strategy-Awareness -----

    def generate_individual(self,icls):

        luminosity = np.zeros((self.height,self.width))

        for y in range(self.height_bound[0], self.height_bound[1]):
            for x in range(self.width_bound[0], self.width_bound[1]):
                luminosity[y,x] = random.choice([0,1])
                #print ('mutating')

        genome = self.encode(luminosity)
        individual = icls(genome)
        # Time-Awareness, Code Injection into Strategy-Awareness
        # Time awareness detected a pattern, the mid section is always empty and therefore should remain untouched
        if self.time_aware:
            individual = self.apply_mid_section_empty_learning(individual)

        return individual

    def mutate(self, individual):
        #print('Mutating')
        #print('Mutating')
        luminosity = self.decode(individual)

        for i in range(self.width):
            x = random.randint(self.width_bound[0], self.width_bound[1])
            y = random.randint(self.height_bound[0], self.height_bound[1])

            if(self.bulbs[y,x] > -1):
                luminosity[y,x] = random.choice([0,1])

        #luminosity = self.encode (luminosity)
        self.update_individual(individual, luminosity)
        #for i in range(self.width):
        #    individual[random.randint(0,len(individual)-1)] = random.choice([0,1])
        #return (individual,)

        #individual = super().mutate(individual)[0]
        #print("Before Mutate ", individual)
        if self.time_aware:
            individual = self.apply_mid_section_empty_learning(individual)

        #print("MUTATE_IND", individual)
        return (individual,)

    # Time-Awareness, Mid section is always empty, make strategy awareness (EA) ignore it
    def apply_mid_section_empty_learning(self, individual):
        #print ("INDIVIDUAL",individual)
        luminosity = self.decode(individual)
        #print("LUMINOSITY", luminosity)
        for y in range(self.time_aware_height_bound[0], self.time_aware_height_bound[1]):
            for x in range(self.time_aware_width_bound[0], self.time_aware_width_bound[1]):
                luminosity[y,x] = 0
        self.update_individual(individual, luminosity)
        #print("UPDATED IND", individual)
        return individual

#    def generate_individual(self,icls):
#        luminosity = np.zeros((self.height,self.width))
#
#        for y in range(self.height_bound[0], self.height_bound[1]):
#            for x in range(self.width_bound[0], self.width_bound[1]):
#                luminosity[y,x] = random.choice([0,1])
#                #print ('mutating')
#
#        genome = self.encode(luminosity)
#        return icls(genome)

    def init_deap(self):
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)
        self.steps = 0
        self.MAX_STEPS = 500
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
        self.toolbox.register("evaluate", self.fitness_ea)
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

    #------------------ goal awareness stuff starts -----------------
    def evaluate_luminosity(self, plan):
        score = 0
        #for selected, bulbs in zip(individual, data):
            #if selected:
        for y in range(self.height): # top left is (X=0,Y=0)
            for x in range(self.width):

                if plan[y,x]>0:
                    #if self.presence_in_radius(1, x, y):
                    presence_score = self.presence_in_radius2(1, x, y, plan)
                    #if self.bulbs[x,y] > -1 and presence_score > 0:
                    #if presence_score > 0:
                    score += presence_score
                    #else:
                        #penalty for using a broken bulb
                    #    score -= int( self.weight['penalty_broken_bulb'] * 1)
        return score


    def evaluate_cost(self, plan):
        cost_score = 0
        #for selected, bulbs in zip(individual, data):
            #if selected:
        for y in range(self.height): # top left is (X=0,Y=0)
            for x in range(self.width):
                if plan[y,x] > 0 and self.bulbs[y,x] > -1:
                    #presence_score = self.presence_in_radius2(1, x, y, individual)
                    #if presence_score is 0:
                    cost_score += int(self.weight['cost'] * self.evaluation_unit)
        return cost_score

    # ------- main fitness function -------

    def fitness_ea(self, individual):
        return (float(self.fitness(self.decode(individual))),)

    def fitness(self, plan):
        #print('goal based fitness')
        fitness = 0

        if self.goal_aware:
            for goal_name, goal in self.goals.items():
                if goal['enabled']:
                    if goal['maximize']:
                        fitness = fitness + goal['evaluate'](plan)
                    else:
                        fitness = fitness - goal['evaluate'](plan)
        #else:
        #    fitness += super().fitness(individual)[0]

        if self.resource_aware:
            fitness += self.evaluate_resource(plan)

        if self.domain_aware and self.context_aware:
            fitness += self.evaluate_domain_context (plan)


        return fitness

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
#                    if self.bulbs[y,x] > -1 and presence_score > 0:
#                        score += presence_score
#                    else:
#                        score -= 1 #penalty for using a broken bulb
#        return (float(score),)


    def presence_in_radius2 (self, radius, x, y, individual):
        block = ((y-1, x-1), (y, x-1), (y+1,x-1), (y+1, x), (y+1, x+1), (y, x+1), (y-1, x+1), (y-1, x)) # starts from left top

        presence_score = 0

        if self.presence[y,x] > 0:
            presence_score += int(self.weight['present'] * self.evaluation_unit) #award for presence under the bulb
            #print ('+50')

        for point in block:
            if point[0] in range(self.height) and point[1] in range(self.width):
                if self.presence[point[0], point[1]] > 0:
                #and self.bulbs[point[0],point[1]] < 0: #individual[point[0]*self.width+point[1]] < 1:#someone present in radius and that area is dark
                    presence_score += int(0.30 * self.weight['present'] * self.evaluation_unit)

        return presence_score


#    def mutate(self, individual):
#        #print('Mutating')
#        luminosity = self.decode(individual)
#
#        for i in range(self.width):
#            x = random.randint(self.width_bound[0], self.width_bound[1])
#            y = random.randint(self.height_bound[0], self.height_bound[1])
#
#            if(self.bulbs[y,x] > -1):
#                luminosity[y,x] = random.choice([0,1])
#
#        #luminosity = self.encode (luminosity)
#        self.update_individual(individual, luminosity)
#        #for i in range(self.width):
#        #    individual[random.randint(0,len(individual)-1)] = random.choice([0,1])
#        return (individual,)

    def update_individual (self, individual, data):
        for y in range(self.height):
            for x in range(self.width):
                individual[y*self.width+x] = data[y,x]

    def encode(self, luminosity):
        return luminosity.flatten()

    def decode(self, individual):
        plan = np.zeros((self.height, self.width))
        for y in range(self.height): # top left is (X=0,Y=0)
            for x in range(self.width):
                plan[y,x] = individual[y*self.width+x]
        return plan #np.reshape(individual, (-1, self.width))

    #------------------ simulation loop ----------------
    def updatefig(self, *args):
        if self.strategy_aware:
            algorithms.eaMuPlusLambda (
                    self.pop, self.toolbox,
                    400, 100, #parents, children
                    0.5, 0.5, #probabilities
                    1) #iterations

            top_plan = sorted(self.pop, key=lambda x:x.fitness.values[0])[-1]
            fit = top_plan.fitness.values[0]
            print ('generation:{}, best fitness-: {}'.format(self.steps, fit))
            #print("TOP:", top)
            #self.luminosity = self.decode(top)

            # TODO: In a realistic setting, EA will generate bunch of top plans
            # that will be pushed to the plans storage and then MAPE will
            # select the best one at the end of EA. EA could be running in
            # background in a realistic setup, always pushing new plans to the
            # plan storage
            self.plans = [self.decode(top_plan)]

#        #print("DRAW:",self.luminosity)
#        self.im.set_data(self.luminosity)
#        #self.im.set_array(self.luminosity)
#        #self.im.set_facecolors(self.luminosity)
#
#
#        self.luminosity_im.set_data(self.luminosity_extrapolate(self.luminosity))
#        #im.set_cmap("gray")
#        #im.update()
#        self.steps += 1
#        if self.steps > self.MAX_STEPS:
#            self.ani.event_source.stop()
#            plt.grid()
#            plt.grid()


        return super().updatefig(args)
        #return self.im, self.luminosity_im

    #------- domain and context, access window control, use windows --------------
    def luminosity_extrapolate(self, luminosity):

        if self.domain_aware and self.context_aware:
            #add windows as bulbs at the edges of top-left corner
            for y in range(int(self.height*0.5)): # top left is (X=0,Y=0)
                luminosity[y,0] = 1
                luminosity[y,1] = 1

            for x in range(int(self.width*0.5)):
                luminosity[0,x] = 1
                luminosity[1,x] = 1

        #there must some function doing this interpolation?
        for y in range(self.height_bound[0], self.height_bound[1]):
            for x in range(self.width_bound[0], self.width_bound[1]):
                if self.bulbs[y,x] > -1:
                    if luminosity[y,x] > 0:
                        block = ((y-1, x-1), (y, x-1), (y+1,x-1), (y+1, x), (y+1, x+1), (y, x+1), (y-1, x+1), (y-1, x))
                        for point in block:
                            if point[1] in range(self.width_bound[0], self.width_bound[1]) and point[0] in range(self.height_bound[0], self.height_bound[1]):
                                luminosity[point[0],point[1]] += 0.15*luminosity[y,x]
                else:
                    luminosity[y,x] = 0

        return luminosity

    #------- resoruce awareness
    def evaluate_resource(self, plan):
        # probe: luminosity sensors are resources too, may be merge prob-aw into resources. lumisity array is kind of probes
        score = 0
        #for selected, bulbs in zip(individual, data):
            #if selected:
        for y in range(self.height): # top left is (X=0,Y=0)
            for x in range(self.width):
                if plan[y,x] > 0 and self.bulbs[y,x] == -1:
                    score += int(self.weight['penalty_broken_bulb'] * self.evaluation_unit)
        #penalty, -1 makes it reduce the fitness of individuals using broken bulbs
        return -1*score

    def evaluate_domain_context(self, plan):
        #domain: windows are source of light
        #context: windows can be controlled for light
        # assumption: one quarter of the space can be lit with windows there, left-top here
        score = 0
        for y in range(self.height): # top left is (X=0,Y=0)
            for x in range(self.width):
                if x < int(0.5*self.width) and y < int(0.5*self.height): #left-top area
                    if plan[y,x] > 0:
                        score += int(self.weight['context'] * self.evaluation_unit)

        #penalty for using bulbs in near window lit area
        return -1*score


    #def run(self):
    #    self.ani = animation.FuncAnimation(self.fig, self.updatefig, interval=50, blit=True)
    #    plt.show()
    #---------------------- awareness ---------------------
    #def awareness_step(self):
        # context: interaction with windows controller
        # resource: luminosity sensors, bulbs broken/working, bulb intensity high/low = radius
        # domain: windows are source of light
        # goal : power saving + luminosity
        # probe: luminosity sensors
        # strategy,
        # enactor
        # time
        # hypothesis



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
