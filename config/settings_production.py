# local settings
import os
from config.settings import SSL
from config.SECRETS import *

# Site specific constants
SITE_NAME = 'gpcrmd' # used for site specific files
SITE_TITLE = 'GPCRmd' # for display in templates
DATA_DIR = '/var/www/GPCRmd/data/' + SITE_NAME
BUILD_CACHE_DIR = DATA_DIR + '/cache'
DEFAULT_NUMBERING_SCHEME = 'gpcrmd'
DEFAULT_PROTEIN_STATE = 'inactive'
REFERENCE_POSITIONS = {'TM1': '1x50', 'ICL1': '12x50', 'TM2': '2x50', 'ECL1': '23x50', 'TM3': '3x50', 'ICL2': '34x50',
    'TM4': '4x50', 'ECL2': '45x50', 'TM5': '5x50', 'TM6': '6x50', 'TM7': '7x50', 'H8': '8x50'}
DOCUMENTATION_URL = 'https://gpcrmd-docs.readthedocs.io/en/latest/'

# Analytics
GOOGLE_ANALYTICS_KEY = False

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'gpcrmd',
        'USER': POSTGRESQLADMIN_USER,
        'PASSWORD': POSTGRESQLADMIN_PASS,
        'HOST': 'localhost',
        'OPTIONS': {
            'options': '-c search_path=public'
        },
    }
}

# Quick-start development settings - unsuitable for production
QUERY_CHECK_PUBLISHED = True
FILES_NO_LOGIN = False

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_TRANSACTIONAL_HEADERS = {}

#Import secrets
from config.SECRETS import SECRET_KEY
from config.SECRETS import PASS_CORPLOTS

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

CACHE_PATH = "/tmp/django_cache"

MDSRV_REVERSE_PROXY = 'ALL' #POST
if SSL==True:
    MDSRV_PORT=443
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    os.environ['wsgi.url_scheme'] = 'https'
else:
    MDSRV_PORT=80

#MDSRV_PORT=8081
