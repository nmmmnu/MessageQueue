MessageQueue
============

Pure Python implementation of Message Queue over memcached protocol.

There is no query service yet, just key/value database.

File description:

Server files:
- **server.py** - server process using asyncore.dispatcher. Nothing fancy there.

**./protocol/**:
- **memcachedhandler.py** - handler implementing memcached telnet protocol using asynchat.async_chat. Fully memcached compatible, but supports only get, delete, set, add and quit.
- **redishandler.py** - handler implementing redis protocol using asynchat.async_chat. Fully redis compatible, but supports only spop, srem, sadd, sismember, scard and quit.

**./processor/**:
- **memcachedprocessor.py** - simple in memory key/value database implementation. It uses Python hashtable, e.g. {}
- **queueprocessor.py** - implements in-memory queue. It uses hashtable of high-performance deque()'s

Start files:
- **memcachedserver.py** - starts new key/value server using **memcachedprocessor.py**
- **queueserver.py** - starts new queue server using **queueprocessor.py**
- **redis_queueserver.py** - starts new queue server using **queueprocessor.py**

Usage
=====

Starts the server on port 4000:

> ./server.py

or

> ./server [host] [port]

Starts the server on specific interface, for example this command will start the server on standard memcached port 11211:

> ./server 0.0.0.0 11211

Testing
=======

Memcached test:

```python
import memcache
mc = memcache.Client(['127.0.0.1:4000'])
print mc.get('niki')
None
print mc.set('niki', 123)
True
print mc.get('niki')
123
```

Redis test:

```python
from redis import Redis
r = Redis("localhost", 4000)
print r.sadd('niki', "12")
True
print r.sadd('niki', "15")
True
print r.scard('niki')
2
print r.sismember('niki', 'abc')
False
print r.sismember('niki', '12')
True
print r.spop('niki')
12
print r.spop('niki')
15
print r.spop('niki')
None
```

[eof]

