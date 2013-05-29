#!/usr/bin/python

import asyncore

from server                      import Server
from protocols.redishandler      import RedisHandler      as ServerHandler
from processors.queueprocessor   import QueueProcessor    as Processor



class QueueServer(Server):
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

	s = QueueServer(host, port)
	asyncore.loop()

"""
from redis import Redis
r = Redis("localhost", 4000)
print r.sadd('niki', "12")
True
print r.sadd('niki', "15")
True
print r.scard('niki')
2
print r.sismember('niki', 'abc')
False
print r.sismember('niki', '12')
True
print r.spop('niki')
12
print r.spop('niki')
15
print r.spop('niki')
None
"""

