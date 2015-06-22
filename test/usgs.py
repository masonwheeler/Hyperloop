from osgeo import gdal
from osgeo import osr
import urllib
import zipfile
import os.path
import math
from subprocess import call

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
    #ftpBaseName = ("_").join(["USGS","NED","13",latstr + lngstr,"IMG"])
    return coordstring

def img_filename(coordstring):
    imgFilename = "img" + coordstring + "_13" + ".img"
    return imgFilename

#def img_filename(imgBasename):
#    imgFilename = imgBasename + ".img"
#    return imgFilename

#def file_needed(fileName, neededFiles):
#    return (fileName in neededFiles)

def file_exists(localFilePath):
    return os.path.isfile(localFilePath)

def unzip_zipfile(zipFilePath, outPath, imgFileName):
    fileHandle = open(zipFilePath, 'rb')
    zipFileData = zipfile.ZipFile(fileHandle)
    #neededFiles = needed_files(ftpBaseName)
    #neededFilePaths = [outPath + neededFile for neededFile in neededFiles]
    #existingFiles = map(file_exists, neededFilePaths)
    #allFilesExist = all(existingFiles)
    imgFilePath = outPath + imgFileName
    imgExists = file_exists(imgFilePath)
    if imgExists:
        print("Already unzipped folder.")
        return 0
    else:
        print("Unzipping folder...")
        for fileName in zipFileData.namelist():
            if (fileName == imgFileName):                
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

def get_elevation(latlngCoord):
    coordstring = get_coordstring(latlngCoord)
    coordZipfile = coordstring + ".zip"
    coordFolderName = coordstring + "/"

    url = config.usgsFtpPath + coordZipfile
    downloadDirectory = config.cachePath
    zipFilePath = downloadDirectory + coordZipfile

    if file_exists(zipFilePath):
        print("Already downloaded " + coordZipfile)
    else:
        print("Not yet downloaded.")
        print("Now downloading " + coordZipfile + "...")
        urllib.urlretrieve(url, zipFilePath)
        
    unzipDirectory = downloadDirectory + coordFolderName
    imgFileName = img_filename(coordstring)
    unzip_zipfile(zipFilePath, unzipDirectory, imgFileName)
    
    geotiffFilePath = unzipDirectory + coordstring + ".tif"
    if file_exists(geotiffFilePath):
        print("Already converted to geotiff.")
    else:
        img_to_geotiff(imgFileName, unzipDirectory, coordstring)

    lonlatCoord = util.swap_pair(latlngCoord)
    pixelVal = geotiff_pixelVal(geotiffFilePath, lonlatCoord)
    #print("Pixel Value is: ")
    #print(pixelVal)
    
    return pixelVal

#latlngCoord = (37, -76)

#get_elevation(latlngCoord)

