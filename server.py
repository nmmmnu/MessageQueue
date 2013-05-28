import asyncore
import socket

class Server(asyncore.dispatcher):
	def __init__(self, host, port, backlog=1):
		#  
		#  Constructs new Server using asyncore.dispatcher
		#  
		#  @param host : interface for listen
		#  @param port : port for listen
		#  @param host : backlog for the socket
		#
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.set_reuse_addr()
		self.bind( (host, port) )
		self.listen(backlog)

	def handle_accept(self):
		socket, address = self.accept()
		
		self.spawn_handler(socket, address)
	
	def spawn_handler(self, socket, address):
		#  
		#  This method must be overriden and 
		#  must return new ServerHandler object
		#  
		#  @param socket : socket from asyncore
		#  @param address : address from asyncore
		#
		print "Call abstract method!!!"
		#ServerHandler(socket, address, Processor())



