
class MemcachedProcessor:
	max_keys = 1024
	
	def __init__(self, max_keys = 1024):
		#  
		#  Constructs new QueueProcessor
		#  
		#  @param max_keys : maximum numbers of keys
		#
		self.max_keys = max_keys
		
	def get(self, key):
		#  
		#  return the value corresponding to the key
		#
		#  @param key : name of the queue
		#  @return : the value, or None if not inserted.
		#  
		try:
			return MemcachedProcessor.mem[key]
		except:
			return None
			
	def delete(self, key):
		#  
		#  Deletes the key and the value
		#
		#  @param key : name of the queue
		#  @return : True if deleted, False if not exists.
		#  
		try:
			del MemcachedProcessor.mem[key]
			return True
		except:
			return False

	def set(self, key, data):
		#  
		#  set the key and corresponding value
		#  if key exists, it is overwritten
		#
		#  @param key : name of the queue
		#  @param data : the value
		#  @return : True if inserted, False if not inserted.
		#  
		if len(MemcachedProcessor.mem) >= self.max_keys:
			return False
		
		MemcachedProcessor.mem[key] = data

		return True
		
	def add(self, key, data):
		#  
		#  set the key and corresponding value,
		#  but only if the key do not exists
		#  if key exists, operation fails
		#
		#  @param key : name of the queue
		#  @param data : the value
		#  @return : True if inserted, False if not inserted.
		#  
		if MemcachedProcessor.mem.get(key) :
			# Key exists
			return False

		return self.set(key, data)

# static
MemcachedProcessor.mem = {}


