import os
import csv
import cPickle as pickle

import config
import util


def create_basefolders():
    cacheDirectory = config.cwd + "/cache/"
    config.cacheDirectory = cacheDirectory
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

def create_workingsavedirectory(workingSaveDirName):
    workingSaveDirectory = config.saveDirectory + workingSaveDirName + "/"
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
    objectPath = config.workingSaveDirectory + objectFileBase + ".csv"
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

def get_object(objectName, computeFunction, computeArgs, saveFunction):    
    if (object_saved(objectName) and object_cached(objectName)):
        print(objectName + " exists.")
        loadedObject = load_object(objectName)
        return loadedObject
    else:
        print(objectName + " computed.")
        computedObject = computeFunction(*computeArgs)
        cache_object(computedObject, objectName)
        saveFunction(computedObject, objectName)
        return computedObject


def save_listlike(inList, listName):    
    listSavePath = get_object_savepath(listName)
    with open(listSavePath, 'wb') as listHandle:
        writer = csv.writer(listHandle)
        writer.writerows(inList)        

def get_pointcoords(point, coordsType):
    coords = eval(".".join(["point", coordsType]))
    return coords

def save_latticelike(inLattice, latticeName, coordsType):
    flatLattice = util.fast_concat(inLattice)
    latticeCoords = [get_pointcoords(point,coordsType) for point in flatLattice]
    latticeSavePath = get_object_savepath(latticeName)
    with open(latticeSavePath, 'wb') as latticeHandle:
        writer = csv.writer(latticeHandle)
        writer.writerows(inLattice)        

def save_baselattice(baseLattice, objectName):
    lattice, envelope = baseLattice
    save_latticelike(lattice, objectName, "latticeCoords")

def save_lnglatlattice(lnglatLattice, objectName):
    save_latticelike(lnglatLattice, objectName, "latlngCoords")
    save_latticelike(lnglatLattice, "xyLattice", "xyCoords")

def save_rightofwaylattice(rightofwayLattice, objectName):
    latticeSavePath = get_object_savepath(objectName)
    open(latticeSavePath, 'wb').close()        
    

def get_edgecoords(edge, coordsType):
    coordsPair = eval(".".join(["edge", coordsType]))
    coords = util.fast_concat(coordsPair)
    return coords

def save_edgeslike(inEdges, edgesName, coordsType):
    flatEdges = util.fast_concat(inEdges)
    edgesCoords = [get_edgecoords(edge,coordsType) for edge in flatEdges]
    edgeSavePath = get_object_savepath(edgesName)
    with open(edgeSavePath, 'wb') as edgeHandle:
        writer = csv.writer(edgeHandle)
        writer.writerows(inEdges)
    
def save_edgessets(edgesSets):
    objectName = "edgesSets"
    save_edgeslike(edgesSets, objectName, "lnglatCoords")
    save_edgeslike(edgesSets, objectName, "xyCoords")

