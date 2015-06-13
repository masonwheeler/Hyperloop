import core
import util
import sys

if __name__ == "__main__":    
    if (len(sys.argv) == 1):
        startCity = raw_input("Input start city or start lat lon pair: ")
        #start
        endCity = raw_input("Input end city or end lat lon pair: ")
        print("You entered: " + startCity + " and " + endCity)
        core.pair_analysis(startCity,endCity)
    elif (len(sys.argv) == 3):
        startCity = sys.argv[1]
        endCity = sys.argv[2]
        print("You entered: " + startCity + " and " + endCity)
        core.pair_analysis(startCity,endCity)
    else:        
        print(" ")
        print("Input start city and end city names in quotation marks.")
        print("E.g.")            
        print("""python main.py "Los Angeles" "San Francisco" """)
        print(" ")

    
