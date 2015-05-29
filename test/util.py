import config
import util

global ndigits
ndigits = config.ndigits

def round_num(num):
    return round(num,ndigits)

def round_nums(nums):
    return [round_num(num) for num in nums]

def round_points(points):
    return [round_nums(point) for point in points]
 
