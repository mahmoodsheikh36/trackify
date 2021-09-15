import json
from time import sleep

from trackify.db.data import DbDataProvider
from trackify.utils import current_time, get_largest_elements
from trackify.cache.data import CacheDataProvider

db_data_provider = DbDataProvider()
cache_data_provider = CacheDataProvider()

if __name__ == '__main__':
    while True:
        for hours in [24, 168, 720]:
            from_time = current_time() - hours * 3600 * 1000
            top_users = db_data_provider.get_top_users(from_time, current_time())

            cache_data_provider.set_top_users(hours, top_users)

        sleep(1)
