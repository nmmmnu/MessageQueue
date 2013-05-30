MessageQueue
============

Pure Python implementation of Disk based Message Queue over memcached protocol or Redis protocol.

There are also queue services in RAM and NoSQL key/value in RAM database (get/set/del).

Queue service in RAM and the NoSQL database are fully functional, but they was written for testing and educational purposes.

# Files

Server files:
- **server.py** - abstract server process using asyncore.dispatcher. Nothing fancy there.

./protocol/:
- **memcachedhandler.py** - handler implementing memcached telnet protocol using asynchat.async_chat. Fully memcached compatible, but supports only get, delete, set, add and quit.
- **redishandler.py** - handler implementing redis protocol using asynchat.async_chat. Fully redis compatible, but supports only spop, srem, sadd, sismember, scard and quit.

./processor/:
- **dbprocessor.py** - simple in memory key/value database implementation. It uses Python hashtable, e.g. {}
- **queueprocessor.py** - implements in-memory queue. It uses hashtable of high-performance deque()'s
- **diskqueueprocessor.py** - implements disk based queue. It uses two BerkleyDB files per queue.

Start files:
- **mc_dbserver.py** - starts new key/value server using **memcachedprocessor.py**
- **mc_queueserver.py** - starts new queue server using **queueprocessor.py**
- **redis_queueserver.py** - starts new queue server using **queueprocessor.py**
- **redis_diskqueueserver.py** - starts new queue server using **diskqueueprocessor**

# Basic usage

Starts the disk based queue server with Redis protocol on port 4000:

> ./redis_diskqueueserver.py

I simplified the server design, and command line params are not longer "accepted".

In order to start the server on different port or interface, to change max clients etc,
you will need to "hard code" those inside the file.

# Testing

## Memcached + database test with Python:

```python
import memcache
mc = memcache.Client(['127.0.0.1:4000'])
print mc.get('niki')
#None
print mc.set('niki', 123)
#True
print mc.get('niki')
#123
```

## Redis + queue test with Python:

```python
from redis import Redis
r = Redis("localhost", 4000)
print r.sadd('niki', "12")
#True
print r.sadd('niki', "15")
#True
print r.scard('niki')
#2
print r.sismember('niki', 'abc')
#False
print r.sismember('niki', '12')
#True
print r.spop('niki')
#12
print r.spop('niki')
#15
print r.spop('niki')
#None
```

## Redis + queue test with PHP:

```php
$r = new Redis();

$r->connect("localhost", 4000);

for ($i = 0; $i < 10; $i++)
	$r->sadd("niki", "Item $i");

echo "Size: " . $r->scard("niki") . "\n";

while($x = $r->spop("niki"))
	echo "$x\n";
```

[eof]
