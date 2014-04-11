#
# @author Cory Dolphin
# @wcdolphin
#
from os import environ

class Config(object):
    """
    Basic default global configuration variables not specific to any environment

    :param response: Flask response
    :param location: relative URL (i.e. without **http://localhost**)
    """
    SQLALCHEMY_ECHO = False
    SECRET_KEY = '\xfb\x12\xdf\xa1@i\xd6>V\xc0\xbb\x8fp\x16#Z\x0b\x81\xeb\x16'
    DEBUG = True
    AWS_KEY = ''
    AWS_SECRET = ''
    CACHE_TYPE = 'simple'
    PASSWORD_MAX_LENGTH = 100
    PASSWORD_MIN_LENGTH = 5
    MAX_TITLE_LENGTH = 80
    MIN_TITLE_LENGTH = 5

class DevelopmentConfig(Config):
    """ 
    The Development Configuration, provides default database and facebook credentials and
    configuration to run the application
    """ 
    BUCKET = 'testbucketorigiart'
    SQLALCHEMY_DATABASE_URI = ''
    FACEBOOK_APP_SECRET = ""
    FACEBOOK_APP_ID = ""


class TestingConfig(DevelopmentConfig):
    """
    The Testing environment at origiart-testing.herokuapp.com, uses the same database as Development.
    """
    DEBUG = False
    FACEBOOK_APP_SECRET = ""
    FACEBOOK_APP_ID = ""


class StagingConfig(TestingConfig):
    '''
    The staging environment uses the same database as Production and aims to simply emulate Production
    but provide a separate domain and application in which to test.
    
    http://origiart-staging.herokuapp.com/ | git@heroku.com:origiart-staging.git
    '''
    FACEBOOK_APP_SECRET = ""
    FACEBOOK_APP_ID = ""
    SQLALCHEMY_DATABASE_URI = ''
    BUCKET = 'origiart'


class ProductionConfig(StagingConfig):
    '''
    Extends and overrides declarations from the DevelopmentConfiguration
    '''
    FACEBOOK_APP_SECRET = ""
    FACEBOOK_APP_ID = ""

def getConfig():
    ''' Should return the proper configuration based upon environmental 
        variables and or other subsequent tests. Currently only distinguishes
        between Heroku and 'other', defaulting other to a local development database.
        TODO: test for local development database, if failed, default to a remote
        database, there should be no need for a full postgres install to test 
        or write client/HTML/CSS/js.
    '''
    if environ.get('PYTHONHOME') != None and 'heroku' in environ.get('PYTHONHOME'): ##we are on Heroku!
        env = environ.get('ORIGIART_ENV')
        if env == 'testing':
            return TestingConfig

        elif env == 'staging':
            return StagingConfig
        
        elif env == 'production':
            return ProductionConfig
        
        else:
            return ProductionConfig
    else:
        return DevelopmentConfig
