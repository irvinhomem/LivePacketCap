import logging

import poplib
import pyshark
import multiprocessing as mp

import os
import csv
import random
import errno

import getpass
from datetime import datetime
import time


class Pop3ClientMulti(object):

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

        self.myNic = 'eth0'

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

    def make_sure_path_exists(self, path):
        try:
            os.makedirs(path)
            print("Path Created: ", path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

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

    def get_msg_size_id_list_STAT_LIST(self):

        numMessages, totalSize = self.pop3MailboxServ.stat()
        #self.logger.debug('-----------------------------------')
        self.logger.debug('Number of TOTAL messages: %s' % str(numMessages))
        self.logger.debug('-----------------------------------')
        numMsg, msg_id_list_octetsSize, not_sure = self.pop3MailboxServ.list()
        #self.logger.debug('-----------------------------------')
        self.logger.debug('Msg Count(#): %s | Msg id & size List: %s | Extra num: %s'
                          % (numMsg, str(msg_id_list_octetsSize), not_sure))
        self.logger.debug('-----------------------------------')

        return msg_id_list_octetsSize

    def pick_single_random_email(self, msg_id_list_octetsSize):

        selected_email = random.choice(msg_id_list_octetsSize)
        #Decode bytes to string and split the string into 'id' and 'octets size' pieces
        selected_email_id, email_octets_size = selected_email.decode().split(' ', 2)
        self.logger.debug('Chosen Email: %s' % selected_email_id)
        self.logger.debug('Chosen Email Size: %s' % email_octets_size)
        self.logger.debug('-----------------------------------')

        # Do UIDL (No idea why, but it seems to appear in normal POP3 communication)
        uidl_result = self.pop3MailboxServ.uidl(selected_email_id)
        self.logger.debug('UIDL Result: %s' % str(uidl_result))
        self.logger.debug('-----------------------------------')

        # Get the email contents
        server_msg, body, octets_size = self.pop3MailboxServ.retr(selected_email_id)
        self.logger.debug('Server Msg: %s' % server_msg)
        #self.logger.debug('MSG Body: %s /n' % body)
        self.logger.debug('-----------------------------------')
        self.logger.debug('MSG Body:')
        self.logger.debug('-----------------------------------')
        for line in body:
            self.logger.debug(line.decode())
        self.logger.debug('-----------------------------------')
        self.logger.debug('Octets Size: %s' % octets_size)

    def pick_multiple_random_emails_serial(self):

        # Get list of all emails with STAT and LIST commands
        # Only needs to be done once in our case, but tos simulate normal email interaction we put it in the loop
#        all_emails = self.get_msg_size_id_list_STAT_LIST()

        # Pick 3 random emails
        for counter in range(3):
            all_emails = self.get_msg_size_id_list_STAT_LIST()
            self.logger.debug('---------------')
            self.logger.debug('Email: %i' % counter)
            self.logger.debug('---------------')
            self.pick_single_random_email(all_emails)

    def close_and_quit_pop3_session(self):
        # Close and Quit session
        self.pop3MailboxServ.quit()

    def run_single_cap_multi_POP3_DL(self):

        self.run_capture('DL')

        self.pick_multiple_random_emails_serial()

        self.close_and_quit_pop3_session()

        self.close_sniffer()

    def setup_capture(self, ftp_type):
        self.logger.debug("Current User: %s", getpass.getuser())
        curr_user = getpass.getuser()

        my_filePath = '/home/' + curr_user + '/pcaps/POP3/'
        my_oFile = "POP3-" + ftp_type + "-" + datetime.strftime(datetime.now(), "%Y-%m-%d-T%H%M%S") + ".pcapng"
        self.cap = pyshark.LiveCapture(interface=self.myNic, output_file=my_filePath + my_oFile)

        self.logger.info("Sniffing Interface : %s" % self.myNic)
        self.logger.info("Output File name : %s" % my_oFile)
        self.logger.debug("File with Path : %s" % (my_filePath + my_oFile))

        # tshark -w (write output file) and pyshark output_file don't create directories
        # tshark -w (write output file) and pyshark output_file need an absolute file path (they don't seem to recognize relative file paths)
        # We need to create the directory where the file will be saved within the /tmp/pcaps/ directory
        self.make_sure_path_exists(my_filePath)

        # Setup capture
        self.cap = pyshark.LiveCapture(interface=self.myNic, output_file=my_filePath + my_oFile)
        self.logger.debug("Pyshark LiveCapture Object type: %s" % type(self.cap))
        # self.cap.sniff()

    def run_capture(self, ftp_type):
        # Set up Capture
        self.setup_capture(ftp_type)

        self.procCapture = mp.Process(name='Capture_process/Sniffing service', target=self.cap.sniff)
        self.procCapture.start()
        self.logger.info("Capture Process is running: %s" % self.procCapture.is_alive())
        self.logger.info("Capture Process ID: %i" % self.procCapture.pid)

        self.logger.debug("Capture started...")
        # Give it 3 seconds to set up the capture interface
        time.sleep(3)

    def close_sniffer(self):
        self.cap.close()
        print("Closed sniffer.")
        self.procCapture.terminate()
        print("... Ended Capture.")


pop3Mailbox = Pop3ClientMulti()
pop3Mailbox.read_configs()
pop3Mailbox.read_creds()

pop3Mailbox.connect_to_Pop3_serv()
pop3Mailbox.login_to_Mailbox()
#pop3Mailbox.pick_single_random_email()
pop3Mailbox.run_single_cap_multi_POP3_DL()
