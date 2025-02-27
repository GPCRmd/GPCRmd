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
      description="Tools related with values stored into the GPCRmd database (e.g. dynamic ids, pdb ids, uniprot ids, state,...)",
   ),
   public=True,
)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
   re_path(r'^$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   # re_path(r'^', include(router.urls)),
   re_path(r'^search_all_pdbs/$', views.SearchAllPdbs.as_view()),
   re_path(r'^search_all_uniprots/$', views.SearchAllUniprots.as_view()),
   re_path(r'^search_dyn_class/(?P<classname>.*)$', views.SearchByClass.as_view()),
   re_path(r'^search_dyn_lig_type/$', views.SearchByLigType.as_view()),
   re_path(r'^search_dyn_pdbs/(?P<pdbid>.*)$', views.SearchByPdbs.as_view()),
   re_path(r'^search_dyn_uniprots/(?P<uniprotid>.*)$', views.SearchByUniprots.as_view()),
   re_path(r'^search_dyn/(?P<dyn_id>.*)$', views.SearchByDyn.as_view()),
   re_path(r'^search_sub/(?P<sub_id>.*)$', views.SearchBySub.as_view()),
   re_path(r'^search_comp/(?P<ligroleids>.*)$', views.SearchCompound.as_view()),
   path('download_id/', views.download_id, name="download_id"),
   path('download_link/<str:task_id>/', views.download_link, name='download_link'),
   # re_path(r'^get_progress/', views.get_progress, name="get_progress"), 

]

urlpatterns = format_suffix_patterns(urlpatterns)