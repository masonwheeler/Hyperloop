import config

def sample_list(inList):
    return inList[::config.Nth]

def group_list(inList,groupSize):
    numGroups = len(inList) - groupSize
    return [inList[x:x+groupSize] for x in range(0,numGroups)]

def group_coords(coordinatesList,groupSize):
    return group_list(sample_list(coordinatesList),groupSize)
