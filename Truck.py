from datetime import datetime, time, timedelta

from DelPackage import DeliveryStatus
from helpers import calculateDistance, matchKey


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
        self.returnHome = False

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
    

    def populateUnvisited(self, hashmap):
        self.unvisited=[]
        for package in self.standardQueue + self.priorityQueue:
            self.unvisited.append([hashmap.lookup(package)[1].id, hashmap.lookup(package)[1].address]) 




    def assignNextStop(self, distanceMatrix, hashmap):
                #Find nearest location/package
            keys = distanceMatrix.keys()
            for id, address in self.unvisited:
                #find fuzzy match
                #trim the beginning of the key for better address matching
                temploc = matchKey(address, distanceMatrix)
                distance = calculateDistance(self.location, temploc, distanceMatrix)
                #Ensure standard packages arent delivered before priority
                if distance < self.nearestDistance and ((len(self.priorityQueue) == 0) or (hashmap.lookup(id)[1].deadline != "EOD")):
                    self.nearestDistance = distance
                    self.nextPackageID = id
                    self.nearestLocation = temploc



    def travelToStop(self): 
            #Deliver the package
        # print('traveling to stop')
        self.mileage += self.nearestDistance
        self.location = self.nearestLocation
        self.clock += timedelta(minutes=int(self.nearestDistance/self.mph*100))
        self.visited.append(self.nearestLocation)
        #Search through list to find match, then remove from unvisited locations
        for subarr in self.unvisited:
            if int(subarr[0]) == int(self.nextPackageID):
                self.unvisited.remove(subarr)
        


    def setHomeNext(self):
            self.unvisited.append([0, "4001 South 700 East, Salt Lake City, UT"])
            self.returnHome = True


    def deliverPackage(self, hashmap):
        hashmap.lookup(self.nextPackageID)[1].status = DeliveryStatus.DELIVERED
        hashmap.lookup(self.nextPackageID)[1].timeDelivered = self.clock
        # print(f"self has updated packageID {self.nextPackageID} to status {hashmap.lookup(self.nextPackageID)[1].status} at time {self.clock} with mileage {self.mileage}")
        if hashmap.lookup(self.nextPackageID)[1].deadline != "EOD" and self.nextPackageID != 0: # =0 is go home
            deadline = datetime.strptime(hashmap.lookup(self.nextPackageID)[1].deadline, "%I:%M %p").time()
            deadline = datetime.combine(datetime.today(), deadline)
            if self.clock > deadline:
                print(f"{self.nextPackageID} was delivered late at {self.clock}")
                raise Exception("Package missed delivery deadline")
            for id in self.standardQueue + self.priorityQueue:
                if int(id) == int(self.nextPackageID):
                    try: 
                        self.priorityQueue.remove(id)
                        print("Package removed from priorityQueue")
                        print(len(self.priorityQueue))
                        break
                    except:
                        self.standardQueue.remove(id)
                        break


    # def prepareForNextDelivery():



#Begin routing
    def beginRoute(self, distanceMatrix, hashmap, endTime=datetime.combine(datetime.today(), time(23, 59, 59))):
        self.location = matchKey(self.location, distanceMatrix)
        self.populateUnvisited(hashmap)

        #Start routing algorithm
        while len(self.unvisited) > 0:
            self.assignNextStop(distanceMatrix, hashmap)

            if self.clock + timedelta(minutes=int(self.nearestDistance/self.mph*100)) < endTime:
                self.travelToStop()
            else:
                break

            self.deliverPackage(hashmap)

            #Remove package from queue. Mark as delivered

            #Search for and remove from queues

            #Return to Hub after all packages delivered.
            if len(self.unvisited) == 0 and self.returnHome == False:
                self.setHomeNext()
            #Reset self.nearestDistance
            self.nearestDistance = 1000

