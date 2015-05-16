def join_lists(lists):
    return reduce(lambda x, y: x + y, lists)

print(join_lists([[1,2,3,4],[5,6,7,8]]))
