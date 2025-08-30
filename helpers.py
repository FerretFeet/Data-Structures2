from difflib import SequenceMatcher


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
    



def matchKey(item, matrix):
    # print(f"MatchKey Item{item}")
    return max(matrix.keys(), key=lambda x: SequenceMatcher(None, normalize(item), normalize(x)).ratio())