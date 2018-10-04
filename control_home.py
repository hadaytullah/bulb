
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
from home import Home

class ControlHome(Home):
    
    def __init__(self, w, h):
        super().__init__(w,h)
        self.scenario = Scenario()
        #self.presence, self.bulbs = self.scenario.diagonal(self.width, self.height)
        self.presence, self.bulbs = self.scenario.corners(self.width, self.height)
         
        
        self.fig = plt.figure(figsize=(1, 2))

        self.fig.add_subplot(121)
        plt.imshow(self.presence, cmap='gray', interpolation='nearest', vmin=0, vmax=1)

        self.fig.add_subplot(122)
        self.im = plt.imshow(self.luminosity, cmap='gray', interpolation='bilinear', animated=True, vmin=0, vmax=2)
        
        
    def updatefig(self, *args):
        
        #self.presence = self.scenario.random(self.width, self.height)
        
        for y in range(self.height):
            for x in range(self.width):
                if self.presence[x,y] > 0:
                    if self.bulbs[x,y] > -1:
                        self.luminosity[x,y] = random.choice([1,2])
                else:
                    self.luminosity[x,y] = 0
        
        self.im.set_data(self.luminosity)
        #im.set_cmap("gray")
        #im.update()
        print("update called")
        return self.im,
    
    def run(self):
        ani = animation.FuncAnimation(self.fig, self.updatefig, interval=50, blit=True)
        plt.show()

