import configparser
import os

working_directory = os.path.dirname(os.path.abspath(__file__))

config = configparser.ConfigParser()
config.read(working_directory+'/lost_in_logs.conf')

# GLOBAL DEFINES
# DATABASE CONF
DB_HOST = config['NEO4J']['DBHost']
DB_USER = config['NEO4J']['DBUser']
DB_PASS = config['NEO4J']['DBPass']

def get_key(section, name):
    key = None
    try:
        key = config[section][name]
    except:
        key = None
    return key