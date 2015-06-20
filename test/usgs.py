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

def get_ftpBaseName(latlngCoord):
    latBound, lngBound = get_bounding_coordinates(latlngCoord)
    latstr, lngstr = "n" + str(latBound), "w" + str(lngBound).zfill(3)
    ftpBaseName = ("_").join(["USGS","NED","13",latstr + lngstr,"IMG"])
    return ftpBaseName

def needed_files(ftpBaseName):
    extensions = [".img",".img.xml",".img.aux.xml"]
    neededFiles = [ftpBaseName + extension for extension in extensions]
    return neededFiles

def file_needed(fileName, neededFiles):
    return (fileName in neededFiles)

def file_exists(localFilePath):
    return os.path.isfile(localFilePath)

def unzip_zipfile(zipFile, outPath, ftpBaseName):
    fileHandle = open(zipFile, 'rb')
    zipFileData = zipfile.ZipFile(fileHandle)
    neededFiles = needed_files(ftpBaseName)
    neededFilePaths = [outPath + neededFile for neededFile in neededFiles]
    existingFiles = map(file_exists, neededFilePaths)
    allFilesExist = all(existingFiles)
    if allFilesExist:
        print("Already unzipped files.")
        return 0
    else:
        print("Unzipping files...")
        for fileName in zipFileData.namelist():
            if file_needed(fileName, neededFiles):
                print("Unzipping:")
                print(name)
                zipFileData.extract(name, outPath)
        fileHandle.close()
        return 0

def img_to_geotiff(ftpBaseName, unzipDirectory):    
    imgFilePath = unzipDirectory + ftpBaseName + ".img"
    tifFilePath = unzipDirectory + ftpBaseName + ".tif"
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
    ftpBaseName = get_ftpBaseName(latlngCoord)
    ftpZipFileName = ftpBaseName + ".zip"
    ftpFolderName = ftpBaseName + "/"

    url = config.usgsFtpPath + ftpZipFileName
    downloadDirectory = config.cachePath
    localFilePath = downloadDirectory + ftpZipFileName

    if file_exists(localFilePath):
        print("Already downloaded " + ftpZipFileName)
    else:
        print("Not yet downloaded.")
        print("Now downloading " + ftpZipFileName + "...")
        urllib.urlretrieve(url, localFilePath)
        
    unzipDirectory = downloadDirectory + ftpFolderName
    unzip_zipfile(localFilePath, unzipDirectory, ftpBaseName)

    
    geotiffFilePath = unzipDirectory + ftpBaseName + ".tif"
    if file_exists(geotiffFilePath):
        print("Already converted to geotiff.")
    else:
        img_to_geotiff(ftpBaseName, unzipDirectory)

    lonlatCoord = util.swap_pair(latlngCoord)
    pixelVal = geotiff_pixelVal(geotiffFilePath, lonlatCoord)
    print("Pixel Value is: ")
    print(pixelVal)
    
    return 0

latlngCoord = (37, -76)

get_elevation(latlngCoord)

