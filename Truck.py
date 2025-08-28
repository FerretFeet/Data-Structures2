from datetime import datetime, time, timedelta
from difflib import get_close_matches

from DelPackage import DeliveryStatus


class Truck:
    def __init__(self, maxcapacity=16):
        self.status =0 #0 is home, 1 is away
        self.maxcapacity = maxcapacity;
        self.mileage = 0;
        self.standardQueue = [];
        self.priorityQueue = [];
        self.curcapacity = 0
        self.location = "4001 South 700 East, Salt Lake City, UT"
        self.visited = []
        self.unvisited = []
        self.mph = 18

        self.nearestDistance = 1000
        self.nearestLocation = None
        self.nextPackageID = None
        self.clock = datetime.combine(datetime.today(), time(8,0,0))

        
    def _assignPackage(self, delpackageid, queue):
        if self.curcapacity < self.maxcapacity:
            queue.append(delpackageid)
            self.curcapacity +=1
            return queue
        else:
            raise ValueError("This truck cannot hold any more packages")

    def assignPackage(self, delpackageid):
        self._assignPackage(delpackageid, self.standardQueue)

    
    def assignPriorityPackage(self, delpackageid):
        self._assignPackage(delpackageid, self.priorityQueue)
    
    def chooseNextStop(self, distanceMatrix, hashmap):
        #Find nearest location
        keys = distanceMatrix.keys()

        for id, address in self.unvisited:
            #find fuzzy match
            temploc = get_close_matches(address, keys, n=1)
            distance = distanceMatrix[self.location][temploc]
            if distance < self.nearestDistance & ((len(self.priorityQueue) == 0) or (hashmap.lookup(id).deadline != "EOD")):
                self.nearestDistance = distance
                self.nextPackage = id
                self.nextLocation = temploc


    def travelToNextStop(self):
        self.mileage += self.nearestDistance
        self.clock += timedelta(minutes=int(self.nearestDistance/self.mph))

