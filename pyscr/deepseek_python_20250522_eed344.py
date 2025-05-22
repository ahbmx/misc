import os
import configparser
from pathlib import Path

# Read config file
config = configparser.ConfigParser()
config.read(Path(__file__).parent.parent / 'config.ini')

# Make variables available to all modules
LOG_PATH = config['LOGGING'].get('log_path', './logs')
LOG_LEVEL = config['LOGGING'].get('log_level', 'INFO')
LOG_FILE = config['LOGGING'].get('log_file', 'application.log')
OUTPUT_PATH = config['GENERAL'].get('output_path', './output')
MAX_RETRIES = config['GENERAL'].getint('max_retries', 3)
DEFAULT_TIMEOUT = config['GENERAL'].getint('default_timeout', 30)

# Create directories if they don't exist
Path(LOG_PATH).mkdir(parents=True, exist_ok=True)
Path(OUTPUT_PATH).mkdir(parents=True, exist_ok=True)