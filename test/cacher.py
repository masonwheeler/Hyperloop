"""
Original Developer: Jonathan Ward
Purpose of Module: To provide data caching functionality for testing purposes.
Last Modified: 7/16/15
Last Modification Purpose: To clarify naming.
"""

#pylint: disable=W0142

# Standard Modules:
import os
import json
#import cPickle as pickle
#import pickle
import dill as pickle

# Our Modules:
import config


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


def create_workingsavedirname(start, end):
    """Names the save folder for a given city pair"""
    working_save_dir_name = "_".join([start, "to", end])
    config.WORKING_SAVE_DIR_NAME = working_save_dir_name
    return working_save_dir_name


def create_workingcachedirectory(working_cache_name):
    """Creates the cache folder for a given city pair"""
    working_cache_directory = config.CACHE_DIRECTORY + working_cache_name + "/"
    config.WORKING_CACHE_DIRECTORY = working_cache_directory
    if not os.path.exists(working_cache_directory):
        os.makedirs(working_cache_directory)
    return working_cache_directory


def create_graphsdirectory(working_save_directory):
    """Creates the folder used to save completed routes"""
    graphs_directory = working_save_directory + "graphs/"
    config.WORKING_GRAPHS_DIRECTORY = graphs_directory
    if not os.path.exists(graphs_directory):
        os.makedirs(graphs_directory)
    return graphs_directory


def create_workingsavedirectory(working_save_dir_name):
    """Creates the save directory for a given city pair"""
    working_save_directory = config.SAVE_DIRECTORY + working_save_dir_name + "/"
    create_graphsdirectory(working_save_directory +
                           working_save_dir_name + "_")
    config.WORKING_SAVE_DIRECTORY = working_save_directory
    if not os.path.exists(working_save_directory):
        os.makedirs(working_save_directory)
    return working_save_directory


def create_necessaryfolders(start, end):
    """Creates all of the cache and save folders"""
    create_basefolders()
    working_cache_name = create_workingcachename(start, end)
    working_save_dir_name = create_workingsavedirname(start, end)
    create_workingcachedirectory(working_cache_name)
    create_workingsavedirectory(working_save_dir_name)


def get_object_cachepath(object_name):
    """Gets the path where the object will be cached"""
    object_file_base = "_".join([config.WORKING_CACHE_NAME, object_name])
    object_file_name = object_file_base + ".p"
    object_path = config.WORKING_CACHE_DIRECTORY + object_file_name
    return object_path


def get_object_savepath(object_name):
    """Gets the path where the object will be saved"""
    object_file_base = "_".join([config.WORKING_SAVE_DIR_NAME, object_name])
    object_path = config.WORKING_SAVE_DIRECTORY + object_file_base
    return object_path


def cache_object(in_object, object_name):
    """Caches the object for future use"""
    object_cache_path = get_object_cachepath(object_name)
    file_handle = open(object_cache_path, "wb")
    pickle.dump(in_object, file_handle)
    file_handle.close()


def load_object(object_name):
    """Loads the cached object"""
    object_cache_path = get_object_cachepath(object_name)
    file_handle = open(object_cache_path, "rb")
    loaded_object = pickle.load(file_handle)
    file_handle.close()
    return loaded_object


def is_object_cached(object_name):
    """Returns a boolean indicating whether the object is cached"""
    object_cache_path = get_object_cachepath(object_name)
    object_cached = os.path.isfile(object_cache_path)
    return object_cached


def is_object_saved(object_name):
    """Returns a boolean indicated whether the object is saved"""
    object_save_path = get_object_savepath(object_name)
    object_saved = os.path.isfile(object_save_path)
    return object_saved


def get_object(object_name, compute_function, compute_args, flag):
    """Either computes the object or loads a cached version"""
    if is_object_cached(object_name) and flag:
        print object_name + " exists."
        loaded_object = load_object(object_name)
        print "Loaded " + object_name
        return loaded_object
    else:
        print "Computing " + object_name + "..."
        computed_object = compute_function(*compute_args)
        print object_name + " computed."
        if config.CACHE_MODE:
            cache_object(computed_object, object_name)
        return computed_object

def save_routes(routes, start, end, start_lat_lng, end_lat_lng):
    """Saves completed routes to json
    """
    routes_dicts = []
    route_index = 0
    for route in routes:
        route_dict = route.as_dict(route_index)
        route_index += 1
        routes_dicts.append(route_dict)
    city_pair = {
        "startCity": {
            "name": start,
            "coordinates": start_lat_lng
        },
        "endCity": {
            "name": end,
            "coordinates": end_lat_lng
        },
        "routes": routes_dicts
    }
    filename = "/" + str(start) + "_" + str(end) + ".json"
    save_path = config.DROPBOX_DIRECTORY + filename 
    with open(save_path, 'w') as file_path:
        json.dump(city_pair, file_path)
