import core
import sys

if __name__ == "__main__":    
    if (len(sys.argv) == 1):
        startCity = input("Input start city: ")
        endCity = input("Input end city: ")
        core.pairAnalysis(startCity,endCity)
    elif (len(sys.argv) == 3):
        startCity = sys.argv[1]
        endCity = sys.argv[2]
        core.pairAnalysis(startCity,endCity)
    else:        
        print(" ")
        print("Input start city and end city names in quotation marks.")
        print("E.g.")            
        print("""python main.py "Los Angeles" "San Francisco" """)
        print(" ")

    
