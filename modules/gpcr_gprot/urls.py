from django.urls import re_path, include
from . import views

urlpatterns = [
	re_path(r'download_csv/',views.get_csv_file, name ='index'),
    re_path(r'(customized)/$', views.customized_heatmap, name = 'index'),
	re_path(r'', views.main, name='index')
]