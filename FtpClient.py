#from ftplib import FTP
import ftplib
import csv
import logging
import os
# from os import listdir
# from os.path import join
import sys
import random


class FtpClient(object):

    def __init__(self):
        # Configure Logging
        logging.basicConfig(level=logging.INFO)
        #logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        #self.logger.setLevel(logging.INFO)
        self.logger.setLevel(logging.DEBUG)
        #self.logger.setLevel(logging.WARNING)

        self.configs_path = './csv_files/ftp_creds.csv'
        self.configs_dict = {}
        self.server_ip = ''
        self.server_port = ''
        self.user = ''
        self.pwd = ''
        self.home_dir = '/'

        self.client = None
        self.logger.info("Created FTP Client ...")

    def read_configs(self):
        self.logger.info("Looking for config file ...")
        csv_filepath = self.configs_path
        with open(csv_filepath, mode='r', newline='') as csvfile:
            domain_name_rdr = csv.reader(csvfile, delimiter=',')
            self.logger.info("Opened config file ...")
            for row in domain_name_rdr:
                if row[0] == 'ip':
                    self.configs_dict['server_ip'] = row[1]
                    self.server_ip = row[1]
                elif row[0] == 'port':
                    self.configs_dict['server_port'] = row[1]
                    self.server_port = row[1]
                elif row[0] == 'user':
                    self.configs_dict['user'] = row[1]
                    self.user = row[1]
                elif row[0] == 'pwd':
                    self.configs_dict['pwd'] = row[1]
                    self.pwd = row[1]
                else:
                    self.logger.debug("Unknown config parameter found")

        self.logger.debug("Server IP: %s" % (self.configs_dict['server_ip']))
        self.logger.debug("Server Port: %s" % (self.configs_dict['server_port']))
        self.logger.debug("User: %s" % (self.configs_dict['user']))
        self.logger.debug("Pass: %s" % (self.configs_dict['pwd']))

    def login(self):
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

        # try:
        #     #dir_objs = self.client.mlsd(path='/', facts=['type', 'size', 'perm'])
        #     dir_objs = self.client.mlsd()
        #     self.logger.debug("Directory List Type: %s" % dir_objs)
        #
        #     for f in dir_objs:
        #         print(type(f[0]))
        # except ftplib.all_errors as exception:
        #     #self.logger.warn(exception.)
        #     raise

    def list_file_names(self):
        #list = self.client.nlst()
        #print(list[0])
        for file_name in self.client.nlst():
            print("Files and Directories: %s" % file_name)

    def list_directories(self):
        for file_name in self.client.nlst():
            try:
                self.client.cwd('/'+file_name)
                print("Directory: %s" % file_name)
            except ftplib.error_perm as detail:
                print("It's probably not a directory: %s : %s", (file_name, detail))

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
        self.logger.debug("Finished Creating directories")

    def ftp_upload_file(self, file_path):
        file_name = file_path.split('/')[-1]
        self.logger.debug("File being uploaded: %s" % file_path)
        ext = os.path.splitext(file_path)[1]
        if ext in (".txt", ".htm", ".html"):
            self.client.storlines("STOR " + "/" + file_name, open(file_path))
        else:
            self.client.storbinary("STOR " + "/" + file_name, open(file_path, "rb"), 1024)

        self.logger.debug("File upload SUCCESS: %s" % file_path)

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

        self.logger.debug("File upload SUCCESS: %s" % loc_file_path)

    def downloadText(self, filename, outfile=None):
        # fetch a text file
        if outfile is None:
            outfile = sys.stdout
        # use a lambda to add newlines to the lines read from the server
        self.client.retrlines("RETR " + filename, lambda s, w=outfile.write: w(s+"\n"))

    def downloadBinary(self, filename, outfile=None):
        # fetch a binary file
        self.logger.debug("Starting file download ...")
        # if outfile is None:
        #     outfile = sys.stdout
        # self.client.retrbinary("RETR " + "/" + filename, outfile.write)

        self.client.retrbinary("RETR " + "/" + filename, open(filename, 'wb').write)

        # fhandle = open(filename, 'wb')
        # self.client.retrbinary("RETR " + '/' + filename, fhandle.write)
        # fhandle.close()

        self.logger.debug("File download SUCCESS ...")

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
        self.logger.debug("Successfullu uploaded: %s to [%s]" % (rand_file, random_upload_dir))


myFTPClient = FtpClient()
myFTPClient.read_configs()
myFTPClient.login()


myFTPClient.listCurrDir()
myFTPClient.list_file_names()

#myFTPClient.ftp_Create_Dirs()

#myFTPClient.list_directories()

#myFTPClient.ftp_upload_file("Fake_Files/TPS Report.pdf")
myFTPClient.ftp_upload_file_spec_loc("/Level_1a/Level_2a/", "Fake_Files/TPS_Report.pdf")
#myFTPClient.ftp_upload_file_spec_loc("/Test/Test3/", "Fake_Files/TPS_Report.pdf")

#myFTPClient.downloadBinary("TPS Report.pdf")

#myFTPClient.change_to_Random_Dir()

#myFTPClient.upload_random_file_2_random_dir()

myFTPClient.ftp_log_out()



