from django.conf.urls import url,patterns,include
from . import views

urlpatterns = [
	url(r'download_csv/',views.get_csv_file, name ='index'),
    url(r'(interaction_types)', views.get_itype_help, name = 'index'),
    url(r'(customized)', views.customized_heatmap, name = 'index'),
	url(r'', views.get_contacts_plots, name='index')
]