import config

def sample_list(inList):
    return inList[::config.Nth]

def group_list(inList,groupSize):
    numGroups = len(inList) - groupSize
    return [coordinatesList[x:x+partitionLength] for x in range(0,numGroups)]

def coords_to_groups(coordinatesList,groupSize):
    return group_list(sample_list(coordinatesList),groupSize)
