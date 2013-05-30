#
# Memcached protocol implementation
# Nikolay Mihaylov nmmm@nmmm.nu
#

# For Memcached telnet protocol see:
# http://blog.elijaa.org/?post/2010/05/21/Memcached-telnet-command-summary



import asynchat
import time

try:
	from cStringIO import StringIO
except ImportError:
	from StringIO  import StringIO



class RedisHandler(asynchat.async_chat):
	
	def __init__(self, sock, addr, processor):
		#  
		#  Constructs new Redis protocol handler
		#  
		#  @param sock : socket from asyncore
		#  @param addr : address from asyncore
		#  @param processor : processor class
		#
		asynchat.async_chat.__init__(self, sock=sock)
		self.addr      = addr
		self.started   = time.time()
		self.lastping  = time.time()

		self.processor = processor

		self.state_change("read_count")

	
	
	def state_change(self, state, size = 0):
		self.io = StringIO()
		
		if state == "read_count":
			self.state_params_count   = 0
			self.state_params_waiting = 0
			self.state_params_temp    = 0
			self.state_params         = []
			self.state                = state
			
			self.set_terminator("\r\n")
			
			return True

		if state == "read_param":
			self.state = state
			self.set_terminator("\r\n")
			
			return True

		if state == "read_data":
			# size == 0 is an error, but we will ignore it.
			if size < 0:
				return False
			
			self.state = state
			self.set_terminator(size + len("\r\n") )
			
			return True

		# Unknown state ?
		return False



	def cmd_parse(self):
		self.lastping = time.time()
		
		args    = self.state_params
		command = args[0].lower()
		
		
		
		if command == "spop":
			key = args[1]

			x = self.processor.get(key)

			if x is None:
				# NULL responce
				self.push("$-1\r\n")
				return

			msg = "$%d\r\n%s\r\n" % (len(x), x)
			self.push(msg)
			return
		
		
		
		if command == "del":
			key = args[1]
			x = self.processor.delete(key)
			
			if x:
				self.cmd_int(1)
				return
			
			self.cmd_int(0)
			return
		
		
		
		# this is ADD. We do not implement SET
		if command == "sadd":
			key = args[1]
			val = args[2]
			x = self.processor.add(key, val)
			
			if x:
				self.cmd_int(1)
				return
				
			self.cmd_int(0)
			return
			
			
			
		# Non standard command
		if command == "scard":
			key = args[1]

			x = self.processor.len(key)

			if x is None:
				x = "0"

			self.cmd_int(int(x))
			return
		
		
		
		if command == "sismember":
			key = args[1]
			val = args[2]
			x = self.processor.contains(key, val)
			
			if x:
				self.cmd_int(1)
				return
		
			self.cmd_int(0)
			return
			
			
			
		if command == "quit":
			self.push("+OK\r\n")
			self.close()
			return
			


		# error, not implemented
		self.cmd_error("Not implemented")
		return		
		
		
	
	def cmd_int(self, id):
		self.push(":%d\r\n" % id)
		
		
		
	def cmd_error(self, msg = None):
		if msg is None:
			s = "-ERR\r\n"
		else:
			s = "-ERR %s\r\n" % msg
		
		self.push(s)
		
		self.state_change("read_count")



	def state_read_count(self):
		x = self.io.getvalue()
		if not x:
			self.cmd_error()
			return False

		if x[0] != "*":
			self.cmd_error("proceed with number of params")
			return False
		
		try:
			self.state_params_count   = int(x[1:])
			self.state_params_waiting = self.state_params_count
		except:
			self.cmd_error("wrong number of params")
			return False
		
		if self.state_params_count is 0:
			self.cmd_error("wrong number of params, *0 is not allowed")
			return False
		
		self.state_change("read_param")
		
		return True


			
	def state_read_param(self):
		x = self.io.getvalue()

		if not x:
			self.cmd_error("proceed with size of param")
			return False

		if x[0] != "$":
			self.cmd_error("proceed with size of param")
			return False

		try:
			self.state_params_temp = int(x[1:])
		except:
			self.cmd_error("wrong size of param")
			return False
					
		self.state_change("read_data", self.state_params_temp )
		
		return True



	def state_read_data(self):
		x = self.io.getvalue()

		if not self.state_params_temp:
			self.state_params_temp = 0
		
		x = x[0:self.state_params_temp]
		
		self.state_params.append(x)
		
		self.state_params_waiting -= 1
				
		if self.state_params_waiting > 0:
			self.state_change("read_param")
			return True

		# Proceed with request
		
		self.cmd_parse()
		
		self.state_change("read_count")



	def found_terminator(self):
		if self.state == "read_count":
			# *2
			return self.state_read_count()
			
		if self.state == "read_param":
			# $3
			return self.state_read_param()

		if self.state == "read_data":
			# <data>
			return self.state_read_data()

		# Unknown state ?
		return False



	def collect_incoming_data(self, data):
		self.io.write(data)


