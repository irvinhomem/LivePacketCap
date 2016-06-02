import ftplib
import csv

class ftpClient(object):

    def __init__(self):
        # Configure Logging
        #logging.basicConfig(level=logging.INFO)
        #logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.INFO)
        #self.logger.setLevel(logging.DEBUG)
        self.logger.setLevel(logging.WARNING)

        self.configs_path = ''
        self.configs_dict = {}
        # self.server_ip = ''
        # self.server_port = ''
        # self.user = ''
        # self.pwd = ''

    def read_configs(self):
        csv_filepath = self.configs_path
        with open(csv_filepath, mode='r', newline='') as csvfile:
            domain_name_rdr = csv.reader(csvfile, delimiter=',')
            for row in domain_name_rdr:
                if row[0] == 'ip':
                    self.configs_dict['server_ip'] = row[1]
                elif row[0] == 'port':
                    self.configs_dict['server_ip'] = row[1]
                elif row[0] == 'user':
                    self.configs_dict['user'] = row[1]
                elif row[0] == 'pwd':
                    self.configs_dict['pwd'] = row[1]
                else:
                    self.logger.debug("Unknown config parameter found")

        self.logger.debug("Server IP: %s" % (self.configs_dict['server_ip']))
        self.logger.debug("Server Port: %s" % (self.configs_dict['server_ip']))
        self.logger.debug("User: %s" % (self.configs_dict['user']))
        self.logger.debug("Pass: %s" % (self.configs_dict['pwd']))




