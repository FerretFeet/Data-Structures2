#WGU Student ID: 005662260

import csv
from datetime import datetime, time
from DelPackage import DeliveryStatus
from DelPackage import DelPackage
from Hashmap import Hashmap
from Truck import Truck
from helpers import calculateDistance, matchLoc, normalize

##Config Vars
NUM_TRUCKS = 3
TOTAL_PACKAGES = 40
LOADED_PACKAGES = [0]


##Package restrictions
REQUIRE_TRUCK_2 = [3, 18, 36, 38]
GROUPED_PACKAGES = [13, 14, 15, 16, 19, 20]
DELAYED_PACKAGES = [
    [6, datetime.combine(datetime.today(), time(9, 5))],
    [9, datetime.combine(datetime.today(), time(10, 20))],
    [25, datetime.combine(datetime.today(), time(9, 5))],
    [28, datetime.combine(datetime.today(), time(9, 5))],
    [32, datetime.combine(datetime.today(), time(9, 5))]
]

##Initialize objects
trucks = [Truck(i+1) for i in range(NUM_TRUCKS)]
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
        hashmap.lookup(packageID)[1].truckAssigned = truck.id
    else:
        print("Truck full")


def getTruckStatus(truckID, statusTime=datetime.combine(datetime.today(), time(23,59,0))):
        
        temp = trucks[truckID - 1].getMileage(statusTime)
        print(f"Truck {truckID} Mileage at {statusTime}: {temp}")

def getAllTruckStatus(statusTime):
    for truck in trucks:
        getTruckStatus(truck.id, statusTime)


def getPkgStatus(pkgID, statusTime=datetime.combine(datetime.today(), time(23,59,0))):
    #If earlier than delayedTime
    pkg = hashmap.lookup(pkgID)[1]
    if pkg.delayedTime and statusTime < pkg.delayedTime:
        print(f"Package {pkg.id} \t Address: {pkg.address} \t Status: {DeliveryStatus.NOT_PREPARED.name} with dedline {pkg.deadline}")
        return

    #if earlier than load time
    if statusTime < pkg.timeLoaded:
        print(f"Package {pkg.id} \t Address: {pkg.address} \t Status: {DeliveryStatus.AT_HUB.name} with deadline {pkg.deadline}")
        return

    #if earlier than deliver time
    if statusTime < pkg.timeDelivered:
        print(f"Package {pkg.id} \t Address: {pkg.address} \t  Status: {DeliveryStatus.EN_ROUTE.name} on Truck {pkg.truckAssigned} since {pkg.timeLoaded} with deadline {pkg.deadline}")
        return

    #if after deliver time
    if statusTime >= pkg.timeDelivered:
        print(f"Package {pkg.id} \t Address: {pkg.address} \t  Status: {DeliveryStatus.DELIVERED.name} by Truck {pkg.truckAssigned} at {pkg.timeDelivered} with a deadline of {pkg.deadline}")
        return

    else:
        raise Exception("Pkg Status not able to be retrieved")
    

def getAllPkgStatus(statusTime):
    for id, pkg in hashmap.data:
        getPkgStatus(id, statusTime)

def getStatusAll(testTime=datetime.combine(datetime.today(), time(23,59,0))):
    #Get package status and truck mileage at time
    getAllTruckStatus(testTime)
    
    
    getAllPkgStatus(testTime)




def promptGetStatus():
    while True:
        #Choose truck or package
        print("Get Truck Mileage or Package Status at Requested Time")
        print("(For truck status, enter t. For package status, enter p)")
        print("q to quit")
        selection = normalize(input())

        #prompt for next input
        if selection == "t":
            print(f"Enter a valid truck id, or 'a' for all trucks")
            print(*range(1, len(trucks)+1))
            print("q to quit")
        
        if selection == "p":
            print("Enter a valid package id or 'a' for all packages")
            print(*range(hashmap.length))
            print("q to quit")

        if selection == "q":
            return
        
        #Choose ID
        chosenID = normalize(input())
        if chosenID == "q":
            return
        chosenID = int(chosenID)

        #Prompt for time
        print("Enter a valid time")
        print("(hh,mm,ss)")
        print("q to quit")

        requestedTime = input()
        if requestedTime == "q":
            return
        
        #format time
        substr = requestedTime.split(",")
        formattedTime = datetime.combine(datetime.today(), time(int(substr[0]), int(substr[1]), int(substr[2])))

        #return request
        if selection == "p":
            if normalize(chosenID) == 'a':
                getAllPkgStatus(formattedTime)
            if (chosenID > hashmap.length):
                print("Invalid package ID given")
                continue
            getPkgStatus(chosenID, formattedTime)
            continue
        if selection == "t":
            if normalize(chosenID) == 'a':
                getAllTruckStatus(formattedTime)
            if chosenID > len(trucks):
                print("Invalid truck id")
                continue
            getTruckStatus(chosenID, formattedTime)
            continue
        print("Invalid value entered")



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


        #Hardcoded Restrictions first:

        if int(pkg.id) in REQUIRE_TRUCK_2:
            print("TRUCK2 PKGS")
            assignToTruck(trucks[1], pkg.id)
            pkg.setStatus(DeliveryStatus.EN_ROUTE)
            hashmap.lookup(pkg.id)[1].timeLoaded = trucks[1].clock
            continue
        
        if int(pkg.id) in GROUPED_PACKAGES:
            print("GROUPED PKGS")
            assignToTruck(trucks[0], pkg.id)
            pkg.setStatus(DeliveryStatus.EN_ROUTE)
            hashmap.lookup(pkg.id)[1].timeLoaded = trucks[0].clock
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

    #All avail pkgs loaded to all avail trucks
    loadTrucks(trucks, NUM_TRUCKS, hashmap, distanceMatrix)

    #Deliver packages
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

getStatusAll()



testTimes = [
    datetime.combine(datetime.today(), time(8, 5, 0)),
    datetime.combine(datetime.today(), time(10, 12, 0)),
    datetime.combine(datetime.today(), time(12,54,0))
]



for testTime in testTimes:
    getStatusAll(testTime)


# promptGetStatus()

