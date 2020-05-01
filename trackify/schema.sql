CREATE TABLE IF NOT EXISTS requests (
  id INT PRIMARY KEY AUTOINCREMENT,
  time_added INT NOT NULL,
  ip TEXT NOT NULL,
  url TEXT NOT NULL,
  headers TEXT NOT NULL,
  request_data TEXT,
  form TEXT,
  referrer TEXT,
  access_route TEXT
);

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(30) NOT NULL,
  password VARCHAR(94) NOT NULL,
  email VARCHAR(255) NOT NULL,
  time_added INT NOT NULL
);

CREATE TABLE IF NOT EXISTS auth_codes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  time_added INT NOT NULL,
  code TEXT NOT NULL,
  user_id INT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS access_tokens (
  id INT AUTO_INCREMENT PRIMARY KEY,
  time_added INT NOT NULL,
  token VARCHAR(310) NOT NULL -- access token length is 303, gotta be safe
);

CREATE TABLE IF NOT EXISTS refresh_tokens (
  id INT AUTO_INCREMENT PRIMARY KEY,
  time_added INT NOT NULL,
  token VARCHAR(140) NOT NULL -- refresh token length is 131 chars but gotta be safe
);

CREATE TABLE IF NOT EXISTS tracks (
  id VARCHAR(25) PRIMARY KEY, -- track ids are 22 chars
  track_name TEXT NOT NULL,
  duration_ms INT NOT NULL,
  popularity INT NOT NULL,
  preview_url TEXT,
  track_number INT NOT NULL,
  explicit BOOL NOT NULL,
  album_id VARCHAR(25) NOT NULL,
  FOREIGN KEY (album_id) REFERENCES albums (id)
);

CREATE TABLE IF NOT EXISTS albums (
  id VARCHAR(25) PRIMARY KEY, -- album ids are 22 chars
  album_name TEXT NOT NULL,
  album_type VARCHAR(10) NOT NULL, -- think values for this are album/single, gotta be safe
  release_date VARCHAR(13) NOT NULL, -- max length is 10
  release_date_precision VARCHAR(10) NOT NULL, -- max length AFAIK is 4
);

CREATE TABLE IF NOT EXISTS artists (
  id VARCHAR(25) PRIMARY KEY, -- artist ids are 22 chars
  artist_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS album_artists (
  id INT AUTO_INCREMENT PRIMARY KEY,
  artist_id VARCHAR(25) NOT NULL,
  album_id VARCHAR(25) NOT NULL,
  FOREIGN KEY (artist_id) REFERENCES artists (id),
  FOREIGN KEY (album_id) REFERENCES albums (id)
);

CREATE TABLE IF NOT EXISTS track_artists (
  id INT AUTO_INCREMENT PRIMARY KEY,
  artist_id VARCHAR(25) NOT NULL,
  track_id VARCHAR(25) NOT NULL,
  FOREIGN KEY (artist_id) REFERENCES artists (id),
  FOREIGN KEY (track_id) REFERENCES tracks (id)
);

CREATE TABLE IF NOT EXISTS plays (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  time_started INT NOT NULL,
  time_ended INT NOT NULL,
  track_id VARCHAR(25) NOT NULL,
  device_id VARCHAR(45) NOT NULL,
  context_id INT,
  FOREIGN KEY (track_id) REFERENCES tracks (id),
  FOREIGN KEY (user_id) REFERENCES users (id),
  FOREIGN KEY (context_id) REFERENCES contexts (id),
  FOREIGN KEY (device_id) REFERENCES devices (id)
);

CREATE TABLE IF NOT EXISTS devices (
  id VARCHAR(45) PRIMARY KEY, -- devices ids are 40 chars long
  device_name TEXT NOT NULL,
  device_type TEXT NOT NULL,
  volume_percent INT NOT NULL
);

CREATE TABLE IF NOT EXISTS contexts (
  uri TEXT PRIMARY KEY,
  context_type VARCHAR(10) NOT NULL -- i think possible values are album/playlist
);

CREATE TABLE IF NOT EXISTS pauses (
  id INT AUTO_INCREMENT PRIMARY KEY,
  time_added INT NOT NULL,
  play_id INT NOT NULL,
  FOREIGN KEY (play_id) REFERENCES plays (id)
);

CREATE TABLE IF NOT EXISTS resumes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  time_added INT NOT NULL,
  play_id INT NOT NULL,
  FOREIGN KEY (play_id) REFERENCES plays (id)
);

CREATE TABLE IF NOT EXISTS seeks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  time_added INT NOT NULL,
  position INT NOT NULL,
  play_id INT NOT NULL,
  FOREIGN KEY (play_id) REFERENCES plays (id)
);
