# -*- coding: utf-8 -*-
"""
Django settings for protwis project.
"""

# import local settings
# by default, local settings are in protwis/settings_local_default.py
# you can override these settings by creating a protwis/settings_local.py file (or copying settings_local_default)
# protwis/settings_local.py is ignored by git


try:
    from protwis.settings_local import *
except ImportError:
    from protwis.settings_local_development import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))



# Application definition

INSTALLED_APPS = (
    'dynadb.apps.DynadbConfig',
    'accounts.apps.AccountsConfig',
    'view.apps.ViewConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'sendfile',
    'debug_toolbar',
    'rest_framework',
    'rest_framework_swagger',
    'common',
    'api',
    'news',
    'pages',
    'home',
    'protein',
    'family',
    'residue',
    'alignment',
    'similaritysearch',
    'similaritymatrix',
    'structure',
    'ligand',
    'interaction',
    'mutation',
    'phylogenetic_trees',
    'sitesearch',
    'build_' + SITE_NAME,
    'construct',
    'tools',
    'haystack',
    'drugs',
    'graphos',
    'revproxy',
)

MIDDLEWARE_CLASSES = (
    'protwis.custom_middlewares.MultipleProxyMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'protwis.urls'

WSGI_APPLICATION = 'protwis.wsgi.application'

# Analytics
GOOGLE_ANALYTICS_KEY = False
# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Madrid'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
STATIC_ROOT = '/protwis/static/protwis'
STATICFILES_DIRS = (os.sep.join([BASE_DIR, "static"]),)
MEDIA_URL = '/files/'
#past: MEDIA_URL = '/media/'
MEDIA_ROOT = '/protwis/sites/files/'
#past: MEDIA_ROOT = '/protwis/media/protwis'
SENDFILE_BACKEND = 'sendfile.backends.xsendfile'

#Search Engine

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.1:8983/solr/collection_gpcrmd'
    },
}

# Serializer

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'


# Templates

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'protwis.context_processors.google_analytics'
            ],
        },
    },
]

MAX_UPLOAD_SIZE=2147483648
FILE_UPLOAD_TEMP_DIR = "/tmp"

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
       'disable_existing_loggers': False,
       'formatters': {
           'verbose': {
               'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
               'datefmt' : "%d/%b/%Y %H:%M:%S"
           },
       },
       'handlers': {
           'django': {
               'level': 'DEBUG',
               'class': 'logging.FileHandler',
               'filename': 'logs/django.log',
               'formatter': 'verbose'
           },
           'build': {
               'level': 'DEBUG',
               'class': 'logging.FileHandler',
               'filename': 'logs/build.log',
               'formatter': 'verbose'
           },
           'protwis': {
               'level': 'DEBUG',
               'class': 'logging.FileHandler',
               'filename': 'logs/protwis.log',
               'formatter': 'verbose'
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
           'protwis': {
               'handlers': ['protwis'],
               'level': 'DEBUG',
           },
       }
    }

SESSION_ENGINE="django.contrib.sessions.backends.file"

#CACHE
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': CACHE_PATH,
    }
}

QUERY_CHECK_PUBLISHED = True

MDSRV_PORT=8081
MDSRV_UPSTREAM='http://localhost:8081'
MDSRV_REVERSE_PROXY = 'POST'

AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:memberpage'
LOGOUT_REDIRECT_URL = 'accounts:memberpage'

# Configure this so that it works with real mail, not terminal
#TEST
#EMAIL_USE_SSL = True
#EMAIL_USE_TLS = False
#EMAIL_HOST = '***REMOVED***'
#EMAIL_PORT = 465
#EMAIL_HOST_USER = '***REMOVED***'
#EMAIL_HOST_PASSWORD = '***REMOVED***'
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

#DEFAULT_FROM_EMAIL = 'info@gpcrmd.org'
#EMAIL_USE_SSL = True
#EMAIL_USE_TLS = False
#EMAIL_HOST = '***REMOVED***'
#EMAIL_PORT = 465
#EMAIL_HOST_USER = '***REMOVED***'
#EMAIL_HOST_PASSWORD = '***REMOVED***'

DEFAULT_FROM_EMAIL = '***REMOVED***'
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
EMAIL_HOST = '***REMOVED***'
EMAIL_PORT = 465
EMAIL_HOST_USER = '***REMOVED***'
EMAIL_HOST_PASSWORD = '***REMOVED***'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_TRANSACTIONAL_HEADERS = {'IsTransactional':True}

import mimetypes
mimetypes.add_type('text/plain; charset=UTF-8', '.log', strict=True)
