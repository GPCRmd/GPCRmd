# -*- coding: utf-8 -*-

from django.conf.urls import url,patterns,include #antes: from django.conf.urls import url,patterns
from django.views.generic import TemplateView
from django.contrib import admin
from django.conf import settings

from . import views

from haystack.query import SearchQuerySet
from haystack.views import SearchView
from .forms import MainSearchForm

sqs = SearchQuerySet().all()

app_name= 'dynadb'
urlpatterns = [
    url(r'^reset/$', views.reset_permissions, name="reset_permissions"),
    #url(r'^prueba_varios/$', TemplateView.as_view(template_name='dynadb/pruebamult_template.html'), name="prueba_varios"),
    #url(r'^profile_setting/$', views.profile_setting, name='profile_setting'),
    #url(r'^sub_sim/$', views.sub_sim, name='sub_sim'),
    #url(r'^name/$', views.get_name, name='name'),
#    url(r'^dyndbfiles/$', views.get_DyndbFiles, name='dyndbfiles'),
    url(r'^db_inputform/(?P<submission_id>[0-9]+)?/?$', views.db_inputformMAIN, name='db_inputform'),
    url(r'^before_db_inputform_prev_moddb_inputform/(?P<submission_id>[0-9]+)?/?$', views.db_inputformMAIN, name='before_db_inputform_prev_mod'),
#    url(r'^db_author_information/$', views.get_Author_Information, name='db_author_information'),
#    url(r'^db_dynamics/$', views.get_Dynamics, name='db_dynamics'),
#    url(r'^db_files/$', views.get_FilesCOMPLETE, name='db_files'),
#    url(r'^db_protein/$', views.get_ProteinForm, name='db_protein'),
#    url(r'^db_molecule/$', views.get_Molecule, name='db_molecule'),
#    url(r'^db_molecule/$', views.get_Molecule, name='db_molecule'),
#    url(r'^db_component/$', views.get_Component, name='db_component'),
#    url(r'^db_model/$', views.get_Model, name='db_model'),
#    url(r'^db_compoundform/$', views.get_CompoundForm, name='db_compoundform'),
#    url(r'^your_name/$', views.get_name, name='your_name'),
#    url(r'^thanks/$', views.get_name, name='thanks'),
#    url(r'^admin/', admin.site.urls),
    url(r'^protein/(?P<submission_id>[0-9]+)/$', views.PROTEINview, name='protein'),
    url(r'^protein/(?P<submission_id>[0-9]+)/delete/$', views.delete_protein, name='delete_protein'),
    url(r'^protein/get_data_upkb/?([A-Z0-9-]+)?$', views.protein_get_data_upkb, name='protein_get_data_upkb'),
    url(r'^protein/download_specieslist/$', views.download_specieslist, name='protein_download_specieslist'),
    url(r'^protein/get_specieslist/$', views.get_specieslist, name='protein_get_specieslist'),
    url(r'^protein/get_mutations/$', views.get_mutations_view, name='protein_get_mutations'),
    url(r'^protein/(?P<alignment_key>[0-9]+)/alignment/$', views.show_alig, name='show_alig'),
    url(r'^protein/id/(?P<protein_id>[0-9]+)/$',views.query_protein, name='query_protein'),
    url(r'^protein/id/(?P<protein_id>[0-9]+)/fasta$',views.query_protein_fasta, name='query_protein_fasta'),
    url(r'^molecule/id/(?P<molecule_id>[0-9]+)/$',views.query_molecule, name='query_molecule'),
    url(r'^molecule/id/(?P<molecule_id>[0-9]+)/sdf$',views.query_molecule_sdf,name='query_molecule_sdf'),
    url(r'^compound/id/(?P<compound_id>[0-9]+)/$',views.query_compound, name='query_compound'),
    url(r'^model/id/(?P<model_id>[0-9]+)/$',views.query_model, name='query_model'),
    url(r'^dynamics/id/(?P<dynamics_id>[0-9]+)/$',views.query_dynamics, name='query_dynamics'),
    url(r'^complex/id/(?P<complex_id>[0-9]+)/$',views.query_complex, name='query_complex'),
    url(r'^references/$', views.REFERENCEview, name='references'),
    url(r'^REFERENCEfilled/(?P<submission_id>[0-9]+)/$', views.REFERENCEview, name='REFERENCEfilled'),
    url(r'^PROTEINfilled/(?P<submission_id>[0-9]+)/$', views.PROTEINview, name='PROTEINfilled'),
    url(r'^submission_summary/(?P<submission_id>[0-9]+)/$', views.submission_summaryiew, name='submission_summary'),
    url(r'^protein_summary/(?P<submission_id>[0-9]+)/$', views.protein_summaryiew, name='protein_summary'),
    url(r'^molecule_summary/(?P<submission_id>[0-9]+)/$', views.molecule_summaryiew, name='molecule_summary'),
    url(r'^model_summary/(?P<submission_id>[0-9]+)/$', views.model_summaryiew, name='model_summary'),
    url(r'^molecule/(?P<submission_id>[0-9]+)/$', views.SMALL_MOLECULEview, name='molecule'),
    url(r'^molecule/(?P<submission_id>[0-9]+)/delete/$', views.delete_molecule, name='delete_molecule'),
    url(r'^moleculereuse/(?P<submission_id>[0-9]+)/(?P<model_id>[0-9]+)/$', views.SMALL_MOLECULEreuseview, name='moleculereuse'),
    url(r'^moleculereuse/(?P<submission_id>[0-9]+)/(?:[0-9]+/)?generate_properties/$', views.generate_molecule_properties, name='generate_molecule_properties_reuse'),
    url(r'^moleculereuse/(?P<submission_id>[0-9]+)/(?:[0-9]+/)?delete/$', views.delete_molecule, name='delete_molecule_reuse'),
    url(r'^moleculereuse/(?P<submission_id>[0-9]+)/(?:[0-9]+/)?get_compound_info_pubchem/$', views.get_compound_info_pubchem, name='get_compound_info_pubchem_reuse'),
    url(r'^moleculereuse/(?P<submission_id>[0-9]+)/(?:[0-9]+/)?get_compound_info_chembl/$', views.get_compound_info_chembl, name='get_compound_info_chembl_reuse'),
    url(r'^moleculereuse/(?P<submission_id>[0-9]+)/(?:[0-9]+/)?submitpost/$', views.submitpost_view, name='submitpost_reuse'),
    #url(r'^moleculereuse/open_pubchem/$', views.open_pubchem, name='molecule_open_pubchem_reuse'),
    #url(r'^moleculereuse/open_chembl/$', views.open_chembl, name='molecule_open_chembl_reuse'),
    url(r'^moleculereuse/(?:[0-9]+/)open_pubchem/$', views.open_pubchem, name='molecule_open_pubchem_reuse'),
    url(r'^moleculereuse/(?:[0-9]+/)open_chembl/$', views.open_chembl, name='molecule_open_chembl_reuse'),
    url(r'^molecule/(?P<submission_id>[0-9]+)/submitpost/$', views.submitpost_view, name='submitpost'),
    url(r'^molecule/(?P<submission_id>[0-9]+)/generate_properties/$', views.generate_molecule_properties, name='generate_molecule_properties'),
    url(r'^molecule/(?P<submission_id>[0-9]+)/get_compound_info_pubchem/$', views.get_compound_info_pubchem, name='get_compound_info_pubchem'),
    url(r'^molecule/(?P<submission_id>[0-9]+)/get_compound_info_chembl/$', views.get_compound_info_chembl, name='get_compound_info_chembl'),
    url(r'^molecule/open_pubchem/$', views.open_pubchem, name='molecule_open_pubchem'),
    url(r'^molecule/open_chembl/$', views.open_chembl, name='molecule_open_chembl'),
    url(r'^molecule2/(?P<submission_id>[0-9]+)/$', views.SMALL_MOLECULEview2, name='molecule2'),
    url(r'^MOLECULEfilled/(?P<submission_id>[0-9]+)/$', views.SMALL_MOLECULEview, name='MOLECULEfilled'),
    url(r'^MOLECULEfilled2/$', views.SMALL_MOLECULEview2, name='MOLECULEfilled2'),
    url(r'^model/(?P<submission_id>[0-9]+)/$', views.MODELview, name='model'),
    url(r'^(?P<form_type>model|dynamics)/(?P<submission_id>[0-9]+)/check_pdb_molecules/$', views.pdbcheck_molecule, name='pdbcheck_molecule'),
    url(r'^(?P<form_type>dynamics)reuse/(?P<submission_id>[0-9]+)/(?:[0-9]+/)?check_pdb_molecules/$', views.pdbcheck_molecule, name='pdbcheck_molecule'), #######
    url(r'^(?P<form_type>model|dynamics)/(?P<submission_id>[0-9]+)/get_submission_molecule_info/$', views.get_submission_molecule_info, name='get_submission_molecule_info'),
    url(r'^model/(?P<submission_id>[0-9]+)/ajax_pdbchecker/$', views.pdbcheck, name='pdbcheck'),
    url(r'^model/(?P<submission_id>[0-9]+)/search_top/$',views.search_top,name='search_top'), #keep this one in a merge
    url(r'^model/(?P<submission_id>[0-9]+)/upload_model_pdb/$', views.upload_model_pdb, name='upload_model_pdb'),
    url(r'^modelreuse/(?P<submission_id>-?[0-9]+)/(?:[0-9]+/)?$', views.MODELreuseview, name='modelreuse'),
    url(r'^proteinreuse/(?P<submission_id>[0-9]+)/(?:[0-9]+/)?$', views.PROTEINreuseview, name='proteinreuse'),
#    url(r'^moleculereuse/(?P<submission_id>[0-9]+)/(?P<model_id>[0-9]+)/$', views.SMALL_MOLECULEreuseview, name='moleculereuse'),
#    url(r'^modelrow/$', views.MODELrowview, name='modelrow'),
    url(r'^modelreuserequest/(?P<model_id>[0-9]+)/$', views.MODELreuseREQUESTview, name='modelreuserequest'),
    url(r'^MODELfilled/(?P<submission_id>[0-9]+)/$', views.MODELview, name='MODELfilled'),
    #url(r'^ajax_pdbchecker/(?P<submission_id>[0-9]+)/$', views.pdbcheck, name='pdbcheck'), 
    url(r'^search/$', SearchView(template='/protwis/sites/protwis/dynadb/templates/search/search.html', searchqueryset=sqs, form_class=MainSearchForm),name='haystack_search'),
    url(r'^ajaxsearch/',views.ajaxsearcher,name='ajaxsearcher'),
    url(r'^empty_search/',views.emptysearcher,name='emptysearcher'),
    url(r'^autocomplete/',views.autocomplete,name='autocomplete'),
    url(r'^advanced_search/$', views.NiceSearcher,name='NiceSearcher'),
    #url(r'^search_top/(?P<submission_id>[0-9]+)/$',views.search_top,name='search_top'),
    url(r'^dynamics/(?P<submission_id>[0-9]+)/$', views.DYNAMICSview, name='dynamics'),
    url(r'^dynamics/(?P<submission_id>[0-9]+)/(?:[0-9]+/)?upload_files/((?P<trajectory>traj)/)?$', views.upload_dynamics_files, name='dynamics_upload_files'),
    url(r'^dynamicsreuse/(?P<submission_id>[0-9]+)/(?:[0-9]+/)?upload_files/((?P<trajectory>traj)/)?$', views.upload_dynamics_files, name='dynamics_upload_files'),
    url(r'^dynamics/(?P<submission_id>[0-9]+)/check_trajectories/$', views.check_trajectories, name='dynamics_check_trajectories'),
    url(r'^dynamics/do_analysis/$', views.do_analysis, name='do_analysis'),
#    url(r'^dynamicsreuse/(?P<submission_id>[0-9]+)/(?P<model_id>[0-9]+)/$', views.DYNAMICSreuseview, name='dynamicsreuse'),
    url(r'^dynamicsreuse/(?P<submission_id>[0-9]+)/(?P<model_id>[0-9]+)/$', views.DYNAMICSview, name='dynamicsreuse'),
    url(r'^DYNAMICSfilled/(?P<submission_id>[0-9]+)/$', views.DYNAMICSview, name='DYNAMICSfilled'),
    #url(r'^form/$', views.get_formup, name='form'),
    url(r'^model/carousel/(?P<model_id>[0-9]+)/$', views.carousel_model_components, name='carousel_model_components'),
    url(r'^dynamics/carousel/(?P<dynamics_id>[0-9]+)/$', views.carousel_dynamics_components, name='carousel_dynamics_components'),
    #url(r'^files/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT,}), #this line shouldnt be here
    url(r'^submitted/(?P<submission_id>[0-9]+)/$', views.SUBMITTEDview, name='submitted'),
    url(r'^close_submission/(?P<submission_id>[0-9]+)/$', views.close_submission, name='close_submission'),
    url(r'^datasets/$', views.datasets, name='datasets'),
    url(r'^table/$', views.table, name='table'),
    url(r'^blank/$', TemplateView.as_view(template_name="dynadb/blank.html"), name='blank'),]

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
else:

    if settings.FILES_NO_LOGIN:
        serve_files_func = views.serve_submission_files_no_login
    else:
        serve_files_func = views.serve_submission_files
    urlpatterns += patterns('',
        url(r'^files/(?P<obj_folder>[^/\\]+)/(?P<submission_folder>[^/\\]+)/(?P<path>.*)$', serve_files_func, name='serve_submission_files'),

)

