from django.urls import include, re_path
from django.conf import settings
from . import views

app_name = "view"

urlpatterns = [
    re_path(r'^(?P<dyn_id>[0-9]+)/$', views.index, name='index'),
    re_path(r'^subid/(?P<sub_id>[0-9]+)/$', views.sub_id_redirect, name='sub_id_redirect'),
    re_path(r'^network/$', views.index,{"network_def":True, "dyn_id":"90"}, name='index'),
    re_path(r'^watermap/$', views.index,{"watervol_def":True, "dyn_id":"90"}, name='index'),
    re_path(r'^pharmacophores/$', views.index,{"pharmacophore_def":True, "dyn_id":"90"}, name='index'),
    re_path(r'^tunnelsandchannels/$', views.index,{"tunnels_channels_def":True, "dyn_id":7}, name='index'),
    re_path(r'^ligprotcontacts/$', views.index,{"ligprotint_def":True, "dyn_id":"90"}, name='index'),
    re_path(r'^nongpcr/(?P<dyn_id>[0-9]+)/$', views.nongpcr, name='nongpcr'),
    re_path(r'^(?P<dyn_id>[0-9]+)/(?P<sel_pos>\d+x\d+_\d+x\d+$)/$', views.index, name='index'),#For contact plots
    re_path(r'^(?P<dyn_id>[0-9]+)/(Ligand_)?(?P<sel_pos>\d+x\d+)(_Ligand)?', views.index, name='index'),#For contact plots when ligand
    re_path(r'^(?P<dyn_id>[0-9]+)/(?P<selthresh>\d\.\d)/(?P<sel_pos>\d+x\d+)/$', views.index, name='index'),
  #  re_path(r'^distances/(?P<dist_str>[0-9]+-[0-9]+(a[0-9]+-[0-9]+)*)/(?P<struc_id>[0-9]+)/(?P<traj_id>[0-9]+)$', views.distances, name='distances'),
  #  re_path(r'^rmsd/$', views.rmsd, name='rmsd'),
    re_path(r'^dwl/(?P<dyn_id>[0-9]+)/(?P<dist_id>dist_[0-9]+)/$', views.download_dist, name="download_dist"),
    re_path(r'^dwl/(?P<dyn_id>[0-9]+)/(?P<rmsd_id>rmsd_[0-9]+)/$', views.download_rmsd, name="download_rmsd"),
    re_path(r'^dwl/(?P<dyn_id>[0-9]+)/(?P<int_id>int_[0-9]+)/$', views.download_int, name="download_int"),
    re_path(r'^dwl/freq/(?P<dyn_id>[0-9]+)/(?P<bond_type>[a-z]+)/(?P<traj_path>.+\.(xtc|dcd))$', views.download_hb_sb, name="download_hb_sb"),
    re_path(r'^docs/$', views.viewer_docs, name='viewer_docs'),
    re_path(r'^hbonds/$', views.hbonds, name='hbonds'),
    re_path(r'^saltbridges/$', views.saltbridges, name='saltbridges'),
    re_path(r'^grid/$', views.sasa, name='sasa'),
#    re_path(r'^fplot/(?P<dyn_id>[0-9]+)/(?P<filename>\w+\.json)/(?P<seg_li>(|\d+(:[A-Z])?|\d+(:[A-Z])?\-\d+(:[A-Z])?),((|\d+(:[A-Z])?|\d+(:[A-Z])?\-\d+(:[A-Z])?),){13}(|\d+(:[A-Z])?|\d+(:[A-Z])?\-\d+(:[A-Z])?))/$', views.fplot_gpcr, name='fplot_gpcr'),
    re_path(r'^fplot2/(?P<dyn_id>[0-9]+)/(?P<filename>\w+\.json)/(?P<seg_li>(|\d+(:[A-Z])?|\d+(:[A-Z])?\-\d+(:[A-Z])?),((|\d+(:[A-Z])?|\d+(:[A-Z])?\-\d+(:[A-Z])?),){13}(|\d+(:[A-Z])?|\d+(:[A-Z])?\-\d+(:[A-Z])?))/$', views.fplot_gpcr_slide, name='fplot_gpcr_slide'),
    re_path(r'^fplot_test/(?P<dyn_id>[0-9]+)/(?P<filename>\w+\.json)/$', views.fplot_test, name='fplot_test'),
    re_path(r'^ref/(?P<dyn_id>[0-9]+)/$', views.view_reference, name='reference'),
    re_path(r'^session/(?P<session_name>\w*)/$', views.view_session, name='view_session'),
    re_path(r'^quickload/(?P<dyn_id>[0-9]+)/(?P<trajfile_id>[0-9]+)/$', views.quickload, name="quickload"),
    re_path(r'^quickloadall/$', views.quickloadall, name="quickloadall"),
    re_path(r'^min/(?P<dyn_id>[0-9]+)/$', views.basicview, name="basicview"),
    re_path(r'^update_bokeh/$', views.update_bokeh, name="update_bokeh"),
    re_path(r'^ac_update/(?P<dyn_id>[0-9]+)/$', views.ac_load_data, name="ac_load_data"),
    re_path(r'^get_pocket_plot_and_files/$', views.get_pocket_plot_and_files, name="get_pocket_plot_and_files"),
    re_path(r'^get_pocket_and_dyn_data/$', views.get_pocket_and_dyn_data, name="get_pocket_and_dyn_data"),
]



