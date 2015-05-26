import pymongo

def connectToDatabase():
    awsMongodb = 'ec2-52-1-191-215.compute-1.amazonaws.com'
    mongoPort = '27017'
    mongoUrl = 'mongodb://' + awsMongodb + ':' + mongoPort
    global client
    client = pymongo.MongoClient(mongoUrl)        
    return client

def storePaths():

    return 0
