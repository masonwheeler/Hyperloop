  @staticmethod
    def vertices_to_frontindices(vertices, x_reverse, y_reverse):
        """
        Computes the Pareto front given the vertices of the convex hull.

        If x_reverse is set to True then the Pareto front minimizes x-values.
        If y_reverse is set to True then the Pareto front minimizes y-values.
        """
        x_max, y_max = np.amax(vertices, axis=0)
        x_min, y_min = np.amin(vertices, axis=0)
        # The vertices with x-values equal to x-max
        x_max_vertices = vertices[np.where(vertices[:, 0] == x_max)]
        # The vertices with y-values equal to y-max
        y_max_vertices = vertices[np.where(vertices[:, 1] == y_max)]
        # The vertices with x-values equal to x-min
        x_min_vertices = vertices[np.where(vertices[:, 0] == x_min)]
        # The vertices with y-values equal to y-min
        y_min_vertices = vertices[np.where(vertices[:, 1] == y_min)]

        if not x_reverse and not y_reverse:  # Taking the top-right vertices
            # To find the maximum y-value of the vertices with maximal x-values
            _, y_min_filter = np.amax(x_max_vertices, axis=0)
            # To find the maximum x-value of the vertices with maximal y-values
            x_min_filter, _ = np.amax(y_max_vertices, axis=0)
            # Take the vertices which pass the x-value and y-value filters.
            front_indices = np.where(np.logical_and(
                vertices[:, 0] >= x_min_filter,
                vertices[:, 1] >= y_min_filter))
            return front_indices

        if not x_reverse and y_reverse:  # Taking the bottom-right vertices
            # To find the minimum y-value of the vertices with maximal x-values
            _, y_max_filter = np.amin(x_max_vertices, axis=0)
            # To find the maximum x-value of the vertices with minimal y-values
            x_min_filter, _ = np.amax(y_min_vertices, axis=0)
            # Take the vertices which pass the x-value and y-value filters.
            front_indices = np.where(np.logical_and(
                vertices[:, 0] >= x_min_filter,
                vertices[:, 1] <= y_max_filter))
            return front_indices

       if x_reverse and not y_reverse:  # Taking the top-left vertices
            # To find the maximum y-value of the vertices with minimal x-values
            _, y_min_filter = np.amax(x_min_vertices, axis=0)
            # To find the minimum x-value of the vertices with maximal y-values
            x_max_filter, _ = np.amin(y_max_vertices, axis=0)
            # Take the vertices which pass the x-value and y-value filters.
            front_indices = np.where(np.logical_and(
                vertices[:, 0] <= x_max_filter,
                vertices[:, 1] >= y_min_filter))
            return front_indices

        if x_reverse and y_reverse:  # Taking the bottom-left vertices
            # To find the minimum y-value of the vertices with minimal x-values
            _, y_max_filter = np.amin(x_min_vertices, axis=0)
            # To find the minimum x-value of the vertices with minimal y-values
            x_max_filter, _ = np.amin(y_min_vertices, axis=0)
            # Take the vertices which pass the x-value and y-value filters.
            front_indices_tuple = np.where(np.logical_and(
                vertices[:, 0] <= x_max_filter,
                vertices[:, 1] <= y_max_filter))
            front_indices = front_indices_tuple[0]
            reduced_vertices = vertices[front_indices]
            sorted_reduced_vertices_indices = np.argsort(reduced_vertices[:, 0])
            sorted_front_indices = front_indices[
                     sorted_reduced_vertices_indices]
            sorted_reduced_vertices = reduced_vertices[
                           sorted_reduced_vertices_indices]
            selected_indices = [0]
            num_vertices = sorted_reduced_vertices.shape[0]
            for i in range(num_vertices - 1):
                vertex_a = sorted_reduced_vertices[i]
                vertex_b = sorted_reduced_vertices[i + 1]
                if vertex_b[1] < vertex_a[1]:
                   selected_indices.append(i + 1)
            selected_front_indices = sorted_front_indices[selected_indices]
            return selected_front_indices

