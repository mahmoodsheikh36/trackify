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

def test3():
    provider = DBProvider()
    row = provider.get_api_access_token(user_id)
    print(row)

def test4():
    provider = DBProvider()
    rows = provider.get_user_settings(user_id)
    print(rows)

#test3()
test4()
