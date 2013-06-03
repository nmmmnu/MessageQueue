#!/usr/bin/python

import logging

from server                          import Server                as _Server
from protocols.redishandler          import RedisHandler          as ServerHandler
from processors.diskqueueprocessor   import DiskQueueProcessor    as Processor



class Server(_Server):
	def spawn_handler(self, socket, address):
		return ServerHandler(socket, address, Processor(self.path_to_db))



if __name__ == "__main__":
	port            = 4000
	max_clients     = 256
	disconnect_idle = 60 * 5
	
	logging.basicConfig(level=logging.INFO, format='%(asctime)s : %(levelname)s : %(message)s')

	path_to_db      = "files/"

	# Single queue = 2 file descriptors 
	DiskQueueProcessor.max_queues = 100

	server = Server(port, max_clients=max_clients, disconnect_idle=disconnect_idle)
	server.path_to_db = path_to_db
	server.serve_forever()



