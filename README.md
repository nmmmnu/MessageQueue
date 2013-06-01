# MessageQueue

Pure Python implementation of "Disk Based Message Queue" over Memcached protocol or Redis protocol.

There are also queue services in RAM and NoSQL key/value in RAM database (get/set/del).

Queue service in RAM and the NoSQL database are fully functional, but they was written for testing and educational purposes.

There are one queue service that acts as well known "normal" FIFO...

... and there are some optimized queues that trade some functionality for some improvements.

One of those is "Random Disk Based Queue" - instead of FIFO, it returns random items, but is much faster and uses much less storage.

## Goals:

- Messages will be strings. If you need to store something different, is up to you to serialize it.
- A message must be delivered only once and must **NOT** be lost. A message can be lost only if there are uncorrectable error with data store, such disk failure.
- Message queue must not get "stuck". This means queue add / pop operations must not depend / affect each other any errors with them, must be self-correctable.
- Multiple queues must be supported.
- Optionally store unique messages only once, in a way similar to Redis sets - sadd() / spop() / sismember()

## Files

Server files:
- **server.py** - abstract server process using asyncore.dispatcher. Nothing fancy there.

./protocol/:
- **memcachedhandler.py**	- handler implementing memcached telnet protocol using asynchat.async_chat. Fully memcached compatible, but supports only get, delete, set, add and quit.
- **redishandler.py**		- handler implementing redis protocol using asynchat.async_chat. Fully redis compatible, but supports only spop, srem, sadd, sismember, scard and quit.

./processor/:
- **dbprocessor.py**			- simple in memory key/value database implementation. It uses Python hashtable, e.g. {} . Provided for testing and education.
- **queueprocessor.py**			- implements in-memory queue. It uses hashtable of high-performance deque()'s. Provided for testing and education.
- **diskqueueprocessor.py**		- implements disk based queue. It uses two BerkleyDB files per queue.
- **singlediskqueueprocessor.py**	- implements disk based queue with some compromises. It uses single BerkleyDB for all queues.
- **randomdiskqueueprocessor.py**	- implements disk based queue with some more compromises. It uses single BerkleyDB for all queues.

Start files:
- **mc_dbserver.py**			- starts new key/value server using **memcachedprocessor.py**
- **mc_queueserver.py**			- starts new queue server using **queueprocessor.py**
- **redis_queueserver.py**		- starts new queue server using **queueprocessor.py**
- **redis_diskqueueserver.py**		- starts new queue server using **diskqueueprocessor**
- **redis_singlediskqueueserver.py**	- starts new queue server using **singlediskqueueprocessor**
- **redis_randomdiskqueueserver.py**	- starts new queue server using **randomdiskqueueprocessor**

## Basic usage

Starts the disk based queue server with Redis protocol on port 4000:

```shell
./redis_diskqueueserver.py
```

I simplified the server design, and command line params are not longer "accepted".

In order to start the server on different port or interface, to change max clients etc,
you will need to "hard code" those inside the file.

## Testing

### Memcached + database test with Python:

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

### Redis + queue test with Python:

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

### Redis + queue test with PHP:

```php
$r = new Redis();

$r->connect("localhost", 4000);

for ($i = 0; $i < 10; $i++)
	$r->sadd("niki", "Item $i");

echo "Size: " . $r->scard("niki") . "\n";

while($x = $r->spop("niki"))
	echo "$x\n";
```

## How **Disk Based Queue** store its files

Disk based queue uses Berkeley DB.

For each queue two separate db files are created.

First file is Berkeley B-Tree db.

Berkeley B-Tree db is ordered, but also it is extremly fast to do db.first().

For order, we use Python time.time(). Unlike PHP and some other languages, 
it have microseconds and return value is as good as UUID.

To avoid any problems, we also concatenate long sequential ID with 30 leading zeros.

The B-Tree db is enought for implementing the queue, but we also implementing "unique" message functionality.
This means one message must not be inserted twice in single queue.

To do so, for each queue, we use second Berkeley Hash db.

We could use single "central" hash db for all queues, but separating give us flexability such:

- Queue data can be copy between servers.
- Ability to delete whole queue.
- Avoiding work with slow huge central database.
- Avoiding problems with central database crash.

Dissadvantage is only one - for each queue, we need to use additional file descriptor.

For keys there, we use md5 of the "message" (e.g. the value). For data, we put the key from the B-Tree db.

### Note about file descriptors

For each client a single file descriptor is used. This is because server is async.

For each queue two file descriptor are used. One for each Berkeley db.

You probably want to increase default descriptors using:

```shell
ulimit -n 4096
./redis_diskqueueserver.py
```
Theoretically Python can do this, but process must be started as root - by this reason we did not implemented this function.

## How **Single Disk Based Queue** store its data and what are compromises there.

This queue processor uses single Berkeley B-Tree db for all queues.

Because all data is in single file there are following advantages:

- Use much much less file descriptors - e.g. single file descriptor.
- Unlimited number of queues.
- Easy backup of whole server.
- When queue is empty, all queue keys are deleted.

Respectively there are following disadvantages:

- There are no way to **delete** a queue.
- There are no way to backup single queue.
- There are no easy way to track the queue size. System supports this using incr / decr value in Berkeley db. Because this is **slow** you need to enable it when you construct new server. If disabled and queue exists size = 1 is returned.
- When Berkeley db file gets big, system probably will slow down.

## What is **Random Disk Based Queue**, how it store its data and what are compromises there.

The idea for this queue processor is directly "borrowed" from Redis set. Queue contains only unique items and get() / spop() operation returns items in "random" order.

However there are huge gain - because for each queue item is set single key/value in Berkeley db, performance is about 4 times faster than "single disk based queue".

Advantages:

- Use much much less file descriptors - e.g. single file descriptor.
- Unlimited number of queues.
- Easy backup of whole server.
- When queue is empty, all queue keys are deleted.

Advantages against **Single Disk Based Queue**:

- at least 4x faster
- at least 2x smaller database
- works exactly as Redis set

Disadvantages:

- There are no way to **delete** a queue.
- There are no way to backup single queue.
- There are no way to track the queue size. If queue exists size = 1 is returned.
- When Berkeley db file gets big, system probably will slow down.

Disadvantages against **Single Disk Based Queue**

- There are no way to track the queue size. If queue exists size = 1 is returned.

## [eof]
