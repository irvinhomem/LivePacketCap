import requests
import csv
from tempfile import NamedTemporaryFile
import shutil
import logging

class RedirectChecker(object):

    def __init__(self):
        # Configure Logging
        #logging.basicConfig(level=logging.INFO)
        #logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.INFO)
        #self.logger.setLevel(logging.DEBUG)
        self.logger.setLevel(logging.WARNING)

        self.csvInputFilePath = 'top-50-Cleaned.csv' #'top-50-Cleaned.csv'    #'top-5.csv'
        self.all_domains = []
        self.csvOutputPath = 'Labeled-http-50.csv'
        self.all_row_data =[]

    def read_csv_file(self):
        csv_filepath = self.csvInputFilePath
        with open(csv_filepath, mode='r', newline='') as csvfile:
            domain_name_rdr = csv.reader(csvfile, delimiter=',')
            for row in domain_name_rdr:
                self.all_domains.append(row[1])

    def check_https(self):
        print("Number of domains: %i" % len(self.all_domains))

        #http_req_headers = {'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        http_req_headers = {'user-agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0'}

        for count, domain in enumerate(self.all_domains):
            single_row = []
            url = "http://"+ domain
            try:
                response = requests.get(url, timeout=40, headers=http_req_headers)  #headers=http_req_headers  # allow_redirects=True
                no_of_redirs = len(response.history)
                status_code = 0
                location_proto = ''
                if no_of_redirs > 0:
                    last_redir_url = response.history[-1].url
                    #location = response.history[-1].headers['Location']
                    if len(response.history[-1].headers['location']) > 0:
                        location_proto = response.history[-1].headers['location'].split(':')[0]
                else:
                    last_redir_url = response.url
                status_code = response.status_code
                protocol = last_redir_url.split(":")[0]
                #print("%i : [%i] %s \t: %s :\t Redirects: %i" % (count, status_code, domain, protocol, no_of_redirs))
                print("%i : [%i] %s \t: %s :\t Location-Proto: [%s] \t: Redirects: %i"
                      % (count, status_code, domain, protocol, location_proto, no_of_redirs))
                # single_row['Domain'] = domain
                # single_row['Proto'] = protocol

                single_row.append(domain)
                single_row.append(protocol)
                single_row.append(location_proto)
            except:
                print("%i : %s \t: Timeout" % (count, domain))
                single_row.append(domain)
                single_row.append("Timeout")
                single_row.append("Timeout")

            self.all_row_data.append(single_row)
            self.logger.debug("SINGLE-ROW: Domain: [%s] | Proto: [%s] | Loc-Proto: [%s]" % (single_row[0], single_row[1], single_row[2]))
            self.logger.debug("Number of rows: %i" % len(self.all_row_data))

    def write_csv_file(self):
        csv_out = self.csvOutputPath
        tempfile = NamedTemporaryFile(delete=False)
        self.logger.debug("Domain: [%s] | Proto: [%s] | Loc-Proto: [%s]" % (self.all_row_data[0][0], self.all_row_data[0][1], self.all_row_data[0][2]))
        self.logger.debug("Domain: [%s] | Proto: [%s] | Loc-Proto: [%s]" % (self.all_row_data[1][0], self.all_row_data[1][1], self.all_row_data[1][2]))
        with open(csv_out, mode = 'w', newline='') as tempfile:
            writer = csv.writer(tempfile, delimiter=',')

            for row in self.all_row_data:
                #writer.writerow([row.item])
                self.logger.debug("Domain: [%s] | Proto: [%s] | Loc-Proto: [%s]" % (row[0], row[1], row[2]))
                #writer.writerow([row[0],row[1],row[2]])    # 3 rows with Domain, Initial-HTTP[S], Location HTTP[S]
                if row[1] == 'https' or row[2] == 'https':  # 2 rows with Domain HTTP or HTTPS (Final location)
                    writer.writerow([row[0], 'https'])
                elif row[1] == 'Timeout' or row[2] == 'Timeout':
                    writer.writerow([row[0], 'Timeout'])
                else:
                    writer.writerow([row[0], 'http'])


        shutil.move(tempfile.name, self.csvOutputPath)


redirChk = RedirectChecker()

redirChk.read_csv_file()
redirChk.check_https()
redirChk.write_csv_file()




