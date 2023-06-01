import os
import sys
from config.settings import MAIN_ROOT
sys.path.append(MAIN_ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django import db
from django.contrib import auth
from accounts.user_functions import is_submission_owner
from modules.dynadb.views import is_allowed_directory
UserModel = auth.get_user_model()

def check_password(environ, username, password):
    """
    Authenticates against Django's auth database
    mod_wsgi docs specify None, True, False as return value depending
    on whether the user exists and authenticates.
    """

    # db connection state is managed similarly to the wsgi handler
    # as mod_wsgi may call these functions outside of a request/response cycle
    db.reset_queries()
    path = '%s/%s' % (environ.get('SCRIPT_NAME').rstrip('/'), environ.get('PATH_INFO').lstrip('/'))
    try:
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            return None
        if not user.is_active:
            return None
        if user.check_password(password):
            if is_allowed_directory(user,url_path=path,prefix='_DB',allow_submission_dir=True):
                return True
            else:
                return None
        else:
            return False
    finally:
        db.close_old_connections()


from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()