def partition_list(coordinatesList,partitionLength):
    numPartitions = len(coordinatesList) - partitionLength
    return [coordinatesList[x:x+partitionLength] for x in range(0,numPartitions)]

