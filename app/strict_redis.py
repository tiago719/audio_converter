import redis
from settings import REDIS


strict_redis = redis.StrictRedis(**REDIS)