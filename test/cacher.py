import os
import cPickle as pickle

import config


def create_workingcachename(start,end):
    cacheName = "_".join([start,"to",end])
    config.cacheName = cacheName
    return cacheName

def create_cache(cacheName):
    cacheDirectory = cacheName + "/"
    if not os.path.exists(cacheDirectory):
        os.makedirs(cacheDirectory)
        config.cacheDirectory
    return cacheDirectory

def cache_directions(directions):
    cachePath = config.cwd + config
    pickle.dump(    

def cache_bounds(bounds):

def cache_boundsxy(boundsXY):

def cache_transformedbounds(transformedBounds):

def cache_baseLattice(baseLattice):

def cache_envelope(envelope):

def cache_lnglatlattice(lnglatLattice):

def cache_finishedlattice(finishedLattice):

def cache_edgessets(edgesSets)
