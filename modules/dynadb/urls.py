# -*- coding: utf-8 -*-

from django.urls import re_path, include #antes: from django.conf.urls import re_path,patterns
from django.views.generic import TemplateView
from django.contrib import admin
from django.conf import settings
from django.views.static import serve
from . import views

from haystack.query import SearchQuerySet
from haystack.views import SearchView
from .forms import MainSearchForm

sqs = SearchQuerySet().all()

app_name= 'dynadb'
urlpatterns = [
    # re_path(r'^reset/$', views.reset_permissions, name="reset_permissions"), # Canviar permisos a files. Obsolet
    # re_path(r'^testsub/$', views.testsub, name="testsub"), # Testing. Obsolet
    # re_path(r'^testpng/$', views.testpng, name="testpng"), # Testing. Obsolet

    # Submssion form starting menu (choose step)
    re_path(r'^db_inputform/(?P<submission_id>[0-9]+)?/?$', views.db_inputformMAIN, name='db_inputform'),
    re_path(r'^before_db_inputform_prev_moddb_inputform/(?P<submission_id>[0-9]+)?/?$', views.db_inputformMAIN, name='before_db_inputform_prev_mod'),

    # Entry pages for proteins, complexes, small molecules, etc.
    re_path(r'^protein/id/(?P<protein_id>[0-9]+)/$',views.query_protein, name='query_protein'),
    re_path(r'^protein/id/(?P<protein_id>[0-9]+)/fasta$',views.query_protein_fasta, name='query_protein_fasta'),
    re_path(r'^molecule/id/(?P<molecule_id>[0-9]+)/$',views.query_molecule, name='query_molecule'),
    re_path(r'^molecule/id/(?P<molecule_id>[0-9]+)/sdf$',views.query_molecule_sdf,name='query_molecule_sdf'),
    re_path(r'^compound/id/(?P<compound_id>[0-9]+)/$',views.query_compound, name='query_compound'),
    re_path(r'^model/id/(?P<model_id>[0-9]+)/$',views.query_model, name='query_model'),
    re_path(r'^dynamics/id/(?P<dynamics_id>[0-9]+)/$',views.query_dynamics, name='query_dynamics'),
    re_path(r'^complex/id/(?P<complex_id>[0-9]+)/$',views.query_complex, name='query_complex'),
    
    # End-of-submission pages. Still used, but need reform-> FROM WHERE ARE THEY REACHED?
    re_path(r'^submission_summary/(?P<submission_id>[0-9]+)/$', views.submission_summaryiew, name='submission_summary'),
    re_path(r'^protein_summary/(?P<submission_id>[0-9]+)/$', views.protein_summaryiew, name='protein_summary'),
    re_path(r'^molecule_summary/(?P<submission_id>[0-9]+)/$', views.molecule_summaryiew, name='molecule_summary'),
    re_path(r'^model_summary/(?P<submission_id>[0-9]+)/$', views.model_summaryiew, name='model_summary'),

    # Regarding the always-broken GPCRmd browser. Not very used and should be hidden or fixed at some point 
    re_path(r'^search/$', SearchView(template=settings.TEMP_ROOT + '/dynadb/search/search.html', searchqueryset=sqs, form_class=MainSearchForm),name='haystack_search'),
    re_path(r'^ajaxsearch/',views.ajaxsearcher,name='ajaxsearcher'),
    re_path(r'^empty_search/',views.emptysearcher,name='emptysearcher'),
    re_path(r'^autocomplete/',views.autocomplete,name='autocomplete'),
    re_path(r'^advanced_search/$', views.NiceSearcher,name='NiceSearcher'),

    # Carousels (image sliders) of small molecules for model/dynamics visualizators
    re_path(r'^model/carousel/(?P<model_id>[0-9]+)/$', views.carousel_model_components, name='carousel_model_components'),
    re_path(r'^dynamics/carousel/(?P<dynamics_id>[0-9]+)/$', views.carousel_dynamics_components, name='carousel_dynamics_components'),

    # Simulation submission index page
    re_path(r'^submitted/(?P<submission_id>[0-9]+)/$', views.SUBMITTEDview, name='submitted'),
    # Command to close a submission. Not returning any html
    re_path(r'^close_submission/(?P<submission_id>[0-9]+)/$', views.close_submission, name='close_submission'),
    # Datasets, search table and whatever "blank" is
    re_path(r'^datasets/$', views.datasets, name='datasets'),
    re_path(r'^table/$', views.table, name='table'),
    re_path(r'^table_reduced/$', views.table_reduced, name='table_reduced'),
    re_path(r'^blank/$', TemplateView.as_view(template_name="dynadb/blank.html"), name='blank'),
    # Special page to view in a table all submissions belonging to same publication. Very important!!! 
    re_path(r'^publications/(?P<ref_id>[0-9]+)/$', views.dyns_in_ref, name='dyns_in_ref'),

    # New submission form
    re_path(r'^step0/$', views.step0, name='step0'),
    re_path(r'^step1/(?P<submission_id>[0-9]+)/$', views.step1, name='step1'),
    re_path(r'^step2/(?P<submission_id>[0-9]+)/$', views.step2, name='step2'),
    re_path(r'^step3/(?P<submission_id>[0-9]+)/$', views.step3, name='step3'),
    re_path(r'^step4/(?P<submission_id>[0-9]+)/$', views.step4, name='step3'),
    re_path(r'^step5/(?P<submission_id>[0-9]+)/$', views.step5, name='step5'),
    re_path(r'^step1_submit/(?P<submission_id>[0-9]+)/$', views.step1_submit, name='step1_submit'),
    re_path(r'^step2_submit/(?P<submission_id>[0-9]+)/$', views.step2_submit, name='step2_submit'),
    re_path(r'^step3_submit/(?P<submission_id>[0-9]+)/$', views.step3_submit, name='step3_submit'),
    re_path(r'^step4_submit/(?P<submission_id>[0-9]+)/$', views.step4_submit, name='step4_submit'),
    re_path(r'^step5_submit/(?P<submission_id>[0-9]+)/$', views.step5_submit, name='step5_submit'),
    re_path(r'^submission_summary/(?P<submission_id>[0-9]+)/$', views.submission_summaryiew, name='submission_summary'),
    # Functions of submission form
    re_path(r'^find_smalmols/(?P<submission_id>[0-9]+)/$', views.find_smalmols, name='find_smalmols'),
    re_path(r'^find_prots/(?P<submission_id>[0-9]+)/$', views.find_prots, name='find_prots'),
    re_path(r'^delete_submission/(?P<submission_id>[0-9]+)/$', views.delete_submission, name='delete_submission'),
    re_path(r'^close__submission/(?P<submission_id>[0-9]+)/$', views.close__submission, name='close__submission'),
    re_path(r'^smalmol_info/', views.smalmol_info_url, name='smalmol_info'),
    re_path(r'^prot_info/', views.prot_info, name='prot_info'),
    re_path(r'^doi_info/', views.doi_info, name='doi_info'),
    re_path(r'^get_alignment/', views.get_alignment_URL, name='get_alignment_URL'),
    re_path(r'^protein/get_mutations/$', views.get_mutations_view, name='protein_get_mutations'),

    #re_path(r'^step2/(?P<submission_id>[0-9]+)/$', views.step2, name='step2'),
    ]

if settings.DEBUG:
    urlpatterns += (
        re_path(r'^files/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}, name='files'),
        re_path(r'^static/(?P<path>.*)$', serve,  {'document_root': settings.STATIC_ROOT}, name='static')
    )
else:
    if settings.FILES_NO_LOGIN:
        serve_files_func = views.serve_submission_files_no_login
    else:
        serve_files_func = views.serve_submission_files
    urlpatterns += (
        re_path(r'^files/(?P<obj_folder>[^/\\]+)/(?P<submission_folder>[^/\\]+)/(?P<path>.*)$', serve_files_func, name='serve_submission_files'),
    )


