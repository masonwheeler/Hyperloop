import urllib2



"""
# submit a job to the Download Service
chunkUrl = "http://nimbex.cr.usgs.gov/axis2/services/DownloadService/initiateDownload?PL=HOIT&MSU=http://ims.cr.usgs.gov/servlet/com.esri.esrimap.Esrimap&MSS=USGS_EDC_Ortho_Urban&MSL=Historical_Orthoimagery_Tiles&MSEA=WEBMAP.ortho_historical_tiles.OBJECTID&DLS=http://edclxs77.cr.usgs.gov/ortho&FID=ZI&ARC=ZI&DLA=WEBMAP.ortho_historical_tiles.FILENAME&EIDL=13428&siz=57&lft=-105.023371493578&bot=39.8129764994474&rgt=-105.005841493561&top=39.82649349946&ORIG=null"

try:
    page = urllib2.urlopen(chunkUrl)
except IOError, e:
    if hasattr(e, 'reason'):
        print 'We failed to reach a server.'
        print 'Reason: ', e.reason
    elif hasattr(e, 'code'):
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code
    else:
        result = page.read()
        print result
        # parse response for request id
    if result.find("VALID>false") > -1:
        # problem with initiateDownload request string
        # handle that here
        print("problem with initiateDownload request string")
    else: # downloadRequest successfully entered into queue
        startPos = result.find("<ns:return>") + 11
        endPos = result.find("</ns:return>")
        requestID = result[startPos:endPos]
        print requestID

# call Download service with request id to get status
downloadStatusUrl = "http://nimbex.cr.usgs.gov/axis2/services/DownloadService/getStatus?downloadID=20090608.150009516.152061160045"
try:
    page2 = urllib2.urlopen(downloadStatusUrl)
except IOError, e:
    if hasattr(e, 'reason'):
        print 'We failed to reach a server.'
        print 'Reason: ', e.reason
"""
