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
procCapture = None
web_process = None

#domain_name = "bbc.co.uk"
#domain_name = "dsv.su.se"
domain_name = "google.com"
#domain_name = "cataclysma.ml"
#domain_name = "baidu.com"
#domain_name = "craigslist.org"
#domain_name = "weibo.com"

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
        print("Path Created: ", path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def run_capture():
    print("Starting Capture ...")
    cap.sniff()

#def run_wget(success):
def run_wget():
    print("Starting wget ...")
    #web_process = subprocess.Popen(wget_cmd_params)
    web_process = subprocess.Popen(google_chrome_params)

    print("Process ID: ", web_process.pid)
    try:
        streamdata = web_process.communicate(timeout=20)[0]

        #rc = web_process.returncode
        print("Success / Return code = ", web_process.returncode)
        print("Finished wget ...")

    except subprocess.TimeoutExpired:
        print("Caught Timeout Error : Killing process Pid: ", web_process.pid)
        web_process.terminate()
    finally:
        if web_process.returncode == 8:
            print("Finished HAPPILY.")
            cap.close()
            print("Closed sniffer.")
            procCapture.terminate()
            print("... Ended Capture.")
        elif web_process.returncode == 0:
            web_process.wait(timeout=30)
            print("Waited 30 secs for timeout...")

            cap.close()
            print("Closed sniffer.")
            procCapture.terminate()
            print("... Ended Capture.")
        else:
            #time.sleep(20)
            print("Past 20s timeout... Killing process ID: ", web_process.pid)
            web_process.terminate()

            cap.close()
            print("Closed sniffer.")
            procCapture.terminate()
            print("... Ended Capture.")

# MAIN FUNCTION
if __name__ == "__main__":
    domain_url = "http://" + domain_name
    my_oFile = domain_name + "-" +datetime.strftime(datetime.now(), "%Y-%m-%d-T%H%M%S") + ".pcapng"
    my_filePath = '/tmp/pcaps/' + domain_name + '/'
    wget_params = "-H -p -nv -e robots=off --no-dns-cache --delete-after http://" + domain_name
    #wget_cmd_params = ['wget','-H','-p', '-nv', '-q', '--show-progress', '-e', 'robots=off', '--no-dns-cache', '--delete-after', domain_url]
    wget_cmd_params = ['wget', '-H', '-p', '-nv', '-e', 'robots=off', '--no-dns-cache', '--delete-after', domain_url]
    google_chrome_params = ['google-chrome','--incognito', domain_url]

    print("Sniffing Interface : ", myNic)
    print("Current Domain : ", domain_name)
    print("Output File name : ", my_oFile)
    print("File with Path : ", my_filePath + my_oFile)
    print("wget Command Parameters: ", wget_params)

    # tshark -w (write output file) and pyshark output_file don't create directories
    # tshark -w (write output file) and pyshark output_file need an absolute file path (they don't seem to recognize relative file paths)
    # We need to create the directory where the file will be saved within the /tmp/pcaps/ directory
    make_sure_path_exists(my_filePath)

    # Setup capture
    cap = pyshark.LiveCapture(interface=myNic, output_file=my_filePath+my_oFile)

    # Run packet capturing process
    procCapture = multiprocessing.Process(target=run_capture)
    procCapture.start()

    #Give it 5 seconds to set up the capture interface
    time.sleep(3)

    # Run Web Request sequence
    procWebRequest = multiprocessing.Process(target=run_wget)
    procWebRequest.start()

