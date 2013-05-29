#!/usr/bin/python

from hashlib import md5

import bsddb
import time
import resource
#from uuid import uuid4


class DiskQueue:
	unique = True
	def __init__(self, name, path = "", unique = True):
		#
		#  Constructs new DiskQueueManager
		#
		#  @param name : name of the queue
		#  @param path : path where databases will be stored
		#  @param unique : if set to False, disable unique capability, 
		#                  also add() begin to work exactly as set()
		#
		

		#  @param ext_tree : file extention of tree db
		#  @param ext_hash : file extention of hash db
		
		ext_tree = ".tree.db"
		ext_hash = ".hash.db"
		
		self.name = name
		
		file_md5 = self._hash(name)

		self.file_tree = path + file_md5 + ext_tree
		self.file_hash = path + file_md5 + ext_hash
			
		self.db_tree = bsddb.btopen(  self.file_tree, "c")
		self.db_hash = bsddb.hashopen(self.file_hash, "c")

		self.new_key_id = 0L
		
		self.unique = unique
	
	def _hash(self, name):
		return md5(name).hexdigest()
	
	def _new_key(self):
		# In rare cases, this may return a key that precede the previous key.
		# this is why we put in the mix self.new_key_id. 
		# However, to avoid the number overload, we make it long.
		#
		# To be 100% unique, we could add an UUID4.
		# However UUID is 100 nanoseconds which is already included in time.time()
		
		self.new_key_id += 1
		
		#key = "%010.6f:%030ld:%s" % ( time.time(), self.new_key_id, uuid.uuid4() )
		
		key = "%010.6f:%030ld" % ( time.time(), self.new_key_id )

		return key
	
	def get(self):
		#  
		#  pops a value from the queue
		#
		#  @return : the value, or None if not inserted.
		#  
		try:
			k, value = self.db_tree.first()
			h        = self._hash(value)
			
			del self.db_tree[k]
			del self.db_hash[h]
			
			return value
		except:
			return None

	def delete(self):
		#  
		#  Deletes the queue
		#  Once this method is called, databases will be empty
		#
		#  @return : True if deleted, False if not exists.
		#
		try:
			self.db_tree.close()
			self.db_tree = bsddb.btopen(  self.file_tree, "n")

			self.db_hash.close()
			self.db_hash = bsddb.hashopen(self.file_hash, "n")
			
			return True
		except:
			return None

	def set(self, value):
		#  
		#  add (push) a value into the queue
		#
		#  @param data : the value
		#  @return : True if inserted, False if not inserted.
		#  
		try:
			k     = self._new_key()
			value = str(value)
			h     = self._hash(value)
			
			self.db_tree[k] = value
			self.db_hash[h] = k
			
			return True
		except:
			return False

	def add(self, value):
		#  add (push) a value into the queue,  
		#  if the value is into the queue, return True,
		#  but the value is not inserted twice.
		#
		#  @param data : the value
		#  @return : True if inserted or exists, False if not inserted.
		#  
		if self.unique: 
			if self.__contains__(value):
				# we could paranoidly check future, but let not do so
				return True
		
		return self.set(value)

	def __len__(self):
		#  
		#  Length of the queue
		#
		#  @return : queue size
		#  
		return len(self.db_hash)
		
	def __contains__(self, value):
		#  
		#  Determine if queue contains the value
		#
		#  @param data : the value
		#  @return : True if is member, False if not.
		#  
		value = str(value)
		h     = self._hash(value)

		if h in self.db_hash:
			return True
	
		return False

import processor

class DiskQueueProcessor(processor.Processor):
	def __init__(self, path, unique = True):
		#
		#  Constructs new DiskQueueProcessor
		#
		#  @param path : path where databases will be stored
		#  @param unique : if set to False, disable unique capability, 
		#                  also add() begin to work exactly as set()
		#
		self.path   = path
		self.unique = unique


	"""
	def _filelimits(self):
		try:
			limit. _ = resource.getrlimit(resource.RLIMIT_NOFILE)
			return limit / 2
		except:
			return 100
	"""
	
	def _get_work_queue(self, name):
		q = DiskQueueProcessor.queues.get(name)
		
		if q is None:
			if len(DiskQueueProcessor.queues) >= DiskQueueProcessor.max_queues:
				return None
				
			q = DiskQueue(name, self.path, self.unique)
			DiskQueueProcessor.queues[name] = q
			
		return q

	def get(self, name):
		#  
		#  pops a value from the queue
		#
		#  @param key : name of the queue
		#  @return : the value, or None if not inserted.
		#  
		x = self._get_work_queue(name)
		if x is not None:
			return x.get()
	
		return None

	def delete(self, name):
		#  
		#  Deletes the queue
		#
		#  @param key : name of the queue
		#  @return : True if deleted, False if not exists.
		#
		x = self._get_work_queue(name)
		
		if x is None:
			return True
		
		x.delete()
		#del QueueProcessor.queues[name]

		return True

	def set(self, name, data):
		#  
		#  add (push) a value into the queue
		#
		#  @param key : name of the queue
		#  @param data : the value
		#  @return : True if inserted, False if not inserted.
		#  
		x = self._get_work_queue(name)
		
		if x is None:
			return True
		
		return x.set(data)

	def add(self, name, data):
		#  add (push) a value into the queue,  
		#  if the value is into the queue, return True,
		#  but the value is not inserted twice.
		#
		#  @param key : name of the queue
		#  @param data : the value
		#  @return : True if inserted or exists, False if not inserted.
		#  
		x = self._get_work_queue(name)
		
		if x is None:
			return True
		
		return x.add(data)
		
	def len(self, name):
		#  
		#  Length of the queue
		#
		#  @param key : name of the queue
		#  @return : queue size
		#  
		x = self._get_work_queue(name)
		if x is not None:
			return len(x)
		
		return 0
		
	def contains(self, name, data):
		#  
		#  Determine if queue contains the value
		#
		#  @param key : name of the queue
		#  @param data : the value
		#  @return : True if is member, False if not.
		#  
		x = self._get_work_queue(name)
		if x is not None:
			if data in x:
				return True
		
		return False

# static
DiskQueueProcessor.queues     = {}
DiskQueueProcessor.max_queues = 512

