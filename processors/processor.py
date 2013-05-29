
class Processor:
	def get(self, key):
		return None
			
	def delete(self, key):
		return False

	def set(self, key, data):
		return False

	def add(self, key, data):
		return self.set(key, data)

	def len(self, key):
		return "0"

	def contains(self, key, data):
		return False

