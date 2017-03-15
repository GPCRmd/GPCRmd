from functools import wraps
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import resolve_url
#from django.utils import six
from django.utils.decorators import available_attrs
from django.utils.six.moves.urllib.parse import urlparse
from dynadb.models import DyndbSubmission, DyndbProtein, DyndbCompound ,DyndbMolecule, DyndbComplexExp, DyndbComplexMolecule, DyndbModel, DyndbDynamics 
from django.db.models import F

def user_passes_test_args(test_func, login_url=None, access_denied_response=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user,*args, **kwargs):
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            # break infinite redirect to login
            if request.user.is_authenticated():
                if access_denied_response is not None:
                    return access_denied_response 
                redirect_field_name_final = None
            else:
                redirect_field_name_final = redirect_field_name
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(
                path, resolved_login_url, redirect_field_name_final)
        return _wrapped_view
    return decorator
    
def is_submission_owner(user,submission_id,*args,**kwargs):
    entry = DyndbSubmission.objects.filter(pk=submission_id,user_id=user)
    return entry.exists()
    
def is_published_or_submission_owner(user,object_type=None,incall=False,*args,**kwargs):
    ''' Returns True or False if the object is published or if the user is 
    owner of a submission linked to the object [object_type]_id keyword 
    when the object ID is an integer or a string that can be converted to an integer.
    
    If '[object_type]_id' is a list or tuple object with object IDs as integers, a set with the IDs
    the user have access to is returned.'''    
    

    object_type_dict = {
        'protein'               : {'dbobject': DyndbProtein,            'path_to_submission_id': 'dyndbsubmissionprotein__submission_id'},
        'compound'              : {'dbobject': DyndbCompound,           'path_to_submission_id': 'dyndbmolecule__dyndbsubmissionmolecule__submission_id'},
        'molecule'              : {'dbobject': DyndbMolecule,           'path_to_submission_id': 'dyndbsubmissionmolecule__submission_id'},
        'complex'               : {'dbobject': DyndbComplexExp,         'path_to_submission_id': 'dyndbcomplexmolecule__dyndbmodel__dyndbsubmissionmodel__submission_id'},
        'model'                 : {'dbobject': DyndbModel,              'path_to_submission_id': 'dyndbsubmissionmodel__submission_id'},
        'dynamics'              : {'dbobject': DyndbDynamics,           'path_to_submission_id': 'submission_id'},
    }
    
    if not settings.QUERY_CHECK_PUBLISHED or incall:
        return True
    
    #if object_type is not defined obtain it from object ID keyword argument name
    if object_type is None:
        kwargs_keys = kwargs.keys()
        object_types = list(filter(lambda x: x.endswith('_id') and x[:-3] in object_type_dict, kwargs_keys))
        object_types_len = len(object_types)
        if object_types_len > 1:
            raise TypeError('Missing object_type argument and found '+str(len(object_types))+' valid [object_type]_id keyword argument(s).')
        elif object_types_len == 1:
            object_type = object_types[0][:-3]
        else:
            raise TypeError('Missing object_type argument or a valid [object_type]_id keyword argument.')
        
    
    if object_type not in object_type_dict:
        raise ValueError('Unknown object type: "'+str(object_type)+'".')
    id_argument = object_type+'_id'
    if id_argument not in kwargs:
        raise TypeError('Missing keyword argument: "'+id_argument+'".')
    
    object_id = kwargs[id_argument]
    if isinstance(object_id, str):
        object_id = int(object_id)
    dbobject_dict = object_type_dict[object_type]
    dbobject = dbobject_dict['dbobject']
    path_to_submission_id = dbobject_dict['path_to_submission_id']
    
    if isinstance(object_id, int):
        object_id_is_list_like = False
        # check if it is published
        if dbobject.objects.values_list('is_published',flat=True).get(pk=object_id):
            return True
    else:
        object_id_is_list_like = True
        object_id = set(object_id)
        published_ids = set(dbobject.objects.values_list('id',flat=True).filter(pk__in=object_id))
        
    if user.is_authenticated():
        if object_id_is_list_like:
            object_id_to_check = object_id.difference(published_ids)
            allowed_object_ids = set(dbobject.objects.filter(**{'pk__in':object_id_to_check,path_to_submission_id+'__user_id':user.id}).values_list('id',flat=True))
            return published_ids.union(allowed_object_ids)
        else:
            if dbobject.objects.filter(**{'pk':object_id,path_to_submission_id+'__user_id':user.id}).exists():
                return True
            else:
                redirect_field_name = None
           
    elif object_id_is_list_like:
        return published_ids
    else:    
        return False