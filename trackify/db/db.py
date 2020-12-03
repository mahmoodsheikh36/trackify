import mysql.connector

from trackify.utils import current_time, generate_id
import config

class DBProvider:
    def __init__(self, user=config.database_user, passwd=config.database_password,
                 database=config.database, host=config.database_host):
        self.user = user
        self.passwd = passwd
        self.database = database
        self.host = host
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            passwd=passwd,
            database=database,
        )

    def cursor(self):
        return self.conn.cursor(dictionary=True)

    def close(self):
        self.conn.close()

    def new_conn(self):
        self.commit()
        self.close()
        self.conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            passwd=self.passwd,
            database=self.database,
        )

    def commit(self):
        self.conn.commit()

    def execute(self, sql, values):
        self.cursor().execute(sql, values)

    def add_request(self, request_id, time_added, ip, url, headers, data, form, referrer,
                    access_route, user_id):
        self.execute('INSERT INTO requests (id, time_added, ip, url, headers,\
                      request_data, form, referrer, access_route, user_id)\
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                     (request_id, time_added, ip, url, headers, data, form,
                      referrer, access_route, user_id))

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

    def add_track(self, track_id, name, duration_ms, popularity, preview_url,
                  track_number, explicit, album_id):
        self.execute('INSERT INTO tracks (id, track_name, duration_ms, popularity,\
                      preview_url, track_number, explicit, album_id)\
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                     (track_id, name, duration_ms, popularity, preview_url, track_number,
                      explicit, album_id))

    def add_artist(self, artist_id, artist_name):
        self.execute('INSERT INTO artists (id, artist_name) VALUES (%s, %s)',
                     (artist_id, artist_name,))

    def add_album_artist(self, row_id, album_id, artist_id):
        self.execute('INSERT INTO album_artists (id, album_id, artist_id)\
                      VALUES (%s, %s, %s)', (row_id, album_id, artist_id))

    def add_track_artist(self, row_id, track_id, artist_id):
        self.execute('INSERT INTO track_artists (id, track_id, artist_id)\
                      VALUES (%s, %s, %s)', (row_id, track_id, artist_id))

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
        self.execute('INSERT INTO seeks (id, time_added, position, play_id)\
                      VALUES (%s, %s, %s, %s)',
                     (seek_id, time_added, position, play_id))

    def add_album_image(self, row_id, url, album_id, width, height):
        self.execute('INSERT INTO album_images (id, width, height, url, album_id)\
                      VALUES (%s, %s, %s, %s, %s)',
                     (row_id, width, height, url, album_id))

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

    def get_tracks(self):
        c = self.cursor()
        c.execute('SELECT * FROM tracks')
        return c.fetchall()

    def get_artists(self):
        c = self.cursor()
        c.execute('SELECT * FROM artists')
        return c.fetchall()

    def get_albums(self):
        c = self.cursor()
        c.execute('SELECT * FROM albums')
        return c.fetchall()

    def get_album_images(self):
        c = self.cursor()
        c.execute('SELECT * FROM album_images')
        return c.fetchall()

    def get_album_artists(self):
        c = self.cursor()
        c.execute('SELECT * FROM album_artists')
        return c.fetchall()

    def get_album(self, album_id):
        c = self.cursor()
        c.execute('SELECT * FROM albums WHERE id = %s', (album_id,))
        return c.fetchone()

    def get_track_artists(self):
        c = self.cursor()
        c.execute('SELECT * FROM track_artists')
        return c.fetchall()

    def get_track(self, track_id):
        c = self.cursor()
        c.execute('SELECT * FROM tracks WHERE id = %s', (track_id,))
        return c.fetchone()

    def get_artist(self, artist_id):
        c = self.cursor()
        c.execute('SELECT * FROM artists WHERE id = %s', (artist_id,))
        return c.fetchone()

    def get_context(self, uri):
        c = self.cursor()
        c.execute('SELECT * FROM contexts WHERE uri = %s', (uri,))
        return c.fetchone()

    def get_device(self, device_id):
        c = self.cursor()
        c.execute('SELECT * FROM devices WHERE id = %s', (device_id,))
        return c.fetchone()

    def get_last_user_play(self, user_id):
        c = self.cursor()
        c.execute('SELECT * FROM plays WHERE user_id = %s', (user_id,))
        return c.fetchone()

    def update_play_time_ended(self, play_id, time_ended):
        self.execute('UPDATE plays SET time_ended = %s WHERE id = %s',
                     (time_ended, play_id))

    def get_play(self, play_id):
        c = self.cursor()
        c.execute('SELECT * FROM plays WHERE id = %s', (play_id,))
        return c.fetchone()

    def get_user_pauses(self, user_id, from_time, to_time):
        c = self.cursor()
        c.execute('SELECT * FROM pauses WHERE time_added >= %s AND play_id IN\
                   (SELECT id FROM plays WHERE user_id = %s)', (from_time, user_id,))
        return c.fetchall()

    def get_user_resumes(self, user_id, from_time, to_time):
        c = self.cursor()
        c.execute('SELECT * FROM resumes WHERE time_added >= %s AND play_id IN\
                   (SELECT id FROM plays WHERE user_id = %s)', (from_time, user_id,))
        return c.fetchall()

    def get_user_seeks(self, user_id, from_time, to_time):
        c = self.cursor()
        c.execute('SELECT * FROM seeks WHERE time_added >= %s AND play_id IN\
                   (SELECT id FROM plays WHERE user_id = %s)', (from_time, user_id,))
        return c.fetchall()

    def get_user_plays(self, user_id, from_time, to_time):
        c = self.cursor()
        c.execute('SELECT * FROM plays WHERE user_id = %s AND\
                   ((time_started >= %s AND time_started <= %s) OR (time_ended >= %s AND time_ended <= %s))',
                (user_id, from_time, to_time, from_time, to_time))
        return c.fetchall()

    def get_user_devices(self, user_id):
        c = self.cursor()
        c.execute('SELECT * FROM devices WHERE id IN\
                   (SELECT device_id FROM plays WHERE user_id = %s)', [user_id])
        return c.fetchall()

    def get_user_tracks(self, user_id, from_time, to_time):
        c = self.cursor()
        c.execute('SELECT * FROM tracks WHERE tracks.id IN\
                   (SELECT track_id FROM plays WHERE user_id = %s AND\
                   ((time_started >= %s AND time_started <= %s) OR (time_ended >= %s AND time_ended <= %s)))',
                  (user_id, from_time, to_time, from_time, to_time))
        return c.fetchall()

    def get_user_albums(self, user_id, from_time, to_time):
        c = self.cursor()
        c.execute('SELECT * FROM albums WHERE albums.id IN\
                   (SELECT album_id FROM tracks WHERE tracks.id IN\
                   (SELECT track_id FROM plays WHERE user_id = %s AND\
                   ((time_started >= %s AND time_started <= %s) OR (time_ended >= %s AND time_ended <= %s))))',
                  (user_id, from_time, to_time, from_time, to_time))
        return c.fetchall()

    def get_user_artists(self, user_id, from_time, to_time):
        c = self.cursor()
        c.execute('SELECT a.* \
FROM plays p \
INNER JOIN tracks t ON t.id = p.track_id \
INNER JOIN track_artists ta ON ta.track_id = t.id \
LEFT JOIN album_artists aa ON aa.album_id = t.album_id \
INNER JOIN artists a ON a.id IN (ta.artist_id, aa.artist_id) \
WHERE p.user_id = %s AND ((p.time_started >= %s AND p.time_started <= %s) OR (p.time_ended >= %s AND p.time_ended <= %s))\
',
                  (user_id, from_time, to_time, from_time, to_time))
        return c.fetchall()

    def get_user_album_images(self, user_id, from_time, to_time):
        c = self.cursor()
        c.execute('SELECT * FROM album_images WHERE album_id IN\
                   (SELECT id FROM albums WHERE album_id IN\
                   (SELECT album_id FROM tracks WHERE tracks.id IN\
                   (SELECT track_id FROM plays WHERE user_id = %s AND\
                   ((time_started >= %s AND time_started <= %s) OR (time_ended >= %s AND time_ended <= %s)))))',
                  (user_id, from_time, to_time, from_time, to_time))
        return c.fetchall()

    def get_user_album_artists(self, user_id, from_time, to_time):
        c = self.cursor()
        c.execute('SELECT * FROM album_artists WHERE album_id IN\
                   (SELECT id FROM albums WHERE album_id IN\
                   (SELECT album_id FROM tracks WHERE tracks.id IN\
                   (SELECT track_id FROM plays WHERE user_id = %s AND\
                   ((time_started >= %s AND time_started <= %s) OR (time_ended >= %s AND time_ended <= %s)))))',
                  (user_id, from_time, to_time, from_time, to_time))
        return c.fetchall()

    def get_user_track_artists(self, user_id, from_time, to_time):
        c = self.cursor()
        c.execute('SELECT * FROM track_artists WHERE track_id IN\
                   (SELECT track_id FROM plays WHERE user_id = %s AND\
                   ((time_started >= %s AND time_started <= %s) OR (time_ended >= %s AND time_ended <= %s)))',
                  (user_id, from_time, to_time, from_time, to_time))
        return c.fetchall()

    def user_has_plays(self, user_id):
        c = self.cursor()
        c.execute('SELECT id FROM plays WHERE user_id = %s LIMIT 1', (user_id,))
        return c.fetchone() is not None

    def get_user_settings(self, user_id):
        c = self.cursor()
        c.execute('SELECT * FROM user_settings WHERE user_id = %s', (user_id,))
        return c.fetchall()

    def get_settings(self):
        c = self.cursor()
        c.execute('SELECT * FROM settings')
        return c.fetchall()

    def add_user_setting(self, setting_id, user_id, value):
        self.execute('INSERT INTO user_settings (setting_value, setting_id, user_id)\
                      VALUES (%s, %s, %s)',
                     (value, setting_id, user_id))
        self.commit()

    def update_user_setting(self, setting_id, user_id, value):
        self.execute('UPDATE user_settings SET setting_value = %s WHERE setting_id = %s\
                      AND user_id = %s',
                     (value, setting_id, user_id))
        self.commit()

    def get_user_setting(self, user_id, setting_id):
        c = self.cursor()
        c.execute('SELECT * FROM user_settings WHERE setting_id = %s AND\
                   user_id = %s', (setting_id, user_id))
        return c.fetchone()

    def execute_fetchall(self, sql, values=[]):
        c = self.cursor()
        c.execute(sql, values)
        return c.fetchall()

    def execute_fetchone(self, sql, values=[]):
        c = self.cursor()
        c.execute(sql, values)
        return c.fetchone()

    def get_user_data(self, user_id, from_time, to_time):
        return self.execute_fetchall('''
        SELECT
        p.id as play_id,
        p.time_started as play_time_started,
        p.time_ended as play_time_ended,
        p.user_id as play_user_id,
        p.track_id as play_track_id,
        p.device_id as play_device_id,
        p.context_uri as play_context_uri,
        p.volume_percent as play_volume_percent,
        a.id as artist_id,
        a.artist_name as artist_name,
        t.id as track_id,
        t.duration_ms as track_duration_ms,
        t.popularity as track_popularity,
        t.preview_url as track_preview_url,
        t.explicit as track_explicit,
        t.album_id as track_album_id,
        t.track_name as track_name,
        t.track_number as track_number,
        al.id as album_id,
        al.release_date as album_release_date,
        al.release_date_precision as album_release_date_precision,
        al.album_name as album_name,
        al.album_type as album_type,
        pa.id as pause_id,
        pa.time_added as pause_time_added,
        r.id as resume_id,
        r.time_added as resume_time_added,
        s.id as seek_id,
        s.time_added as seek_time_added,
        s.position as seek_position,
        ali.id as album_image_id,
        ali.width as album_image_width,
        ali.height as album_image_height,
        ali.url as album_image_url
        FROM plays p
        JOIN tracks t ON t.id = p.track_id
        JOIN track_artists ta ON t.id = ta.track_id
        JOIN artists a ON a.id = ta.artist_id
        JOIN albums al ON al.id = t.album_id
        JOIN album_images ali on ali.album_id = t.album_id
        LEFT JOIN pauses pa ON pa.play_id = p.id
        LEFT JOIN resumes r ON r.play_id = p.id
        LEFT JOIN seeks s ON s.play_id = p.id
        WHERE p.user_id = %s AND ((p.time_started >= %s AND p.time_started <= %s) OR
                                    (p.time_ended >= %s AND p.time_ended <= %s))
        ''', (user_id, from_time, to_time, from_time, to_time)) 

    def get_all_users_data(self, from_time, to_time):
        return self.execute_fetchall('''
        SELECT
        u.id as user_id,
        u.username as user_username,
        u.time_added as user_time_added,
        p.id as play_id,
        p.time_started as play_time_started,
        p.time_ended as play_time_ended,
        p.user_id as play_user_id,
        p.track_id as play_track_id,
        p.device_id as play_device_id,
        p.context_uri as play_context_uri,
        p.volume_percent as play_volume_percent,
        a.id as artist_id,
        a.artist_name as artist_name,
        t.id as track_id,
        t.duration_ms as track_duration_ms,
        t.popularity as track_popularity,
        t.preview_url as track_preview_url,
        t.explicit as track_explicit,
        t.album_id as track_album_id,
        t.track_name as track_name,
        t.track_number as track_number,
        al.id as album_id,
        al.release_date as album_release_date,
        al.release_date_precision as album_release_date_precision,
        al.album_name as album_name,
        al.album_type as album_type,
        pa.id as pause_id,
        pa.time_added as pause_time_added,
        r.id as resume_id,
        r.time_added as resume_time_added,
        s.id as seek_id,
        s.time_added as seek_time_added,
        s.position as seek_position,
        ali.id as album_image_id,
        ali.width as album_image_width,
        ali.height as album_image_height,
        ali.url as album_image_url
        FROM users u
        JOIN plays p ON p.user_id = u.id AND ((p.time_started >= %s AND p.time_started <= %s) OR (p.time_ended >= %s AND p.time_ended <= %s))
        JOIN tracks t ON t.id = p.track_id
        JOIN track_artists ta ON t.id = ta.track_id
        JOIN artists a ON a.id = ta.artist_id
        JOIN albums al ON al.id = t.album_id
        JOIN album_artists aa ON al.id = aa.album_id
        JOIN album_images ali on ali.album_id = t.album_id
        LEFT JOIN pauses pa ON pa.play_id = p.id
        LEFT JOIN resumes r ON r.play_id = p.id
        LEFT JOIN seeks s ON s.play_id = p.id
        ''', (from_time, to_time, from_time, to_time))
