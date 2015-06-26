import os
import csv
import cPickle as pickle

import config


def create_workingcachename(start,end):
    workingCacheName = "_".join([start,"to",end,"cache"])
    config.workingCacheName = workingCacheName
    return workingCacheName

def create_workingsavedirname(start,end):
    workingSaveDirName = "_".join([start,"to",end,"savedir"])
    config.workingSaveDirName = workingSaveDirName
    return workingSaveDirName

def create_workingcachedirectory(workingCacheName):
    workingCacheDirectory = workingCacheName + "/"
    if not os.path.exists(workingCacheDirectory):
        os.makedirs(workingCacheDirectory)
        config.workingCacheDirectory = workingCacheDirectory
    return workingCacheDirectory

def get_object_cachepath(objectName):
    objectFileBase = "_".join([config.workingCacheName, objectName])
    objectFileName = objectFileBase + ".p"
    objectPath = config.cwd + config.workingCacheDirectory + objectFileName
    return objectPath

def get_object_savepath(objectName):

def cache_object(inObject, objectName):
    objectCachePath = get_object_cachepath(objectName)
    fileHandle = open(objectCachePath, "wb")
    pickle.dump(inObject, fileHandle)

def load_object(objectName):
    objectCachePath = get_object_cachepath(inObject, objectName)
    fileHandle = open(objectCachePath, "wb")
    loadedObject = pickle.load(fileHandle)
    return loadedObject

def save_listlike(inObject, objectName):    
    objectSavePath = get_object_savepath(objectName)
    with open(objectPath + '.csv', 'wb') as objectHandle:
        writer = csv.writer(objectHandle)
        writer.writerows(inObject)        

def save_directions(directions):
    objectName = "directions"
    cache_object(directions, objectName)
    save_listlike(objectName)

def load_directions():
    directions = load_object("directions")
    return directions

def save_bounds(bounds):
    objectName = "bounds"
    cache_object(directions, objectName)
    save_listlike(objectName)

def load_bounds():
    bounds = load_object("bounds")
    return bounds

def save_boundsxy(boundsXY):
    cache_object(boundsXY, "boundsXY")

def load_boundsxy():
    boundsXY = load_object("boundsXY")
    return boundsXY

def save_transformedbounds(transformedBounds):
    cache_object(transformedBounds, "transformedBounds")        

def load_transformedbounds():
    transformedBounds = load_object("transformedBounds")
    return transformedBounds

def save_baselattice(baseLattice):

def load_baselattice():

def save_envelope(envelope):

def load_envelope():

def save_lnglatlattice(lnglatLattice):

def load_lnglatlattice():

def save_finishedlattice(finishedLattice):

def load_finishedlattice():

def save_edgessets(edgesSets)

def load_edgessets():
