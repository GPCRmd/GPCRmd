from django.urls import include, re_path, path
from modules.structure.views import *
from modules.structure import views
from django.conf import settings
from django.views.generic import TemplateView
from django.views.decorators.cache import cache_page

urlpatterns = [
    re_path(r'^$', cache_page(60*60*24*7)(StructureBrowser.as_view()), name='structure_browser'),
    re_path(r'^selection_convert$', ConvertStructuresToProteins, name='convert'),
    re_path(r'^template_browser', TemplateBrowser.as_view(), name='structure_browser'),
    re_path(r'^template_selection', TemplateTargetSelection.as_view(), name='structure_browser'),
    re_path(r'^template_segment_selection', TemplateSegmentSelection.as_view(), name='structure_browser'),
    re_path(r'^statistics$', cache_page(60*60*24*7)(StructureStatistics.as_view()), name='structure_statistics'),
    re_path(r'homology_models', ServeHomologyModels, name='homology_models'),
    re_path(r'^pdb_download_index$', PDBClean.as_view(), name='pdb_download'),
    re_path(r'pdb_segment_selection', PDBSegmentSelection.as_view(), name='pdb_download'),
    re_path(r'^pdb_download$', PDBClean.as_view(), name='pdb_download'),
    re_path(r'^pdb_download/(?P<substructure>\w+)$', PDBDownload.as_view(), name='pdb_download'),
    re_path(r'^generic_numbering_index', GenericNumberingIndex.as_view(), name='generic_numbering'),
    re_path(r'^generic_numbering_results$', GenericNumberingResults.as_view(), name='generic_numbering'),
    re_path(r'^generic_numbering_results/(?P<substructure>\w+)$', GenericNumberingDownload.as_view(), name='generic_numbering'),
    re_path(r'^generic_numbering_selection', GenericNumberingSelection.as_view(), name='generic_numbering'),
    re_path(r'^superposition_workflow_index$', SuperpositionWorkflowIndex.as_view(), name='superposition_workflow'),
    re_path(r'^superposition_workflow_index/(?P<clear>\w{4})$', SuperpositionWorkflowIndex.as_view(), name='superposition_workflow'),
    re_path(r'^superposition_workflow_selection', SuperpositionWorkflowSelection.as_view(), name='superposition_workflow'),
    re_path(r'^superposition_workflow_results$', SuperpositionWorkflowResults.as_view(), name='superposition_workflow'),
    re_path(r'^superposition_workflow_results/(?P<substructure>\w+)$', SuperpositionWorkflowDownload.as_view(), name='superposition_workflow'),
    re_path(r'^fragment_superposition_index', FragmentSuperpositionIndex.as_view(), name='fragment_superposition'),
    re_path(r'^fragment_superposition_results', FragmentSuperpositionResults.as_view(), name='fragment_superposition'),
    re_path(r'^output/(?P<outfile>\w+.\w{3})/(?P<replacement_tag>\w+)$', ServePdbOutfile, name='structural_tools_result'),
    re_path(r'^zipoutput/(?P<outfile>\w+.\w{3})/', ServeZipOutfile, name='structural_tools_result'),
    re_path(r'^showtrees', RenderTrees, name='render'),
    re_path(r'^webform$', views.webform, name='webform'),
    re_path(r'^webformdata$', views.webformdata, name='webformdata'),
    re_path(r'^construct$', views.webform_two, name='webform_two'),
    re_path(r'^construct/(?P<slug>[\w_]+)$', views.webform_two, name='webform_two'),
    re_path(r'^webform/(?P<slug>[\w_]+)$', views.webform_download, name='webform_download'),
    re_path(r'^(?P<pdbname>\w+)$', StructureDetails, name='structure_details'),
    re_path(r'^pdb/(?P<pdbname>\w+)$', ServePdbDiagram, name='structure_serve_pdb'),
    re_path(r'^pdb/(?P<pdbname>\w+)/ligand/(?P<ligand>.+)$', ServePdbLigandDiagram, name='structure_serve_pdb_ligand'),
]
