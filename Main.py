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



# def preSort():
#     unevaldPackageIDs = []
#     sortedPackageIDs = []
#     unavailablePackageIDs = []
    
#     unevaldPackageIDs = [i for i in range(TOTAL_PACKAGES)]
#     startingLocation = matchLoc("hub", locationTuple)

#     counter = 0
#     while counter > TOTAL_PACKAGES:
#         #Reset Distance at beginning of each NN search
#         startingDistance = 1000
#         #Initialize extraction variables
#         nextPackageID = None
#         nearestLocation = None

#         for pkgID in unevaldPackageIDs:
#             #Skip if already sorted
#             if pkgID == -1:
#                 continue

#             pkg = hashmap.lookup(pkgID)[1]

#             #Only Sort If At_HUB
#             if pkg.status != DeliveryStatus.AT_HUB:
#                 unevaldPackageIDs[pkgID] = -1
#                 unavailablePackageIDs.append(pkgID)
#                 counter += 1
#                 continue

#             #Calc Distance
#             destination = matchLoc(pkg.address, locationTuple)
#             distance = calculateDistance(startingLocation, destination, distanceMatrix)

#             #Replace if lesser
#             if distance < startingDistance:
#                 nextPackageID = pkgID
#                 nearestLocation = destination

#         #Extract nearest values, then repeat until done
#         print(f"NEXT PACKAGE ID: {nextPackageID}")
#         print(f"unevald packaes = {unevaldPackageIDs}")
#         unevaldPackageIDs[nextPackageID] = -1
#         sortedPackageIDs.append(nextPackageID)
#         startingLocation = nearestLocation
#         counter += 1

#     print("Sorted and unvailable package ids")
#     print(sortedPackageIDs)
#     print(unavailablePackageIDs)
#     return sortedPackageIDs




# def preSort():
#     mepo = Truck(TOTAL_PACKAGES) #Will be using truck methods to order
#     # mepo.location = matchKey(mepo.location, distanceMatrix)
#     mepo.populateUnvisited(hashmap)
#     mepo.location = matchLoc(mepo.location, locationTuple)
#     plist = []
#     counter = 0
#     print(mepo.unvisited)
#     while i < TOTAL_PACKAGES:
#         mepo.assignPackage(i)
    

#     #For Each Unloaded Package, sort
#     while counter < TOTAL_PACKAGES - LOADED_PACKAGES[0]:
#         #Reset Distance
#         mepo.nearestDistance = 1000
#         finalDest = None

#         # mepo.assignNextStop(distanceMatrix, hashmap, locationTuple)
#         for id, address in mepo.unvisited:

#             temploc = matchLoc(address, locationTuple)
#             distance = calculateDistance(mepo.location, temploc, distanceMatrix)
#             #Ensure standard packages arent delivered before priority
#             if distance < mepo.nearestDistance and ((len(mepo.priorityQueue) == 0) or (hashmap.lookup(id)[1].deadline != "EOD")):
#                 mepo.nearestDistance = distance
#                 mepo.nextPackageID = id
#                 mepo.nearestLocation = temploc
#         plist.append(mepo.nextPackageID)
#         counter += 1
            


#         # for key, val in hashmap.data:
#         #     #Ensure package AT_HUB
#         #     if val.status in (DeliveryStatus.DELIVERED, DeliveryStatus.EN_ROUTE, DeliveryStatus.NOT_PREPARED):
#         #         continue
#         #     #Ensure NOT already sorted
#         #     if val.sortedFlag == True:
#         #         continue

#         #     print(f"VAL ID {val.id}")
#         #     print(f"Val Sorted Flag = {val.sortedFlag}")
#         #     #Calc Distance
#         #     print(f"mepo locatoin {mepo.location}")
#         #     dest = matchLoc(val.address, locationTuple)
#         #     print(f"Destination: {dest}")
#         #     distance = calculateDistance(mepo.location, dest, distanceMatrix)
#         #     print(f"Calc'd distance {distance}")
#         #     #Replace if new distance < old distance
#         #     if distance < mepo.nearestDistance:
#         #         mepo.nearestDistance = distance
#         #         mepo.nextPackageID = val.id
#         #         finalDest = dest
#         # #Lowest found, add to list and mark sorted
#         # plist.append(mepo.nextPackageID)
#         # hashmap.lookup(len(plist)-1)[1].sortedFlag = True
#         # mepo.location = finalDest
#         # counter += 1
#         # print(f"Hash Item Marked as Sorted: {hashmap.lookup(len(plist)-1)[1].sortedFlag}")
#         # #Repeat while
#     print(plist)
#     return plist


