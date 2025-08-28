
from datetime import datetime, time, timedelta
from difflib import SequenceMatcher

from DelPackage import DeliveryStatus


def normalize(loc):
    #used to enable pattern matching for distanceMatrix
    substr = loc.lower().split()
    for i, ch in enumerate(substr):
        if ch.isdigit():
            return "".join(substr[i:])
    return "".join(substr)


def calculateDistance(location1, location2, distanceMatrix):
    try:
        #not all two-way combinations exist in matrix, so try each way
        return distanceMatrix[location1][location2]
    except:
        return distanceMatrix[location2][location1]

def assignNextStop(truck, distanceMatrix, hashmap):
            #Find nearest location/package
        keys = distanceMatrix.keys()
        for id, address in truck.unvisited:
            #find fuzzy match
            #trim the beginning of the key for better address matching
            temploc = max(distanceMatrix.keys(), key=lambda x: SequenceMatcher(None, normalize(address), normalize(x)).ratio())
            distance = calculateDistance(truck.location, temploc, distanceMatrix)
            if distance < truck.nearestDistance and ((len(truck.priorityQueue) == 0) or (hashmap.lookup(id)[1].deadline != "EOD")):
                truck.nearestDistance = distance
                truck.nextPackageID = id
                truck.nearestLocation = temploc
        # print(f"Truck has chosen PackageID {truck.nextPackageID} for next delivery at {truck.nearestLocation}, {truck.nearestDistance} away")


def TravelToStop(truck): 
            #Deliver the package
        # print('traveling to stop')
        truck.mileage += truck.nearestDistance
        truck.location = truck.nearestLocation
        truck.clock += timedelta(minutes=int(truck.nearestDistance/truck.mph*100))


#Begin routing
def beginRoute(truck, distanceMatrix, hashmap, endTime=datetime.combine(datetime.today(), time(23, 59, 59))):
    #Convert default location to matching matrix key
    truck.location = max(distanceMatrix.keys(), key=lambda x: SequenceMatcher(None, normalize(truck.location), normalize(x)).ratio())
    flag = True #Used to mark return to home
    startingTime = truck.clock


    #populate unvisited list
    for package in truck.standardQueue + truck.priorityQueue:
        truck.unvisited.append([hashmap.lookup(package)[1].id, hashmap.lookup(package)[1].address])
        # print(f"Truck Package Queue length {len(truck.standardQueue + truck.priorityQueue)}")
    #Start routing algorithm
    while len(truck.unvisited) > 0:
        assignNextStop(truck, distanceMatrix, hashmap)
        if truck.clock + timedelta(minutes=int(truck.nearestDistance/truck.mph*100)) < endTime:
            TravelToStop(truck)
        else:
            break



        hashmap.lookup(truck.nextPackageID)[1].status = DeliveryStatus.DELIVERED
        hashmap.lookup(truck.nextPackageID)[1].timeDelivered = truck.clock
        # print(f"Truck has updated packageID {truck.nextPackageID} to status {hashmap.lookup(truck.nextPackageID)[1].status} at time {truck.clock} with mileage {truck.mileage}")
        if hashmap.lookup(truck.nextPackageID)[1].deadline != "EOD" and truck.nextPackageID != 0:
            deadline = datetime.strptime(hashmap.lookup(truck.nextPackageID)[1].deadline, "%I:%M %p").time()
            deadline = datetime.combine(datetime.today(), deadline)
            print(f"{deadline}, {truck.clock}")
            if truck.clock > deadline:
                print(f"{truck.nextPackageID} was delivered late at {truck.clock}")
                raise Exception("Package missed delivery deadline")
            

        #Remove package from queue. Mark as delivered
        truck.visited.append(truck.nearestLocation)
        #Search through list to find match, then remove from unvisited locations
        for subarr in truck.unvisited:
            if int(subarr[0]) == int(truck.nextPackageID):
                truck.unvisited.remove(subarr)
                # print(f"Location {subarr[1]} removed from unvisited, {truck.visited[len(truck.visited) - 1]} added to visisted")
        #Search for and remove from queues
        for id in truck.standardQueue + truck.priorityQueue:
            if int(id) == int(truck.nextPackageID):
                try: 
                    truck.priorityQueue.remove(int(id))
                    print("Package removed from priorityQueue")
                    print(len(truck.priorityQueue))
                    break
                except:
                    truck.standardQueue.remove(id)
                    # print("Package removed from standardQueue")
                    break
        #Return to Hub after all packages delivered.
        if len(truck.unvisited) == 0 and flag == True:
            truck.unvisited.append([0, "4001 South 700 East, Salt Lake City, UT"])
            flag = False
        #Reset truck.nearestDistance
        truck.nearestDistance = 1000

