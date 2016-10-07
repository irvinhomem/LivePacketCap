import smtplib
import logging
import csv
import os.path
import random

from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

from SMTP.pickRandomPara import PickRandomParagraph
from SMTP.pickRandomFile import PickRandomFile


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
        creds_path = "creds/email_list.csv"
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

        self.msg = None
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
        #Strip of any extra leading or trailing spaces
        self.email_address_login = chosen_row[1].strip()
        self.email_pass = chosen_row[2].strip()

        self.email_FROM = chosen_row[0].strip() + " <" + self.email_address_login.strip() + ">"
        self.email_TO = email_to_row[0].strip() + " <" + email_to_row[1].strip() + ">"
        self.logger.debug("Email FROM field: %s" % self.email_FROM)
        self.logger.debug("Email TO field: %s" % self.email_TO)

    def connect_to_SMTP_serv(self):
        self.logger.debug("Connecting to SMTP fqdn ... %s : %s" % (self.smtp_serv_fqdn, self.smtp_serv_port))
        try:
            self.logger.debug("-----------------------------------------")
            self.logger.debug("Trying to connect to SMTP ... ")
            self.logger.debug("-----------------------------------------")
            self.server = smtplib.SMTP(self.smtp_serv_fqdn, self.smtp_serv_port)  # port 465 or 587
            #self.server = smtplib.SMTP_SSL(self.smtp_serv_fqdn, 465)  # port 465 or 587
            self.server.set_debuglevel(True)
            self.logger.debug("-----------------------------------------")
            self.logger.debug("SMTP connection success ... ")
            self.logger.debug("-----------------------------------------")
        except smtplib.SMTPException:
            self.logger.debug("************** Error connecting to SMTP")

        #Authentication is now working, but the SMTP server is still permissive (allows unauthenticated requests :( )
        try:
            self.server.ehlo()
            self.server.starttls()
            self.server.ehlo()
        except smtplib.SMTPException:
            self.logger.debug("**************** Error doing EHLO")

        try:
            self.logger.debug("USER LOGIN: |%s||%s|" % (self.email_address_login, self.email_pass))
            #self.server.esmtp_features['auth'] = 'PLAIN LOGIN'  # To remove CRAM-MD5 authentication method causing errors
            self.server.login(self.email_address_login, self.email_pass)
        except smtplib.SMTPException:
            self.logger.debug("**************** Error logging into SMTP")

    def get_email_msg(self):
        # Code adapted from python documentation
        # Create the container (outer) email message.
        msg = MIMEMultipart('Mixed')
        # me == the sender's email address
        # family = the list of all recipients' email addresses
        msg['From'] = self.email_FROM
        msg['To'] = self.email_TO
        #msg['To'] = COMMASPACE.join(family)
        msg.preamble = "Message PREAMBLE TEXT --> that doesn't appear within the body" #'Our family reunion'

        #the_message = "Random message text"
        paragraph_picker = PickRandomParagraph()
        the_message, the_subject = paragraph_picker.get_random_paragraph_text()

        # Get the first 7 words in the first line and use them as the subject (Including the first Random Word:")
        msg['Subject'] = ' '.join(the_subject.split(' ', 8)[:7])

        message_text = MIMEText(the_message,'plain')
        msg.attach(message_text)

        attachment_random_file_picker = PickRandomFile()
        mime_formatted_file = attachment_random_file_picker.pick_random_file_and_make_mime()
        msg.attach(mime_formatted_file)

        #self.msg = 'Hello world.'
        self.msg = msg

    def send_single_email(self):
        try:
            #self.server.sendmail(self.email_FROM, self.email_TO, self.msg)
            self.server.send_message(self.msg)
            self.server.quit()
        except smtplib.SMTPException:
            self.logger.debug("***************** Error sending email ...")

smtpClient = SmtpClientTest()
smtpClient.read_configs()
smtpClient.get_emails_n_creds()

smtpClient.connect_to_SMTP_serv()
smtpClient.get_email_msg()
smtpClient.send_single_email()