def updateDelayedPackages(truck):
        #Prevent delayed packages to be assigned until they are available
    #PackageID and time
        for package, time in DELAYED_PACKAGES:
            if hashmap.lookup(package)[1].status != DeliveryStatus.NOT_PREPARED:
                continue
            if (time <= truck.clock):
                #Mark as AT_HUB then proceed to execute function
                hashmap.lookup(package)[1].setStatus(DeliveryStatus.AT_HUB)
                if package == 9:
                    #Update Address
                    hashmap.lookup(package)[1].address = "410 S State St"
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

    # plist = preSort()
    #used to evenly distribute priority packages
    i = 0
    # print(plist)
    for key, pkg in hashmap.data:
        # pkg = hashmap.lookup(pkgId)[1]

        if pkg.status == DeliveryStatus.NOT_PREPARED:
        #Only trucks[0] checked b/c after initial function call
        #trucks length will be 1
            updateDelayedPackages(trucks[0])

        print(pkg.address)
        print(key)
        print(pkg.deadline)

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
            elif i % numTrucks == 1 and trucks[1].status == 0 and len(trucks[1].priorityQueue) < 5:
                assignToTruck(trucks[1], pkg.id)
                flag = True
            elif i % numTrucks == 2 and trucks[2].status == 0 and len(trucks[2].priorityQueue) < 5:
                assignToTruck(trucks[2], pkg.id)
                flag = True
            #If assigned, continue
            if flag == True:
                pkg.setStatus(DeliveryStatus.EN_ROUTE)
                i += 1
                continue

        # All Other Packages go here
        for truck in trucks:
            print("CurTest:")
            print(f"{truck.status}")
            print(f"{truck.curcapacity}")
            if truck.curcapacity + 1 < truck.maxcapacity and truck.status == 0: 
                print(pkg.id)
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
        print(f"truck begin route at {truck.clock} with {truck.standardQueue} and {truck.priorityQueue}")
        truck.beginRoute(distanceMatrix, hashmap, locationTuple)

        print(f"TRUCK FINISHED WITH MILEAGE {truck.mileage} AND TIME {truck.clock}")





    #all trucks loaded once, now reload based off first return
    x = 0
    while LOADED_PACKAGES[0] < TOTAL_PACKAGES:
        print("While loop executing")
        truck = min(trucks, key=lambda t: t.clock)
        if truck.curcapacity == truck.maxcapacity:
            print("Truck Full")
            
        # If Truck is early, wait
        waitTime = datetime.combine(datetime.today(), time(23,59,0))
        print(f"DELAYED PKGS = {DELAYED_PACKAGES}")
        for pkgID, pkgTime in DELAYED_PACKAGES:
            pkg = hashmap.lookup(pkgID)[1]
            if waitTime > pkgTime and pkg.status == DeliveryStatus.NOT_PREPARED:
                waitTime = pkgTime
        if waitTime != datetime.combine(datetime.today(), time(23,59,0)) and waitTime > truck.clock:
            truck.clock = waitTime
        print(waitTime)

        loadTrucks([truck], 1, hashmap, distanceMatrix)
        print(truck.standardQueue + truck.priorityQueue)
        print(f"Truck dispatched at {truck.clock}")
        print(f"truck begin route at {truck.clock} with {truck.standardQueue} and {truck.priorityQueue}")
        truck.beginRoute(distanceMatrix, hashmap, locationTuple, endTime=datetime.combine(datetime.today(), time(10, 15, 0)) if testFlag == True else datetime.combine(datetime.today(), time(23, 59, 0)))
    #     testFlag = False
    #     print("while loop iteration complete")
        print(f"LOADED TOTAL PKGS: {LOADED_PACKAGES[0]}: {TOTAL_PACKAGES}")
        # if x == 3:
        #     break
        # x += 1
        
    print("ALL PACKAGES LOADED")


# loadTrucks(trucks, NUM_TRUCKS, hashmap, distanceMatrix)
# trucks[0].beginRoute(distanceMatrix, hashmap, locationTuple)

# trucks[0].populateUnvisited(hashmap, locationTuple)
# print(trucks[0].unvisited)
# trucks[1].populateUnvisited(hashmap, locationTuple)
# print(trucks[1].unvisited)
# trucks[2].populateUnvisited(hashmap, locationTuple)
# print(trucks[2].unvisited)

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
