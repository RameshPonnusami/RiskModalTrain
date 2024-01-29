secret_key = "your_secret_key"
# Define static user credentials



# logging_config.py

# config.py

import os

class Config:
    DEBUG = True
    TESTING = False
    SECRET_KEY = 'your_secret_key'
    # Logging configuration
    LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOGGING_LOCATION = 'app.log'
    LOGGING_LEVEL = 'DEBUG'  # Adjust as needed
    VALID_USERNAME = "admin"
    VALID_PASSWORD = "admin"


