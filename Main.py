import csv
from datetime import datetime, time
from DelPackage import DeliveryStatus
from DelPackage import DelPackage
from Hashmap import Hashmap
from Truck import Truck
from helpers import calculateDistance, matchKey, matchLoc, normalize

##Config Vars
NUM_TRUCKS = 3
TOTAL_PACKAGES = 40
LOADED_PACKAGES = [0]


##Package restrictions
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
locationTuple = []


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
            normalize(row["Address"]),
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

        rowLocation = normalize(row[0])
        distanceMatrix[rowLocation] = {}
        rowLocationMatch = normalize(row[1].split("(")[0].strip())
        locationTuple.append([rowLocation, rowLocationMatch])
        for i, value in enumerate(row[2:]): #skip first two columns
            if value:
                distanceMatrix[rowLocation][normalize(headers[i])] = float(value)


##helper functions

def updateDelayedPackages(truckTime):
    #Prevent delayed packages to be assigned until they are available
    for packageID, time in DELAYED_PACKAGES:
        pkg = hashmap.lookup(packageID)[1]
        if pkg.delayedTime == None:
            pkg.delayedTime = time

        if pkg.status != DeliveryStatus.NOT_PREPARED:
            continue
        if (time <= truckTime):
            #Mark as AT_HUB then proceed to execute function
            pkg.setStatus(DeliveryStatus.AT_HUB)
            if packageID == 9:
                #Update Address
                pkg.address = "410 S State St"
                pkg.zip = "84111"


def assignToTruck(truck, packageID):
    #Ensure there is space, then assign package with/without priority
    if truck.curcapacity < truck.maxcapacity:
        if hashmap.lookup(packageID)[1].deadline != "EOD":
            truck.assignPackage(packageID, True)
        else:
            truck.assignPackage(packageID)
        LOADED_PACKAGES[0] += 1
    else:
        print("Truck full")



def getStatus(testTime):
    #Get package status and truck mileage at time
    for truck in trucks:
        temp = truck.getMileage(testTime)
        print(f"Truck Mileage at {testTime}: {temp}")
    
    
    #print pkg data
    for id, pkg in hashmap.data:
        #If earlier than delayedTime
        if pkg.delayedTime and testTime < pkg.delayedTime:
            print(f"Package {pkg.id} Status: {DeliveryStatus.NOT_PREPARED.name}")
            continue

        #if earlier than load time
        if testTime < pkg.timeLoaded:
            print(f"Package {pkg.id} Status: {DeliveryStatus.AT_HUB.name}")
            continue

        #if earlier than deliver time
        if testTime < pkg.timeDelivered:
            print(f"Package {pkg.id} Status: {DeliveryStatus.EN_ROUTE.name}")
            continue

        #if after deliver time
        if testTime >= pkg.timeDelivered:
            print(f"Package {pkg.id} Status: {DeliveryStatus.DELIVERED.name}")
            continue 

        else:
            raise Exception("Pkg Status not able to be retrieved")



def promptGetStatus():
    while True:
        print("Get Truck and Package Status at Requested Time")
        print("(Input Format hh,mm,ss. q to quit)")
        requestedTime = input()
        if requestedTime == "q":
            return
        substr = requestedTime.split(",")
        formattedTime = datetime.combine(datetime.today(), time(int(substr[0]), int(substr[1]), int(substr[2])))
        getStatus(formattedTime)


#Due to complex restrictions, certain packages are loaded to trucks
#Through hard-coding
def loadTrucks(trucks, numTrucks, hashmap, distanceMatrix):

    #used to evenly distribute priority packages
    #incremented seperately from for loop
    i = 0

    for key, pkg in hashmap.data:

        if pkg.status == DeliveryStatus.NOT_PREPARED:
            #Only uses first truck clock
            #if multiple trucks are passed to loadTrucks, they
            #  SHOULD have the same clock time.
            updateDelayedPackages(trucks[0].clock)

        #Skip if not at hub
        if pkg.status != DeliveryStatus.AT_HUB:
            continue


        #Hardcoded Restrictions:

        if pkg.id in REQUIRE_TRUCK_2:
            assignToTruck(trucks[1], pkg.id)
            pkg.setStatus(DeliveryStatus.EN_ROUTE)
            continue
        
        if pkg.id in GROUPED_PACKAGES:
            assignToTruck(trucks[0], pkg.id)
            pkg.setStatus(DeliveryStatus.EN_ROUTE)
            continue

        #Take care of early deadlines
        if pkg.deadline != "EOD":
            flag = False

            if i % numTrucks == 0 and trucks[0].status == 0 and len(trucks[0].priorityQueue) < 5:
                assignToTruck(trucks[0], pkg.id)
                flag = True
                hashmap.lookup(pkg.id)[1].timeLoaded = trucks[0].clock
            elif i % numTrucks == 1 and trucks[1].status == 0 and len(trucks[1].priorityQueue) < 5:
                assignToTruck(trucks[1], pkg.id)
                flag = True
                hashmap.lookup(pkg.id)[1].timeLoaded = trucks[1].clock
            elif i % numTrucks == 2 and trucks[2].status == 0 and len(trucks[2].priorityQueue) < 5:
                assignToTruck(trucks[2], pkg.id)
                hashmap.lookup(pkg.id)[1].timeLoaded = trucks[2].clock
                flag = True

            #If assigned, update and continue
            if flag == True:
                pkg.setStatus(DeliveryStatus.EN_ROUTE)
                i += 1
                continue


        # All Other Packages go here
        for truck in trucks:
            if truck.curcapacity + 1 < truck.maxcapacity and truck.status == 0: 
                assignToTruck(truck, pkg.id)
                hashmap.lookup(pkg.id)[1].timeLoaded = truck.clock
                break
        
        #if final truck is full, no more package to assign
        if trucks[numTrucks-1].curcapacity == trucks[numTrucks-1].maxcapacity:
            break

        if i == TOTAL_PACKAGES:
            break





        
def beginDay():
    #Main Function

    loadTrucks(trucks, NUM_TRUCKS, hashmap, distanceMatrix)
    for truck in trucks:
        truck.beginRoute(distanceMatrix, hashmap, locationTuple)

    #all trucks loaded once, now reload based off first return
    while LOADED_PACKAGES[0] < TOTAL_PACKAGES:
        #Get earliest truck
        truck = min(trucks, key=lambda t: t.clock)
            
        # If Truck is early, wait
        waitTime = datetime.combine(datetime.today(), time(23,59,0))
        for pkgID, pkgTime in DELAYED_PACKAGES:
            pkg = hashmap.lookup(pkgID)[1]
            if waitTime > pkgTime and pkg.status == DeliveryStatus.NOT_PREPARED:
                waitTime = pkgTime
        if waitTime != datetime.combine(datetime.today(), time(23,59,0)) and waitTime > truck.clock:
            truck.clock = waitTime

        #Load and deliver
        loadTrucks([truck], 1, hashmap, distanceMatrix)
        truck.beginRoute(distanceMatrix, hashmap, locationTuple)
  
        




beginDay()





testTimes = [
    datetime.combine(datetime.today(), time(8, 5, 0)),
    datetime.combine(datetime.today(), time(10, 12, 0)),
    datetime.combine(datetime.today(), time(12,54,0))
]



for testTime in testTimes:
    getStatus(testTime)


promptGetStatus()

# getStatus(trucks, hashmap, testTime)
