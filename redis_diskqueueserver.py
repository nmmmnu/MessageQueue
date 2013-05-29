#!/usr/bin/python

import asyncore

from server                          import Server
from protocols.redishandler          import RedisHandler          as ServerHandler
from processors.diskqueueprocessor   import DiskQueueProcessor    as Processor



class QueueServer(Server):
	def spawn_handler(self, socket, address):
		ServerHandler(socket, address, Processor("files/"))



import sys

if __name__ == "__main__":
	try:
		host = sys.argv[1]
		port = int(sys.argv[2])
	except:
		host = "0.0.0.0"
		port = 4000

	s = QueueServer(host, port)
	asyncore.loop()


