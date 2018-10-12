import numpy as np
import math 
import random

class Scenario:
    #def __init__(self):
        
    def diagonal(self, w, h):
        presence = np.zeros((h, w)) #np.random.randint(2, size=(self.width,self.height))
        bulbs = np.zeros((h, w))
        x=0
        for y in range(h):
            presence [y,x] = 1
            bulbs [y,x] = random.choice([-1,0]) #-1 means out of order
            x += 1
        return presence, bulbs
    
    def stripes(self, w, h):
        presence = np.zeros((h, w)) #np.random.randint(2, size=(self.width,self.height))
        bulbs = np.zeros((h, w))
        points = [[ math.floor(h*0.25), math.floor(w*0.25)], [math.floor(h*0.75), math.floor(w*0.25)], [math.floor(h*0.25), math.floor(w*0.75)],[math.floor(h*0.75), math.floor(w*0.75)]]

        bulbs[points[0]] = -1

        for point in points:
            presence [point] = 1

        return presence, bulbs

    def corners(self, w, h):
        presence = np.zeros((h, w)) #np.random.randint(2, size=(self.width,self.height))
        bulbs = np.zeros((h, w))
        points = [ [math.floor(h*0.25), math.floor(w*0.25)], [math.floor(h*0.75), math.floor(w*0.25)], [math.floor(h*0.25), math.floor(w*0.75)],[math.floor(h*0.75), math.floor(w*0.75)]]

        bulbs[tuple(points[0])] = -1

        for point in points:
            presence [tuple(point)] = 1

        return presence, bulbs

    def corners2(self, w, h):
        presence = np.zeros((h, w)) #np.random.randint(2, size=(self.width,self.height))
        bulbs = np.zeros((h, w))
        points = np.array([ [math.floor(h*0.25), math.floor(w*0.25)], [math.floor(h*0.75), math.floor(w*0.25)], [math.floor(h*0.25), math.floor(w*0.75)],[math.floor(h*0.75), math.floor(w*0.75)]])

        #bulbs[tuple(points[0])] = -1

        slash = np.array([[1,1],[0,0],[-1,-1]])
        circle = np.array([[-1,-1],[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0]])*2
        line = np.array([[-1,0],[0,0],[1,0]])
        cross = np.array([[-1,-1],[0,-1],[1,-1],[0,0],[0,1]])

        point = points[3]
        for k in slash:
            presence [tuple(point+k)] = 1
            #bulbs[tuple(point+k)] = -1

        point = points[1]
        for k in circle:
            presence [tuple(point+k)] = 1
            bulbs[tuple(point+k)] = -1

        point = points[2]
        for k in line:
            presence [tuple(point+k)] = 1
            #bulbs[tuple(point+k)] = -1

        point = points[0]
        for k in cross:
            presence [tuple(point+k)] = 1
            bulbs[tuple(point+k)] = -1

        return presence, bulbs

    def random (self, w, h):
        presence = np.zeros((h, w)) #np.random.randint(2, size=(self.width,self.height))
        for i in range(math.floor(w/2)):
            x = random.randint(0,w-1)
            y = random.randint(0,h-1)
            presence [y,x] = 1
        return presence

    def extreme(self, w, h):
        presence = np.zeros((h, w)) #np.random.randint(2, size=(self.width,self.height))
        bulbs = np.zeros((h, w))

        bulbs[2:5,2:w-2] = -1
        bulbs[h-5:h-2,2:w-2] = -1
        bulbs[5:8, int(w/2)-1:int(w/2)+2] = -1
        bulbs[h-8:h-5, int(w/2)-1:int(w/2)+2] = -1

        presence[3,4:w-4] = 1
        presence[h-4,4:w-4] = 1
        presence[5:7, int(w/2)] = 1
        presence[h-7:h-5, int(w/2)] = 1

        return presence, bulbs
