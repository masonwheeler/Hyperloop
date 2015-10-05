    def circle_function(self, x, r):
        if x > r:
            return -float("Inf")
        else:
            y = np.sqrt(np.square(r) - np.square(x)) - r
            return y

    def build_window(self, left_bound, right_bound, radius):
        relative_indices = range(-left_bound, right_bound + 1)
        window = [{"relative_index": relative_index,
                   "relative_elevation": self.circle_function(
                       abs(relative_index * parameters.PYLON_SPACING), radius)}
                  for relative_index in relative_indices]
        return window

    def add_current_window(self, envelope, current_window):
        for point in current_window:
            current_index = point["index"]
            envelope[current_index].append(point["elevation"])

    def build_envelope(self, elevations, radius):
        window_size = int(radius / config.PYLON_SPACING)
        envelope_lists = [[] for i in xrange(len(elevations))]
        for current_index in range(0, len(elevations)):
            if current_index < window_size:
                left_bound = current_index
            else:
                left_bound = window_size
            if current_index > (len(elevations) - 1) - window_size:
                right_bound = (len(elevations) - 1) - current_index
            else:
                right_bound = window_size
            relative_window = self.build_window(
                left_bound, right_bound, radius)
            current_elevation = elevations[current_index]
            current_window = [{
                "index": point["relative_index"] + current_index,
                "elevation": point["relative_elevation"] + current_elevation}
                for point in relative_window]
            self.add_current_window(envelope_lists, current_window)
        envelope = map(max, envelope_lists)
        return envelope

   def build_pylons_envelopes(self, elevation_profile):
        distances = []
        elevations = []
        for elevation_point in elevation_profile:
            distances.append(elevation_point["distance_along_path"])
            elevations.append(elevation_point["land_elevation"])
        max_speed = parameters.MAX_SPEED
        curvature_threshold_upper = interpolate.compute_curvature_threshold(
            max_speed, parameters.MAX_VERTICAL_ACCEL)
        radius_upper = 1.0 / curvature_threshold_upper
        envelope_upper = self.build_envelope(elevations, radius_upper)
        min_speed = parameters.MIN_SPEED
        curvature_threshold_lower = interpolate.compute_curvature_threshold(
            min_speed, paramters.MAX_VERTICAL_ACCEL)
        radius_lower = 1.0 / curvature_threshold_lower
        envelope_lower = self.build_envelope(elevations, radius_lower)
        return [envelope_upper, envelope_lower]

    def envelope_point_to_bounds(self, data_point):
        elevation_point, envelope_point_upper, envelope_point_lower = data_point
        land_elevation = elevation_point["land_elevation"]
        pylons_slice_bounds = {
            "tallest_pylon_height": envelope_point_upper - land_elevation,
            "shortest_pylon_height": envelope_point_lower - land_elevation,
            "distance_along_path": elevation_point["distance_along_path"],
            "geospatial": elevation_point["geospatial"],
            "latlng": elevation_point["latlng"],
            "land_elevation": land_elevation,
            "pylon_height_step_size": parameters.PYLON_HEIGHT_STEP_SIZE
        }
        return pylons_slice_bounds

    def build_pylons_slices_bounds(self, elevation_profile, pylons_envelope_upper,
                                   pylons_envelope_lower):
        pylons_data = zip(elevation_profile, pylons_envelope_upper,
                          pylons_envelope_lower)
        pylons_slices_bounds = [self.envelope_point_to_bounds(data_point)
                                for data_point in pylons_data]
        return pylons_slices_bounds

