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
        self.deliveredPackages = []

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
    

    # def populateUnvisited(self, hashmap):
    #     self.unvisited=[]
    #     for package in self.standardQueue + self.priorityQueue:
    #         self.unvisited.append([hashmap.lookup(package)[1].id, hashmap.lookup(package)[1].address]) 

    def populateUnvisited(self, hashmap, locationTuple):
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
        print(
              "PopulateUnvisited: "
              f"{self.unvisited}"
              )


    def assignNextStop(self, distanceMatrix, hashmap, locationTuple):
        #Find nearest location/package
        self.nearestDistance = 1000
        for address, id in self.unvisited:

            temploc = matchLoc(address, locationTuple)
            distance = calculateDistance(self.location, temploc, distanceMatrix)
            print(f"PRIORITY QUEUE: {len(self.priorityQueue)}: {self.priorityQueue}")
            print(f"Distance: {distance}")
            print(f"PkgID: {id}")
            #Needed bc ids in array
            isPriority = any(
                hashmap.lookup(pkgID)[1].deadline != "EOD"
                for pkgID in id
            )

            #Ensure standard packages arent delivered before priority
            if distance < self.nearestDistance: 
                print(hashmap.lookup(id[0])[1].deadline)
                if len(self.priorityQueue) == 0 or isPriority:
                    self.nearestDistance = distance
                    self.nextPackageID = id
                    self.nearestLocation = temploc
                    print(f"Nearest Package ID: {self.nextPackageID}")
                    print(f"{self.nearestLocation}")
                    print(f"Nearest Distance: {self.nearestDistance}")
             
        print(f"Assigning Next Stop: {self.location} -> {self.nearestLocation}")



    def travelToStop(self): 
        self.mileage += self.nearestDistance
        temp = self.location
        self.location = self.nearestLocation
        self.clock += timedelta(minutes=int(self.nearestDistance/self.mph*60))
        print(
              "TravelToStop:\n"
              f"Mileage: {self.mileage}\n"
              f"Location: {self.location}\n"
              f"Distance: {self.nearestDistance}\n"
              f"Time: {self.clock}\n"
              f"Package: {self.nextPackageID}"
              )
        #Search through list to find match, then remove from unvisited locations
        for subarr in self.unvisited:
            if (subarr[1]) == (self.nextPackageID):
                print("Removing Subarr")
                self.unvisited.remove(subarr)
                self.visited.append(subarr)
        


    def setHomeNext(self, matchKey):
            self.unvisited.insert(0, [0, matchLoc("hub", matchKey)])
            self.returnHome = True


    def deliverPackage(self, hashmap, id=-1):
        #If not given, set
        if id == -1: 
            id = self.nextPackageID
        
        #Update variables
        hashmap.lookup(id)[1].status = DeliveryStatus.DELIVERED
        hashmap.lookup(id)[1].timeDelivered = self.clock
        self.deliveredPackages.append(id)


        if hashmap.lookup(id)[1].deadline != "EOD" and id != 0: # =0 is go home

            #Check package delivered on-time
            deadline = datetime.strptime(hashmap.lookup(id)[1].deadline, "%I:%M %p").time()
            deadline = datetime.combine(datetime.today(), deadline) 
            if self.clock > deadline:
                raise Exception(f"Package {id} missed delivery deadline")
            
            #Remove from queue
        for idx in self.standardQueue + self.priorityQueue:
            if int(idx) == int(id):
                try: 
                    self.priorityQueue.remove(id)
                    print("Removed from priority queue")
                    break
                except:
                    self.standardQueue.remove(id)
                    print("Removed from standard queue")

                    break
        print(f"Package Delivered: {id}")


    # def prepareForNextDelivery():


    def deliverPackages(self, hashmap, locationTuple):
        pkgs = None
        for item in self.visited:
            if item[0] == self.location:
                pkgs = item[1]
                print(f"Deliver Pkgs {pkgs}")
        for pkgID in pkgs:
            print(pkgID)
            self.deliverPackage(hashmap, pkgID)


#Begin routing
    def beginRoute(self, distanceMatrix, hashmap, locationTuple, endTime=datetime.combine(datetime.today(), time(23, 59, 59))):
        self.location = matchLoc(self.location, locationTuple)

        # self.populateUnvisited(hashmap)
        self.populateUnvisited(hashmap, locationTuple)

        #Start routing algorithm
        while len(self.unvisited) > 0:

            self.assignNextStop(distanceMatrix, hashmap, locationTuple)
            
            # if self.clock + timedelta(minutes=int(self.nearestDistance/self.mph*60)) < endTime:
            self.travelToStop()
            # else:
            #     break


            # if self.location == matchKey("4001 South 700 East, Salt Lake City, UT", distanceMatrix):
            # if self.location == matchLoc("Hub", locationTuple):
            #     self.nearestDistance = 1000
            #     break

            self.deliverPackages(hashmap, locationTuple)

            #Reset self.nearestDistance
            self.nearestDistance = 1000

        print("Going Home")
        print(
            f"CurLocation: {self.location}"
            f"Unvisited: {len(self.unvisited)} {self.unvisited}\n"
            f"Packages left: {self.priorityQueue + self.standardQueue}"
        )
        self.setHomeNext(locationTuple)
        self.travelToStop
        self.visited = []
        self.curcapacity = 0
        