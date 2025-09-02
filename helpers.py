from difflib import SequenceMatcher

def normalize(uglyString):
    return uglyString.lower().strip()


def calculateDistance(location1, location2, distanceMatrix):
    try:
        #not all two-way combinations exist in matrix, so try each way
        return distanceMatrix[location1][location2]
    except:
        return distanceMatrix[location2][location1]
    

def matchLoc(loc, matchTuple):
    loc = normalize(loc)
    for tloc in matchTuple:
        if loc == normalize(tloc[1]):
            return normalize(tloc[0])
    #if not found, return given loc
    return loc
