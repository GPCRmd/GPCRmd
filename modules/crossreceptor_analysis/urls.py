from django.urls import include, re_path
from django.conf import settings
from . import views

app_name = "gpcrome"

urlpatterns = [
    re_path(r'ligres/(?P<sel_thresh>\d\.\d)/$', views.ligand_receptor_interaction, name='ligand_receptor_interaction'),
#    re_path(r'molpx/(?P<dyn_id>[0-9]+)/$', views.molpx_plots, name='molpx_plots'),

]

""" if settings.DEBUG:
    urlpatterns += patterns('',
        re_path(r'^files/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
        re_path(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT,
        }),
)
 """