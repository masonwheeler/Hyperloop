import config

def sample_coords(coordinatesList):
    return coordinatesList[::config.Nth]

def partition_list(coordinatesList,partitionLength):
    numPartitions = len(coordinatesList) - partitionLength
    return [coordinatesList[x:x+partitionLength] for x in range(0,numPartitions)]

def coords_to_partitions(coordinatesList,partitionLength):
    return partition_list(sample_coords(coordinatesList),partitionLength)
