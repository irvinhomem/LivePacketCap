import smtplib
import logging
import csv
import os.path
import random

from email.mime.text import MIMEText


class SmtpClientTest(object):

    def __init__(self):
        #Configure Logging
        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.INFO)
        self.logger.setLevel(logging.DEBUG)
        # self.logger.setLevel(logging.WARNING)

        #__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        #configs_file_name = "smtp_configs.csv"
        configs_path = "configs/smtp_configs.csv"
        #self.configs_path = os.path.join(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(configs_file_name))), configs_file_name)
        self.configs_path = os.path.join(
            os.path.realpath(os.path.join(os.getcwd(), os.pardir)), configs_path)
        #self.configs_path ="./configs/smtp_configs.csv"
        self.configs_dict = {}

        # self.creds_path = "../creds/smtp_creds.csv"
        creds_path = "creds/smtp_creds.csv"
        self.logger.debug("Current Working Dir Parent: %s" % os.path.realpath(os.path.join(os.getcwd(), os.pardir)))
        parent_dir = os.path.realpath(os.path.join(os.getcwd(), os.pardir))
        self.logger.debug("CWD Grand Parent: %s" % os.path.realpath(os.path.join(parent_dir, os.pardir)))
        grandparent_dir = os.path.realpath(os.path.join(parent_dir, os.pardir))
        self.creds_path = os.path.join(grandparent_dir,creds_path)
        self.creds_list = []

        self.smtp_serv_fqdn = ""
        self.smtp_serv_port = ""
        self.email_address_login = ""
        self.email_pass = ""

        self.msg = ""
        self.server = None

        return

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
                    self.smtp_serv_fqdn = row[1].strip()
                elif row[0] == 'port':
                    self.configs_dict['server_port'] = row[1].strip()
                    self.smtp_serv_port = row[1].strip()
                else:
                    self.logger.debug("Unknown config parameter found")

        self.logger.debug("Server FQDN: [%s]" % (self.configs_dict['server_fqdn']))
        self.logger.debug("Server Port: [%s]" % (self.configs_dict['server_port']))

    def get_emails_n_creds(self):
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
                #self.logger.debug("| %s | %s | %s |" % (self.creds_list[i][0], self.creds_list[i][1], self.creds_list[i][2]))
        self.logger.debug("Creds list length: %i" % len(self.creds_list))

        # Select random row in list
        chosen_row = []
        email_to_row = []
        while(chosen_row == email_to_row):
            self.logger.debug("In loop to chose random email addresses ...")
            chosen_row = random.choice(self.creds_list)
            self.logger.debug("Chosen: Real Name: %s | Email: %s | Pwd: %s |" % (chosen_row[0], chosen_row[1], chosen_row[2]))
            email_to_row = random.choice(self.creds_list)
            self.logger.debug("Chosen: Email To Name: %s | Email: %s | Pwd: %s |" % (email_to_row[0], email_to_row[1], email_to_row[2]))
            if(chosen_row != email_to_row):
                break

        self.logger.debug("Chosen: Real Name: %s | Email: %s | Pwd: %s |" % (chosen_row[0], chosen_row[1], chosen_row[2]))
        self.logger.debug("Chosen: Email To Name: %s | Email: %s |" % (email_to_row[0], email_to_row[1]))

        # return chosen_row, email_to_row
        self.email_address_login = chosen_row[1]
        self.email_pass = chosen_row[2]
        self.email_FROM = chosen_row[0] + "<" + self.email_address_login + ">"
        self.email_TO = email_to_row[0] + "<" + email_to_row[1] + ">"


    def connect_to_SMTP_serv(self):
        self.server = smtplib.SMTP(self.smtp_serv_fqdn, self.smtp_serv_port)  # port 465 or 587
        self.server.ehlo()
        self.server.starttls()
        self.server.ehlo()
        self.server.login(self.email_address_login, self.email_pass)

    def get_email_msg(self):
        self.msg = 'Hello world.'

    def send_single_email(self):
        self.server.sendmail(self.email_FROM, self.email_TO, self.msg)
        self.server.close()


smtpClient = SmtpClientTest()
smtpClient.read_configs()
smtpClient.get_emails_n_creds()

smtpClient.connect_to_SMTP_serv()
smtpClient.get_email_msg()
smtpClient.send_single_email()
