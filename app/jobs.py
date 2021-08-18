from rq import Queue
from strict_redis import strict_redis

queue = Queue('queue', connection=strict_redis)