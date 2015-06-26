import os
import csv
import cPickle as pickle

import config
import util


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

def create_workingsavedirectory(workingSaveDirName):
    workingSaveDirectory = workingSaveDirName + "/"
    if not os.path.exists(workingSaveDirectory):
        os.makedirs(workingSaveDirectory)
        config.workingSaveDirectory = workingSaveDirectory
    return workingSaveDirectory

def get_object_cachepath(objectName):
    objectFileBase = "_".join([config.workingCacheName, objectName])
    objectFileName = objectFileBase + ".p"
    objectPath = config.cwd + config.workingCacheDirectory + objectFileName
    return objectPath

def get_object_savepath(objectName):
    objectFileBase = "_".join([config.workingSaveDirName, objectName])
    objectPath = config.cwd + config.workingSaveDirectory + objectFileBase
    return objectPath

def cache_object(inObject, objectName):
    objectCachePath = get_object_cachepath(objectName)
    fileHandle = open(objectCachePath, "wb")
    pickle.dump(inObject, fileHandle)

def load_object(objectName):
    objectCachePath = get_object_cachepath(inObject, objectName)
    fileHandle = open(objectCachePath, "wb")
    loadedObject = pickle.load(fileHandle)
    return loadedObject

def save_listlike(inList, listName):    
    listSavePath = get_object_savepath(listName)
    with open(listSavePath + '.csv', 'wb') as listHandle:
        writer = csv.writer(listHandle)
        writer.writerows(inList)        

def save_directions(directions):
    objectName = "directions"
    cache_object(directions, objectName)
    save_listlike(directions, objectName)

def load_directions():
    directions = load_object("directions")
    return directions

def save_bounds(bounds):
    objectName = "bounds"
    cache_object(bounds, objectName)
    save_listlike(bounds, objectName)

def load_bounds():
    bounds = load_object("bounds")
    return bounds

def save_boundsxy(boundsXY):
    objectName = "boundsxy"
    cache_object(boundsXY, objectName)
    save_listlike(boundsxy, objectName)

def load_boundsxy():
    boundsXY = load_object("boundsxy")
    return boundsXY

def save_transformedbounds(transformedBounds):
    objectName = "transformedbounds"
    cache_object(transformedBounds, objectName)        
    save_listlike(transformedBounds, objectName)

def load_transformedbounds():
    transformedBounds = load_object("transformedBounds")
    return transformedBounds

def get_pointcoords(point, coordsType):
    coords = eval(".".join(["point", coordsType]))
    return coords

def save_latticelike(inLattice, latticeName, coordsType):
    flatLattice = util.fast_concat(inLattice)
    latticeCoords = [get_pointcoords(point,coordsType) for point in flatLattice]
    latticeSavePath = get_object_savepath(latticeName)
    with open(latticeSavePath + '.csv', 'wb') as latticeHandle:
        writer = csv.writer(latticeHandle)
        writer.writerows(inLattice)        

def save_baselattice(baseLattice):
    objectName = "baselattice"
    cache_object(baseLattice, objectName)
    save_latticelike(baseLattice, objectName, "latticeCoords")

def load_baselattice():
    baseLattice = load_object("baselattice")
    return baseLattice

def save_envelope(envelope):
    objectName = "envelope"
    cache_object(envelope, objectName)

def load_envelope():
    envelope = load_object("envelope")
    return envelope

def save_lnglatlattice(lnglatLattice):
    objectName = "lnglatlattice"
    cache_object(lnglatLattice, objectName)
    save_latticelike(lnglatLattice, objectName, "lnglatCoords")
    save_latticelike(lnglatLattice, objectName, "xyCoords")

def load_lnglatlattice():
    lnglatLattice = load_object("lnglatlattice")
    return lnglatLattice

def get_edgecoords(edge, coordsType):
    coordsPair = eval(".".join(["edge", coordsType]))
    coords = util.fast_concat(coordsPair)
    return coords

def save_edgeslike(inEdges, edgesName, coordsType):
    flatEdges = util.fast_concat(inEdges)
    edgesCoords = [get_edgecoords(edge,coordsType) for edge in flatEdges]
    edgeSavePath = get_object_savepath(edgesName)
    with open(edgeSavePath + '.csv', 'wb') as edgeHandle:
        writer = csv.writer(edgeHandle)
        writer.writerows(inEdges)
    
def save_edgessets(edgesSets):
    objectName = "edgesSets"
    cache_object(edgesSets, objectName)
    save_edgeslike(edgesSets, objectName, "lnglatCoords")
    save_edgeslike(edgesSets, objectName, "xyCoords")
     
def load_edgessets():
    edgessets = load_object("edgessets")
    return edgessets

