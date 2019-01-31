
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
import time

class CreativeHome(AdaptiveHome):

    def __init__(self, w, h, awarenesses=[True, True, True, True, True, True], pickle_file='stats.pkl', show_ani=True):
        super().__init__(w,h)
        self.scenario = Scenario()
        self.width_bound = [1, w-1]
        self.height_bound = [1, h-1]
        self.evaluation_unit = 10

        #Enables/Disables EA
        #self.strategy_aware = awarenesses[0]

        self.goal_aware = awarenesses[1] # each goal can be seperately turned on/off
        self.resource_aware = awarenesses[2] #awareness of broken bulbs

        #awarenss of window and its control system
        self.context_aware = awarenesses[3] #window controls system
        self.domain_aware = awarenesses[4] #window gives light



        # time awareness: Pattern detected --> the mid section is always empty
        # Mid section should be ignore in initial population and mutations, it will lead to more efficient strategy generation. it worked! mutate() and generate_individuals() have been updated to reflect this.
        self.time_aware = awarenesses[5]
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

        #if self.strategy_aware:
        self.init_deap()
        #self.init_figures()

        self.show_ani = show_ani
        self.stats = {'fitness': [], 'time': []}
        self.pickle_file = pickle_file
        self.starting_time = time.monotonic()

    #----- Strategy-Awareness -----

    def generate_individual(self,icls):

        luminosity = np.zeros((self.height,self.width))
        #luminosity = np.random.choice([0., 1.], (self.height, self.width))

        for y in range(self.height_bound[0], self.height_bound[1]):
            for x in range(self.width_bound[0], self.width_bound[1]):
                if(self.bulbs[y,x] > -1):
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
        luminosity = self.decode(individual)

        for i in range(self.width):
            x = random.randint(self.width_bound[0], self.width_bound[1])
            y = random.randint(self.height_bound[0], self.height_bound[1])

            if(self.bulbs[y,x] > -1):
                luminosity[y,x] = random.choice([0,1])

        #luminosity = self.encode (luminosity)
        self.update_individual(individual, luminosity)
        if self.time_aware:
            individual = self.apply_mid_section_empty_learning(individual)

        #print("MUTATE_IND", individual)
        return (individual,)

    # Time-Awareness, Mid section is always empty, make strategy awareness (EA) ignore it
    def apply_mid_section_empty_learning(self, individual):
        #print ("INDIVIDUAL",individual)
        luminosity = self.decode(individual)
        hb = self.time_aware_height_bound
        wb = self.time_aware_width_bound
        luminosity[hb[0]:hb[1], wb[0]:wb[1]] = 0

        individual[:] = self.encode(luminosity)
        return individual


    def init_deap(self):
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", np.ndarray, fitness=creator.FitnessMax)
        self.steps = 0
        self.MAX_STEPS = 800
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


    #------------------ goal awareness stuff starts -----------------
    def evaluate_luminosity(self, plan):
        score = 0
        #for selected, bulbs in zip(individual, data):
            #if selected:

        for y in range(self.height): # top left is (X=0,Y=0)
            for x in range(self.width):
                if plan[y, x] > 0:
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
        return float(self.fitness(self.decode(individual))),

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
            fitness += self.evaluate_domain_context(plan)

        return fitness

    def presence_in_radius2(self, radius, x, y, individual):
        # starts from left top
        block = ((y-1, x-1), (y, x-1), (y+1, x-1), (y+1, x), (y+1, x+1), (y, x+1), (y-1, x+1), (y-1, x))

        presence_score = 0

        if self.presence[y,x] > 0:
            presence_score += int(self.weight['present'] * self.evaluation_unit)  # award for presence under the bulb
            #print ('+50')

        for point in block:
            if 0 <= point[0] < self.height and 0 <= point[1] < self.width:
                if self.presence[point[0], point[1]] > 0:
                #and self.bulbs[point[0],point[1]] < 0: #individual[point[0]*self.width+point[1]] < 1:#someone present in radius and that area is dark
                    presence_score += int(0.30 * self.weight['present'] * self.evaluation_unit)

        #pres_num = np.sum(self.presence[y-1:y+2, x-1:x+2] > 0)
        #pres2 = self.presence[y, x] > 0
        #if pres2:
        #    presence_score2 = (pres_num - 1) * int(0.30 * self.weight['present'] * self.evaluation_unit) + \
        #                      int(self.weight['present'] * self.evaluation_unit)
        #else:
        #    presence_score2 = presence_score2 = pres_num * int(0.30 * self.weight['present'] * self.evaluation_unit)

        #if presence_score != presence_score2:
        #    print("HJÄLP!")
        #print(presence_score == presence_score2)

        return presence_score


    def update_individual (self, individual, data):
        individual[:] = data.flatten()

    def encode(self, luminosity):
        return luminosity.flatten()

    def decode(self, individual):
        return individual.reshape((self.width, self.height))

    #------------------ simulation loop ----------------
    def updatefig(self, *args):
        #if self.strategy_aware:
        t = time.monotonic()
        algorithms.eaMuPlusLambda(
                self.pop, self.toolbox,
                400, 100, #parents, children
                0.5, 0.5, #probabilities
                1) #iterations

        top_plan = sorted(self.pop, key=lambda x:x.fitness.values[0])[-1]
        fit = top_plan.fitness.values[0]
        t2 = time.monotonic()
        print('generation:{}, best fitness-: {}, deap_time ({:.3f}s), total_time: ({:.3f}s)'.format(self.steps, fit, t2 - t, t2-self.t_start))

        # Add bookkeeping of needed stats
        self.stats['fitness'].append(fit)
        self.stats['time'].append(t2 - self.starting_time)
        #print("TOP:", top)
        #self.luminosity = self.decode(top)

        # TODO: In a realistic setting, EA will generate bunch of top plans
        # that will be pushed to the plans storage and then MAPE will
        # select the best one at the end of EA. EA could be running in
        # background in a realistic setup, always pushing new plans to the
        # plan storage
        self.plans = [self.decode(top_plan)]

        return super().updatefig(args)
        #return self.im, self.luminosity_im

    #------- domain and context, access window control, use windows --------------
    def luminosity_extrapolate(self, luminosity):

        if self.domain_aware and self.context_aware:
            #add windows as bulbs at the edges of top-left corner
            for y in range(int(self.height * 0.5)): # top left is (X=0,Y=0)
                luminosity[y, 0] = 1
                luminosity[y, 1] = 1

            for x in range(int(self.width * 0.5)):
                luminosity[0, x] = 1
                luminosity[1, x] = 1

        #there must some function doing this interpolation?
        wb = self.width_bound
        hb = self.height_bound
        for y in range(hb[0], hb[1]):
            for x in range(wb[0], wb[1]):
                if self.bulbs[y, x] > -1:
                    if luminosity[y, x] > 0:
                        block = ((y-1, x-1), (y, x-1), (y+1, x-1), (y+1, x), (y+1, x+1), (y, x+1), (y-1, x+1), (y-1, x))
                        for point in block:
                            if wb[0] <= point[1] < wb[1] and hb[0] <= point[0] < hb[1]:
                                luminosity[point[0], point[1]] += 0.15 * luminosity[y, x]
                else:
                    luminosity[y, x] = 0

        return luminosity

    #------- resoruce awareness
    def evaluate_resource(self, plan):
        # probe: luminosity sensors are resources too, may be merge prob-aw into resources. lumisity array is kind of probes
        score = 0
        #for selected, bulbs in zip(individual, data):
            #if selected:
        for y in range(self.height): # top left is (X=0,Y=0)
            for x in range(self.width):
                if plan[y, x] > 0 and self.bulbs[y, x] == -1:
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

    def hof_eq(self, a1, a2):
        if np.any(a1 != a2):
            return False
        return True

    def run(self):
        if self.show_ani:
            self.t_start = time.monotonic()
            super().run()
        else:
            hall_of_fame = tools.HallOfFame(10, self.hof_eq)
            stats = tools.Statistics(key=lambda ind: ind.fitness.values[0])
            stats.register('max', np.max)
            stats.register('avg', np.mean)
            stats.register("std", np.std)
            log_book = algorithms.eaMuPlusLambda(
                self.pop, self.toolbox,
                400, 100,  #parents, children
                0.5, 0.5,  #probabilities
                500,
                stats=stats,
                halloffame=hall_of_fame,
                verbose=True)  #iterations

            #print(log_book)
            top_plan = hall_of_fame[0]
            fit = top_plan.fitness.values[0]
            t2 = time.monotonic()
            print(fit, t2 - self.starting_time)
            self.stats['fitness'] = fit
            self.stats['time'] = t2 - self.starting_time
            self.stats['logbook'] = log_book
