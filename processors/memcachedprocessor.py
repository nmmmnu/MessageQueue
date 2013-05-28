
class MemcachedProcessor:
	mem_max_keys = 1024
	
	def __init__(self):
		pass
		
	def get(self, key):
		try:
			return MemcachedProcessor.mem[key]
		except:
			return None
			
	def delete(self, key):
		try:
			del MemcachedProcessor.mem[key]
			return True
		except:
			return False

	def set(self, key, data):
		if len(MemcachedProcessor.mem) >= self.mem_max_keys:
			return False
		
		MemcachedProcessor.mem[key] = data

		return True

MemcachedProcessor.mem = {}


