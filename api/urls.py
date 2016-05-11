from django.conf.urls import patterns, include, url
from rest_framework import routers

from api import views

urlpatterns = [
    url(r'^reference/', include('rest_framework_swagger.urls')),
    url(r'^protein/accession/(?P<accession>[^/].+)/$', views.ProteinByAccessionDetail.as_view(),
        name='proteinbyaccession'),
    url(r'^protein/(?P<entry_name>[^/].+)/$', views.ProteinDetail.as_view(), name='protein-detail'),
    
    url(r'^proteinfamily/$', views.ProteinFamilyList.as_view(), name='proteinfamily-list'),
    url(r'^proteinfamily/(?P<slug>[^/]+)/$', views.ProteinFamilyDetail.as_view(), name='proteinfamily-detail'),
    url(r'^proteinfamily/children/(?P<slug>[^/]+)/$', views.ProteinFamilyChildrenList.as_view(),
        name='proteinfamily-children'),
    url(r'^proteinfamily/descendants/(?P<slug>[^/]+)/$', views.ProteinFamilyDescendantList.as_view(),
        name='proteinfamily-descendants'),
    url(r'^proteinfamily/proteins/(?P<slug>[^/]+)/$', views.ProteinsInFamilyList.as_view(),
        name='proteinfamily-proteins'),
    url(r'^proteinfamily/proteins/(?P<slug>[^/]+)/(?P<latin_name>[^/]+)/$', views.ProteinsInFamilySpeciesList.as_view(),
        name='proteinfamily-proteins'),

    url(r'^residues/(?P<entry_name>[^/]+)/$', views.ResiduesList.as_view(), name='residues'),
    url(r'^residues/extended/(?P<entry_name>[^/]+)/$', views.ResiduesExtendedList.as_view(), name='residues-extended'),
    
    url(r'^alignment/family/(?P<slug>[^/]+)/$', views.FamilyAlignment.as_view(), name='familyalignment'),
    url(r'^alignment/family/(?P<slug>[^/]+)/statistics/$', views.FamilyAlignment.as_view(), {'statistics': True}, name='familyalignment-statistics'),
    url(r'^alignment/family/(?P<slug>[^/]+)/(?P<segments>[^/]+)/$', views.FamilyAlignmentPartial.as_view(),
        name='familyalignment-partial'),
    url(r'^alignment/family/(?P<slug>[^/]+)/(?P<segments>[^/]+)/statistics/$', views.FamilyAlignmentPartial.as_view(), {'statistics': True},
        name='familyalignment-partial-statistics'),
    url(r'^alignment/family/(?P<slug>[^/]+)/(?P<segments>[^/]+)/(?P<latin_name>[^/]+)/$', views.FamilyAlignmentPartialSpecies.as_view(),
        name='familyalignment-partial-statistics'),
    url(r'^alignment/family/(?P<slug>[^/]+)/(?P<segments>[^/]+)/(?P<latin_name>[^/]+)/statistics/$', views.FamilyAlignmentPartialSpecies.as_view(), {'statistics': True},
        name='familyalignment-partial'),
    url(r'^alignment/protein/(?P<proteins>[^/]+)/$', views.ProteinAlignment.as_view(),
        name='proteinalignment'),
    url(r'^alignment/protein/(?P<proteins>[^/]+)/statistics/$', views.ProteinAlignmentStatistics.as_view(), {'statistics': True},
        name='proteinalignment-statistics'),
    url(r'^alignment/protein/(?P<proteins>[^/]+)/(?P<segments>[^/]+)/$', views.ProteinAlignmentPartial.as_view(),
        name='proteinalignment-partial'),
    url(r'^alignment/protein/(?P<proteins>[^/]+)/(?P<segments>[^/]+)/statistics/$', views.ProteinAlignmentStatistics.as_view(), {'statistics': True},
        name='proteinalignment-statistics'),
    url(r'^alignment/similarity/(?P<proteins>[^/]+)/(?P<segments>[^/]+)/$', views.ProteinSimilaritySearchAlignment.as_view(),
        name='proteinsimilarityalignment'),

    url(r'^structure/$', views.StructureList.as_view(), name='structure-list'),
    url(r'^structure/representative/$', views.RepresentativeStructureList.as_view(), {'representative': True},
        name='structure-representative-list'),
    url(r'^structure/protein/(?P<entry_name>[^/]+)/$', views.StructureListProtein.as_view(),
        name='structure-list-protein'),
    url(r'^structure/protein/(?P<entry_name>[^/]+)/representative/$',
        views.RepresentativeStructureListProtein.as_view(), {'representative': True},
        name='representative-structure-list-protein'),
    url(r'^structure/(?P<pdb_code>[^/]+)/$', views.StructureDetail.as_view(), name='structure-detail'),
    url(r'^structure/(?P<pdb_code>[^/]+)/interaction/$', views.StructureLigandInteractions.as_view(), name='interaction'),
    url(r'^structure/template/(?P<entry_name>[^/]+)/$', views.StructureTemplate.as_view(),
        name='structuretemplate'),
    url(r'^structure/template/(?P<entry_name>[^/]+)/(?P<segments>[^/]+)/$', views.StructureTemplatePartial.as_view(),
        name='structuretemplate-partial'),
    url(r'structure/assign_generic_numbers$', views.StructureAssignGenericNumbers.as_view(),
        name='assign_generic_numbers'),

    url(r'^species/$', views.SpeciesList.as_view(), name='species-list'),
    url(r'^species/(?P<latin_name>[^/]+)/$', views.SpeciesDetail.as_view(), name='species-detail'),

    url(r'^mutants/(?P<entry_name>[^/].+)/$', views.MutantList.as_view(), name='mutants')
]