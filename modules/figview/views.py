from django.shortcuts import render
from django.conf import settings
from django.core import serializers
from django.views.generic import View
from django.views.decorators.csrf import ensure_csrf_cookie

from modules.figview.models import Figview

from modules.view.views import trim_path_for_mdsrv, obtain_domain_url

import json, os

@ensure_csrf_cookie
def figviewer(request,figviewname):
    request.session.set_expiry(0)
    mdsrv_url=obtain_domain_url(request)
    modelsfile=list(Figview.objects.filter(title=figviewname).values_list('strucfile'))
    
    context={
        "struc_file":modelsfile[0][0],
        "mdsrv_url":mdsrv_url,
            }
    return render(request, 'figview/basicview.html', context)