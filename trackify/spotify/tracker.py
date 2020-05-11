from time import sleep

import logging
logging.basicConfig(filename='/tmp/tracker.log', level=logging.WARNING)
logger=logging.getLogger(__name__)

from trackify.utils import current_time, generate_id
from trackify.db.classes import Pause, Resume, Seek

REQUEST_TIMEOUT = 0.03
ITERATION_TIMEOUT = 0.6

class SpotifyTracker:
    def __init__(self, music_provider, spotify_client):
        self.music_provider = music_provider
        self.spotify_client = spotify_client

    def start_tracking(self):
        # map user id to their last play and the time of the last request made for them
        user_data = {}
        while True:
            try:
                self.music_provider.new_conn()
                users = self.music_provider.get_users()
                for user in users:
                    user.access_token = self.music_provider.get_user_access_token(user)
                    if not user.access_token:
                        continue
                    if user.access_token.expired():
                        user.refresh_token =\
                            self.music_provider.get_user_refresh_token(user)
                        user.access_token = self.spotify_client.fetch_access_token(
                            user.refresh_token)
                        self.music_provider.add_access_token(user.access_token)

                    play, retry_after = self.spotify_client.get_current_play(
                        user.access_token)
                    if not play: # nothing playing
                        if retry_after:
                            sleep(retry_after)
                        else:
                            user_data[user.id] = None, current_time()
                        continue
                    if user.id in user_data:
                        last_play = user_data[user.id][0]
                    else:
                        last_play = None

                    if last_play is None:
                        self.music_provider.add_play(play)
                        if not play.is_playing:
                            pause = Pause(generate_id(), play, current_time())
                            self.music_provider.add_pause(pause)
                    else:
                        track_changed = not play.has_same_track_as(last_play)
                        if not track_changed:
                            play.id = last_play.id
                        if track_changed: # track changed
                            last_play.time_ended = current_time()
                            self.music_provider.update_play_time_ended(last_play)
                            self.music_provider.add_play(play)
                            if not play.is_playing:
                                pause = Pause(generate_id(), play, current_time())
                                self.music_provider.add_pause(pause)
                        elif not play.is_playing and last_play.is_playing: # track paused
                            pause = Pause(generate_id(), play, current_time())
                            self.music_provider.add_pause(pause)
                        elif play.is_playing and not last_play.is_playing: # track resumed
                            resume = Resume(generate_id(), play, current_time())
                            self.music_provider.add_resume(resume)
                        else: # if no actions just update time_ended
                            play.time_ended = current_time()
                            self.music_provider.update_play_time_ended(play)

                        # checking if a seek action (skip to position) was made
                        if not track_changed:
                            prev_request_time = user_data[user.id][1]
                            seconds_passed = (current_time() - prev_request_time) / 1000.
                            gap = abs(seconds_passed -
                                    abs(play.progress_ms - last_play.progress_ms) / 1000.)
                            if gap > 5:
                                seek = Seek(generate_id(), play, play.progress_ms,
                                            current_time())
                                self.music_provider.add_seek(seek)

                    user_data[user.id] = play, current_time()
                    sleep(REQUEST_TIMEOUT)
                    #print('{} - {}'.format(play.track.name, play.track.artists[0].name))
            except Exception as e:
                user_data = {}
                logger.exception(e)

            sleep(ITERATION_TIMEOUT)

if __name__ == '__main__':
    from trackify.config import Config
    from trackify.spotify.spotify import SpotifyClient
    from trackify.db.classes import MusicProvider

    music_provider = MusicProvider(Config.database_user, Config.database_password,
                                   Config.database, Config.database_host)
    spotify_client = SpotifyClient(Config.client_id, Config.client_secret,
                                   Config.redirect_uri, Config.scope)

    spotify_tracker = SpotifyTracker(music_provider, spotify_client)
    spotify_tracker.start_tracking()
