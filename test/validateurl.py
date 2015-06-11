wsdlUrlValidationService = 'http://nimbex.cr.usgs.gov/requestValidationService/wsdl/RequestValidationService.wsdl'
try:
    #Query the Validation Service
    server = ServiceProxy(wsdl=wsdlUrlValidationService)
    xmlRequestString = "<REQUEST_SERVICE_INPUT><AOI_GEOMETRY><EXTENT><TOP>40.840</TOP><BOTTOM>40.815</BOTTOM><LEFT>-96.715</LEFT><RIGHT>-96.689</RIGHT></EXTENT><SPATIALREFERENCE_WKID/></AOI_GEOMETRY><LAYER_INFORMATION><LAYER_IDS>P1402XZ</LAYER_IDS></LAYER_INFORMATION><CHUNK_SIZE>250</CHUNK_SIZE><JSON></JSON></REQUEST_SERVICE_INPUT>"
    processAOI2ResponseDict = server.processAOI2(requestInfoXml=xmlRequestString)
    processAOI2Response = processAOI2ResponseDict['serviceResponse']
except:
    processAOI2Response = ""
    print("didnt work")
    #raise
# Process processAOI2Response here

