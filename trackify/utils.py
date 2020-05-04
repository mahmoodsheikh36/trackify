import uuid
import time
import urllib.parse

def generate_id():
    return str(uuid.uuid4())

# time since the unix epoch in milliseconds
current_time = lambda: int(round(time.time() * 1000))

def uri_encode(text):
    return urllib.parse.quote(text)
