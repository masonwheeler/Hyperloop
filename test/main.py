"""
Original Developer: Jonathan Ward
Purpose of Module: Main entry point for the route optimization code.
Last Modified: 7/16/15
Last Modified By: Jonathan Ward
Last Modification Purpose: To clarify Module usage.
"""


#Standard Modules:
import sys
import os

#Our Modules:
import core
import util
import config

if __name__ == "__main__":   
    config.cwd = os.getcwd()
    if config.testingMode:                
        core.pair_analysis("Los_Angeles","San_Francisco")
    #    core.pair_analysis("Dallas","Austin")
    #    core.pair_analysis("Portland","San_Francisco")
    #    core.pair_analysis("New_York", "Boston")
    else:
        if (len(sys.argv) == 1):
            startCity = raw_input("Input start city or start lat lon pair: ")
            endCity = raw_input("Input end city or end lat lon pair: ")
            if config.verboseMode: 
                print("You entered: " + startCity + " and " + endCity)
            core.pair_analysis(startCity,endCity)
        elif (len(sys.argv) == 3):
            startCity = sys.argv[1]
            endCity = sys.argv[2]
            if config.verboseMode:
                print("You entered: " + startCity + " and " + endCity)
            core.pair_analysis(startCity,endCity)
        else:        
            print(" ")
            print("Input start city and end city names in quotation marks.")
            print("E.g.")            
            print("""python main.py "Los Angeles" "San Francisco" """)
            print(" ")

    
