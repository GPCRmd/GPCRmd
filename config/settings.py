# -*- coding: utf-8 -*-
"""
Django settings for GPCRmd project.
"""

#Defaults
QUERY_CHECK_PUBLISHED = True
FILES_NO_LOGIN = False

#Determine http or https (ssl)
SSL=True
DEV = True

#Settings selection
if DEV == False:
    from config.settings_production import *
else:
    from config.settings_development import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__)) #/var/www/GPCRmd

DEBUG_TOOLBAR = True

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_yasg',
    'modules.accounts.apps.AccountsConfig',
    'modules.api',
    'modules.common',
    'modules.contact_maps',
    'modules.corplots',
    'modules.covid19',
    'modules.crossreceptor_analysis.apps.CrossreceptorAnalysisConfig',
    'modules.drugs',
    'modules.dynadb.apps.DynadbConfig',
    'modules.home',
    'modules.interaction',
    'modules.ligand',
    'modules.mutation',
    'modules.news',
    'modules.protein',
    'modules.residue',
    'modules.sc2md',
    'modules.structure',
    'modules.view.apps.ViewConfig'

]
# INSTALLED_APPS = [
#     'sendfile',
#     'pages',
#     'family',
#     'alignment',
#     'similaritysearch',
#     'similaritymatrix',
#     'phylogenetic_trees',
#     'sitesearch',
#     'build_' + SITE_NAME,
#     'construct',
#     'tools',
#     'haystack',
#     'graphos',
#     'revproxy',
# ]

if DEBUG_TOOLBAR:
    INSTALLED_APPS.append('debug_toolbar')

DEBUG_TOOLBAR_MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware']
    
if not DEBUG_TOOLBAR:
    DEBUG_TOOLBAR_MIDDLEWARE = []
    
# ['config.custom_middlewares.MultipleProxyMiddleware']+\
MIDDLEWARE = DEBUG_TOOLBAR_MIDDLEWARE+\
    ['django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django_session_timeout.middleware.SessionTimeoutMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'config.custom_middlewares.WsgiLogErrors',
]

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

# Analytics
GOOGLE_ANALYTICS_KEY = False

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_L10N = True
USE_TZ = True

#DATABASE
DB_ENGINE = 'gpcrmd_admin'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
# STATIC_ROOT = '/var/www/GPCRmd/static'
# STATICFILES_DIRS = (os.sep.join([BASE_DIR, "static"]),)
if DEBUG:
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'static')
    ]
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/files/'
MEDIA_ROOT = '/GPCRmd/media/files/'
SENDFILE_BACKEND = 'sendfile.backends.xsendfile'

MAIN_ROOT = '/var/www/GPCRmd'
TEMP_ROOT = '/var/www/GPCRmd/templates'
#MODULES DIR
MODULES_ROOT = "/var/www/GPCRmd/modules"
DOWNLOAD_FILES = "/GPCRmd/media/tmp/GPCRmd_downloads"
#Search Engine
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.1:8983/solr/collection_gpcrmd'
    },
}

# Serializer
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# Rest Framework
REST_FRAMEWORK = {
    # 'DEFAULT_AUTHENTICATION_CLASSES': [
    #     'rest_framework.authentication.BasicAuthentication',
    #     'rest_framework.authentication.SessionAuthentication',
    # ]
}
SWAGGER_SETTINGS = {
    'DOC_EXPANSION': "None", # Collapse everything 
    'SECURITY_DEFINITIONS': {
        'Basic': {
            'type': 'basic'
        },
    },
}

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
            f'{TEMP_ROOT}/'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'config.context_processors.google_analytics', 
            ],
        },
    },
]

DEFAULT_AUTO_FIELD="django.db.models.AutoField"

#File settings
MAX_UPLOAD_SIZE=2147483648
DATA_UPLOAD_MAX_MEMORY_SIZE = 20971520
NO_FILE_MAX_POST_SIZE = 52428800
# FILE_UPLOAD_TEMP_DIR = "/tmp"
# FILE_UPLOAD_PERMISSIONS = 0o660

if DEBUG:
   TEMPLATES[0]['OPTIONS']['debug'] = True
   #VOLVER A PONER EN TRUE

# Debug toolbar
if DEBUG:
    DEBUG_TOOLBAR_PATCH_SETTINGS = False
    INTERNAL_IPS = ('10.0.2.2')

# Logging
if DEBUG:
    LOGGING = {
       'version': 1,
       'disable_existing_loggers': True,
       'formatters': {
           'verbose': {
               'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
               'datefmt' : "%d/%b/%Y %H:%M:%S"
           },
       },
       'handlers': {
           'django': {
               'level': 'DEBUG',
               'class': 'logging.handlers.RotatingFileHandler',
               'filename': f'{BASE_DIR}/logs/django.log',
               'formatter': 'verbose',
               'backupCount': 10, # keep at most 10 log files
                'maxBytes': 5242880, # 5*1024*1024 bytes (5MB)
           },
           'build': {
               'level': 'DEBUG',
               'class': 'logging.handlers.RotatingFileHandler',
               'filename': f'{BASE_DIR}/logs/build.log',
               'formatter': 'verbose',
               'backupCount': 10, # keep at most 10 log files
                'maxBytes': 5242880, # 5*1024*1024 bytes (5MB)
           },
           'gpcrmd': {
               'level': 'DEBUG',
               'class': 'logging.handlers.RotatingFileHandler',
               'filename': f'{BASE_DIR}/logs/gpcrmd.log',
               'formatter': 'verbose',
               'backupCount': 10, # keep at most 10 log files
                'maxBytes': 5242880, # 5*1024*1024 bytes (5MB)
           },
       },
       'loggers': {
           'django': {
               'handlers':['django'],
               'propagate': True,
               'level':'DEBUG',
           },
           'build': {
               'handlers': ['build'],
               'level': 'DEBUG',
           },
           'gpcrmd': {
               'handlers': ['gpcrmd'],
               'level': 'DEBUG',
           },
       }
    }

SESSION_ENGINE="django.contrib.sessions.backends.file"

#session expire
SESSION_EXPIRE_SECONDS = 1800 # Expire after 30 minutes
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True #Invalid session

SESSION_TIMEOUT_REDITECT = 'accounts:login'

#CACHE
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': CACHE_PATH,
    }
}

#MDSRV
MDSRV_UPSTREAM='https://localhost:8081'

AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:memberpage'
LOGOUT_REDIRECT_URL = 'accounts:memberpage'

import mimetypes
mimetypes.add_type('text/x-log; charset=UTF-8', '.log', strict=True)
mimetypes.add_type('chemical/x-mdl-sdfile; charset=UTF-8', '.sdf', strict=True)
mimetypes.add_type('chemical/x-pdb', '.pdb', strict=True)
mimetypes.add_type('chemical/x-charmm-param', '.prm', strict=True)
mimetypes.add_type('chemical/x-charmm-psf', '.psf', strict=True)

