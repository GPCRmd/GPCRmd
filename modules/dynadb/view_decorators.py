from django.conf import settings
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect


from modules.dynadb.models import DyndbSubmission


from functools import wraps

# decorator generators

def response_by_test(view_func,test_func,view_func_on_pass=None,view_func_on_fail=None):
    """
    Function that creates a decorator function which, depending on the result obtained from the provided test function
    (True, False or None), executes one of the provided views instead of the decorated one.
    A django.http.Http404 is raised if test_func returns None.
    
    test_func:          function to be tested with the same args and kwargs that the decorated view.
    view_func_on_pass:  function to execute if test_func returns True. None means that the decorated function should be
                        executed.
    view_func_on_fail   function to execute if test_func returns False. None means that the decorated function should be
                        executed.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            test_result = test_func(request,*args, **kwargs)
            if test_result is None:
                raise Http404
            elif test_result and view_func_on_pass is None \
            or not test_result and view_func_on_fail is None:
                return view_func(request, *args, **kwargs)
            elif test_result:
                return view_func_on_pass(request, *args, **kwargs)
            else:
                return view_func_on_fail(request, *args, **kwargs)
        return _wrapped_view
    return decorator
    
# decorators    

def test_if_closed(view_func):
    '''Decorator that checks if the corresponding submission is closed and redirects to submission closed error page
    on a positive result.'''
    decorator = response_by_test(view_func,submission_is_closed,view_func_on_pass=submission_closed_error)
    return decorator(view_func)

    
# test functions

def submission_is_closed(request,submission_id,*args,**kwargs):
    ''' Test function for decorators that returns if a submission is closed.'''
    try:
        submission = DyndbSubmission.objects.get(pk=submission_id)
    except ObjectDoesNotExist:
        return None
    return submission.is_closed



# auxiliary views  

def submission_closed_error(request,*args,**kwargs):
    '''View that renders submission closed error.'''
    return render(request,template_name="errors/closed_403.html",status=403)