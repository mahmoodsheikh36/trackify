#!/usr/bin/python3

from trackify.db.db import DBProvider

tables = ['users', 'requests', 'auth_codes', 'access_tokens',
          'refresh_tokens', 'pauses', 'resumes', 'seeks']

db = DBProvider()

for table in tables:
    print(table)
    try:
        db.execute('alter table ' + table + ' add time_added2 bigint', [])
    except:
        print('time_added2 column already exists')
    rows = db.execute_fetchall('select * from ' + table, [])
    for row in rows:
        db.execute('update ' + table + ' set time_added2 = %s where id = %s',
                   [int(row['time_added']), row['id']])
    db.execute('alter table ' + table + ' drop column time_added', [])
    db.execute('ALTER TABLE ' + table + ' CHANGE `time_added2` `time_added` bigint', [])

print('plays')
db.execute('alter table plays add time_ended2 bigint', [])
db.execute('alter table plays add time_started2 bigint', [])
rows = db.execute_fetchall('select * from plays', [])
for row in rows:
    db.execute('update plays set time_ended2 = %s where id = %s', [int(row['time_ended']), row['id']])
    db.execute('update plays set time_started2 = %s where id = %s', [int(row['time_started']), row['id']])
db.execute('alter table plays drop column time_ended', [])
db.execute('alter table plays drop column time_started', [])
db.execute('ALTER TABLE plays CHANGE `time_ended2` `time_ended` bigint', [])
db.execute('ALTER TABLE plays CHANGE `time_started2` `time_started` bigint', [])

print('committing')
db.commit()
