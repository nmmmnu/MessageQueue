#!/usr/bin/python

from hashlib import md5

import bsddb
import time

import processor

db = {}

class SingleDiskQueueProcessor(processor.Processor):
	prefix_queue = "q"	# e.g. q:xxxx:<timestamp>
	prefix_hash  = "h"	# e.g. h:xxxx:<md5>
	prefix_len   = "_"	# e.g. c:xxxx:<number>
	# it is very important that prefix_queue is sorted *after* prefix_hash
	
	def __init__(self, dbname, calc_len = False):
		#
		#  Constructs new SingleDiskQueueProcessor
		#
		#  @param dbname : path to the single databases bsddb
		#  @param calc_len : calculate len() of the queue,
		#                   will slow down the server
		#
		self.dbname  = dbname
		self.calc_len = calc_len
		
		if db.get(self.dbname) is None:
			# Open the database
			db[self.dbname] = bsddb.btopen(self.dbname, "c")
		
		# Collect a copy of the db
		self.db = db[self.dbname]
	
	def _q_key(self, name, timestamp = False):
		key = "%s:%s:" % (name, self.prefix_queue)
		
		if timestamp:
			return key + "%010.6f" % time.time()
			
		return key
	
	def _h_key(self, name, value):
		return "%s:%s:%s" % (name, self.prefix_hash, self._hash(value) )

	def _l_key(self, name):
		return "%s:%s" % (name, self.prefix_len)

	def _hash(self, name):
		return md5(name).hexdigest()
	
	def _get(self, name):
		try:
			self.db.first()
			
			qkey = self._q_key(name)

			key, value = self.db.set_location(qkey)

			if key[:len(qkey)] == qkey:
				# This is our key...
				return key, value
		except:
			# KeyError
			pass

		return None, None
	
	def _incr_len(self, name, increment = 1):
		if not self.calc_len:
			return False

		key = self._l_key(name)
		
		try:
			l = long(self.db[key])
		except:
			# KeyError, ValueError
			l = 0

		l = l + increment
		
		if l:
			try:
				self.db[key] = str(l)
				return True
			except:
				return False
		else:
			# if we are here, then l is 0. 
			# if l is 0, we delete it from the db.
			try:
				del self.db[key]
			except:
				pass

		return True
	
	
	
	def get(self, name):
		#
		#  pops a value from the queue
		#
		#  @param key : name of the queue
		#  @return : the value, or None if not inserted.
		#
		key, value = self._get(name)
		
		if key is None:
			return None
		
		hkey = self._h_key(name, value)

		try:
			del self.db[key]
		except:
			pass

		try:
			del self.db[hkey]
		except:
			pass

		self._incr_len(name, -1)

		return value
	
	def delete(self, name):
		#  
		#  Deletes the queue
		#
		#  @param key : name of the queue
		#  @return : Always returns False,
		#            because the op is not supported
		#
		return False
	
	def set(self, name, value):
		#  
		#  add (push) a value into the queue
		#
		#  @param key : name of the queue
		#  @param data : the value
		#  @return : True if inserted, False if not inserted.
		#  
		qkey = self._q_key(name, timestamp = True)
		hkey = self._h_key(name, value)
		
		try:
			self.db[qkey] = value
			self.db[hkey] = qkey
			
			self._incr_len(name)
			
			return True
		except:
			return False

	def add(self, name, value):
		#  add (push) "unique" value into the queue,  
		#  if the value is into the queue, return True,
		#  but the value is not inserted twice.
		#
		#  @param key : name of the queue
		#  @param data : the value
		#  @return : True if inserted or exists, False if not inserted.
		#  
		if self.contains(name, value):
			return True

		return self.set(name, value)
	
	def len(self, name):
		#  
		#  Length of the queue
		#
		#  @param name : name of the queue
		#  @return : queue size,
		#            if self.calc_len if False,
		#            return value will be 0 or 1
		#  
		key, _ = self._get(name)
		
		if key is None:
			return 0
		
		if not self.calc_len :
			return 1

		# Try to get the size from db
		key = self._l_key(name)
		
		try:
			qsize = long(self.db[key])
		except:
			qsize = 0

		# Be safe, queue exists,
		# but qsize is obviously wrong... 

		if qsize > 0:
			return qsize

		return 1

	def contains(self, name, value):
		#  
		#  Determine if queue contains the value
		#
		#  @param key : name of the queue
		#  @param data : the value
		#  @return : True if is member, False if not.
		#  
		try:
			hkey = self._h_key(name, value)
			if self.db.has_key(hkey):
				return True
		except:
			pass

		return False
		
	def _dump(self, name = "", limit = 100):
		print 
		print "Queue %s dump" % name
		print "-" * 115
		print "| %5s | %-50s | %-50s |" % ("#", "Key", "Value")
		print "-" * 115
	
		try:
			br = 0
			self.db.first()
			key, value = self.db.set_location(name + ":")
			while key:
				if key[:len(name)] != name:
					break
				
				print "| %5d | %-50s | %-50s |" % (br, key, value)
				
				key, value = self.db.next()

				br += 1
				if br >= limit:
					break
		except:
			pass

		print "-" * 115
		print "[EOF]"



if __name__ == "__main__":
	q = SingleDiskQueueProcessor("queue.tree.db", calc_len = True)
	
	if (1):
		q.add("niki", "edno")
		q.add("niki", "dve")
		q.add("niki", "tri")

		q.add("zztop", "zz edno")
		q.add("zztop", "zz dve")
		q.add("zztop", "zz tri")
		
	print "zztop size:", q.len("zztop")
	print "niki  size:",  q.len("niki")

	if (1):
		while True:
			x = q.get("niki")
			if x == None:
				break
				
			print x
	
	if 1:
		q._dump()



