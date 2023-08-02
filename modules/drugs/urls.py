from django.urls import re_path

from drugs import views

urlpatterns = [
    re_path(r'^drugbrowser',  views.drugbrowser, name='drugbrowser'),
    re_path(r'^drugstatistics',  views.drugstatistics, name='drugstatistics'),
    re_path(r'^drugmapping',  views.drugmapping, name='drugmapping'),
]