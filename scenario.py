import numpy as np
import math 
import random

class Scenario:
    #def __init__(self):
        
    def diagonal(self, w, h):
        presence = np.zeros((w, h)) #np.random.randint(2, size=(self.width,self.height))
        bulbs = np.zeros((w, h))
        for i in range(w):
            presence [i,i] = 1
            bulbs [i,i] = random.choice([-1,0]) #-1 means out of order
        return presence, bulbs
    
    def stripes(self, w, h):
        presence = np.zeros((w, h)) #np.random.randint(2, size=(self.width,self.height))
        bulbs = np.zeros((w, h))
        points = [ [math.floor(w*0.25), math.floor(h*0.25)], [math.floor(w*0.25), math.floor(h*0.75)], [math.floor(w*0.75), math.floor(h*0.25)],[math.floor(w*0.75), math.floor(h*0.75)]]

        bulbs[points[0]] = -1

        for point in points:
            presence [point] = 1

        return presence, bulbs

    def corners(self, w, h):
        presence = np.zeros((w, h)) #np.random.randint(2, size=(self.width,self.height))
        bulbs = np.zeros((w, h))
        points = [ [math.floor(w*0.25), math.floor(h*0.25)], [math.floor(w*0.25), math.floor(h*0.75)], [math.floor(w*0.75), math.floor(h*0.25)],[math.floor(w*0.75), math.floor(h*0.75)]]

        bulbs[tuple(points[0])] = -1

        for point in points:
            presence [tuple(point)] = 1

        return presence, bulbs

    def corners2(self, w, h):
        presence = np.zeros((w, h)) #np.random.randint(2, size=(self.width,self.height))
        bulbs = np.zeros((w, h))
        points = np.array([ [math.floor(w*0.25), math.floor(h*0.25)], [math.floor(w*0.25), math.floor(h*0.75)], [math.floor(w*0.75), math.floor(h*0.25)],[math.floor(w*0.75), math.floor(h*0.75)]])

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
        presence = np.zeros((w, h)) #np.random.randint(2, size=(self.width,self.height))
        for i in range(math.floor(w/2)):
            x = random.randint(0,w-1)
            y = random.randint(0,h-1)
            presence [x,y] = 1
        return presence

