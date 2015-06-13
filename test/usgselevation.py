import proj

usgsProj = proj.usgs_proj()
print(proj.lonlats_to_xys([[-118,34],[-122,37]],usgsProj))

#def get_boundingbox(latlng)
