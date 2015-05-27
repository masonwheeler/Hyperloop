import config

def round_nums(nums,ndigits):
    return [round(val,ndigits) for val in nums]

def round_points(nums,ndigits):
    return [round_nums(point,ndigits) for point in points]
 
