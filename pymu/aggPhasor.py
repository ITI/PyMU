# # # # # # # #
# Meant to provide a quick look up mechanism 
# but chose to go a different route
# # # # # # # #

from pmuEnum import *
import math
import random
from datetime import datetime
from time import *
from calendar import timegm

class AggPhasor:

    def __init__(self, theName, theUnit):
 
        self.name = theName
        self.unit = Unit[theUnit.upper()].name

        self.samples = {}
        self.numOfSamples = 0

        self.totVal = 0.0
        self.avgVal = 0.0
        self.maxVal = [0.0, -9999999999.0, 0.0]
        self.minVal = [0.0, 9999999999.0, 0.0]

        self.totRad = 0.0
        self.avgRad = 0.0
        self.maxRad = [0.0, -9999999999.0, 0.0]
        self.minRad = [0.0, 9999999999.0, 0.0]

        self.begin = 0.0
        self.end = 0.0 

    # # # # # #
    # Adds a sample to the samples array and update statistics
    # Angle always in radians
    # # # # # #
    def addSample(self, time, value, radians):
        print(self.name, "Time:", "{:.4f}".format(time), "Val:", value, "Rad:", radians)
        print(self)
        self.samples[round(time, 4)] = [value, radians]
        for t in sorted(list(self.samples.keys())):
                print("{:.4f}".format(t), ": ", self.samples[t], sep="")
        self.updateResults(time, value, radians)

    # # # # # #
    # Updates statistics incrementally based on new values
    # # # # # #
    def updateResults(self, time, val, rad):
#        numOfSamples = len(self.samples.keys())
        self.numOfSamples = self.numOfSamples + 1
        self.totVal = self.totVal + val 
        self.avgVal = self.totVal / self.numOfSamples 
        self.maxVal = [time, val, rad] if val > self.maxVal[1] else self.maxVal
        self.minVal = [time, val, rad] if val < self.minVal[1] else self.minVal

        self.totRad = self.totRad + rad 
        self.avgRad = self.totRad / self.numOfSamples 
        self.maxRad = [time, val, rad] if rad > self.maxRad[2] else self.maxRad
        self.minRad = [time, val, rad] if rad < self.minRad[2] else self.minRad
        
        self.begin = time if time < self.begin or self.begin == 0 else self.begin
        self.end = time if time > self.end else self.end
            
    # # # # # #
    # Returns array of samples received in the last X milliseconds
    # # # # # #
    def lastSamplesMS(self, numOfMS):
        lastSamples = []
        now = mktime(gmtime())
        for s in self.samples.keys():
            if now - s < numOfMS:
                lastSamples.append(self.samples[s])
        
        return lastSamples

    # # # # # #
    # Returns the sample nearest to the timestamp passed in
    # # # # # #
    def sampleNearest(self, desiredTimeUTC):
        diff = list(self.samples.keys())[-1] 
        closestSample = self.samples[diff]
        closestTime = 0
        for s in self.samples.keys():
            newDiff = abs(desiredTimeUTC - s)    
            if newDiff < diff:
                diff = newDiff
                closestTime = s
                closestSample = self.samples[s]
        
        return closestTime, closestSample 

    # # # # # #
    # Prints all stats in a somewhat formal manner
    # # # # # #
    def printResults(self):
        print("*****", self.name, "*****")
        print("Units:", self.unit)
        print("Start: ", datetime.fromtimestamp(int(self.begin)).strftime('%Y/%m/%d %H:%M:%S'), str(self.begin - int(self.begin))[1:5], sep="")
        print("End: ", datetime.fromtimestamp(self.end).strftime('%Y/%m/%d %H:%M:%S'), str(self.end - int(self.end))[1:5], sep="")
        print("Total Samples:", len(self.samples))
        print("Duration:", round(self.end - self.begin, 4), "seconds")
        print("Samples/Sec:", round(len(self.samples)/(self.end - self.begin), 4)) if (self.end != self.begin) else None
        print("--- --- --- --- ---")
        #print("Tot Val =", self.totVal)
        print("Avg Val =", self.avgVal)
        print("Min Val =", self.minVal)
        print("Max Val =", self.maxVal)
        print("Avg Rad = ", self.avgRad, " (", round(math.degrees(float(self.avgRad)), 4), " deg)", sep="")
        print("Min Rad =", self.minRad)
        print("Max Rad =", self.maxRad)
        #for t in sorted(list(self.samples.keys())):
         #       print("{:.4f}".format(t), ": ", self.samples[t], sep="")
        print("*****")
