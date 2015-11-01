"""
Original Developer: Jonathan Ward
Purpose of Module: To provide data caching functionality for testing purposes.
Last Modified: 7/16/15
Last Modification Purpose: To clarify naming.
"""

#pylint: disable=W0142

# Standard Modules:
import os
import time
import dill as pickle

# Our Modules:
import config


############################
#Cache Overwriting Switches#
############################

USE_CACHED_DIRECTIONS = True
USE_CACHED_SPATIAL_LATTICE = True
USE_CACHED_SPATIAL_EDGES = True
USE_CACHED_SPATIAL_GRAPHS = True
USE_CACHED_SPATIAL_PATHS_2D = True
USE_CACHED_SPATIAL_PATHS_3D = True
USE_CACHED_SPATIOTEMPORAL_PATHS_4D = True


def create_basefolders():
    """Creates the cache and save folders"""
    cache_directory = config.CWD + "/cache/"
    config.CACHE_DIRECTORY = cache_directory
    if config.USE_DROPBOX:
        save_directory = config.DROPBOX_DIRECTORY + "/save/"
    else:
        save_directory = config.CWD + "/save/"
    config.SAVE_DIRECTORY = save_directory
    if not os.path.exists(cache_directory):
        os.makedirs(cache_directory)
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

def create_workingcachename(start, end):
    """Names the cache folder for a given city pair"""
    working_cache_name = "_".join([start, "to", end])
    config.WORKING_CACHE_NAME = working_cache_name
    return working_cache_name

def create_working_cache_directory(working_cache_name):
    """Creates the cache folder for a given city pair"""
    working_cache_directory = config.CACHE_DIRECTORY + working_cache_name + "/"
    config.WORKING_CACHE_DIRECTORY = working_cache_directory
    if not os.path.exists(working_cache_directory):
        os.makedirs(working_cache_directory)
    return working_cache_directory

def create_necessary_folders(start, end):
    """Creates all of the cache and save folders"""
    create_basefolders()
    working_cache_name = create_workingcachename(start, end)
    create_working_cache_directory(working_cache_name)

def get_object_cache_path(object_name):
    """Gets the path where the object will be cached"""
    object_file_base = "_".join([config.WORKING_CACHE_NAME, object_name])
    object_file_name = object_file_base + ".p"
    object_path = config.WORKING_CACHE_DIRECTORY + object_file_name
    return object_path

def cache_object(in_object, object_name):
    """Caches the object for future use"""
    object_cache_path = get_object_cache_path(object_name)
    file_handle = open(object_cache_path, "wb")
    pickle.dump(in_object, file_handle)
    file_handle.close()

def load_object(object_name):
    """Loads the cached object"""
    object_cache_path = get_object_cache_path(object_name)
    file_handle = open(object_cache_path, "rb")
    loaded_object = pickle.load(file_handle)
    file_handle.close()
    return loaded_object

def is_object_cached(object_name):
    """Returns a boolean indicating whether the object is cached"""
    object_cache_path = get_object_cache_path(object_name)
    object_cached = os.path.isfile(object_cache_path)
    return object_cached

def get_object(object_name, compute_function, compute_args, flag, is_skipped):
    """Either computes the object or loads a cached version"""
    if is_skipped and config.SKIPPING_MODE:
        return None
    else:
        if is_object_cached(object_name) and flag:
            print object_name + " exists."
            start = time.time()
            loaded_object = load_object(object_name)
            end = time.time()
            print "Loaded " + object_name + " in " + str(end - start) + " seconds."
            return loaded_object
        else:
            print "Computing " + object_name + "..."
            start = time.time()
            computed_object = compute_function(*compute_args)
            end = time.time()
            print object_name + " computed in " + str(end - start) + " seconds."
            if config.CACHE_MODE:
                start = time.time()
                cache_object(computed_object, object_name)
                end = time.time()
                print "Cached " + object_name + " in " + str(end - start) + " secs."
            return computed_object

###################
#Overwriting Bools#
###################

DIRECTIONS_BOOLS = [USE_CACHED_DIRECTIONS]
SPATIAL_LATTICE_BOOLS = DIRECTIONS_BOOLS + [USE_CACHED_SPATIAL_LATTICE]
SPATIAL_EDGES_BOOLS = SPATIAL_LATTICE_BOOLS + [USE_CACHED_SPATIAL_EDGES]
SPATIAL_GRAPHS_BOOLS = SPATIAL_EDGES_BOOLS + [USE_CACHED_SPATIAL_GRAPHS]
SPATIAL_PATHS_2D_BOOLS = SPATIAL_GRAPHS_BOOLS + [USE_CACHED_SPATIAL_PATHS_2D]
SPATIAL_PATHS_3D_BOOLS = SPATIAL_PATHS_2D_BOOLS + [USE_CACHED_SPATIAL_PATHS_3D]
SPATIOTEMPORAL_PATHS_4D_BOOLS = SPATIAL_PATHS_3D_BOOLS + \
                                [USE_CACHED_SPATIOTEMPORAL_PATHS_4D]

###################
#Overwriting Flags#
###################

DIRECTIONS_FLAG = all(DIRECTIONS_BOOLS)
SPATIAL_LATTICE_FLAG = all(SPATIAL_LATTICE_BOOLS)
SPATIAL_EDGES_FLAG = all(SPATIAL_EDGES_BOOLS)
SPATIAL_GRAPHS_FLAG = all(SPATIAL_GRAPHS_BOOLS)
SPATIAL_PATHS_2D_FLAG = all(SPATIAL_PATHS_2D_BOOLS)
SPATIAL_PATHS_3D_FLAG = all(SPATIAL_PATHS_3D_BOOLS)
SPATIOTEMPORAL_PATHS_4D_FLAG = all(SPATIOTEMPORAL_PATHS_4D_BOOLS)

####################
#Skip Loading Flags#
####################

SKIP_DIRECTIONS = DIRECTIONS_FLAG and SPATIAL_LATTICE_FLAG
SKIP_LATTICE = SKIP_DIRECTIONS and SPATIAL_EDGES_FLAG
SKIP_EDGES = SKIP_LATTICE and SPATIAL_GRAPHS_FLAG
SKIP_GRAPHS = SKIP_EDGES and SPATIAL_PATHS_2D_FLAG
SKIP_PATHS_2D = SKIP_GRAPHS and SPATIAL_PATHS_3D_FLAG
SKIP_PATHS_3D = SKIP_PATHS_2D and SPATIOTEMPORAL_PATHS_4D_FLAG
SKIP_PATHS_4D = False

###############################
#Uninitialized Directory Paths#
###############################

CACHE_DIRECTORY = ""
#SAVE_DIRECTORY = ""
WORKING_CACHE_NAME = ""
#WORKING_SAVE_DIR_NAME = ""
WORKING_CACHE_DIRECTORY = ""
#WORKING_SAVE_DIRECTORY = ""
WORKING_GRAPHS_DIRECTORY = ""
