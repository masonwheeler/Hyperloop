import urllib
import zipfile
import os.path
import math
from subprocess import call

import config

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

def correct_extension(name):
    fileName, fileExtension = os.path.splitext(name)
    return (fileExtension in [".img",".xml"])

def unzip_zipfile(zipFile, outPath):
    fileHandle = open(zipFile, 'rb')
    zipFileData = zipfile.ZipFile(fileHandle)
    for name in zipFileData.namelist():
        if correct_extension(name):
            print("Unzipping:")
            print(name)
            zipFileData.extract(name, outPath)
    fileHandle.close()
    return 0

def file_downloaded(localFilePath):
    return os.path.isfile(localFilePath)

def img_to_geotiff(ftpBaseName, unzipDirectory):    
    imgFilePath = unzipDirectory + ftpBaseName + ".img"
    tifFilePath = unzipDirectory + ftpBaseName + ".tif"
    call(["gdal_translate","-of","Gtiff",imgFilePath,tifFilePath])
    return 0

def get_elevation(latlngCoord):
    ftpBaseName = get_ftpBaseName(latlngCoord)
    ftpZipFileName = ftpBaseName + ".zip"
    ftpFolderName = ftpBaseName + "/"

    url = config.usgsFtpPath + ftpZipFileName
    downloadDirectory = config.cachePath
    localFilePath = downloadDirectory + ftpZipFileName

    if file_downloaded(localFilePath):
        print("Already downloaded " + ftpZipFileName)
    else:
        print("Not yet downloaded.")
        print("Now downloading " + ftpZipFileName + "...")
        urllib.urlretrieve(url, localFilePath)
    
    unzipDirectory = downloadDirectory + ftpFolderName
    unzip_zipfile(localFilePath, unzipDirectory)

    img_to_geotiff(ftpBaseName, unzipDirectory)
    
    return 0

latlngCoord = (37, -76)

get_elevation(latlngCoord)

