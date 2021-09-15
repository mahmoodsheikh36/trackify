#!/usr/bin/python3
from trackify.utils import current_time, generate_id
from trackify.db.classes import DbDataProvider, User

def insert_user(username, password, email=None):
    user_id = generate_id()
    time_added = current_time()
    user = User(user_id, username, password, email, time_added)
    mp = DbDataProvider('mahmooz', 'test', database='trackify')
    mp.add_user(user)

if __name__ == '__main__':
    insert_user('test', 'test', None)
