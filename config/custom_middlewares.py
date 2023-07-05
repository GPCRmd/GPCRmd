import traceback

from django.shortcuts import reverse, redirect
from django.conf import settings

# class MultipleProxyMiddleware(object):
#     FORWARDED_FOR_FIELDS = [
#         'HTTP_X_FORWARDED_FOR',
#         'HTTP_X_FORWARDED_HOST',
#         'HTTP_X_FORWARDED_SERVER',
#     ]

#     def process_request(self, request):
#         """
#         Rewrites the proxy headers so that only the most
#         recent proxy is used.
#         """
#         for field in self.FORWARDED_FOR_FIELDS:
#             if field in request.META:
#                 if ',' in request.META[field]:
#                     parts = request.META[field].split(',')
#                     request.META[field] = parts[-1].strip()


# class WsgiLogErrors(object):
#     def process_exception(self, request, exception):
#         tb_text = traceback.format_exc()
#         url = request.build_absolute_uri()
#         request.META['wsgi.errors'].write(url + '\n' + str(tb_text) + '\n')

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.META.get('PATH_INFO', "")
        query = request.META.get('QUERY_STRING', "")

        if settings.MAINTENANCE_BYPASS_QUERY in query:
            request.session['bypass_maintenance']=True

        if not request.session.get('bypass_maintenance', False):
            if settings.MAINTENANCE_MODE and path!= reverse("maintenance"):
                response = redirect(reverse("maintenance"))
                return response

        response = self.get_response(request)

        return response