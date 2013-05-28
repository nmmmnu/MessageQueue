#!/usr/bin/python



import asyncore
import socket



from memcachedhandler   import MemcachedHandler   as ServerHandler
from memcachedprocessor import MemcachedProcessor as Processor



class Server(asyncore.dispatcher):
	def __init__(self, host, port, backlog=1):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.set_reuse_addr()
		self.bind( (host, port) )
		self.listen(backlog)

	def handle_accept(self):
		socket, address = self.accept()
		ServerHandler(socket, address, Processor())


import sys

if __name__ == "__main__":
	try:
		host = sys.argv[1]
		port = int(sys.argv[2])
	except:
		host = "0.0.0.0"
		port = 4000

	s = Server(host, port)
	asyncore.loop()



