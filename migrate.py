#!/usr/bin/python3

from trackify.db.db import DBProvider

db = DBProvider()

db.execute('ALTER TABLE access_tokens RENAME TO spotify_access_tokens')
db.execute('ALTER TABLE refresh_tokens RENAME TO spotify_refresh_tokens')
db.execute('''
CREATE TABLE IF NOT EXISTS api_refresh_tokens (
  id VARCHAR(36) PRIMARY KEY,
  time_added BIGINT NOT NULL,
  user_id VARCHAR(36) CHARACTER SET utf8mb4 NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users (id)
);
''')
db.execute('''
CREATE TABLE IF NOT EXISTS api_access_tokens (
  id VARCHAR(36) PRIMARY KEY,
  time_added BIGINT NOT NULL,
  refresh_token_id VARCHAR(36) NOT NULL,
  FOREIGN KEY (refresh_token_id) REFERENCES api_refresh_tokens (id)
);
''')

print('committing')
db.commit()
