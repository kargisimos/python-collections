#this script extracts wifi SSIDs, their passwords and
# their wireless security protocols which
#are locally stored in a machine. Saves output
#into wifi_creds.csv. Works on both
#Windows and Unix.

import os
import re
import csv
import sys
import subprocess

def wifi_creds_extractor_func():
	#check whether the OS is Windows or UNIX
	if os.name == 'nt':
		#use netsh system command to grep the SSIDs
		netsh = subprocess.check_output("netsh wlan show profiles").decode()
		profiles = re.findall(r"All User Profile(.*)", netsh)

		SSIDs = list()
		for profile in profiles:
			SSIDs.append(profile.replace(":","",1).strip())

		
		#get the password and the authentication protocol for each SSID
		passwords = list()
		protocols = list()

		for SSID in SSIDs:
			netsh2 = subprocess.check_output(f"""netsh wlan show profiles name="{SSID}" key=clear""").decode()
			password = re.findall((r"Key Content(.*)"),netsh2)
			protocol = re.findall((r"Authentication(.*)"),netsh2)[0]
			try:
				passwords.append((str(password).split(":")[1].split("\r")[0].split(r"\r")[0]))
			except:
				passwords.append("")

			try:
				protocols.append(protocol.replace(":","",1).strip()) 
			except:
				protocols.append("")

		
		for SSID,password,protocol in zip(SSIDs,passwords,protocols):
			print(f"SSID:\t\t{SSID}\nPassword:\t{password}\nProtocol:\t{protocol}\n")

		#save result into csv file
		with open('wifi_creds.csv',mode='w') as f:
			csv_writer = csv.writer(f,delimiter=',')
			csv_writer.writerow(["SSID","Password","Protocol"])
			for SSID,password,protocol in zip(SSIDs,passwords,protocols):
				csv_writer.writerow([SSID,password,protocol])

	elif os.name == 'posix':
	    	#In Unix, the NetworkManager service stores wireless connection configurations
	    	#in the '/etc/NetworkManager/system-connections' directory.
	    	#By default, root permissions are required to view the content
	    	#of the configuration files
	    	
	    	path = '/etc/NetworkManager/system-connections'
	    	config_files = list()
	    	
	    	for config_file in os.listdir(path):
	    		if config_file.endswith('.nmconnection'):
	    			config_files.append(config_file)
	    	
	    	#get SSIDs, passwords, protocols
	    	SSIDs = list()
	    	passwords = list()
	    	protocols = list()
	    	
	    	for config_file in config_files:
	    		try:
	    			output = subprocess.check_output(f'cat {os.path.join(path,config_file)}',shell=True).decode()
	    			ssid = re.findall((r'ssid=(.*)'),output)
	    			password = re.findall((r'psk=(.*)'),output)
	    			protocol = re.findall((r'key-mgmt=(.*)'),output)
	    			
	    			SSIDs.append(str(ssid)[2:-2])
	    			passwords.append(str(password)[2:-2])
	    			protocols.append(str(protocol)[2:-2])
	    			
	    			for SSID,password,protocol in zip(SSIDs,passwords,protocols):
	    				print(f"SSID:\t\t{SSID}\nPassword:\t{password}\nProtocol:\t{protocol}\n")
	    				
	    			#save result into csv file
	    			with open('wifi_creds.csv',mode='w') as f:
	    				csv_writer = csv.writer(f,delimiter=',')
	    				csv_writer.writerow(["SSID","Password","Protocol"])
	    				for SSID,password,protocol in zip(SSIDs,passwords,protocols):
	    					csv_writer.writerow([SSID,password,protocol])
	    			
	    		except Exception:
	    			pass
	else:
		print("[-]OS doesn't seem to be Windows nor UNIX...")
		sys.exit(1)

wifi_creds_extractor_func()
