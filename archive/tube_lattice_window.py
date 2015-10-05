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

