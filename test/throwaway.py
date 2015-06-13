import time

def testing():
    t0 = time.clock()
    t1 = time.clock()
    print(t1 - t0)
    t2 = time.time()
    time.sleep(5)
    t3 = time.time()
    print(t3 - t2)

testing()
