from datetime import datetime, time, timedelta

from DelPackage import DeliveryStatus
from helpers import calculateDistance, matchLoc


class Truck:
    def __init__(self, maxcapacity=16):
        self.status =0 #0 is home, 1 is away
        self.maxcapacity = maxcapacity;
        self.mileage = 0;
        self.standardQueue = [];
        self.priorityQueue = [];
        self.curcapacity = 0
        self.location = "Hub"
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

    def assignPackage(self, delpackageid, isPriority=False):
        if isPriority:
            self._assignPackage(delpackageid, self.priorityQueue)
        else:
            self._assignPackage(delpackageid, self.standardQueue)

    
    def assignPriorityPackage(self, delpackageid):
        self._assignPackage(delpackageid, self.priorityQueue)
    

    def populateUnvisited(self, hashmap):
        self.unvisited=[]
        for package in self.standardQueue + self.priorityQueue:
            self.unvisited.append([hashmap.lookup(package)[1].id, hashmap.lookup(package)[1].address]) 




    def assignNextStop(self, distanceMatrix, hashmap, locationTuple):
        #Find nearest location/package
        for id, address in self.unvisited:
            #find fuzzy match
            #trim the beginning of the key for better address matching
            # temploc = matchKey(address, distanceMatrix)
            print(f"Looking for next stop to assign. Current Loc: {self.location}, Potential match = {address}")
            temploc = matchLoc(address, locationTuple)
            print(f"TEMPLOC created as {temploc}")
            distance = calculateDistance(self.location, temploc, distanceMatrix)
            #Ensure standard packages arent delivered before priority
            if distance < self.nearestDistance and ((len(self.priorityQueue) == 0) or (hashmap.lookup(id)[1].deadline != "EOD")):
                self.nearestDistance = distance
                self.nextPackageID = id
                self.nearestLocation = temploc
                return id



    def travelToStop(self): 
        print(f"Traveling To Next Stop {self.nearestLocation}, From {self.location}")
            #Deliver the package
        # print('traveling to stop')
        self.mileage += self.nearestDistance
        self.location = self.nearestLocation
        self.clock += timedelta(minutes=int(self.nearestDistance/self.mph*60))
        self.visited.append(self.nearestLocation)
        #Search through list to find match, then remove from unvisited locations
        for subarr in self.unvisited:
            if int(subarr[0]) == int(self.nextPackageID):
                self.unvisited.remove(subarr)
        


    def setHomeNext(self, matchKey):
            self.unvisited.insert(0, [0, matchLoc("hub", matchKey)])
            self.returnHome = True


    def deliverPackage(self, hashmap, id=-1):
        if id == -1: 
            id = self.nextPackageID
        
        hashmap.lookup(id)[1].status = DeliveryStatus.DELIVERED
        hashmap.lookup(id)[1].timeDelivered = self.clock

        if hashmap.lookup(id)[1].deadline != "EOD" and id != 0: # =0 is go home
            
            #Check package delivered on-time
            deadline = datetime.strptime(hashmap.lookup(id)[1].deadline, "%I:%M %p").time()
            deadline = datetime.combine(datetime.today(), deadline) 
            if self.clock > deadline:
                print(f"{id} was delivered late at {self.clock}")
                raise Exception("Package missed delivery deadline")
            
            #Remove from queue
        for id in self.standardQueue + self.priorityQueue:
            if int(id) == int(id):
                try: 
                    self.priorityQueue.remove(id)
                    print("Package removed from priorityQueue: ")
                    print(len(self.priorityQueue))
                    break
                except:
                    self.standardQueue.remove(id)
                    break


    # def prepareForNextDelivery():



#Begin routing
    def beginRoute(self, distanceMatrix, hashmap, locationTuple, endTime=datetime.combine(datetime.today(), time(23, 59, 59))):
        # self.location = matchKey(self.location, distanceMatrix)
        self.location = matchLoc(self.location, locationTuple)
        print(f"TruckLoc: {self.location} PACKAGES: {self.priorityQueue}, {self.standardQueue}")

        self.populateUnvisited(hashmap)

        #Start routing algorithm
        while len(self.unvisited) > 0:
            self.assignNextStop(distanceMatrix, hashmap, locationTuple)
            

            if self.clock + timedelta(minutes=int(self.nearestDistance/self.mph*60)) < endTime:
                self.travelToStop()
            # else:
            #     break


            # if self.location == matchKey("4001 South 700 East, Salt Lake City, UT", distanceMatrix):
            if self.location == matchLoc("Hub", locationTuple):
                self.nearestDistance = 1000
                break

            self.deliverPackage(hashmap)
            deliverHere =  [pkg for pkg in self.unvisited if hashmap.lookup(pkg[0])[1].address == self.location]
            for id in deliverHere:
                self.deliverPackage(hashmap, id)
            #Remove package from queue. Mark as delivered

            #Search for and remove from queues

            #Return to Hub after all packages delivered.
            if len(self.unvisited) == 0 and self.returnHome == False:
                self.setHomeNext(locationTuple)
            #Reset self.nearestDistance
            self.nearestDistance = 1000

