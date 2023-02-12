import redis


cache = redis.Redis(host="172.16.238.10", port=6379, db=0)
cache.set('foo', 'bar')
x = cache.get('foo')
'myapp_default'
print(x)