import os
import cPickle as pickle

import config


def create_workingcachename(start,end):
    workingCacheName = "_".join([start,"to",end])
    config.workingCacheName = workingCacheName
    return workingCacheName

def create_workingcachedirectory(workingCacheName):
    workingCacheDirectory = workingCacheName + "/"
    if not os.path.exists(workingCacheDirectory):
        os.makedirs(workingCacheDirectory)
        config.workingCacheDirectory = workingCacheDirectory
    return workingCacheDirectory

def get_object_path(inObject, objectName):
    objectFileName = "_".join([config.workingCacheName, objectName])
    objectPath = config.cwd + config.workingCacheDirectory + objectFileName
    return objectPath

def cache_object(inObject, objectName):
    objectPath = get_object_path(inObject, objectName)
    fileHandle = open(objectPath, "wb")
    pickle.dump(inObject, fileHandle)

def load_object(objectName):
    objectPath = get_object_path(inObject, objectName)
    fileHandle = open(objectPath, "wb")
    loadedObject = pickle.load(fileHandle)
    return loadedObject

def cache_directions(directions):

def cache_bounds(bounds):

def cache_boundsxy(boundsXY):

def cache_transformedbounds(transformedBounds):

def cache_baseLattice(baseLattice):

def cache_envelope(envelope):

def cache_lnglatlattice(lnglatLattice):

def cache_finishedlattice(finishedLattice):

def cache_edgessets(edgesSets)
