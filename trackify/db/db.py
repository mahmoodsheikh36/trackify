import mysql.connector
from trackify.utils import current_time, generate_id

class DBProvider:
    def __init__(self, user, passwd, database='trackify', host='localhost'):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            passwd=passwd,
            database=database,
        )

    def cursor(self):
        return self.conn.cursor()

    def close(self):
        self.conn.close()

    def commit(self):
        self.conn.commit()

    def execute(self, sql, values):
        self.cursor().execute(sql, values)

    def add_request(self, request_id, time_added, ip, url, headers, data, form, referrer,
                    access_route):
        self.execute('INSERT INTO requests (id, time_added, ip, url, headers, request_data,\
                                            form, referrer, access_route)\
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                     (request_id, time_added, ip, url, headers, data, form,
                      referrer, access_route))

    def add_user(self, user_id, username, password, email, time_added):
        self.execute('INSERT INTO users (id, username, password, email, time_added)\
                      VALUES (%s, %s, %s, %s, %s)', (user_id, username, password, email,
                                                     time_added))

    def add_auth_code(self, auth_code_id, time_added, code, user_id):
        self.execute('INSERT INTO auth_codes (id, time_added, code, user_id)\
                      VALUES (%s, %s, %s, %s)', (auth_code_id, time_added, code, user_id))

    def add_access_token(self, access_token_id, token, user_id, time_added):
        self.execute('INSERT INTO access_tokens (id, time_added, user_id, token)\
                      VALUES (%s, %s, %s, %s)', (access_token_id, time_added, user_id,
                                                 token))

    def add_refresh_token(self, refresh_token_id, token, user_id, time_added):
        self.execute('INSERT INTO refresh_tokens (id, time_added, user_id, token)\
                      VALUES (%s, %s, %s, %s)', (refresh_token_id, time_added, user_id,
                                                 token))

    def add_album(self, album_id, name, album_type, release_date, release_date_precision):
        self.execute('INSERT INTO albums (id, album_name, album_type, release_date,\
                                          release_date_precision)\
                     VALUES (%s, %s, %s, %s, %s)', (album_id, name, album_type,
                                                    release_date, release_date_precision,))

    def add_track(self, track_id, name, duration_ms, popularity, preview_url, track_number,
                  explicit, album_id):
        self.execute('INSERT INTO tracks (id, track_name, duration_ms, popularity,\
                                          preview_url, track_number, explicit, album_id)\
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                     name, duration_ms, popularity, preview_url, track_number, explicit,
                     album_id)

    def add_artist(self, artist_id, artist_name):
        self.execute('INSERT INTO artists (id, artist_name) VALUES (%s)',
                     (artist_id, artist_name,))

    def add_album_artist(self, row_id, album_id, artist_id):
        self.execute('INSERT INTO album_artists (id, album_id, artist_id)\
                      VALUES (%s, %s, %s)', (row_id, album_id, artist_id))

    def add_track_artist(self, row_id, track_id, artist_id):
        self.execute('INSERT INTO album_artists (id, album_id, artist_id)\
                      VALUES (%s, %s, %s)', (row_id, album_id, artist_id))

    def add_device(self, device_id, name, device_type):
        self.execute('INSERT INTO devices (id, device_name, device_type)\
                      VALUES (%s, %s, %s)', (device_id, name, device_type))

    def add_context(self, uri, context_type):
        self.execute('INSERT INTO contexts (uri, context_type)\
                      VALUES (%s, %s)', (uri, context_type))

    def add_play(self, play_id, time_started, time_ended, volume_percent, user_id,
                 track_id, device_id, context_uri):
        self.execute('INSERT INTO plays (id, time_started, time_ended, volume_percent,\
                      user_id, track_id, device_id, context_uri)\
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                     (play_id, time_started, time_ended, volume_percent, user_id,
                      track_id, device_id, context_uri))

    def add_pause(self, pause_id, time_added, play_id):
        self.execute('INSERT INTO pauses (id, time_added, play_id)\
                      VALUES (%s, %s, %s)', (pause_id, time_added, play_id))

    def add_resume(self, resume_id, time_added, play_id):
        self.execute('INSERT INTO resumes (id, time_added, play_id)\
                      VALUES (%s, %s, %s)', (resume_id, time_added, play_id))

    def add_seek(self, seek_id, time_added, position, play_id):
        self.execute('INSERT INTO seeks (id, time_added, position, play_id)',
                     (seek_id, time_added, position, play_id))

    def get_user_by_username(self, username):
        c = self.cursor()
        c.execute('SELECT * FROM users WHERE username = %s', (username,))
        return c.fetchone()

    def get_user(self, user_id):
        c = self.cursor()
        c.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        return c.fetchone()

    def get_user_auth_code(self, user_id):
        c = self.cursor()
        c.execute('SELECT * FROM auth_codes WHERE user_id = %s ORDER BY time_added DESC\
                   LIMIT 1',
                  (user_id,))
        return c.fetchone()

    def get_user_access_token(self, user_id):
        c = self.cursor()
        c.execute('SELECT * FROM access_tokens WHERE user_id = %s\
                   ORDER BY time_added DESC LIMIT 1',
                  (user_id,))
        return c.fetchone()

    def get_user_refresh_token(self, user_id):
        c = self.cursor()
        c.execute('SELECT * FROM refresh_tokens WHERE user_id = %s\
                   ORDER BY time_added DESC LIMIT 1',
                  (user_id,))
        return c.fetchone()

    def get_users(self):
        c = self.cursor()
        c.execute('SELECT * FROM users')
        return c.fetchall()

    def get_users_with_tokens(self):
        c = self.cursor()
        c.execute('\
        SELECT * FROM users, access_tokens, refresh_tokens\
        WHERE users.id = refresh_tokens.user_id AND refresh_tokens.id =\
        (SELECT id FROM refresh_tokens ORDER BY time_added DESC LIMIT 1) AND\
        users.id = access_tokens.user_id AND access_tokens.id =\
        (SELECT id from access_tokens ORDER BY time_added DESC LIMIT 1)\
        ')
        return c.fetchall()
