
from collections import deque

class QueueProcessor:
	max_queues     = 1024
	max_queue_size = 1024 * 32
	
	unique         = True
	
	def __init__(self, max_queues = 1024, max_queue_size = 1024 * 32, unique = True):
		#  
		#  Constructs new QueueProcessor
		#
		#  @param max_queues : maximum number of queues
		#  @param max_queue_size : maximum size of each queue
		#  @param unique : if set to False, disable unique capability, 
		#                  also add() begin to work exactly as set()
		#  
		self.unique = unique
		
	def get(self, key):
		#  
		#  pops a value from the queue
		#
		#  @param key : name of the queue
		#  @return : the value, or None if not inserted.
		#  
		t = QueueProcessor.mem.get(key)
		
		if t is None:
			return None
			
		deck, sets = t
		
		if len(deck) is 0:
			# tidy up unused deque
			del QueueProcessor.mem[key]
			return None
		
		x = deck.popleft()
		
		if x in sets:
			sets.remove(x)
		
		return x
			
	def delete(self, key):
		#  
		#  Deletes the queue
		#
		#  @param key : name of the queue
		#  @return : True if deleted, False if not exists.
		#  
		try:
			del QueueProcessor.mem[key]
			return True
		except:
			return False

	def set(self, key, data):
		#  
		#  add (push) a value into the queue
		#
		#  @param key : name of the queue
		#  @param data : the value
		#  @return : True if inserted, False if not inserted.
		#  
		if len(QueueProcessor.mem) >= self.max_queues:
			return False
		
		t = QueueProcessor.mem.get(key)
		
		if t is None:
			t = ( deque(), set() )
			QueueProcessor.mem[key] = t
		
		deck, sets = t

		if len(deck) >= self.max_queue_size:
			return False
			
		deck.append(data)
		
		if self.unique: 
			sets.add(data)

		return True

	def add(self, key, data):
		#  add (push) a value into the queue,  
		#  if the value is into the queue, return True,
		#  but the value is not inserted twice.
		#
		#  @param key : name of the queue
		#  @param data : the value
		#  @return : True if inserted or exists, False if not inserted.
		#  
		if self.unique: 
			t = QueueProcessor.mem.get(key)

			if t is not None:
				_, sets = t
				if data in sets:
					# Data already in the queue
					return True
		
		return self.set(key, data)

# static
QueueProcessor.mem = {}


