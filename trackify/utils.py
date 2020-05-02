import uuid
  
def generate_id():
    return str(uuid.uuid4())

# time since the unix epoch in milliseconds
current_time = lambda: int(round(time.time() * 1000))
