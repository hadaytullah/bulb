
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
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math
import random
from scenario import Scenario
from control_home import ControlHome

class AdaptiveHome(ControlHome):

    def __init__(self, w, h):
        super().__init__(w,h)
        self.width_bound = [1, w-2]
        self.height_bound = [1, h-2]
        self.scenario = Scenario()
        #self.presence, self.bulbs = self.scenario.diagonal(self.width, self.height)
        #self.presence, self.bulbs = self.scenario.corners(self.width, self.height)
        self.presence, self.bulbs = self.scenario.corners2(self.height, self.width)
        #self.presence, self.bulbs = self.scenario.stripes(self.width, self.height)

#        self.init_figures()
#        self.fig = plt.figure(figsize=(1, 3))
#
#        self.fig.add_subplot(131)
#        plt.imshow(self.presence, cmap='gray', interpolation='nearest', vmin=0, vmax=1)
#
#        self.fig.add_subplot(132)
#        plt.imshow(self.bulbs, cmap='gray', interpolation='nearest', vmin=-1, vmax=0)
#
#        self.fig.add_subplot(133)
#        self.im = plt.imshow(self.luminosity, cmap='gray', interpolation='bilinear', animated=True, vmin=0, vmax=1)


    def updatefig(self, *args):

        #self.presence = self.scenario.random(self.width, self.height)

        for y in range(self.height):
            for x in range(self.width):
                if self.presence[y,x] > 0:
                    if self.bulbs[y,x] > -1:
                        self.luminosity[y,x] = 1 #random.choice([1,2])
                    else:
                        y_near, x_near = self.strategy_find_near_bulb(y,x)
                        #if x_near > -1 and y_near > -1:
                        self.luminosity[y_near,x_near] = 1 #random.choice([1,2])
                            #print('bulb found near')
                #else:
                #    self.luminosity[x,y] = 0

        self.im.set_data(self.luminosity)
        self.luminosity_im.set_data(self.luminosity_extrapolate(self.luminosity))
        #im.set_cmap("gray")
        #im.update()

        #self.ani.event_source.stop()
        plt.grid()
        plt.grid()


        return self.im, self.luminosity_im

        #im.set_cmap("gray")
        #im.update()
        #print("update called")
        #return self.im,self.luminosity_im

    def luminosity_extrapolate(self, luminosity):
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

    def strategy_find_near_bulb(self, y, x):
        block = ((y-1, x-1), (y, x-1), (y+1,x-1), (y+1, x), (y+1, x+1), (y, x+1), (y-1, x+1), (y-1, x))
        candidate_bulbs = []
        point = [-1, -1]

        for point in block:
            if point[0] in range(self.height) and point[1] in range(self.width):
                if self.bulbs[point[0], point[1]] > -1:
                    candidate_bulbs.append(point)

        if len(candidate_bulbs) > 0:
            point = random.choice(candidate_bulbs)

        print(point)
        return point[0], point[1]

    def run(self):
        #ani = animation.FuncAnimation(self.fig, self.updatefig, interval=50, blit=True)
        self.updatefig()
        plt.show()

