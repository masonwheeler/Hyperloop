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
    workingCacheName = "_".join([start,"to",end])
    config.workingCacheName = workingCacheName
    return workingCacheName

def create_workingsavedirname(start,end):
    workingSaveDirName = "_".join([start,"to",end])
    config.workingSaveDirName = workingSaveDirName
    return workingSaveDirName

def create_workingcachedirectory(workingCacheName):
    workingCacheDirectory = config.cacheDirectory + workingCacheName + "/"
    config.workingCacheDirectory = workingCacheDirectory
    if not os.path.exists(workingCacheDirectory):
        os.makedirs(workingCacheDirectory)
    return workingCacheDirectory

def create_routesdirectory(workingSaveDirectory):
    routesDirectory = workingSaveDirectory + "routes/"
    if not os.path.exists(routesDirectory):
        os.makedirs(routesDirectory)
    return routesDirectory

def create_workingsavedirectory(workingSaveDirName):
    workingSaveDirectory = config.saveDirectory + workingSaveDirName + "/"
    create_routesdirectory(workingSaveDirectory + workingSaveDirName + "_")
    config.workingSaveDirectory = workingSaveDirectory
    if not os.path.exists(workingSaveDirectory):
        os.makedirs(workingSaveDirectory)
    return workingSaveDirectory

def create_necessaryfolders(start, end):
    create_basefolders()
    workingCacheName = create_workingcachename(start,end)
    workingSaveDirName = create_workingsavedirname(start,end)
    create_workingcachedirectory(workingCacheName)
    create_workingsavedirectory(workingSaveDirName)


def get_object_cachepath(objectName):
    objectFileBase = "_".join([config.workingCacheName, objectName])
    objectFileName = objectFileBase + ".p"
    objectPath = config.workingCacheDirectory + objectFileName
    return objectPath

def get_object_savepath(objectName):
    objectFileBase = "_".join([config.workingSaveDirName, objectName])
    objectPath = config.workingSaveDirectory + objectFileBase
    return objectPath

def cache_object(inObject, objectName):
    objectCachePath = get_object_cachepath(objectName)
    fileHandle = open(objectCachePath, "wb")
    pickle.dump(inObject, fileHandle)
    fileHandle.close()

def load_object(objectName):
    objectCachePath = get_object_cachepath(objectName)
    fileHandle = open(objectCachePath, "rb")
    loadedObject = pickle.load(fileHandle)
    fileHandle.close()
    return loadedObject

def object_cached(objectName):
    objectCachePath = get_object_cachepath(objectName)
    objectCached = os.path.isfile(objectCachePath)
    return objectCached

def object_saved(objectName):
    objectSavePath = get_object_savepath(objectName)
    objectSaved = os.path.isfile(objectSavePath)
    return objectSaved

def get_object(objectName, computeFunction, computeArgs, saveFunction, flag):    
    if (object_cached(objectName) and flag):
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


def save_listlike(listObject, listName):    
    listSavePath = get_object_savepath(listName)
    with open(listSavePath + ".csv", 'wb') as listHandle:
        writer = csv.writer(listHandle)
        writer.writerows(listObject)       

def save_directions(directionsObject, directionsName):
    pass

def save_spline(splineObject, splineName):
    pass

def save_lattice(latticeObject, latticeName):
    pass

def save_graphs(graphsObject, graphsName):
    pass

def save_edgessets(edgesSets, edgesName):
    flattenedEdges = util.fast_concat(edgesSets)
    edgeDicts = [edge.as_dict() for edge in flattenedEdges]
    edgesSavePath = get_object_savepath(edgesName)
    with open(edgesSavePath + ".json", 'w') as edgeHandle:
        json.dump(edgeDicts, edgeHandle)

