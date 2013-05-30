#!/usr/bin/python

from server                          import Server                as _Server
from protocols.redishandler          import RedisHandler          as ServerHandler
from processors.diskqueueprocessor   import DiskQueueProcessor    as Processor



class Server(_Server):
	def spawn_handler(self, socket, address):
		return ServerHandler(socket, address, Processor("files/"))



if __name__ == "__main__":
	port            = 4000
	max_clients     = 256
	disconnect_idle = 60 * 5

	server = Server(port, max_clients=max_clients, disconnect_idle=disconnect_idle)
	server.serve_forever()



