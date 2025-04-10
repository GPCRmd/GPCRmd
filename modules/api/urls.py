"""
Quickstart: https://drf-yasg.readthedocs.io/en/stable/readme.html#quickstart
"""

from django.contrib import admin
from django.urls import include, re_path, path

from rest_framework.urlpatterns import format_suffix_patterns

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from . import views

# Schema
schema_view = get_schema_view(
   openapi.Info(
      title="GPCRmd API",
      default_version='v1.3',
      description="This is the GPCRmd REST API. " +
      "This API grants programmatic access to the GPCRmd database. It may retrieve files and metadata. " +
      "Below, API endpoints are listed and documented. Click on any endpoint to drop more information such as the description and accepted parameters. " +
      "Use the 'try it out' button to test any endpoint at the moment. " +
      "For the large-scale downloader is necessary to access via log-in account. This measure is to avoid unwanted massive requests from unrecognized devices.",
   ),
   public=True,
)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
   re_path(r'^$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   # re_path(r'^', include(router.urls)),
   re_path(r'^search_all/pdbs/$', views.SearchAllPdbs.as_view()),
   re_path(r'^search_all/uniprots/$', views.SearchAllUniprots.as_view()),
   re_path(r'^search_dyn/info/(?P<dyn_id>.*)$', views.SearchByDyn.as_view()),
   re_path(r'^search_dyn/class/(?P<classname>.*)$', views.SearchByClass.as_view()),
   re_path(r'^search_dyn/lig_type/$', views.SearchByLigType.as_view()),
   re_path(r'^search_dyn/pdbs/(?P<pdbid>.*)$', views.SearchByPdbs.as_view()),
   re_path(r'^search_dyn/uniprots/(?P<uniprotid>.*)$', views.SearchByUniprots.as_view()),
   re_path(r'^search_sub/(?P<sub_id>.*)$', views.SearchBySub.as_view()),
   re_path(r'^search_comp/(?P<ligroleids>.*)$', views.SearchCompound.as_view()),
   path('download_id/', views.download_id, name="download_id"),
   path('download_link/<str:task_id>/', views.download_link, name='download_link'),
   # re_path(r'^get_progress/', views.get_progress, name="get_progress"), 

]

urlpatterns = format_suffix_patterns(urlpatterns)