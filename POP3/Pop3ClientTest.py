import logging
import poplib
import os
import csv
import random

class Pop3ClientTest(object):

    def __init__(self):
        # Configure Logging
        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.INFO)
        self.logger.setLevel(logging.DEBUG)
        # self.logger.setLevel(logging.WARNING)

        # Get configs from config file (CSV)
        configs_path = "configs/pop3_configs.csv"
        self.configs_path = os.path.join(
            os.path.realpath(os.path.join(os.getcwd(), os.pardir)), configs_path)
        self.configs_dict = {}

        #Get creds from creds file (CSV)
        creds_path = "creds/email_list.csv"
        self.logger.debug("Current Working Dir Parent: %s" % os.path.realpath(os.path.join(os.getcwd(), os.pardir)))
        parent_dir = os.path.realpath(os.path.join(os.getcwd(), os.pardir))
        self.logger.debug("CWD Grand Parent: %s" % os.path.realpath(os.path.join(parent_dir, os.pardir)))
        grandparent_dir = os.path.realpath(os.path.join(parent_dir, os.pardir))
        self.creds_path = os.path.join(grandparent_dir, creds_path)
        self.creds_list = []

        self.pop3_serv_fqdn = ''
        self.pop3_serv_port = ''

        self.pop3_user = ''
        self.pop3_pass = ''

    def read_configs(self):
        self.logger.info("Looking for config file ...")
        csv_filepath = self.configs_path
        # Make sure to strip the spaces from the credentials being added from the file into the configs object and obj parameters
        with open(csv_filepath, mode='r', newline='') as csvfile:
            domain_name_rdr = csv.reader(csvfile, delimiter=',')
            self.logger.info("Opened config file ...")
            for row in domain_name_rdr:
                if row[0] == 'fqdn':
                    self.configs_dict['server_fqdn'] = row[1].strip()
                    self.pop3_serv_fqdn = row[1].strip()
                elif row[0] == 'port':
                    self.configs_dict['server_port'] = row[1].strip()
                    self.pop3_serv_port = row[1].strip()
                else:
                    self.logger.debug("Unknown config parameter found")

        self.logger.debug("Server FQDN: [%s]" % (self.configs_dict['server_fqdn']))
        self.logger.debug("Server Port: [%s]" % (self.configs_dict['server_port']))

    def read_creds(self):
        self.logger.info("Looking for creds file ...")
        csv_filepath = self.creds_path
        # Make sure to strip the spaces from the credentials being added from the file into the configs object and obj parameters
        with open(csv_filepath, mode='r', newline='') as csvfile:
            domain_name_rdr = csv.reader(csvfile, delimiter=',')
            self.logger.info("Opened creds file ...")
            for i, row in enumerate(domain_name_rdr):
                self.creds_list.append(row)
                self.logger.debug("| %s |" % (self.creds_list[i]))
                self.logger.debug("| %s |" % (self.creds_list[i][0]))
                # self.logger.debug("| %s | %s | %s |" % (self.creds_list[i][0], self.creds_list[i][1], self.creds_list[i][2]))
        self.logger.debug("Creds list length: %i" % len(self.creds_list))

        #Pick a random row from the creds
        chosen_row = random.choice(self.creds_list)
        self.logger.debug(
            "Chosen: Real Name: %s | Email: %s | Pwd: %s |" % (chosen_row[0], chosen_row[1], chosen_row[2]))

        self.pop3_user = chosen_row[1].strip().split('@', 2)[0]
        self.pop3_pass = chosen_row[2].strip()
        self.logger.debug("Pop3 Username: |%s|" % self.pop3_user)
        self.logger.debug("Pop3 Pass: |%s|" % self.pop3_pass)

    def connect_to_Pop3_serv(self):
        self.pop3MailboxServ = poplib.POP3(self.pop3_serv_fqdn, port=self.pop3_serv_port)
        self.pop3MailboxServ.set_debuglevel(True)
        self.pop3MailboxServ.getwelcome()

    def login_to_Mailbox(self):
        self.pop3MailboxServ.user(self.pop3_user)
        self.pop3MailboxServ.pass_(self.pop3_pass)

        self.logger.debug('-----------------------------------')
        self.logger.debug('Login seems to be SUCCESSFUL.')
        self.logger.debug('-----------------------------------')

        self.pop3MailboxServ.stat()
        numMessages = self.pop3MailboxServ.list()
        self.logger.debug('-----------------------------------')
        self.logger.debug('Number of NEW messages: %s' % str(numMessages))
        self.logger.debug('-----------------------------------')

    #def pick_random_email():


pop3Mailbox = Pop3ClientTest()
pop3Mailbox.read_configs()
pop3Mailbox.read_creds()

pop3Mailbox.connect_to_Pop3_serv()
pop3Mailbox.login_to_Mailbox()
