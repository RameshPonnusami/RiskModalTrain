from flask import Flask
from ml.config.logging_config import configure_logging
from ml.config.config import Config
app = Flask(__name__, static_folder='static',instance_relative_config=True)
app.config.from_object(Config)
configure_logging(app)

from ml import main_pages, api