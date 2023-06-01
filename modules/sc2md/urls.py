from django.urls import include, re_path
from django.conf import settings
from . import views

app_name = "sc2md"


urlpatterns = [
    re_path(r'^$', views.home, name='home'),
    re_path(r'^search/$', views.index, name='index'),
    re_path(r'^search/prot/(?P<prot_name>\w+)/$', views.index, name='index'),
    re_path(r'^(?P<dyn_id>[0-9]+)/$', views.dynanalysis, name='dynanalysis'),
    re_path(r'^report/(?P<dyn_id>[0-9]+)/$', views.report, name='report'),
    #re_path(r'^prot/(?P<prot_name>\w+)/(?P<genome_id>EPI_ISL_\d+)/$', views.index, name='index'),
    #re_path(r'^allprot/(?P<genome_id>EPI_ISL_\d+)/$', views.index_allprot, name='index_allprot'),
    #re_path(r'^(?P<dyn_id>[0-9]+)/(?P<sel_genome_id>EPI_ISL_\d+)/$', views.dynanalysis, name='dynanalysis'),
    re_path(r'^upload/$', views.upload, name='upload'),
    re_path(r'^upload/success/(?P<dyn_id>[0-9]+)$', views.upload_success, name='upload_success'),
    re_path(r'^about/contact/$', views.contact, name='contact'),

    re_path(r'^ajax_notshow_warn/$', views.ajax_notshow_warn, name='ajax_notshow_warn'),
    re_path(r'^ajax_rmsd/$', views.ajax_rmsd, name='ajax_rmsd'),
    re_path(r'^ajax_rmsf/$', views.ajax_rmsf, name='ajax_rmsf'),
    #re_path(r'^ajax_variant_impact/$', views.ajax_variant_impact, name='ajax_variant_impact'),
    re_path(r'^dwl/(?P<dyn_id>[0-9]+)/(?P<obj_type>[a-z]+)/(?P<obj_id>[0-9]+)/$', views.download_data, name="download_data"),
    re_path(r'^dwl/fasta/(?P<genome_id>EPI_ISL_\d+)/(?P<prot_name>\w+)/$', views.download_fasta, name="download_fasta"),
    #re_path(r'^dwl/variantimpact/(?P<dyn_id>[0-9]+)/(?P<traj_id>[0-9]+)/(?P<position>[0-9]+)/(?P<analysis>\w+)/$', views.download_varimpact, name='download_varimpact'),

]


