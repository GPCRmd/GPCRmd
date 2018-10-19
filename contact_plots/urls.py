from django.conf.urls import url,patterns,include
from . import views

urlpatterns = [
	url(r'(download_csv)',views.get_csv_file, name ='index'),
    url(r'(?P<itypes>\w+)/(?P<ligandonly>\w+)' , views.get_contacts_plots, name='index'),
]
