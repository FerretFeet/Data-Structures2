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

def updateDelayedPackages(truck):
        #Prevent delayed packages to be assigned until they are available
    #PackageID and time
        for packageID, time in DELAYED_PACKAGES:
            pkg = hashmap.lookup(packageID)[1]
            if pkg.delayedTime == None:
                pkg.delayedTime = time

            if pkg.status != DeliveryStatus.NOT_PREPARED:
                continue
            if (time <= truck.clock):
                #Mark as AT_HUB then proceed to execute function
                pkg.setStatus(DeliveryStatus.AT_HUB)
                if packageID == 9:
                    #Update Address
                    pkg.address = "410 S State St"
                    pkg.zip = "84111"


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

    #used to evenly distribute priority packages
    i = 0
    for key, pkg in hashmap.data:
        # pkg = hashmap.lookup(pkgId)[1]

        if pkg.status == DeliveryStatus.NOT_PREPARED:
        #Only trucks[0] checked b/c after initial function call
        #trucks length will be 1
            updateDelayedPackages(trucks[0])


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
            #If assigned, continue
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




# def getStatus(trucks, hashmap, curTime=time(23, 59, 0)):

        
def beginDay():

    availableTrucks = trucks.copy()
    loadTrucks(trucks, NUM_TRUCKS, hashmap, distanceMatrix)
    testFlag = True
    for truck in availableTrucks:
        truck.beginRoute(distanceMatrix, hashmap, locationTuple)






    #all trucks loaded once, now reload based off first return
    x = 0
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

        loadTrucks([truck], 1, hashmap, distanceMatrix)

        truck.beginRoute(distanceMatrix, hashmap, locationTuple, endTime=datetime.combine(datetime.today(), time(10, 15, 0)) if testFlag == True else datetime.combine(datetime.today(), time(23, 59, 0)))
  
        




beginDay()

# getStatus(trucks, hashmap)

# trucks[0].getStatus(datetime.combine(datetime.today() ,time(9,0,0)))
# trucks[0].getStatus(datetime.combine(datetime.today() ,time(10,12,0)))


testTimes = [
    datetime.combine(datetime.today(), time(8, 5, 0)),
    datetime.combine(datetime.today(), time(10, 12, 0)),
    datetime.combine(datetime.today(), time(12,54,0))
]
def getStatus(testTime):
    # fullTime = datetime.combine(datetime.today() + timedelta(testTime))
    for truck in trucks:
        temp = truck.getMileage(testTime)
        print(f"Truck Mileage at {testTime}: {temp}")
    
    # getStatus(trucks, hashmap, testTime)
    
    #print pkg data
    for id, pkg in hashmap.data:
        if pkg.delayedTime and testTime < pkg.delayedTime:
            print(f"Package {pkg.id} Status: {DeliveryStatus.NOT_PREPARED.name}")
            continue


        if testTime < pkg.timeLoaded:
            print(f"Package {pkg.id} Status: {DeliveryStatus.AT_HUB.name}")
            continue

        if testTime < pkg.timeDelivered:
            print(f"Package {pkg.id} Status: {DeliveryStatus.EN_ROUTE.name}")
            continue

        if testTime > pkg.timeDelivered:
            print(f"Package {pkg.id} Status: {DeliveryStatus.DELIVERED.name}")
            continue 

        else:
            raise Exception("Pkg Status not able to be retrieved")



def promptGetStatus():
    print("Get Truck and Package Status at Requested Time")
    print("(Input Format hh,mm,ss)")
    requestedTime = input()
    substr = requestedTime.split(",")
    formattedTime = datetime.combine(datetime.today(), time(int(substr[0]), int(substr[1]), int(substr[2])))
    getStatus(formattedTime)



for testTime in testTimes:
    getStatus(testTime)


promptGetStatus()

# getStatus(trucks, hashmap, testTime)
