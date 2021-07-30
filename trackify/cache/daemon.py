import json
from time import sleep

from trackify.cache import cache
from trackify.db.classes import MusicProvider
from trackify.utils import current_time, get_largest_elements

music_provider = MusicProvider()

def generate_top_users_data(from_time, to_time):
    users, artists, albums, tracks, plays =\
        music_provider.get_all_users_data(from_time, to_time)

    users_to_sort = []
    for user in users.values():
        if user.settings.get_by_name('show_on_top_users').value:
            if user.plays:
                users_to_sort.append(user)

    for user in users_to_sort:
        for play in user.plays:
            listened_ms = play.listened_ms(from_time=from_time)
            if hasattr(play.track, 'listened_ms'):
                if user.id in play.track.listened_ms:
                    play.track.listened_ms[user.id] += listened_ms
                else:
                    play.track.listened_ms[user.id] = listened_ms
            else:
                play.track.listened_ms = {user.id: listened_ms}
            if not hasattr(user, 'top_track') or\
               play.track.listened_ms[user.id] > user.top_track.listened_ms[user.id]:
                user.top_track = play.track
            if not hasattr(user, 'listened_ms'):
                user.listened_ms = listened_ms
            else:
                user.listened_ms += listened_ms
            
    def compare(user1, user2):
        if not hasattr(user1, 'listened_ms'):
            return False
        if not hasattr(user2, 'listened_ms'):
            return True
        return user1.listened_ms > user2.listened_ms
    top_users = get_largest_elements(users_to_sort, 10, compare)

    return top_users

if __name__ == '__main__':
    while True:
        for hours in [24, 168, 720]:
            from_time = current_time() - hours * 3600 * 1000
            top_users = generate_top_users_data(from_time, current_time())
            data = [{
                'id': user.id,
                'username': user.username,
                'settings': [{
                    'id': setting.id,
                    'name': setting.name,
                    'value': setting.value,
                } for setting in user.settings.settings],
                'top_track': {
                    'id': user.top_track.id,
                    'name': user.top_track.name,
                    'artists': [{
                        'id': artist.id,
                        'name': artist.name
                    } for artist in user.top_track.artists],
                    'album': {
                        'id': user.top_track.album.id,
                        'name': user.top_track.album.name,
                        'artists': [{
                            'id': artist.id,
                            'name': artist.name
                        } for artist in user.top_track.album.artists],
                        'images': [{
                            'id': image.id,
                            'url': image.url,
                            'width': image.width,
                            'height': image.height,
                        } for image in user.top_track.album.images]
                    },
                },
                'listened_ms': user.listened_ms
            } for user in top_users]

            cache.set(hours, json.dumps(data))

        sleep(1)
