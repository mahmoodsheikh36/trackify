from time import sleep

RATE_LIMIT_TIMEOUT = 2.5
REQUEST_TIMEOUT = 0.1
ITERATION_TIMEOUT = 1

class SpotifyTracker:
    def __init__(self, music_provider, spotify_client):
        self.music_provider = music_provider
        self.spotify_client = spotify_client

    def start_tracking(self):
        plays = {}
        while True:
            users = self.music_provider.get_users_with_tokens()
            for user in users:
                if user.access_token.expired():
                    print('access token expired!')
                    print(user.access_token.token)
                    user.access_token = self.spotify_client.fetch_access_token(
                        user.refresh_token)
                    self.music_provider.add_access_token(user.access_token)

                play = self.spotify_client.get_current_play(
                    user.access_token)
                print(play.track.name)
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
