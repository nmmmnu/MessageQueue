#!/usr/bin/python

from hashlib import md5

import bsddb
import time
import resource

import processor

db = {}

class RandomDiskQueueProcessor(processor.Processor):
	
	def __init__(self, dbname):
		#
		#  Constructs new RandomDiskQueueProcessor
		#
		#  @param dbname : path to the single databases bsddb
		#  @param calc_len : calculate len() of the queue,
		#                   will slow down the server
		#
		self.dbname  = dbname
		
		if db.get(self.dbname) is None:
			# Open the database
			db[self.dbname] = bsddb.btopen(self.dbname, "c")
		
		# Collect a copy of the db
		self.db = db[self.dbname]
	
	def _key(self, name, value = None):
		if value:
			return "%s:%s" % (name, self._hash(value) )

		return "%s:" % name

	def _hash(self, name):
		return md5(name).hexdigest()
	
	def _get(self, name):
		try:
			self.db.first()
			
			qkey = self._key(name)

			key, value = self.db.set_location(qkey)

			if key[:len(qkey)] == qkey:
				# This is our key...
				return key, value
		except:
			# KeyError
			pass

		return None, None
	
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
		
		hkey = self._key(name, value)

		try:
			del self.db[key]
		except:
			pass

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
		qkey = self._key(name, value)
		
		try:
			self.db[qkey] = value
			
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
			qkey = self._key(name, value)
			if self.db.has_key(qkey):
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
	q = RandomDiskQueueProcessor("queue.tree2.db")
	
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



