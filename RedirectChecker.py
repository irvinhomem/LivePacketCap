import requests
import string
import csv

class RedirectChecker(object):

    def __init__(self):
        self.CsvFilePath = 'top-50-Cleaned.csv'
        self.all_domains = []

    def read_csv_file(self):
        csv_filepath = self.CsvFilePath
        with open(csv_filepath, mode='r', newline='') as csvfile:
            domain_name_rdr = csv.reader(csvfile, delimiter=',')
            for row in domain_name_rdr:
                self.all_domains.append(row[1])

    def check_https(self):
        print("Number of domains: %i" % len(self.all_domains))

        #http_req_headers = {'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        http_req_headers = {'user-agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0'}

        for count, domain in enumerate(self.all_domains):
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
            except:
                print("%i : %s \t: Timeout" % (count, domain))

redirChk = RedirectChecker()

redirChk.read_csv_file()
redirChk.check_https()




