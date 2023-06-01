from django.urls import include, re_path
from django.conf import settings
from . import views

urlpatterns = [
    re_path(r'cor_login',views.login_in, name ='cor_login'),
	re_path(r'main',views.main, name ='index'),
	re_path(r'custom_plot',views.custom_plot, name ='custom_plot'),
	re_path(r'topcor_plot',views.topcor_plot, name ='topcor_plot'),
	re_path(r'infoplot/(?P<out>[a-zA-Z0-9_]*)/(?P<path>[a-zA-Z0-9_]*)$',views.infoplot, name ='infoplot'),
]