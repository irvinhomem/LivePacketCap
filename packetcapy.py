import pyshark
from datetime import datetime
#from subprocess import call
import subprocess
import multiprocessing
import time
import os
import errno
#import threading
#subprocess.run python 3.5


myNic = "eth0"
#domain_name = "bbc.co.uk"
#domain_name = "dsv.su.se"
#domain_name = "google.com"
#domain_name = "cataclysma.ml"
#domain_name = "baidu.com"
#domain_name = "craigslist.org"
#domain_name = "weibo.com"
domain_url = "http://" + domain_name
my_oFile = domain_name + "-" +datetime.strftime(datetime.now(), "%Y-%m-%d-T%H%M%S") + ".pcapng"
my_filePath = '/tmp/pcaps/' + domain_name + '/'
wget_params = "-H -p -nv -e robots=off --no-dns-cache --delete-after http://" + domain_name
#wget_cmd_params = ['wget','-H','-p', '-nv', '-q', '--show-progress', '-e', 'robots=off', '--no-dns-cache', '--delete-after', domain_url]
wget_cmd_params = ['wget', '-H', '-p', '-nv', '-e', 'robots=off', '--no-dns-cache', '--delete-after', domain_url]

print("Sniffing Interface : ", myNic)
print("Current Domain : ", domain_name)
print("Output File name : ", my_oFile)
print("File with Path : ", my_filePath + my_oFile)
print("wget Command Parameters: ", wget_params)

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
        print("Path Created: ", path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

# tshark -w (write output file) and pyshark output_file don't create directories
# tshark -w (write output file) and pyshark output_file need an absolute file path (they don't seem to recognize relative file paths)
# We need to create the directory where the file will be saved within the /tmp/pcaps/ directory
make_sure_path_exists(my_filePath)

# Setup capture
cap = pyshark.LiveCapture(interface=myNic, output_file=my_filePath+my_oFile)
successful = -1

def run_Capture():
    print("Starting Capture ...")
    cap.sniff()

def run_Wget():
    print("Starting wget ...")
    success = subprocess.call(wget_cmd_params)
    print("Success = ", success)
    print("Finished wget ...")
    return success

p = multiprocessing.Process(target=run_Capture)
p.start()

#Give it 5 seconds to set up the capture interface
time.sleep(5)

successful = run_Wget()

if successful == 8:
    cap.close()
    print("Closed sniffer.")
    p.terminate()


print("... Ended Capture.")