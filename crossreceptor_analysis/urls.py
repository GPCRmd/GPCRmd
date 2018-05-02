from django.conf.urls import url,patterns,include
from django.conf import settings
from . import views

app_name = "gpcrome"

urlpatterns = [
    url(r'ligres/(?P<sel_thresh>\d\.\d)/$', views.ligand_receptor_interaction, name='ligand_receptor_interaction'),
]

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^files/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT,
        }),
)
