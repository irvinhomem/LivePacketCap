#from ftplib import FTP
import ftplib
import csv
import logging


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
                self.client.cwd(file_name)
                print("Directory: %s" % file_name)
            except ftplib.error_perm as detail:
                print("It's probably not a directory:", detail)

    def ftp_log_out(self):
        self.client.quit()


myFTPClient = FtpClient()
myFTPClient.read_configs()
myFTPClient.login()


myFTPClient.listCurrDir()
myFTPClient.list_file_names()
myFTPClient.list_directories()

myFTPClient.ftp_log_out()



