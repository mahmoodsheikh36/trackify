import json

def load_config():
    with open('config.json') as config_file:
        config_dict = json.loads(config_file.read())
        Config.database = config_dict['database']
        Config.database_user = config_dict['database_user']
        Config.database_password = config_dict['database_password']
        Config.database_host = config_dict['database_host']
        Config.secret_key = config_dict['secret_key']

class Config:
    database = 'trackify'
    database_user = 'trackify'
    database_password = 'password'
    database_host = '0.0.0.0'
    secret_key = 'my_super_secret_key'

load_config()
