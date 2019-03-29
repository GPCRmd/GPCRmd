from django.conf.urls import url,patterns,include
from . import views

urlpatterns = [
	url(r'ngl_clus/(?P<cluster>\w+)&(?P<dynid>\w+)',views.get_nglviewer),
	url(r'download_csv/(?P<itype>\w+)&(?P<ligandonly>\w+)&(?P<rev>\w+)',views.get_csv_file, name ='index'),
    url(r'(?P<itype>\w+)&(?P<cluster>\w+)&(?P<ligandonly>\w+)&(?P<rev>\w+)' , views.get_contacts_plots, name='index'),
    url(r'(interaction_types)', views.get_itype_help, name = 'index'),
	url(r'', views.get_contacts_plots, name='index')
]