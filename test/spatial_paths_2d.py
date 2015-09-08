"""
Original Developer:
    Jonathan Ward

Purpose of Module:
    To create 2d spatial paths (i.e. interpolated spatial graphs)

Last Modified: 
    09/08/15

Last Modified By:
    Jonathan Ward

Last Modification Purpose:
    Created Module
"""

import abstract

class SpatialPath2d(abstract.AbstractPath2d):
    def sample_geospatials(self, graph_geospatials, geospatial_sample_distance):
        sampled_geospatials = interpolate.sample_path(graph_geospatials,
                                             geospatial_sample_distance)
        return sampled_geospatials

    def get_interpolating_geospatials(self, sampled_geospatials):
        x_array, y_array = points_2d_to_arrays(sampled_geospatials)
        num_points = len(sampled_geospatials)
        s_values = interpolate.get_s_values(num_points)
        x_spline, y_spline = interpolate.interpolating_splines_2d(x_array,
                                                         y_array, s_values)
        x_values = interpolate.get_spline_values(x_spline, s_values)
        y_values = interpolate.get_spline_values(y_spline, s_values)
        interpolating_geospatials = [x_values, y_values]
        return interpolating_geospatials

    def get_interpolating_geospatials_v2(self, geospatials):
        interpolating_geospatials_array = interp.para_super_q(geospatials, 25)
        interpolating_geospatials = interpolating_geospatials_array.tolist()
        arc_lengths = util.compute_arc_lengths(interpolating_geospatials)
        return [interpolating_geospatials, arc_lengths]

    def get_interpolating_latlngs(self, interpolating_geospatials):
        interpolating_lat_lngs = proj.geospatials_to_latlngs(
                         interpolating_geospatials, config.PROJ)
        return interpolating_lat_lngs

    def get_tube_graphs(self, elevation_profile):

    def get_tube_graphs_v2(self, elevation_profile):
        geospatials = [elevation_point["geospatial"] for elevation_point
                                                    in elevation_profile]
        land_elevations = [elevation_point["land_elevation"] for elevation_point
                                                         in elevation_profile]
        arc_lengths = [elevation_point["distance_along_path"] for elevation_point
                                                         in elevation_profile]
        s_interp, z_interp = landscape.match_landscape(arc_lengths,
                                   land_elevations, "elevation")
        tube_spline = PchipInterpolator(s_interp, z_interp)
        tube_elevations = tube_spline(arc_lengths)
          plt.plot(arc_lengths, tube_elevations, 'b.',
                    arc_lengths, land_elevations, 'r.')
          plt.show()
        spatial_x_values, spatial_y_values = zip(*geospatials)

     def __init__(self, spatial_graph):
        graph_geospatials = spatial_graph.geospatials
        sampled_geospatials = self.sample_geospatials(graph_geospatials)
        interpolating_geospatials = self.get_interpolating_geospatials(
                                                       sampled_geospatials)
        interpolating_geospatials, arc_lengths = \
          self.get_interpolating_geospatials_v2(graph_geospatials)
        interpolating_lat_lngs = self.get_interpolating_latlngs(
                                           interpolating_geospatials)
        self.elevation_profile = elevation.get_elevation_profile(
                            interpolating_geospatials, arc_lengths)
        self.land_cost = landcover.get_land_cost(interpolating_lat_lngs)
        self.tube_graphs = self.get_tube_graphs_v2(self.elevation_profile)

#def SpatialPathsSet2d(abstract.AbstractPathsSet2d):
