from difflib import SequenceMatcher


# def normalize(loc):
#     #used to enable pattern matching for distanceMatrix
#     substr = loc.lower().split()
#     for i, ch in enumerate(substr):
#         if ch.isdigit():
#             return "".join(substr[i:])
#     return "".join(substr)

def normalize(loc):
    return loc.lower().strip()


def calculateDistance(location1, location2, distanceMatrix):
    print(f"CALC DISTANCE: {location1}, {location2}")
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
        # if loc == normalize(tloc[0]):
        #     return normalize(tloc[1])
    return loc


def matchKey(item, matrix):
    # print(f"MatchKey Item{item}")
    return max(matrix.keys(), key=lambda x: SequenceMatcher(None, normalize(item), normalize(x)).ratio())