from django.urls import include, re_path
from django.conf import settings
from . import views

app_name = "covid19"

urlpatterns = [
    re_path(r'^search/$', views.index, name='index'),
    re_path(r'^project/$', views.project, name='project'),
    re_path(r'^$', views.home, name='home'),
    re_path(r'^home/$', views.home, name='home'),
#    re_path(r'^plottest/$', views.plottest, name='plottest'),
  #  re_path(r'^hometest/$', views.hometest, name='hometest'),
  #  re_path(r'^hometest2/$', views.hometest2, name='hometest2'),
    re_path(r'^prot/(?P<prot_name>\w+)/$', views.index, name='index'),
    re_path(r'^prot/(?P<prot_name>\w+)/(?P<genome_id>EPI_ISL_\d+)/$', views.index, name='index'),
    re_path(r'^allprot/(?P<genome_id>EPI_ISL_\d+)/$', views.index_allprot, name='index_allprot'),
    re_path(r'^(?P<dyn_id>[0-9]+)/$', views.dynanalysis, name='dynanalysis'),
    re_path(r'^(?P<dyn_id>[0-9]+)/(?P<sel_genome_id>EPI_ISL_\d+)/$', views.dynanalysis, name='dynanalysis'),
    re_path(r'^example/$', views.dynanalysis,{"variantimpact_def":True, "dyn_id":"28"}, name='dynanalysis'),
    #re_path(r'^report/(?P<dyn_id>[0-9]+)/$', views.report, name='report'),
    re_path(r'^upload/$', views.upload, name='upload'),
    re_path(r'^upload/success/(?P<dyn_id>[0-9]+)$', views.upload_success, name='upload_success'),
    re_path(r'^ajax_notshow_warn/$', views.ajax_notshow_warn, name='ajax_notshow_warn'),
    re_path(r'^ajax_rmsd/$', views.ajax_rmsd, name='ajax_rmsd'),
    re_path(r'^ajax_rmsf/$', views.ajax_rmsf, name='ajax_rmsf'),
    re_path(r'^ajax_variant_impact/$', views.ajax_variant_impact, name='ajax_variant_impact'),
    re_path(r'^ajax_muts_in_isolate/$', views.ajax_muts_in_isolate, name='ajax_muts_in_isolate'),
    re_path(r'^ajax_autocomp_isolates/$', views.ajax_autocomp_isolates, name='ajax_autocomp_isolates'),
    re_path(r'^dwl/(?P<dyn_id>[0-9]+)/(?P<obj_type>[a-z]+)/(?P<obj_id>[0-9]+)/$', views.download_data, name="download_data"),
    re_path(r'^dwl/fasta/(?P<genome_id>EPI_ISL_\d+)/(?P<prot_name>\w+)/$', views.download_fasta, name="download_fasta"),
    re_path(r'^quickloadall/$', views.quickloadall, name="quickloadall"),
    re_path(r'^dwl/variantimpact/(?P<dyn_id>[0-9]+)/(?P<traj_id>[0-9]+)/(?P<position>[0-9]+)/(?P<analysis>\w+)/$', views.download_varimpact, name='download_varimpact'),
    re_path(r'^dwl/variantscores_traj/(?P<dyn_id>[0-9]+)/(?P<traj_id>[0-9]+)/(?P<protein>\w+)/(?P<position>[0-9]+)/(?P<variant>\w[0-9]+\w)/(?P<parameters_me>[\w_,]+)/(?P<parameters_td>[\w_,]+)/$', views.download_varscores_traj, name='download_varscores_traj'),
    re_path(r'^dwl/variantscores_all/(?P<dyn_id>[0-9]+)/$', views.download_variantscores_all, name='download_variantscores_all'),
    re_path(r'^dwl/cdescr_template/(?P<dyn_id>[0-9]+)/$', views.download_custom_descriptors_template, name="download_custom_descriptors_template"),
    re_path(r'^upload_descriptors/(?P<dyn_id>[0-9]+)/$', views.upload_descriptors, name="upload_descriptors"),
#    re_path(r'^(?P<dyn_id>[0-9]+)/$', views.index, name='index'),
]

