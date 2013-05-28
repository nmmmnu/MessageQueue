# For Memcached telnet protocol see:
# http://blog.elijaa.org/?post/2010/05/21/Memcached-telnet-command-summary



import asynchat

try:
	from cStringIO import StringIO
except ImportError:
	from StringIO  import StringIO



class MemcachedHandler(asynchat.async_chat):
	commands_with_data = ['set']
	
	def __init__(self, sock, addr, processor):
		asynchat.async_chat.__init__(self, sock=sock)
		self.addr   = addr

		self.head   = ""
		self.data   = ""

		self.processor = processor

		self.state_change("read_header")

	
	
	def state_change(self, state, size = 0):
		self.io = StringIO()
		
		if state == "read_header":
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



	def cmd_parse_head(self):
		m2 = self.head.split(" ")
		
		# clean up empty arguments.
		
		m = []
		for x in m2:
			x = x.strip()
			if x != "":
				m.append(x)


		# for easy access, put some blanks at the end.

		while len(m) < 10:
			m.append("")
		
		return m



	def cmd_parse(self):
		args = self.cmd_parse_head()
		
		command = args[0].lower()
				
		
		
		if command == "get":
			key = args[1]

			x = self.processor.get(key)

			if x is None:
				self.push("END\r\n")
				return

			msg = "VALUE %s 0 %d\r\n%s\r\nEND\r\n" % (key, len(x), x)
			self.push(msg)
			return
		
		
		if command == "delete":
			key = args[1]
			x = self.processor.delete(key)
			
			if x:
				self.push("DELETED\r\n")
				return
			
			self.push("NOT_FOUND\r\n")
			return
			
		
		
		if command == "set":
			# It is protocol responsibility to check the size.
			try:
				size = int(args[4])

				if len(self.data) > size:
					self.data = self.data[:size]
			except:
				pass
			
			key = args[1]
			x = self.processor.set(key, self.data)
			
			if x:
				self.push("STORED\r\n")
				return
		
			self.push("NOT_STORED\r\n")
			return
			
			

		if command == "quit":
			self.push("QUIT\r\n")
			self.close()
			return
			


		# error, not implemented
		self.push("ERROR\r\n")
		return



	def state_read_header(self):
		self.head = self.io.getvalue()
		
		m = self.cmd_parse_head()

		if m[0] in self.commands_with_data:
			try:
				size = int(m[4])
			except:
				size = 0

			self.state_change("read_data", size)

			return

		self.state_change("read_header")
		
		self.cmd_parse()
	
	
	
	def state_read_data(self):
		self.data = self.io.getvalue()

		self.state_change("read_header")
		
		self.cmd_parse()



	def found_terminator(self):
		if self.state == "read_header":
			return self.state_read_header()

		if self.state == "read_data":
			return self.state_read_data()

		# Unknown state ?
		return False



	def collect_incoming_data(self, data):
		self.io.write(data)
