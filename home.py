#from scenario import Scenario
import numpy as np

class Home:
    def __init__(self, w, h):
        self.width = w
        self.height = h
        
        #self.scenario = Scenario()
        
        #self.room = np.zeros((self.width,self.height))
        #self.environment = np.zeros((self.width,self.height))
        self.bulbs = np.zeros((self.width,self.height))
        self.luminosity = np.zeros((self.width,self.height))
        self.presence = np.zeros((self.width,self.height))
    
    def control(self):
        pass
            