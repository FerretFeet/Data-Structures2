import csv
from datetime import datetime, time, timedelta
from difflib import SequenceMatcher, get_close_matches
from DelPackage import DeliveryStatus
from DelPackage import DelPackage
from Hashmap import Hashmap
from Route import beginRoute
from Truck import Truck

## Prepare data and objects
#Initialize trucks
numTrucks = 3
trucks = [Truck() for i in range(numTrucks)]

#Initialize the hashmap
hashmap = Hashmap(40)
totalPackages = 40
#packages loaded is in a list so it can be passed by ref
packagesLoaded = [0]
#Import data using files from WGU, converted to CSV files
#Insert into hashmap
with open('WGUPS_Package_File.csv', newline='') as csvfile:
    packageList = csv.DictReader(csvfile)
    for row in packageList:
        status = DeliveryStatus.AT_HUB
        #Packages 6,9,25,28,32 are awaiting arrival at the depot or
        # awaiting updated information
        if int(row["Package ID"]) in [6,9,25,28,32]:
            status = DeliveryStatus.NOT_PREPARED

        hashmap.insert(int(row["Package ID"]), DelPackage(
            row["Package ID"], 
            row["Address"],
            row["City"],
            row["Zip"],
            row["Weight KILO"],
            row["Special Notes"],
            row["Delivery Deadline"],
            status
    
        ))

#Create the Distance Matrix using files from WGU
distanceMatrix = {}
with open('WGUPS Distance Table.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    #First row is locations
    needHeaders = True;
    for row in reader:
        if needHeaders == True:
            headers = row[2:] #Skip first two columns
            needHeaders = False
            continue

        row_location = row[0]
        distanceMatrix[row_location] = {}
        i = 0
        for value in row[2:]: #skip first to columns
            if not value: #Value is empty, skip
                continue;
            
            distanceMatrix[row_location][headers[i]] = float(value)
            i += 1



#Assign packages to truck
#Due to complex restrictions, certain packages are loaded to trucks
#Through hard-coding
def loadTrucks(trucks, numTrucks, hashmap, counter):

    for i, val in enumerate(hashmap.data):
        key = val[0]
        value = val[1]


    #Prevent delayed packages to be assigned until they are available
        delayedPackages = [[6, datetime.combine(datetime.today(), time(9, 5, 0))],[9, datetime.combine(datetime.today(), time(10, 20, 0))],[25, datetime.combine(datetime.today(), time(9, 5, 0))],[28, datetime.combine(datetime.today(), time(9, 5, 0))],[32, datetime.combine(datetime.today(), time(9, 5, 0))]]
        if value.status == DeliveryStatus.NOT_PREPARED:
            for package in delayedPackages:
                
                if (package[1] <= trucks[0].clock):
                    hashmap.lookup(package[0])[1].status = DeliveryStatus.AT_HUB
                    if package[0] == 9:
                        value.address = "410 S. State St"
                        value.zip = "84111"
                        print(hashmap.lookup(9)[1].address)

        #If not as hub, skip
        if value.status != DeliveryStatus.AT_HUB:
            continue


        #Take care of early deadlines
        if value.deadline != "EOD":
            try:
                if i % numTrucks == 0 and trucks[0].status == 0:
                    trucks[0].assignPriorityPackage(key)
                elif i % numTrucks == 1 and trucks[1].status == 0:
                    trucks[1].assignPriorityPackage(key)
                elif i % numTrucks == 2 and trucks[2].status == 0:
                    trucks[2].assignPriorityPackage(key)
            except ValueError:
                #As implemented, if Truck 3 is full, all trucks will be full.
                #So only truck 3 check is necessary
                if trucks[numTrucks-1].curcapacity >= trucks[numTrucks-1].maxcapacity and trucks[numTrucks -1].status == 0:
                    break #if truck 3 is full, all trucks are full
                trucks[2].assignPriorityPackage(key)
            finally:
                value.status = DeliveryStatus.EN_ROUTE
                i += 1
                counter[0] += 1
                continue


        # Packages which must be on a certain truck or delivered
        # With other certain packages will be hardcoded here
        #PackageIDs 3, 18, 36, and 38 must be on truck 2
        requireTruck2 = [3, 18, 36, 38]
        if value.id in requireTruck2:
            trucks[1].assignPackage(value.id)
            value.status = DeliveryStatus.EN_ROUTE
            counter[0] += 1
            continue
        
        #Packages 14,15,16,19, and 20 must be delivered together
        groupedTogether = [14, 15, 16, 19, 20]
        if value.id in groupedTogether:
            trucks[0].assignPackage(value.id)
            value.status = DeliveryStatus.EN_ROUTE
            counter[0] += 1
            continue

        #if a package is not caught by any previous checks
        #simply assign it to the first available truck
        #after initial priority route is sent
        for truck in trucks:

            if truck.curcapacity >= truck.maxcapacity and truck.status == 0 or truck.clock == datetime.combine(datetime.today(), time(8, 0, 0)): #available
                continue
            truck.assignPackage(value.id)
            counter[0] += 1
            break
        
        #if final truck is full, no more package to assign
        if trucks[numTrucks-1].curcapacity == trucks[numTrucks-1].maxcapacity:
            break

        if i == totalPackages:
            break

def getStatus(trucks, hashmap, curTime=time(23, 59, 0)):
    i=0
    print(f"Status at time {curTime}")
    for truck in trucks:
        i +=1
        print(f"Truck {i} has {truck.mileage} miles driven")
    for key, package in hashmap.data:
        print(f"PackageID {package.id} has status {package.status.name}, {package.timeDelivered}")
        
def beginDay():
    availableTrucks = trucks.copy()
    loadTrucks(trucks, numTrucks, hashmap, packagesLoaded)

    for truck in availableTrucks:
        print(truck.standardQueue)
        print(truck.priorityQueue)
        beginRoute(trucks[0], distanceMatrix, hashmap)
        beginRoute(trucks[1], distanceMatrix, hashmap)
        print(hashmap.lookup(9)[1].status)

        print(f"####################TRUCK FINISHED WITH MILEAGE {truck.mileage} AND TIME {truck.clock}")
    #all trucks loaded once, now reload based off first return

    while totalPackages > packagesLoaded[0]:
        print("While loop executing")
        availableTruck = min(trucks, key=lambda t: t.clock)
        loadTrucks([availableTruck], 1, hashmap, packagesLoaded)
        print(f"Truck dispatched at {truck.clock}")
        beginRoute(availableTruck, distanceMatrix, hashmap)
        
    print("ALL PACKAGES LOADED")



beginDay()

getStatus(trucks, hashmap)

# testTimes = [
#     datetime.combine(datetime.today(), time(9, 0, 0)),
#     datetime.combine(datetime.today(), time(10, 12, 0)),
#     datetime.combine(datetime.today(), time(12,54,0))
# ]

# for testTime in testTimes:
#     # fullTime = datetime.combine(datetime.today() + timedelta(testTime))
#     for truck in trucks:
#         beginRoute(truck, distanceMatrix, hashmap, testTime)
#     getStatus(trucks, hashmap, testTime)


# getStatus(trucks, hashmap, testTime)
