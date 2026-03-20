import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.db')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    DEBUG = True
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
