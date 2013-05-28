from collections import deque

class QueueProcessor:
	max_queues     = 1024
	max_queue_size = 1024 * 32
	
	def __init__(self):
		pass
		
	def get(self, key):
		print QueueProcessor.mem
		
		deck = QueueProcessor.mem.get(key)
		
		if deck is None:
			return None
		
		if len(deck) is 0:
			# tidy up unused deque
			del QueueProcessor.mem[key]
			return None
		
		return deck.popleft()
			
	def delete(self, key):
		try:
			del QueueProcessor.mem[key]
			return True
		except:
			return False

	def set(self, key, data):
		if len(QueueProcessor.mem) >= self.max_queues:
			return False
		
		deck = QueueProcessor.mem.get(key)
		
		# Remember if statement with __len__()
		if deck is None:
			deck = deque()
			QueueProcessor.mem[key] = deck

		if len(deck) >= self.max_queue_size:
			return False
			
		deck.append(data)

		return True

QueueProcessor.mem = {}


