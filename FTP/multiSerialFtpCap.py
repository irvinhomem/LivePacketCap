#from ftplib import FTP
import ftplib
import csv
import logging
import os
# from os import listdir
# from os.path import join
import sys
import random
import errno
from datetime import datetime
import time

import pyshark
import multiprocessing as mp
import subprocess
import getpass

class FtpClientTest(object):

    def __init__(self):
        # Configure Logging
        logging.basicConfig(level=logging.INFO)
        #logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        #self.logger.setLevel(logging.INFO)
        self.logger.setLevel(logging.DEBUG)
        #self.logger.setLevel(logging.WARNING)

        configs_path = 'creds/ftp_creds.csv'
        self.logger.debug("Current Working Dir Parent: %s" % os.path.realpath(os.path.join(os.getcwd(), os.pardir)))
        parent_dir = os.path.realpath(os.path.join(os.getcwd(), os.pardir))
        self.logger.debug("CWD Grand Parent: %s" % os.path.realpath(os.path.join(parent_dir, os.pardir)))
        grandparent_dir = os.path.realpath(os.path.join(parent_dir, os.pardir))
        self.configs_path = os.path.join(grandparent_dir, configs_path)

        self.configs_dict = {}
        self.server_ip = ''
        self.server_port = ''
        self.user = ''
        self.pwd = ''
        self.home_dir = '/'

        self.client = None

        # Remember to change ethernet  adapter name !!!!
        self.myNic = 'ens33'   #"eth0"
        self.cap = None
        self.procCapture = None
        self.logger.info("Created FTP Client ...")

    def read_configs(self):
        self.logger.info("Looking for config file ...")
        csv_filepath = self.configs_path
        with open(csv_filepath, mode='r', newline='') as csvfile:
            domain_name_rdr = csv.reader(csvfile, delimiter=',')
            self.logger.info("Opened config file ...")
            for row in domain_name_rdr:
                if row[0] == 'ip':
                    self.configs_dict['server_ip'] = row[1].strip()
                    self.server_ip = row[1].strip()
                elif row[0] == 'port':
                    self.configs_dict['server_port'] = row[1].strip()
                    self.server_port = row[1].strip()
                elif row[0] == 'user':
                    self.configs_dict['user'] = row[1].strip()
                    self.user = row[1].strip()
                elif row[0] == 'pwd':
                    self.configs_dict['pwd'] = row[1].strip()
                    self.pwd = row[1].strip()
                else:
                    self.logger.debug("Unknown config parameter found")

        self.logger.debug("Server IP: %s" % (self.configs_dict['server_ip']))
        self.logger.debug("Server Port: %s" % (self.configs_dict['server_port']))
        self.logger.debug("User: %s" % (self.configs_dict['user']))
        self.logger.debug("Pass: %s" % (self.configs_dict['pwd']))

    def make_sure_path_exists(self, path):
        try:
            os.makedirs(path)
            print("Path Created: ", path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def setup_connection(self):
        # ip = self.configs_dict['server_ip']
        # port = self.configs_dict['server_port']
        # username = self.configs_dict['user']
        # pwd = self.configs_dict['pwd']

        self.client = ftplib.FTP(host=self.server_ip)       #FTP(host=ip, user=username, passwd=pwd)
        self.client.login(user=self.user, passwd=self.pwd)
        self.logger.debug("Welcome Message: %s" % self.client.getwelcome())
        #self.client.cwd(self.home_dir)

    def listCurrDir(self):
        self.logger.debug("Working Directory: %s" % self.client.pwd())
        self.client.dir()

    def list_files_and_dirs(self):
        for file_name in self.client.nlst():
            print("Files and Directories: %s" % file_name)

    def list_directories(self):
        for file_name in self.client.nlst():
            try:
                self.client.cwd('/'+file_name)
                print("Directory: %s" % file_name)
            except ftplib.error_perm as detail:
                print("It's probably not a directory: %s : %s", (file_name, detail))

    def list_only_files(self):
        files = []

        try:
            files = self.client.nlst()
        except ftplib.error_perm as err_resp:
            if str(err_resp) == "550 No files found":
                print("No files in this directory")
            else:
                raise
        self.logger.debug("Num of FILES in DIR: %i" % len(files))
        for f_name in files:
            self.logger.debug("FILE: %s" % f_name)

        return files

    def ftp_log_out(self):
        self.client.quit()

    def ftp_Create_Dirs(self):
        level1_lbls = "abcde"
        level2_lbls = "abc"
        for char in level1_lbls:
            self.client.mkd("Level_1" + char)
            self.client.cwd("Level_1" + char)
            for char2 in level2_lbls:
                self.client.mkd("Level_2" + char2)
            self.client.cwd('/')
        self.logger.info("Finished Creating directories")

    def ftp_upload_file(self, file_path):
        file_name = file_path.split('/')[-1]
        self.logger.info("File being uploaded: %s" % file_path)
        ext = os.path.splitext(file_path)[1]
        if ext in (".txt", ".htm", ".html"):
            self.client.storlines("STOR " + "/" + file_name, open(file_path))
        else:
            self.client.storbinary("STOR " + "/" + file_name, open(file_path, "rb"), 1024)

        self.logger.info("File upload SUCCESS: %s" % file_path)

    def ftp_upload_file_spec_loc(self, ftp_path, loc_file_path):
        file_name = loc_file_path.split('/')[-1]
        self.logger.debug("File being uploaded: %s" % loc_file_path)
        ext = os.path.splitext(loc_file_path)[1]
        self.client.cwd(ftp_path)
        #self.client.mkd('Test')
        #self.client.cwd('Test')
        #self.client.mkd('Test3')
        #self.client.cwd('Test3')

        self.logger.debug("Current FTP Directory for Random UPLOAD: %s" % self.client.pwd())

        #ftp_stor_cmd = "STOR %s%s" % (ftp_path, file_name)
        ftp_stor_cmd = "STOR %s" % (file_name)
        self.logger.debug("FTP upload command: %s" % ftp_stor_cmd )
        if ext in (".txt", ".htm", ".html"):
            #self.logger.debug("FTP upload command: STOR %s%s" % (ftp_path, file_name))
            self.client.storlines(ftp_stor_cmd, open(loc_file_path))
        else:
            #self.logger.debug("FTP upload binary command: STOR %s%s" % (ftp_path, file_name))
            #self.client.storbinary("STOR " + ftp_path + file_name, open(loc_file_path, "rb"), 1024)
            self.client.storbinary(ftp_stor_cmd, open(loc_file_path, "rb"), 1024)

        self.logger.info("File upload SUCCESS: %s" % loc_file_path)

    def downloadText(self, filename, outfile=None):
        # fetch a text file
        if outfile is None:
            outfile = sys.stdout
        # use a lambda to add newlines to the lines read from the server
        self.client.retrlines("RETR " + filename, lambda s, w=outfile.write: w(s+"\n"))

    def downloadBinary(self, filename, outfile=None):
        # fetch a binary file
        self.logger.debug("Starting file download ...")

        self.make_sure_path_exists("Downloads/")
        self.client.retrbinary("RETR " + filename, open("Downloads/" +filename, 'wb').write)

        self.logger.info("File download SUCCESS ...")

    # def absoluteFilePaths(self, directory):
    #     for dirpath, _, filenames in os.walk(directory):
    #         for f in filenames:
    #             yield os.path.abspath(os.path.join(dirpath, f))

    def change_to_Random_Dir(self):
        self.logger.debug("Current DIR: %s" % self.client.pwd())
        level1_dirs = []
        for file_name in self.client.nlst():
            try:
                self.client.cwd('/' + file_name)
                level1_dirs.append(file_name)
                self.logger.debug("Directory [L-1]: %s" % file_name)
            except ftplib.error_perm as detail:
                self.logger.debug("It's probably not a directory [L-1]: %s : %s" % (file_name, detail))
        self.logger.debug("Number of L1-Dirs: %i" % len(level1_dirs))

        randomly_sampled_L1_dir = random.sample(level1_dirs, 1)[0]
        self.client.cwd('/' + randomly_sampled_L1_dir)
        self.logger.debug("Current Level-1 DIR selected: %s" % self.client.pwd())

        level2_dirs = []
        for file_name_l2 in self.client.nlst():
            try:
                self.client.cwd('/' + randomly_sampled_L1_dir + '/' +file_name_l2)
                level2_dirs.append(file_name_l2)
                self.logger.debug("Directory [L-2]: %s" % file_name_l2)
            except ftplib.error_perm as detail:
                self.logger.debug("It's probably not a directory [L-2]: %s : %s" % (file_name_l2, detail))
        self.logger.debug("Number of L2-Dirs: %i" % len(level2_dirs))

        rand_L2_dir = random.sample(level2_dirs, 1)[0]
        self.client.cwd('/' + randomly_sampled_L1_dir + '/' + rand_L2_dir)
        self.logger.debug("Current Level-2 DIR selected: %s" % self.client.pwd())
        return self.client.pwd() + '/'

    def upload_random_file_2_random_dir(self):
        #--> Select Random File
        # from os import listdir
        # from os.path import isfile, join
        mypath = os.getcwd() + '/Fake_Files/'
        onlyfiles = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
        self.logger.debug("Number of FILES in directory: %i " % len(onlyfiles))

        rand_file = random.sample(onlyfiles, 1)[0]
        path_of_rand_file = mypath + rand_file
        self.logger.debug("Local File to UPLOAD: %s" % path_of_rand_file)

        #-->Select Random Location to upload to
        random_upload_dir = self.change_to_Random_Dir()
        self.logger.debug("Random path on FTP Server: %s" % random_upload_dir)

        self.ftp_upload_file_spec_loc(random_upload_dir, path_of_rand_file)
        self.logger.info("Successfully uploaded: %s to [%s]" % (rand_file, random_upload_dir))

    def download_from_random_dir(self):
        ###--> Get all directories (Level1 and Level2)
        #--> Change to a Random Directory
        random_dir = self.change_to_Random_Dir()

        #--> Select a directory, list files and select a random file
        self.logger.debug("Current random DIR for DOWNLOAD: %s" % self.client.pwd())
        #self.client.cwd(random_dir)

        if len(self.list_only_files()) > 0:
            if len(random.sample(self.list_only_files(), 1)) > 0:
                selected_file = random.sample(self.list_only_files(), 1)[0]
                self.logger.debug("Preparing to downlaod: %s" % selected_file)
                self.downloadBinary(selected_file)      #--> Download the file to the downloads directory
                self.logger.debug("DOWNLOAD SUCCESS: %s " % selected_file)
        else:
            self.logger.debug("ZERO files in DIR to download !")

    def setup_Capture(self, ftp_type):
        self.logger.debug("Current User: %s", getpass.getuser())
        curr_user = getpass.getuser()

        my_filePath = '/home/'+curr_user+'/pcaps/FTP/'
        my_oFile = "FTP-" +ftp_type + "-" + datetime.strftime(datetime.now(), "%Y-%m-%d-T%H%M%S") + ".pcapng"
        self.cap = pyshark.LiveCapture(interface=self.myNic, output_file=my_filePath+my_oFile)

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

    def run_Capture(self, ftp_type):

        #Set up Capture
        self.setup_Capture(ftp_type)

        self.procCapture = mp.Process(name='Capture_process/Sniffing service', target=self.cap.sniff)
        self.procCapture.start()
        self.logger.info("Capture Process is running: %s" % self.procCapture.is_alive())
        self.logger.info("Capture Process ID: %i" % self.procCapture.pid)

        self.logger.debug("Capture started...")
        # Give it 3 seconds to set up the capture interface
        time.sleep(3)

    def run_Single_Cap_Multi_DL_Random(self):

        #Populate list with 5 random Dirs to download from
        random_dir_list = []
        for i in range(5):
            rand_dir = self.change_to_Random_Dir()
            random_dir_list.append(rand_dir)
            self.logger.debug("RANDOM DIR %i :----->>>> %s" %(i, rand_dir))
            self.client.cwd('/')    #Change back to home for next round

        self.logger.debug("Number of RANDOM DIRs: %i" % len(random_dir_list))

        #####
        # Ideally we can log out here and login later in order to also capture the login process
        #self.ftp_log_out()
        #####

        self.run_Capture('DL')

        # #LOGIN HERE AGAIN***********
        # self.login()

        #Start off with the FTP root Directory
        self.client.cwd('/')

        # #LIST CURRENT DIRECTORY CONTENTS ********
        # self.listCurrDir()

        #Run random download from random dir 5 times
        for count, random_dir in enumerate(random_dir_list):
            self.client.cwd(random_dir)
            self.logger.debug("Current random DIR for DOWNLOAD: %s" % self.client.pwd())
            if len(self.list_only_files()) > 0:
                if len(random.sample(self.list_only_files(), 1)) > 0:
                    self.logger.debug("******************************")
                    self.logger.debug("Starting Random DL: %i" % count)
                    self.logger.debug("******************************")
                    selected_file = random.sample(self.list_only_files(), 1)[0]
                    self.logger.debug("Preparing to download: %s" % selected_file)
                    self.downloadBinary(selected_file)  # --> Download the file to the downloads directory
                    self.logger.debug("DOWNLOAD SUCCESS: %s " % selected_file)
                    self.logger.debug("******************************")
                    self.logger.debug("COMPLETED Random DL: %i" % count)
                    self.logger.debug("******************************")
            else:
                self.logger.debug("ZERO files in DIR to download !")

        self.logger.debug("Completed RANDOM [Multi] DOWNLOADS")

        #self.procCapture.join()
        self.closeSniffer()

    def run_Single_Cap_Multi_Upload_Random(self):
        # --> Select Random Files from the "Fake Files" directory
        # from os import listdir
        # from os.path import isfile, join
        mypath = os.getcwd() + '/Fake_Files/'
        onlyfiles = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
        self.logger.debug("Number of FILES in directory: %i " % len(onlyfiles))

        # Select 5 random files to upload
        rand_file_list = random.sample(onlyfiles, 5)
        self.logger.debug("Number of RANDOM FILES: %i" % len(rand_file_list))

        # Select 5 random upload paths
        random_dir_list = []
        for i in range(5):
            rand_dir = self.change_to_Random_Dir()
            random_dir_list.append(rand_dir)
            self.logger.debug("RANDOM DIR %i :----->>>> %s" % (i, rand_dir))
            self.client.cwd('/')  # Change back to home for next round

        self.logger.debug("Number of RANDOM DIRs: %i" % len(random_dir_list))

        #Run Capture
        self.run_Capture("UL")

        for i, rand_ftp_path in enumerate(random_dir_list):
            self.logger.debug("--------------------------------")
            self.logger.debug("STARTING FTP UPLOAD: %i" % i)
            self.logger.debug("--------------------------------")

            self.logger.debug("Local File to UPLOAD: %s" % rand_file_list[i])
            path_of_rand_file = mypath + rand_file_list[i]
            self.logger.debug("Path of Local File to UPLOAD: %s" % path_of_rand_file)
            self.logger.debug("Random path on FTP Server: %s" % rand_ftp_path)

            self.ftp_upload_file_spec_loc(rand_ftp_path, path_of_rand_file)

            self.logger.debug("--------------------------------")
            self.logger.info("Successfully uploaded: %s to [%s]" % (rand_file_list[i], rand_ftp_path))
            self.logger.debug("--------------------------------")

        self.logger.debug("Completed RANDOM [Multi] UPLOADS")

        self.closeSniffer()

    def closeSniffer(self):
        self.cap.close()
        print("Closed sniffer.")
        self.procCapture.terminate()
        print("... Ended Capture.")


myFTPClient = FtpClientTest()
myFTPClient.read_configs()
myFTPClient.setup_connection()

myFTPClient.listCurrDir()
##--
#myFTPClient.list_files_and_dirs()

#myFTPClient.ftp_Create_Dirs()

#myFTPClient.list_directories()

#myFTPClient.ftp_upload_file("Fake_Files/TPS Report.pdf")
#myFTPClient.ftp_upload_file_spec_loc("/Level_1a/Level_2a/", "Fake_Files/TPS_Report.pdf")
#myFTPClient.ftp_upload_file_spec_loc("/Test/Test3/", "Fake_Files/TPS_Report.pdf")

#myFTPClient.downloadBinary("TPS Report.pdf")

#myFTPClient.change_to_Random_Dir()

#myFTPClient.upload_random_file_2_random_dir()

#myFTPClient.download_from_random_dir()

myFTPClient.run_Single_Cap_Multi_DL_Random()        # <<<<<======= DOWNLOAD

#myFTPClient.run_Single_Cap_Multi_Upload_Random()        # <<<<<======== UPLOAD

myFTPClient.ftp_log_out()



