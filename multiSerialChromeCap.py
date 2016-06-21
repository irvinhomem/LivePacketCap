import pyshark
from datetime import datetime
#from subprocess import call
import subprocess
import multiprocessing as mp
import time
import os
import errno
import csv
import random
#import threading
#subprocess.run #python 3.5

import logging

#########################################################################
#    More or less working:                                              #
#       - Remember to check the file paths of:
#           - Where the domain names are being picked from              #
#           - Where the pcap is going to be stored
#       - Check that the correct Network interface is being used [IMPORTANT]
#           - Otherwise tshark will fail
#########################################################################

class multiSerialChromeWebCap(object):

    def __init__(self):
        # Configure Logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        #self.logger.setLevel(logging.INFO)
        self.logger.setLevel(logging.DEBUG)
        #self.logger.setLevel(logging.WARNING)

        #self.theCsvFilePath = 'csv_files/top-5.csv'
        self.theCsvFilePath = 'csv_files/only-http-50-dyn-stat.csv'
        self.myNic = "eno16777736"         #"eth0"
        self.cap = None
        self.procCapture = None
        self.web_process = None
        self.domain_name_list = []
        self.all_domains = []
        self.google_chrome_params = []

    def read_csv_file(self):
        csv_filepath = self.theCsvFilePath
        with open(csv_filepath, mode='r', newline='') as csvfile:
            domain_name_rdr = csv.reader(csvfile, delimiter=',')
            for row in domain_name_rdr:
                #if row[2] == "dyn":    # For dynamic domains
                if row[2] == "static":  # For static domains
                    #self.all_domains.append(row[1])
                    self.all_domains.append(row[0])

    def make_sure_path_exists(self, path):
        try:
            os.makedirs(path)
            print("Path Created: ", path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def run_capture(self):
        self.logger.debug("###########################################################")
        self.logger.debug("Starting Capture (Inside Capture function)...")
        self.logger.debug("###########################################################")
        name = mp.current_process().name
        self.logger.info("%s Starting" % name)

        self.cap.sniff()

    def get_5_random_domains(self):
        self.domain_name_list = random.sample(self.all_domains, 5)

    def createFileName(self):
        self.get_5_random_domains()
        domain_list = self.domain_name_list

        file_prefix = ""
        for domain in domain_list:
            file_prefix = file_prefix + domain[0:3] + "-"
        three_char_prefix = file_prefix.strip("-")
        return three_char_prefix

    def run_Capture_Single_File(self):
        self.logger.debug("###########################################################")
        self.logger.debug("Starting Capture (Inside Capture function)...")
        self.logger.debug("###########################################################")
        name = mp.current_process().name
        self.logger.info("%s Starting" % name)

        domain_list = self.domain_name_list

        f_name_domains = self.createFileName()

        my_oFile = f_name_domains + "-" + datetime.strftime(datetime.now(), "%Y-%m-%d-T%H%M%S") + ".pcapng"
        #my_filePath = '/home/irvin/pcaps/' + f_name_domains + '/'
        my_filePath = '/home/student/pcaps/HTTP/'

        self.logger.info("Sniffing Interface : %s" % self.myNic)
        self.logger.info("Output File name : %s" % my_oFile)
        self.logger.debug("File with Path : %s" % (my_filePath + my_oFile))

        # tshark -w (write output file) and pyshark output_file don't create directories
        # tshark -w (write output file) and pyshark output_file need an absolute file path (they don't seem to recognize relative file paths)
        # We need to create the directory where the file will be saved within the /tmp/pcaps/ directory
        self.make_sure_path_exists(my_filePath)

        # Setup capture
        self.cap = pyshark.LiveCapture(interface=self.myNic, output_file=my_filePath+my_oFile)
        self.logger.debug("Pyshark LiveCapture Object type: %s" % type(self.cap))
        #self.cap.sniff()

    def run_Single_Capture_Multi_Domain(self):
        #Set up Capture Sniffing file/process
        self.run_Capture_Single_File()
        self.logger.info("Ready to Start Capture Process ...")
        # cap.sniff()
        #self.procCapture = mp.Process(name='Capture_process/Sniffing service', target=self.run_Capture_Single_File)
        # Get the Sniffing process ready and START it
        self.procCapture = mp.Process(name='Capture_process/Sniffing service', target=self.cap.sniff)
        self.procCapture.start()
        self.logger.info("Capture Process is running: %s" % self.procCapture.is_alive())
        self.logger.info("Capture Process ID: %i" % self.procCapture.pid)

        self.logger.debug("Capture started...")
        # Give it 5 seconds to set up the capture interface
        time.sleep(3)

        for domain_url in self.domain_name_list:
            self.google_chrome_params = ['google-chrome','--incognito', domain_url]
            my_args = [self.google_chrome_params, ]
            self.procWebRequest = mp.Process(name='Chrome Browser process/ service',
                                             target=self.run_chrome_browser, args=my_args)
            self.procWebRequest.start()
            self.procWebRequest.join()

        #self.procCapture.join()

    def closeSniffer(self):
        self.cap.close()
        print("Closed sniffer.")
        self.procCapture.terminate()
        print("... Ended Capture.")

    def run_chrome_browser(self, web_req_params):
        self.logger.debug("############################################################")
        self.logger.debug("Starting Chrome ...")
        self.logger.debug("###########################################################")
        name = mp.current_process().name
        self.logger.debug("%s Starting" % name)
        web_process = subprocess.Popen(web_req_params)

        self.logger.info("Chrome Process ID: %i [%s]" % (web_process.pid, web_req_params[2]))
        self.logger.info("PyShark LiveCap Type: %s" % type(self.cap))
        try:
            streamdata = web_process.communicate(timeout=20)[0]

            #rc = web_process.returncode
            print("Success / Return code = ", web_process.returncode)
            print("Finished Chrome load page ...")

        except subprocess.TimeoutExpired:
            print("Caught Timeout Error : Killing process Pid: %i [%s]" % (web_process.pid, web_req_params[2]))
            web_process.terminate()
            #self.logger.debug("Web Capture termination ReturnCode: %i " % web_process.returncode)
        finally:
            if web_process.returncode == 8:
                print("Finished HAPPILY.")
                # self.cap.close()
                # print("Closed sniffer.")
                # self.procCapture.terminate()
                # print("... Ended Capture.")
            elif web_process.returncode == 0:
                web_process.wait(timeout=30)
                print("Waited 30 secs for timeout...")

                # self.cap.close()
                # print("Closed sniffer.")
                # self.procCapture.terminate()
                # print("... Ended Capture.")
            else:
                #time.sleep(20)
                #self.logger.debug("Web Capture termination ReturnCode: %i " % web_process.returncode)
                print("Past 20s timeout... Killing process ID: %i [%s]" % (web_process.pid, web_req_params[2]))
                web_process.terminate()

                # self.cap.close()
                # print("Closed sniffer.")
                # self.procCapture.terminate()
                # print("... Ended Capture.")

    def run_cap_n_chrome(self, domain_name):
        #domain_name = "weibo.com"
        domain_url = "http://" + domain_name
        #google_chrome_params = []
        self.google_chrome_params = ['google-chrome','--incognito', domain_url]
        self.logger.debug("Chrome Command Parameters: %s" % self.google_chrome_params)

        my_oFile = domain_name + "-" + datetime.strftime(datetime.now(), "%Y-%m-%d-T%H%M%S") + ".pcapng"
        my_filePath = '/home/irvin/pcaps/' + domain_name + '/'

        self.logger.info("Sniffing Interface : %s" % self.myNic)
        self.logger.info("Current Domain : %s" % domain_name)
        self.logger.info("Output File name : %s" % my_oFile)
        self.logger.debug("File with Path : %s" % (my_filePath + my_oFile))

        # tshark -w (write output file) and pyshark output_file don't create directories
        # tshark -w (write output file) and pyshark output_file need an absolute file path (they don't seem to recognize relative file paths)
        # We need to create the directory where the file will be saved within the /tmp/pcaps/ directory
        self.make_sure_path_exists(my_filePath)

        # Setup capture
        self.cap = pyshark.LiveCapture(interface=self.myNic, output_file=my_filePath+my_oFile)
        self.logger.debug("Pyshark LiveCapture Object type: %s" % type(self.cap))

        self.logger.info("Ready to Start Capture Process ...")
        #cap.sniff()
        self.procCapture = mp.Process(name='Capture_process/Sniffing service', target=self.run_capture)
        self.procCapture.start()
        self.logger.info("Capture Process is running: %s" % self.procCapture.is_alive())
        self.logger.info("Capture Process ID: %i" % self.procCapture.pid)

        self.logger.debug("Capture started...")
        #Give it 5 seconds to set up the capture interface
        time.sleep(3)
        my_args = [self.google_chrome_params,]
        self.procWebRequest = mp.Process(name='Chrome Browser process/ service',
                                    target=self.run_chrome_browser, args=my_args)
        self.procWebRequest.start()

if __name__ == "__main__":
    multi_serial_web_cap = multiSerialChromeWebCap()

    multi_serial_web_cap.read_csv_file()

    # # Run capture and loop through domains
    # for list_item in serial_web_cap.domain_name_list:
    #     print(list_item)
    #     serial_web_cap.run_cap_n_chrome(list_item)

    multi_serial_web_cap.run_Single_Capture_Multi_Domain()

    multi_serial_web_cap.closeSniffer()



