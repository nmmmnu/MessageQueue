#!/usr/bin/python

from server					import Server			as _Server
from protocols.redishandler			import RedisHandler		as ServerHandler
from processors.singlediskqueueprocessor	import SingleDiskQueueProcessor	as Processor



class Server(_Server):
	def spawn_handler(self, socket, address):
		return ServerHandler(socket, address, Processor(self.path_to_db))



if __name__ == "__main__":
	port            = 4000
	max_clients     = 256
	disconnect_idle = 60 * 5

	path_to_db      = "queue.db"

	server = Server(port, max_clients=max_clients, disconnect_idle=disconnect_idle)
	server.path_to_db = path_to_db
	server.serve_forever()



