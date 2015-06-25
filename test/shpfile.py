import shapefile

boundingPointsList = [[34.05,-118.25],[34.05,-122.4167],[37.7833,-122.4167],[37.7833,-118.25]]

w = shapefile.Writer(shapefile.POLYGON)
w.poly(parts=[boundingPointsList])
w.save('bounding')
