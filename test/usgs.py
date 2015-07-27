"""
Original Developer: Jonathan Ward
Purpose of Module: To download, cache, and access usgs elevation data.
Last Modified: 7/25/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Redesigned logic flow to save memory.
"""

#Standard Modules:
from osgeo import gdal
from osgeo import osr
import urllib
import zipfile
import os
import math
from subprocess import call

#Our Modules
import config
import util
import geotiff

def get_bounding_coordinates(latlngCoord):
    lat, lng = latlngCoord
    latBound = int(math.ceil(lat))
    lngBound = int(math.ceil(abs(lng)))
    return [latBound, lngBound]

def get_coordstring(latlngCoord):
    latBound, lngBound = get_bounding_coordinates(latlngCoord)
    latstr, lngstr = "n" + str(latBound), "w" + str(lngBound).zfill(3)
    coordstring = latstr + lngstr
    return coordstring

def img_filename(coordstring):
    imgFilename = "img" + coordstring + "_13" + ".img"
    return imgFilename

def file_exists(localFilePath):
    return os.path.isfile(localFilePath)

def unzip_zipfile(zipFilePath, outPath, imgFileName):
    fileHandle = open(zipFilePath, 'rb')
    zipFileData = zipfile.ZipFile(fileHandle)
    imgFilePath = outPath + imgFileName
    imgExists = file_exists(imgFilePath)
    if imgExists:
        if config.verboseMode:
            print(".img file already exists")
    else:
        if config.verboseMode:
            print("Unzipping folder...")
        for fileName in zipFileData.namelist():
            if (fileName == imgFileName):                
                if config.verboseMode:
                    print(fileName + " extracted.")
                zipFileData.extract(fileName, outPath)
        fileHandle.close()
        return 0

def img_to_geotiff(imgFileName, unzipDirectory, coordstring):    
    imgFilePath = unzipDirectory + imgFileName
    tifFilePath = unzipDirectory + coordstring + ".tif"
    call(["gdal_translate","-of","Gtiff",imgFilePath,tifFilePath])
    return tifFilePath

def geotiff_pixelVal(geotiffFilePath, lonlatCoord):
    ds = gdal.Open(geotiffFilePath)
    gt = ds.GetGeoTransform()
    rb = ds.GetRasterBand(1)
    srs = osr.SpatialReference()
    srs.ImportFromWkt(ds.GetProjection())
    srsLatLon = srs.CloneGeogCS()
    ct = osr.CoordinateTransformation(srsLatLon,srs)
    pixelVal = geotiff.pixel_val(ct, gt, rb, lonlatCoord)
    return pixelVal

def remove_file(filePath):
    os.remove(filePath)
    

def get_elevation(latlngCoord):
    coordstring = get_coordstring(latlngCoord)
    coordZipfile = coordstring + ".zip"
    coordFolderName = coordstring + "/"     

    url = config.usgsFtpPath + coordZipfile
    downloadDirectory = config.cwd + config.usgsFolder
    zipFilePath = downloadDirectory + coordZipfile
    unzipDirectory = downloadDirectory + coordFolderName
    imgFileName = img_filename(coordstring)
    imgFilePath = unzipDirectory + imgFileName
    geotiffFilePath = unzipDirectory + coordstring + ".tif"

    if file_exists(geotiffFilePath):
        pass
    else:
        if file_exists(imgFilePath):
            pass
        else:
            if file_exists(zipFilePath):
                pass
            else:
                util.smart_print("Not yet downloaded.")
                util.smart_print("Now downloading " + coordZipfile + "...")
                urllib.urlretrieve(url, zipFilePath)        
            unzip_zipfile(zipFilePath, unzipDirectory, imgFileName)   
            remove_file(zipFilePath)
        img_to_geotiff(imgFileName, unzipDirectory, coordstring)
        remove_file(imgFilePath)
        

    lonlatCoord = util.swap_pair(latlngCoord)
    pixelVal = geotiff_pixelVal(geotiffFilePath, lonlatCoord)
    
    return pixelVal





