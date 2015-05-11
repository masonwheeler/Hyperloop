#From http://zacharybears.com/using-python-to-translate-latlon-locations-to-pixels-on-a-geotiff/

from osgeo import gdal
from osgeo import osr

import struct
import Image

def latLonToPixel(geotiff, latLonPairs):
    #tiffImage = Image.open(geotiff)
    #print(tiffImage.getpalette())
    #rgbtiff = tiffImage.convert('RGB')
    ds = gdal.Open(geotiff)
    gt = ds.GetGeoTransform()
    #print(ds.RasterCount)
    rb = ds.GetRasterBand(1)
    srs = osr.SpatialReference()
    srs.ImportFromWkt(ds.GetProjection())
    srsLatLon = srs.CloneGeogCS()
    ct = osr.CoordinateTransformation(srsLatLon,srs)
    pixelPairs = []
    vals = []
    for point in latLonPairs:
	(point[1],point[0],holder) = ct.TransformPoint(point[1],point[0])
        x = int((point[1] - gt[0])/gt[1])
        y = int((point[0] - gt[3])/gt[5])
        #pixelPairs.append([x, y])
	structval = rb.ReadRaster(x,y,1,1,buf_type=gdal.GDT_Float32)
	intval = struct.unpack('f', structval)
	#print(len(intval))
        val = intval[0]
        vals.append(val)          
    return vals

print(latLonToPixel("ca_south_NLCD_042800_erd.tif",[[34.05,-118.25]]))
