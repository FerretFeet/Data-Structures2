import csv
from datetime import datetime, time
from DelPackage import DeliveryStatus
from DelPackage import DelPackage
from Hashmap import Hashmap
from Truck import Truck
from helpers import calculateDistance, matchKey

##Config Vars
NUM_TRUCKS = 3
TOTAL_PACKAGES = 40
LOADED_PACKAGES = [0]
# TOTAL_PRIORITY_PACKAGES = 14

##Ppackage restrictions
REQUIRE_TRUCK_2 = [3, 18, 36, 38]
GROUPED_PACKAGES = [14, 15, 16, 19, 20]
DELAYED_PACKAGES = [
    [6, datetime.combine(datetime.today(), time(9, 5))],
    [9, datetime.combine(datetime.today(), time(10, 20))],
    [25, datetime.combine(datetime.today(), time(9, 5))],
    [28, datetime.combine(datetime.today(), time(9, 5))],
    [32, datetime.combine(datetime.today(), time(9, 5))]
]

##Initialize objects
trucks = [Truck() for i in range(NUM_TRUCKS)]
hashmap = Hashmap(TOTAL_PACKAGES)
distanceMatrix = {}


##Load Data

#Hashmap
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

#Distance Matrix
with open('WGUPS Distance Table.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    needHeaders = True;
    for idx ,row in enumerate(reader):
        if idx == 0:
            headers = row[2:] #Skip first two columns
            continue

        row_location = row[0]
        distanceMatrix[row_location] = {}

        for i, value in enumerate(row[2:]): #skip first two columns
            if value:
                distanceMatrix[row_location][headers[i]] = float(value)


##helper functions

def preSort():
    mepo = Truck(TOTAL_PACKAGES) #Will be using truck methods to order
    mepo.location = matchKey(mepo.location, distanceMatrix)
    plist = []
    while len(plist) < TOTAL_PACKAGES:
        mepo.nearestDistance = 1000
        for key, val in hashmap.data:
            if val.status in (DeliveryStatus.DELIVERED, DeliveryStatus.EN_ROUTE, DeliveryStatus.NOT_PREPARED):
                continue
            if val.sortedFlag == True:
                continue

            dest = matchKey(val.address, distanceMatrix)
            distance = calculateDistance(mepo.location, dest, distanceMatrix)

            if distance < mepo.nearestDistance:
                mepo.nearestDistance = distance
                mepo.nextPackageID = val.id

        plist.append(mepo.nextPackageID)
        hashmap.lookup(len(plist)-1)[1].sortedFlag = True
    return plist


def updateDelayedPackages(truck):
        #Prevent delayed packages to be assigned until they are available
    #PackageID and time
        for package, time in DELAYED_PACKAGES:
            if (time <= truck.clock):
                #Mark as AT_HUB then proceed to execute function
                hashmap.lookup(package)[1].status = DeliveryStatus.AT_HUB
                if package == 9:
                    #Update Address
                    hashmap.lookup(package)[1].address = "410 S. State St"
                    hashmap.lookup(package)[1].zip = "84111"


def assignToTruck(truck, packageID):
    if truck.curcapacity < truck.maxcapacity:
        if hashmap.lookup(packageID)[1].deadline != "EOD":
            truck.assignPackage(packageID, True)
        else:
            truck.assignPackage(packageID)
        LOADED_PACKAGES[0] += 1
    else:
        print("Truck full")



#Due to complex restrictions, certain packages are loaded to trucks
#Through hard-coding
def loadTrucks(trucks, numTrucks, hashmap, distanceMatrix):

    plist = preSort()
    #used to evenly distribute priority packages
    i = 0

    for key, pkg in hashmap.data:

        if pkg.status == DeliveryStatus.NOT_PREPARED:
        #Only trucks[0] checked b/c after initial function call
        #trucks length will be 1
            updateDelayedPackages(trucks[0])
                
        if pkg.status != DeliveryStatus.AT_HUB:
            continue

        #Hardcoded Restrictions:

        if pkg.id in REQUIRE_TRUCK_2:
            assignToTruck(trucks[1], pkg.id)
            pkg.status = DeliveryStatus.EN_ROUTE
            continue
        
        if pkg.id in GROUPED_PACKAGES:
            assignToTruck(trucks[0], pkg.id)
            pkg.status = DeliveryStatus.EN_ROUTE
            continue

        #Take care of early deadlines
        if pkg.deadline != "EOD":
            flag = False

            if i % numTrucks == 0 and trucks[0].status == 0 and len(trucks[0].priorityQueue) < 5:
                assignToTruck(trucks[0], pkg.id)
                flag = True
            elif i % numTrucks == 1 and trucks[1].status == 0 and len(trucks[1].priorityQueue) < 5:
                assignToTruck(trucks[1], pkg.id)
                flag = True
            elif i % numTrucks == 2 and trucks[2].status == 0 and len(trucks[2].priorityQueue) < 5:
                assignToTruck(trucks[2], pkg.id)
                flag = True
            #If assigned, continue
            if flag == True:
                pkg.status = DeliveryStatus.EN_ROUTE
                i += 1
                continue

        # All Other Packages go here
        for truck in trucks:

            if truck.curcapacity + 1 < truck.maxcapacity and truck.status == 0: 
                assignToTruck(truck, pkg.id)
                break
        
        #if final truck is full, no more package to assign
        if trucks[numTrucks-1].curcapacity == trucks[numTrucks-1].maxcapacity:
            break

        if i == TOTAL_PACKAGES:
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
    loadTrucks(trucks, NUM_TRUCKS, hashmap, distanceMatrix)
    testFlag = True
    for truck in availableTrucks:
        print(f"truck begin route at {truck.clock}")

        print(hashmap.lookup(9)[1].status)
        truck.beginRoute(distanceMatrix, hashmap)

        print(f"####################TRUCK FINISHED WITH MILEAGE {truck.mileage} AND TIME {truck.clock}")
    #all trucks loaded once, now reload based off first return

    while LOADED_PACKAGES[0] < TOTAL_PACKAGES:
        print("While loop executing")
        availableTruck = min(trucks, key=lambda t: t.clock)
        if availableTruck.curcapacity == 0:
            return
        loadTrucks([availableTruck], 1, hashmap, distanceMatrix)
        print(f"Truck dispatched at {truck.clock}")
        availableTruck.beginRoute(distanceMatrix, hashmap, endTime=datetime.combine(datetime.today(), time(10, 15, 0)) if testFlag == True else datetime.combine(datetime.today(), time(23, 59, 0)))
        testFlag = False
        
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
