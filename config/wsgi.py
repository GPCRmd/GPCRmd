"""
WSGI config for gpcrmd project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""


import os
SSL = False

#Determine if the app runs with SSL or not (determined by the config.settings file)
if SSL==True:
    os.environ['HTTPS'] = "on"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

