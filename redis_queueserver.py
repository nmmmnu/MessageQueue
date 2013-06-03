#!/usr/bin/python

import logging

from server                      import Server            as _Server
from protocols.redishandler      import RedisHandler      as ServerHandler
from processors.queueprocessor   import QueueProcessor    as Processor



class Server(_Server):
	def spawn_handler(self, socket, address):
		return ServerHandler(socket, address, Processor())



if __name__ == "__main__":
	port            = 4000
	max_clients     = 256
	disconnect_idle = 60 * 5

	logging.basicConfig(level=logging.INFO, format='%(asctime)s : %(levelname)s : %(message)s')

	server = Server(port, max_clients=max_clients, disconnect_idle=disconnect_idle)
	server.serve_forever()


