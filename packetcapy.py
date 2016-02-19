import pyshark
from datetime import datetime
#from subprocess import call
import subprocess
import multiprocessing
import time
#import threading
#subprocess.run python 3.5


myNic = "eth0"
#domain_name = "bbc.co.uk"
#domain_name = "dsv.su.se"
#domain_name = "google.com"
domain_name = "cataclysma.ml"
domain_url = "http://" + domain_name
my_oFile = domain_name + "-" +datetime.strftime(datetime.now(), "%Y-%m-%d-T%H%M%S") + ".pcapng"
my_filePath = '/pcaps/' + domain_name + '/' +my_oFile
wget_params = "-H -p -e robots=off --no-dns-cache --delete-after http://" + domain_name
#wget_cmd_params = ['wget','-H','-p','-e', 'robots=off', '--no-dnscache', '--delete-after', domain_url]
wget_cmd_params = ['wget', '-H', '-p', '-e', 'robots=off', '--no-dns-cache', '--delete-after', domain_url]

print("Sniffing Interface : ", myNic)
print("Current Domain : ", domain_name)
print("Output File name : ", my_oFile)
print("File Path : ", my_filePath)
print("wget Command Parameters: ", wget_params)

#Setup capture
cap = pyshark.LiveCapture(interface=myNic, output_file=my_oFile)
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