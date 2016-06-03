#from ftplib import FTP
import ftplib
import csv
import logging
import os
import sys


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

    def ftp_upload_file(self, file_path):
        file_name = file_path.split('/')[-1]
        self.logger.debug("File being uploaded: %s" % file_path)
        ext = os.path.splitext(file_path)[1]
        if ext in (".txt", ".htm", ".html"):
            self.client.storlines("STOR " + "/" + file_name, open(file_path))
        else:
            self.client.storbinary("STOR " + "/" + file_name, open(file_path, "rb"), 1024)

        self.logger.debug("File upload SUCCESS: %s" % file_path)

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



myFTPClient = FtpClient()
myFTPClient.read_configs()
myFTPClient.login()


myFTPClient.listCurrDir()
myFTPClient.list_file_names()
myFTPClient.list_directories()

#myFTPClient.ftp_upload_file("Fake_Files/TPS Report.pdf")

#myFTPClient.downloadBinary("TPS Report.pdf")

myFTPClient.ftp_log_out()



