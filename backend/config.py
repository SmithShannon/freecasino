import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:abc@localhost:5432/slots'

SQLALCHEMY_ENGINE = "postgresql://postgres:abc@localhost"

SQLALCHEMY_TRACK_MODIFICATIONS = True
