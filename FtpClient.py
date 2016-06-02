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
        # self.server_ip = ''
        # self.server_port = ''
        # self.user = ''
        # self.pwd = ''
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
                elif row[0] == 'port':
                    self.configs_dict['server_port'] = row[1]
                elif row[0] == 'user':
                    self.configs_dict['user'] = row[1]
                elif row[0] == 'pwd':
                    self.configs_dict['pwd'] = row[1]
                else:
                    self.logger.debug("Unknown config parameter found")

        self.logger.debug("Server IP: %s" % (self.configs_dict['server_ip']))
        self.logger.debug("Server Port: %s" % (self.configs_dict['server_port']))
        self.logger.debug("User: %s" % (self.configs_dict['user']))
        self.logger.debug("Pass: %s" % (self.configs_dict['pwd']))


myFTPClient = FtpClient()
myFTPClient.read_configs()




