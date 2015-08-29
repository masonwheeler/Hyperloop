"""
Original Developer: Jonathan Ward
Purpose of Module: To provide data caching functionality for testing purposes.
Last Modified: 7/16/15
Last Modification Purpose: To clarify naming.
"""

# Standard Modules:
import os
import csv
import json
import cPickle as pickle

# Our Modules:
import config
import util


def create_basefolders():
    """Creates the cache and save folders"""
    cache_directory = config.cwd + "/cache/"
    config.cache_directory = cache_directory
    if config.use_dropbox:
        save_directory = config.dropbox_directory + "/save/"
    else:
        save_directory = config.cwd + "/save/"
    config.save_directory = save_directory
    if not os.path.exists(cache_directory):
        os.makedirs(cache_directory)
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)


def create_workingcachename(start, end):
    """Names the cache folder for a given city pair"""
    working_cache_name = "_".join([start, "to", end])
    config.working_cache_name = working_cache_name
    return working_cache_name


def create_workingsavedirname(start, end):
    """Names the save folder for a given city pair"""
    working_save_dir_name = "_".join([start, "to", end])
    config.working_save_dir_name = working_save_dir_name
    return working_save_dir_name


def create_workingcachedirectory(working_cache_name):
    """Creates the cache folder for a given city pair"""
    working_cache_directory = config.cache_directory + working_cache_name + "/"
    config.working_cache_directory = working_cache_directory
    if not os.path.exists(working_cache_directory):
        os.makedirs(working_cache_directory)
    return working_cache_directory


def create_graphsdirectory(working_save_directory):
    """Creates the folder used to save completed routes"""
    graphs_directory = working_save_directory + "graphs/"
    config.working_graphs_directory = graphs_directory
    if not os.path.exists(graphs_directory):
        os.makedirs(graphs_directory)
    return graphs_directory


def create_workingsavedirectory(working_save_dir_name):
    """Creates the save directory for a given city pair"""
    working_save_directory = config.save_directory + working_save_dir_name + "/"
    create_graphsdirectory(working_save_directory +
                           working_save_dir_name + "_")
    config.working_save_directory = working_save_directory
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
    object_file_base = "_".join([config.working_cache_name, object_name])
    object_file_name = object_file_base + ".p"
    object_path = config.working_cache_directory + object_file_name
    return object_path


def get_object_savepath(object_name):
    """Gets the path where the object will be saved"""
    object_file_base = "_".join([config.working_save_dir_name, object_name])
    object_path = config.working_save_directory + object_file_base
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


def get_object(object_name, compute_function, compute_args, save_function, flag):
    """Either computes the object or loads a cached version"""
    if (is_object_cached(object_name) and flag):
        print(object_name + " exists.")
        loaded_object = load_object(object_name)
        print("Loaded " + object_name)
        return loaded_object
    else:
        print("Computing " + object_name + "...")
        computed_object = compute_function(*compute_args)
        print(object_name + " computed.")
        cache_object(computed_object, object_name)
        return computed_object

########## Functions for saving specific datatypes ##########


def save_directions(directions_object, directions_name):
    pass


def save_spline(spline_object, spline_name):
    pass


def save_lattice(lattice_object, lattice_name):
    pass


def save_edgessets(edges_sets, edges_name):
    pass


def save_graphs(graphs, graphs_name):
    pass


def save_spatial_paths_2d(spatial_paths2d, spatial_paths2d_name):
    pass


def save_routes(routes, start, end, start_lat_lng, end_lat_lng):
    routes_dicts = []
    route_index = 0
    for route in routes:
        route_dict = route.as_dict()
        route_dict["index"] = route_index
        route_index += 1
        routes_dicts.append(route_dict)
    city_pair = {
        "start_city": {
            "name": start,
            "coordinates": start_lat_lng
        },
        "end_city": {
            "name": end,
            "coordinates": end_lat_lng
        },
        "routes":  routes_dicts
    }
    save_path = config.dropbox_directory + "/example_city_pair.json"
    with open(save_path, 'w') as file_path:
        json.dump(city_pair, file_path)
