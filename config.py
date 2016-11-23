import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'bolshoi/secret'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    GOOGLE_ID = '1051230521823-84p3bvacn277acsfidcv61csb12a4rsj.apps.googleusercontent.com'
    GOOGLE_SECRET = 'dPKh5D8AijaJPydiywLsYzM2'


class ProductionConfig(Config):
    DEBUG = False


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True