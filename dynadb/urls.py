# -*- coding: utf-8 -*-
from django.conf.urls import url,patterns,include #antes: from django.conf.urls import url,patterns
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView
from django.contrib import admin
from django.conf import settings
from . import views

app_name= 'dynadb'
urlpatterns = [
    url(r'^prueba_varios/$', TemplateView.as_view(template_name='dynadb/pruebamult_template.html'), name="prueba_varios"),
    url(r'^profile_setting/$', views.profile_setting, name='profile_setting'),
    url(r'^sub_sim/$', views.sub_sim, name='sub_sim'),
    url(r'^name/$', views.get_name, name='name'),
    url(r'^dyndbfiles/$', views.get_DyndbFiles, name='dyndbfiles'),
    url(r'^db_inputform/(?P<submission_id>[0-9]+)?/?$', views.db_inputformMAIN, name='db_inputform'),
    url(r'^db_author_information/$', views.get_Author_Information, name='db_author_information'),
    url(r'^db_dynamics/$', views.get_Dynamics, name='db_dynamics'),
    url(r'^db_files/$', views.get_FilesCOMPLETE, name='db_files'),
    url(r'^db_protein/$', views.get_ProteinForm, name='db_protein'),
    url(r'^db_molecule/$', views.get_Molecule, name='db_molecule'),
    url(r'^db_component/$', views.get_Component, name='db_component'),
    url(r'^db_model/$', views.get_Model, name='db_model'),
    url(r'^db_compoundform/$', views.get_CompoundForm, name='db_compoundform'),
    url(r'^your_name/$', views.get_name, name='your_name'),
    url(r'^thanks/$', views.get_name, name='thanks'),
    url(r'^admin/', admin.site.urls),
    url(r'^protein/(?P<submission_id>[0-9]+)/$', views.PROTEINview, name='protein'),
    url(r'^protein/get_data_upkb/?([A-Z0-9-]+)?$', views.protein_get_data_upkb, name='protein_get_data_upkb'),
    url(r'^protein/download_specieslist/$', views.download_specieslist, name='protein_download_specieslist'),
    url(r'^protein/get_specieslist/$', views.get_specieslist, name='protein_get_specieslist'),
    url(r'^protein/get_mutations/$', views.get_mutations_view, name='protein_get_mutations'),
    url(r'^protein/alignment/$', views.show_alig, name='show_alig'),
    url(r'^protein/showalignment/(?P<alignment_key>[0-9]+)$', views.popup_alig, name='popup_alig'),
    url(r'^protein/id/(?P<protein_id>[0-9]+)/$',views.query_protein, name='query_protein'),
    url(r'^protein/id/(?P<protein_id>[0-9]+)/fasta$',views.query_protein_fasta, name='query_protein_fasta'),
    url(r'^molecule/id/(?P<molecule_id>[0-9]+)/$',views.query_molecule, name='query_molecule'),
    url(r'^molecule/id/(?P<molecule_id>[0-9]+)/sdf$',views.query_molecule_sdf,name='query_molecule_sdf'),
    url(r'^compound/id/(?P<compound_id>[0-9]+)/$',views.query_compound, name='query_compound'),
    url(r'^model/id/(?P<model_id>[0-9]+)/$',views.query_model, name='query_model'),
    url(r'^dynamics/id/(?P<dynamics_id>[0-9]+)/$',views.query_dynamics, name='query_dynamics'),
    url(r'^references/$', views.REFERENCEview, name='references'),
    url(r'^REFERENCEfilled/(?P<submission_id>[0-9]+)/$', views.REFERENCEview, name='REFERENCEfilled'),
    url(r'^PROTEINfilled/(?P<submission_id>[0-9]+)/$', views.PROTEINview, name='PROTEINfilled'),
    url(r'^molecule/(?P<submission_id>[0-9]+)/$', views.SMALL_MOLECULEview, name='molecule'),
    url(r'^MOLECULEfilled/(?P<submission_id>[0-9]+)/$', views.SMALL_MOLECULEview, name='MOLECULEfilled'),
    url(r'^MOLECULEfilled2/$', views.SMALL_MOLECULEview2, name='MOLECULEfilled2'),
    url(r'^model/(?P<submission_id>[0-9]+)/$', views.MODELview, name='model'),
    url(r'^MODELfilled/(?P<submission_id>[0-9]+)/$', views.MODELview, name='MODELfilled'),
    #url(r'^ajax_pdbchecker/(?P<combination_id>[a-zA-Z0-9_]+)$', views.pdbcheck, name='pdbcheck'),
    url(r'^ajax_pdbchecker/(?P<combination_id>[a-zA-Z0-9_]+)$', views.pdbcheck, name='pdbcheck'),
    url(r'^upload_pdb/$', views.upload_pdb, name='upload_pdb'),
    url(r'^search/$', include('haystack.urls')),
    url(r'^tmp/(?P<pdbname>[a-zA-Z0-9_/]+_corrected.pdb)$', views.servecorrectedpdb,name='servecorrectedpdb'),
    url(r'^search_top/$',views.search_top,name='search_top'),
    url(r'^dynamics/(?P<submission_id>[0-9]+)/$', views.DYNAMICSview, name='dynamics'),
    url(r'^DYNAMICSfilled/(?P<submission_id>[0-9]+)/$', views.DYNAMICSview, name='DYNAMICSfilled'),
    url(r'^form/$', views.get_formup, name='form'),
    #url(r'^files/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT,}), #this line shouldnt be here
    url(r'^submitted/(?P<submission_id>[0-9]+)/$', views.SUBMITTEDview, name='submitted')]

#    url(r'^some_temp/$', views.some_view, name='some_temp')
#    url(r'^prueba_varios/$', views.profile_setting, name='PRUEBA_varios'),

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^files/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT,
        }),
)

