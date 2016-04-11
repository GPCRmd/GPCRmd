from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from protwis import settings
from . import views

app_name = 'juanmaapp'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<question_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^(?P<question_id>[0-9]+)/results/$', views.results, name='results'),
    url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
    url(r'^uploadform/$', views.upload, name='uploadform'),

#    url(r'^uploadform/prueba/$', views.form_dyndbmodel,name='pruebaform'),
#    url(r'^thanks/$', views.DyndbModelFormView.form_valid,name='formview')
#    url(r'^uploadform/(?P<pk>[0-9]+)/$', views.upload_detail,name='uploadform_details')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
