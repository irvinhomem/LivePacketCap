import multiprocessing as mp
#import time

##############################
## THIS ACTUALLY WORKS   #####
##############################

def firstFunction():
    name = mp.current_process().name
    print("In 1st Function")
    print("%s Starting" % name)
    #time.sleep(4)
    z = 0
    for i in range(100000000):
        z=z+i
    print("z = %i :: Finished LOOOONG process ..." % z)
    print("%s Exiting" % name)

def secondFunction():
    name = mp.current_process().name
    print("In 2nd Function")
    print("%s Starting" % name)
    #time.sleep(2)
    print("%s Exiting" % name)

function1 = mp.Process(name='my_service', target=firstFunction)
function2 = mp.Process(name='Function 2', target=secondFunction)

function1.start()
function2.start()
