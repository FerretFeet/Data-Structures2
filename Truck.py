from datetime import datetime, time, timedelta

from DelPackage import DeliveryStatus
from helpers import calculateDistance, matchLoc


class Truck:
    startTime = datetime.combine(datetime.today(), time(8,0,0))
    def __init__(self, id, maxcapacity=16):
        self.id = id
        self.status =0 #0 is home, 1 is away
        self.maxcapacity = maxcapacity
        self.mileage = 0
        self.standardQueue = []
        self.priorityQueue = []
        self.curcapacity = 0
        self.location = "Hub"
        self.visited = []
        self.unvisited = []
        self.mph = 18
        self.returnHome = False
        self.deliveredPackages = []
        self.routeSeg = []

        self.nearestDistance = 1000
        self.nearestLocation = None
        self.nextPackageID = None
        self.clock = self.startTime

        
    def _assignPackage(self, delpackageid, queue):
        if self.curcapacity < self.maxcapacity:
            queue.append(delpackageid)
            self.curcapacity +=1
            return queue
        else:
            raise ValueError("This truck cannot hold any more packages")

    def assignPackage(self, delpackageid, isPriority=False):
        if isPriority:
            self._assignPackage(delpackageid, self.priorityQueue)
        else:
            self._assignPackage(delpackageid, self.standardQueue)
    

    def populateUnvisited(self, hashmap, locationTuple):
        #creat a list of tuples with [addr, [list of pkgIDs]]
        self.unvisited=[]

        for pkgID in self.standardQueue + self.priorityQueue:
            pkg = hashmap.lookup(pkgID)[1]
            found = False

            for addr, ids in self.unvisited:
                if matchLoc(addr, locationTuple) == matchLoc(pkg.address, locationTuple):
                    ids.append(pkgID)
                    found = True
            if found == False:
                self.unvisited.append([matchLoc(pkg.address, locationTuple), [pkg.id]]) 



    def assignNextStop(self, distanceMatrix, hashmap, locationTuple):
        #Find nearest location/package
        self.nearestDistance = 1000
        for address, id in self.unvisited:

            temploc = matchLoc(address, locationTuple)
            distance = calculateDistance(self.location, temploc, distanceMatrix)
            #Needed bc ids in array
            isPriority = any(
                hashmap.lookup(pkgID)[1].deadline != "EOD"
                for pkgID in id
            )

            #Ensure standard packages arent delivered before priority
            if distance < self.nearestDistance: 
                if len(self.priorityQueue) == 0 or isPriority:
                    self.nearestDistance = distance
                    self.nextPackageID = id
                    self.nearestLocation = temploc
             


    def travelToStop(self): 

        timeTravelled = timedelta(seconds=self.nearestDistance/self.mph*3600)
        self.mileage += self.nearestDistance

        self.routeSeg.append([timeTravelled, self.nearestDistance])

        self.location = self.nearestLocation
        self.clock += timeTravelled

        #Search through list to find match, then remove from unvisited locations
        for subarr in self.unvisited:
            if (subarr[1]) == (self.nextPackageID):
                self.unvisited.remove(subarr)
                self.visited.append(subarr)
        


    def setHomeNext(self, matchKey):
            self.unvisited.insert(0, [0, matchLoc("hub", matchKey)])
            self.returnHome = True


    def deliverPackage(self, hashmap, id=-1):
        #If not given, set
        if id == -1: 
            id = self.nextPackageID[0]
        
        #Update variables
        hashmap.lookup(id)[1].status = DeliveryStatus.DELIVERED
        hashmap.lookup(id)[1].timeDelivered = self.clock
        self.deliveredPackages.append(id)


        #Check package hasnt missed deadline
        if hashmap.lookup(id)[1].deadline != "EOD" and id != 0: # =0 is go home
            deadline = datetime.strptime(hashmap.lookup(id)[1].deadline, "%I:%M %p").time()
            deadline = datetime.combine(datetime.today(), deadline) 
            if self.clock > deadline:
                raise Exception(f"Package {id} missed delivery deadline")


        #Remove from queue
        for idx in self.standardQueue + self.priorityQueue:
            if int(idx) == int(id):
                try: 
                    self.priorityQueue.remove(id)
                    break
                except:
                    self.standardQueue.remove(id)

                    break



    def deliverPackages(self, hashmap):
        pkgs = None
        for item in self.visited:
            if item[0] == self.location:
                pkgs = item[1]
        for pkgID in pkgs:
            self.deliverPackage(hashmap, pkgID)


    def getMileage(self, statusTime):
    #get mileage at given time
        totalTime = self.startTime
        totalMileage = 0
        type(statusTime)
        if type(statusTime) == datetime.time:
            datetime.combine(datetime.today(), statusTime)
        for rTime, mileage in self.routeSeg:
            if statusTime > totalTime + rTime:
                totalTime += rTime
                totalMileage += mileage
        return totalMileage


#Begin routing
    def beginRoute(self, distanceMatrix, hashmap, locationTuple, endTime=datetime.combine(datetime.today(), time(23, 59, 59))):
        
        #Prepare variables
        self.location = matchLoc(self.location, locationTuple)
        self.populateUnvisited(hashmap, locationTuple)

        #Start routing algorithm
        while len(self.unvisited) > 0:

            self.assignNextStop(distanceMatrix, hashmap, locationTuple) 
            self.travelToStop()
            self.deliverPackages(hashmap)

            #Reset self.nearestDistance
            self.nearestDistance = 1000

        #End Loop

        self.setHomeNext(locationTuple)
        self.travelToStop

        #Empty used variables
        self.visited = []
        self.curcapacity = 0
        