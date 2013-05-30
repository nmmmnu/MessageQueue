import asyncore
import socket
import time

class Server(asyncore.dispatcher):
	max_clients     = 256
	disconnect_idle = 3600
	backlog         = 5
	quant           = 1
	
	def __init__(self, port, host = "0.0.0.0", max_clients=256, backlog=5, reuse_addr = True, disconnect_idle=3600, quant = 1):
		"""
		Constructs new Server using asyncore.dispatcher
		
		@param port		: port for listen
		@param host		: interface for listen
		@param max_clients	: server max clients
		@param backlog		: backlog for the socket
		@param disconnect_idle	: disconnect if idle for so many seconds
		@param quant		: timeout for asyncore.loop
		"""
		asyncore.dispatcher.__init__(self)

		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)

		if reuse_addr:
			self.set_reuse_addr()

		self.bind( (host, port) )
		
		self.listen(backlog)
		
		self.clients      = []
		self.max_clients  = max_clients
		self.backlog      = backlog
				
		if disconnect_idle >= 0:
			self.disconnect_idle = disconnect_idle

	def handle_accept(self):
		# we accept anyway, else asyncore will keep handle_accept()
		socket, address = self.accept()
		
		if len(self.clients) >= self.max_clients:
			# too many connections,
			# and we close the socket here...
			socket.close()
			
			return
		
		handler = self.spawn_handler(socket, address)
				
		self.clients.append(handler)
	
	def spawn_handler(self, socket, address):
		#  
		#  This method must be overriden and 
		#  must return new ServerHandler object
		#  
		#  @param socket : socket from asyncore
		#  @param address : address from asyncore
		#
		print "Call abstract method!!!"
		#return ServerHandler(socket, address, Processor())

	def gc_handler(self):
		if not self.disconnect_idle:
			return
		
		if len(self.clients) is 0:
			return

		t = time.time()
		
		clients = []
				
		for client in self.clients:
			if t - client.lastping > self.disconnect_idle:
				# Manually disconnect this client
				client.close()
			else:
				clients.append(client)
		
		self.clients = clients

	def serve_forever(self):
		while True:
			asyncore.loop(timeout=1, count=1)
			
			if self.disconnect_idle:
				self.gc_handler()



