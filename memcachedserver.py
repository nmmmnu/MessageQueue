#!/usr/bin/python

import asyncore

from server                        import Server
from protocols.memcachedhandler    import MemcachedHandler   as ServerHandler
from processors.dbprocessor        import DBProcessor        as Processor



class MemcachedServer(Server):
	def spawn_handler(self, socket, address):
		ServerHandler(socket, address, Processor())



import sys

if __name__ == "__main__":
	try:
		host = sys.argv[1]
		port = int(sys.argv[2])
	except:
		host = "0.0.0.0"
		port = 4000

	s = MemcachedServer(host, port)
	asyncore.loop()



