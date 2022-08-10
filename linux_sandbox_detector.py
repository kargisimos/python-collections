#this script evaluates whether
#the running Linux operating system
#is a sandbox or not,based on the 
#following criteria:
#https://evasions.checkpoint.com
#
#   @artifacts:         directories 
#                       files
#
#   @generic os checks: username
#                       hostname
#                       hard disk size
#                       number of processors
#
#   @network: 
#                       MAC address
#                       internet connection

import sys
import netifaces
import os
from requests import head
from getpass import getuser
import socket
import shutil
from multiprocessing import cpu_count

def artifacts_func():
    #check for default directories
    directories = [
                'vmlinuz','vmlinuz.old'  #VirtualBox
                ]
    for directory in directories:
        if os.path.exists(os.path.join('/',directory)):
            print(f"[-]Sandbox detected: Default directory: {os.path.join('/',directory)}")
            sys.exit(1)
    else:
        print('[+]Default directories OK')

    #check for default files
    files = [
            '.vboxclient'   #VirtualBox
            ]
    home_files = []
    for file in os.listdir(os.path.expanduser("~")):
        home_files.append(file)

    for file in files:
        for home_file in home_files:
            if home_file.startswith(file):
                print(f"[-]Sandbox detected: Default file: {home_file}")
                sys.exit(1)
    else:
        print('[+]Default files OK')

def generic_os_checks_func():
    #check known sandbox usernames
    #https://evasions.checkpoint.com

    usernames = ['sandbox','sandboxdetect',
                'testuser','malware','maltest','malwaretest',
                'virus','fortinet','johndoe','andy','honey',
                'john','malnetvm','roo','snort','tequilaboomboom',
                'test','virusclone','wilbert','nepenthes','currentuser',
                'username','vmware'
                ]

    username = getuser().lower()

    if username in usernames:
        print(f'[-]Sandbox detected: username: {username}')
        sys.exit(1)
    else:
        print('[+]Username OK')

    #check known sandbox hostnames

    hostnames = ['sandbox','sandboxdetect','john-pc','mueller-pc',
                'virus','malware','hanspeter-pc',
                'malwaretest','fortinet'
                ]

    hostname = socket.gethostname().lower()

    if hostname in hostnames:
        print(f"[-]Sandbox detected: hostname: {hostname}")
        sys.exit(1)
    else:
        print('[+]Hostname OK')
    
    #check  hard disk size

    hard_disk_GBs = shutil.disk_usage('/')[0] // 2**30
    if hard_disk_GBs < 230:
        print(f"[-]Sandbox detected: hard disk size: {hard_disk_GBs} GigaBytes")
        sys.exit(1)
    else:
        print('[+]Hard disk size OK')

    #check number of cpu processors
    cpu_processors = cpu_count()
    if cpu_processors < 5:
        print(f'[-]Sandbox detected: Number of cpu processors: {cpu_processors}')
        sys.exit(1)
    else:
        print('[+]Number of CPU processors OK')

def network_detection_func():
    #check MAC address based on known vendors

    MACs = [
            '00:05:69','00:0C:29','00:1C:14','00:50:56', #VMware, Inc.
            '00:0F:4F','08:00:27',                       #PCS Systemtechnik GmbH (VirtualBox)
            'EC:75:ED',                                  #Citrix Systems, Inc.
            '00:1C:42'                                   #Parallels, Inc.
            ]

    mac = []
    mac_vendor = []
    for interface in netifaces.interfaces():
    	addrs = netifaces.ifaddresses(interface)
    	m = addrs[netifaces.AF_LINK][0]['addr']
    	mac.append(m)
    	mac_vendor.append(':'.join(m.split(':',3)[:3]))
	
    for m in mac_vendor:
    	if m in MACs:
        	print(f'[-]Sandbox detected: MAC Address (vendor): {m}')
        	sys.exit(1)
    else:
        print('[+]MAC Address OK')
        
    #check internet connection
    
    sample_urls = ['https://www.google.com','https://www.tesla.com','https://www.w3schools.com']
    timeout = 5
    conn_errors = 0
    for url in sample_urls:
        try:
            r = head(url,timeout=timeout)
        except:
            conn_errors += 1
    if conn_errors == 3:
        print("[-]Sandbox detected: No internet connection")
        sys.exit(1)
    else:
        print('[+]Internet connection OK')
