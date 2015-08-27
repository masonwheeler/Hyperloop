"""
Original Developer: Jonathan Ward
Purpose of Module: To provide data caching functionality for testing purposes.
Last Modified: 7/16/15
Last Modification Purpose: To clarify naming.
"""

#Standard Modules:
import os
import csv
import json
import cPickle as pickle

#Our Modules:
import config
import util


def create_basefolders():
    """Creates the cache and save folders"""    
    cacheDirectory = config.cwd + "/cache/"
    config.cacheDirectory = cacheDirectory
    if config.useDropbox:
        saveDirectory = config.dropboxDirectory + "/save/"
    else:
        saveDirectory = config.cwd + "/save/"
    config.saveDirectory = saveDirectory
    if not os.path.exists(cacheDirectory):
        os.makedirs(cacheDirectory)       
    if not os.path.exists(saveDirectory):
        os.makedirs(saveDirectory)

def create_workingcachename(start,end):
    """Names the cache folder for a given city pair"""
    workingCacheName = "_".join([start,"to",end])
    config.workingCacheName = workingCacheName
    return workingCacheName

def create_workingsavedirname(start,end):
    """Names the save folder for a given city pair"""
    workingSaveDirName = "_".join([start,"to",end])
    config.workingSaveDirName = workingSaveDirName
    return workingSaveDirName

def create_workingcachedirectory(workingCacheName):
    """Creates the cache folder for a given city pair"""
    workingCacheDirectory = config.cacheDirectory + workingCacheName + "/"
    config.workingCacheDirectory = workingCacheDirectory
    if not os.path.exists(workingCacheDirectory):
        os.makedirs(workingCacheDirectory)
    return workingCacheDirectory

def create_graphsdirectory(workingSaveDirectory):
    """Creates the folder used to save completed routes"""
    graphsDirectory = workingSaveDirectory + "graphs/"
    config.workingGraphsDirectory = graphsDirectory 
    if not os.path.exists(graphsDirectory):
        os.makedirs(graphsDirectory)
    return graphsDirectory

def create_workingsavedirectory(workingSaveDirName):
    """Creates the save directory for a given city pair"""
    workingSaveDirectory = config.saveDirectory + workingSaveDirName + "/"
    create_graphsdirectory(workingSaveDirectory + workingSaveDirName + "_")
    config.workingSaveDirectory = workingSaveDirectory
    if not os.path.exists(workingSaveDirectory):
        os.makedirs(workingSaveDirectory)
    return workingSaveDirectory

def create_necessaryfolders(start, end):
    """Creates all of the cache and save folders"""
    create_basefolders()
    workingCacheName = create_workingcachename(start,end)
    workingSaveDirName = create_workingsavedirname(start,end)
    create_workingcachedirectory(workingCacheName)
    create_workingsavedirectory(workingSaveDirName)

def get_object_cachepath(objectName):
    """Gets the path where the object will be cached"""
    objectFileBase = "_".join([config.workingCacheName, objectName])
    objectFileName = objectFileBase + ".p"
    objectPath = config.workingCacheDirectory + objectFileName
    return objectPath

def get_object_savepath(objectName):
    """Gets the path where the object will be saved"""
    objectFileBase = "_".join([config.workingSaveDirName, objectName])
    objectPath = config.workingSaveDirectory + objectFileBase
    return objectPath

def cache_object(inObject, objectName):
    """Caches the object for future use"""
    objectCachePath = get_object_cachepath(objectName)
    fileHandle = open(objectCachePath, "wb")
    pickle.dump(inObject, fileHandle)
    fileHandle.close()

def load_object(objectName):
    """Loads the cached object"""
    objectCachePath = get_object_cachepath(objectName)
    fileHandle = open(objectCachePath, "rb")
    loadedObject = pickle.load(fileHandle)
    fileHandle.close()
    return loadedObject

def is_object_cached(objectName):
    """Returns a boolean indicating whether the object is cached"""
    objectCachePath = get_object_cachepath(objectName)
    objectCached = os.path.isfile(objectCachePath)
    return objectCached

def is_object_saved(objectName):
    """Returns a boolean indicated whether the object is saved"""
    objectSavePath = get_object_savepath(objectName)
    objectSaved = os.path.isfile(objectSavePath)
    return objectSaved

def get_object(objectName, computeFunction, computeArgs, saveFunction, flag):    
    """Either computes the object or loads a cached version"""
    if (is_object_cached(objectName) and flag):
        print(objectName + " exists.")
        loadedObject = load_object(objectName)
        print("Loaded " + objectName)
        return loadedObject
    else:
        print("Computing " + objectName + "...")
        computedObject = computeFunction(*computeArgs)
        print(objectName + " computed.")
        cache_object(computedObject, objectName)
        saveFunction(computedObject, objectName)
        return computedObject

########## Functions for saving specific datatypes ########## 

def save_list_csv(aList, savePath):        
    with open(savepath + ".csv", 'wb') as listHandle:
        writer = csv.writer(listHandle)
        writer.writerows(aList)       

def save_directions(directionsObject, directionsName):
    pass

def save_spline(splineObject, splineName):
    pass

def save_lattice(latticeObject, latticeName):
    pass

def save_edgessets(edgesSets, edgesName):
    pass

def save_graphs(graphs, graphsName):
    pass

def save_spatial_paths_2d(spatialPaths2d, spatialPaths2dName):
    pass

def save_routes(routes):
    routesDicts = [route.as_dict() for route in routes]
    routesList = {"routes" :  routesDicts}
    savePath = config.dropboxDirectory + "/routes.json"
    with open(savePath, 'w') as filePath:
        json.dump(routesList, filePath)



