CONFIG = {
        'database': 'trackify',
        'database_user': 'mahmooz',
        'database_password': 'mahmooz',
        'database_host': '0.0.0.0',
        'secret_key': 'my_super_secret_key',
        'client_id': None,
        'client_secret': None,
        'scope': "user-library-read playlist-read-private user-read-playback-state user-read-currently-playing user-modify-playback-state",
        'redirect_uri': "http://localhost:5000/spotify/callback",
        'jwt_secret_key': "dev",
        'jwt_access_token_expires': 60 * 60, # 1 hour
        'jwt_refresh_token_expires': False,
        'permanent_session': True,
        # 'permanent_session_lifetime': 2678400, # the default (31 days)
}
CONFIG_UPPERCASE = {}
for key, value in CONFIG.items():
    CONFIG_UPPERCASE[key.upper()] = value
