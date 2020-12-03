"""
a script to test database functions
use like: python3 -i scripts/db_tests.py
"""

import sys
import os
sys.path.append(os.path.abspath('../trackify'))

from trackify.db.db import *
from trackify.db.classes import *
from trackify.utils import current_time

user_id = 'af38a714-bcba-419e-804c-96d910d0e975'

def speed_test():
    user = User(user_id, None, None, None, None)
    provider = MusicProvider()
    begin = current_time()
    data = provider.get_user_data(user)
    old = current_time() - begin
    print('with old method it took {} milliseconds'.format(old))
    begin = current_time()
    data = provider.get_user_data_new(user)
    new = current_time() - begin
    print('with new method it took {} milliseconds'.format(new))

def speed_test2():
    provider = DBProvider()
    begin = current_time()
    data = provider.get_user_data(user_id)
    time = current_time() - begin
    print(time)

speed_test2()
