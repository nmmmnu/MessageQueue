
from redis import Redis

r = Redis("localhost", 4000)

for i in range(10):
	r.sadd('niki', "Item %05d" % i)

print "Size:", r.scard('niki')

print "Membership:", r.sismember('niki', "Item %05d" % 5)

while True:
	x = r.spop('niki')

	if x is None:
		break

	print x

