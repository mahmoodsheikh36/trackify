import redis

r = redis.Redis(host='localhost', port=6379, db=0)

def get(key):
    return r.get(key)

def set(key, val):
    return r.set(key, val)

def delete(key):
    val = r.get(key)
    delete(key)
    return val
