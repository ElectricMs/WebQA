import redis

r = redis.Redis(host='localhost', port=6379)
# print(r.set('foo', 'zbar'))
print(r.get('foo'))
