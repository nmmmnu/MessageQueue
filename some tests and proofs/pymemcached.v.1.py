#!/usr/bin/python

# For Memcached telnet protocol see:
# http://blog.elijaa.org/?post/2010/05/21/Memcached-telnet-command-summary

import asyncore, asynchat
import socket

from cStringIO import StringIO

mem = {}

class QueueProcessor:
	def __init__(self, handler):
		self.handler = handler
	
	def router(self, args, data):
		print args, data
		print mem
		
		cmd = args[0]
				
		if cmd == "get":
			return self.do_get(args)
		
		if cmd == "delete":
			return self.do_delete(args)
		
		elif cmd == "set":
			return self.do_set(args, data)
		
		elif cmd == "quit":
			self.handler.push("QUIT\r\n")
			self.handler.close()
			
			return "QUIT\r\n"

		else:
			# error
			return "SERVER_ERROR\r\n"
	
	def do_get(self, args):
		try:
			k = args[1]
			x = mem[k]
			return "VALUE %s 0 %d\r\n%s\r\nEND\r\n" % (k, len(x), x)
		except:
			return "END\r\n"
			
	def do_delete(self, args):
		try:
			k = args[1]
			del mem[k]
			return "DELETED\r\n"
		except:
			return "NOT_FOUND\r\n"

	def do_set(self, args, data):
		k = args[1]

		try:
			size = int(args[4])

			if len(data) > size:
				data = data[:size]
		except:
			pass
			
		mem[k] = data

		return "STORED\r\n"


class MemcachedHandler(asynchat.async_chat):
	commands_with_data = ['set']
	
	def __init__(self, sock, addr):
		asynchat.async_chat.__init__(self, sock=sock)
		self.addr = addr
		self.set_terminator("\r\n")
		self.data_reading = "read_header"
		self.head = ""
		self.data = ""
		self.io = StringIO()
		self.processor = QueueProcessor(self)
	
	def cmd_parse_head(self):
		m2 = self.head.split(" ")
		
		# clean up empty arguments
		
		m = []
		for x in m2:
			if x != "":
				m.append(x)

		if len(m):
			return m

		return [""]
	
	def cmd_parse(self):
		m = self.cmd_parse_head()
		print self.processor
		x = self.processor.router(m, self.data)
		
		self.push(x)

		print mem
	
	def collect_incoming_data(self, data):
		self.io.write(data)
		
	def found_terminator(self):
		print self.data_reading
		
		if self.data_reading == "read_header" :
			self.head = self.io.getvalue()

			self.io   = StringIO()
			
			m = self.cmd_parse_head()
			print m
			if m[0] in self.commands_with_data:
				self.data_reading = "read_data"
				
				try:
					size = int(m[4])
				except:
					size = 0

				self.set_terminator( size + len("\r\n") )

				return

			self.cmd_parse()
	
		elif self.data_reading == "read_data" :
			self.data = self.io.getvalue()

			self.io   = StringIO()

			self.data_reading = "read_header"
			self.set_terminator("\r\n")
			self.cmd_parse()
			
			
			
class Server(asyncore.dispatcher):
	def __init__(self, host, port, backlog=1):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.set_reuse_addr()
		self.bind( (host, port) )
		self.listen(backlog)

	def handle_accept(self):
		socket, address = self.accept()
		MemcachedHandler(socket, address)


	
s = Server("0.0.0.0", 4000)
asyncore.loop()

