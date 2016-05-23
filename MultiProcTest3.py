import multiprocessing as mp
import pyshark
#import time
from datetime import datetime

class MultiProcTest(object):

    def __init__(self):
        print("Init function mpTest ...")
        self.myNic = 'eth0'
        domain_name = 'google.com'
        my_oFile = domain_name + "-" +datetime.strftime(datetime.now(), "%Y-%m-%d-T%H%M%S") + ".pcapng"
        my_filePath = '/home/irvin/pcaps/' + domain_name + '/'
        self.cap = pyshark.LiveCapture(interface=self.myNic, output_file=my_filePath + my_oFile)
        #self.myNic = "eth0"
        #self.myCap = pyshark.LiveCapture(interface=self.myNic, output_file=my_filePath+my_oFile)

    def firstFunction(self):
        name = mp.current_process().name
        print("In 1st Function")
        print("%s Starting" % name)
        #time.sleep(4)
        z = 0
        for i in range(100000000):
            z=z+i
        print("z = %i :: Finished long process ..." % z)
        print("%s Exiting" % name)

    def sniffing(self):
        name = mp.current_process().name
        print("%s Starting" % name)
        self.cap.sniff()
        print("%s Exiting" % name)

    def secondFunction(self):
        name = mp.current_process().name
        print("In 2nd Function")
        print("%s Starting" % name)
        #time.sleep(2)
        print("%s Exiting" % name)

#if __name__ == "main":
mpTest = MultiProcTest()
print("Created multi-process object")

sniffFunction = mp.Process(name='Sniffing_service', target=mpTest.sniffing)
function1 = mp.Process(name='my_service_function_1', target=mpTest.firstFunction)
function2 = mp.Process(name='Function 2', target=mpTest.secondFunction)

sniffFunction.start()
function1.start()
function2.start()
