import uuid
import time
import urllib.parse
import string
import random

def generate_id(length=None):
    if not length:
        return str(uuid.uuid4())
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# time since the unix epoch in milliseconds
current_time = lambda: int(round(time.time() * 1000))

def uri_encode(text):
    return urllib.parse.quote(text)

def get_largest_elements(list_to_sort, limit, compare):
    mylist = list_to_sort.copy()
    final_list = []
    for i in range(limit):
        if not mylist:
            return final_list
        biggest = mylist[0]
        for j in range(len(mylist)):
            element = mylist[j]
            if compare(element, biggest):
                biggest = element
        final_list.append(biggest)
        mylist.remove(biggest)
    return final_list

def hrs_from_ms(ms):
    return ms // 3600000
    
def mins_from_ms(ms):
    return (ms // 60000) % 60

def secs_from_ms(ms):
    return (ms // 1000) % 60

def str_to_bool(val):
    if val == 'True':
        return True
    return False

def get_user_setting_by_name(settings, setting_name):
    for setting_id in settings:
        if settings[setting_id].name == setting_name:
            return settings[setting_id]
    return None
