from django.urls import re_path, include

from modules.common import views


urlpatterns = [
    re_path(r'^addtoselection', views.AddToSelection, name='addtoselection'),
    re_path(r'^removefromselection', views.RemoveFromSelection, name='removefromselection'),
    re_path(r'^clearselection', views.ClearSelection, name='clearselection'),
    re_path(r'^selectrange', views.SelectRange, name='selectrange'),
    re_path(r'^togglefamilytreenode', views.ToggleFamilyTreeNode, name='togglefamilytreenode'),
    re_path(r'^selectionannotation', views.SelectionAnnotation, name='selectionannotation'),
    re_path(r'^selectionspeciespredefined', views.SelectionSpeciesPredefined, name='selectionspeciespredefined'),
    re_path(r'^selectionspeciestoggle', views.SelectionSpeciesToggle, name='selectionspeciestoggle'),
    re_path(r'^expandsegment', views.ExpandSegment, name='expandsegment'),
    re_path(r'^selectfullsequence', views.SelectFullSequence, name='selectfullsequence'),
    re_path(r'^selectalignablesegments', views.SelectAlignableSegments, name='selectalignablesegments'),
    re_path(r'selectionschemespredefined', views.SelectionSchemesPredefined, name='selectionschemespredefined'),
    re_path(r'selectionschemestoggle', views.SelectionSchemesToggle, name='selectionschemestoggle'),
    re_path(r'settreeselection', views.SetTreeSelection, name='settreeselection'),
    re_path(r'selectresiduefeature', views.SelectResidueFeature, name='selectresiduefeature'),
    re_path(r'addresiduegroup', views.AddResidueGroup, name='addresiduegroup'),
    re_path(r'selectresiduegroup', views.SelectResidueGroup, name='selectresiduegroup'),
    re_path(r'removeresiduegroup', views.RemoveResidueGroup, name='removeresiduegroup'),
    re_path(r'setgroupminmatch', views.SetGroupMinMatch, name='setgroupminmatch'),
    re_path(r'residuesdownload', views.ResiduesDownload, name='residuesupload'),
    re_path(r'residuesupload', views.ResiduesUpload, name='residuesupload'),
    re_path(r'^selectiongproteinpredefined', views.SelectionGproteinPredefined, name='selectiongproteinpredefined'),
    re_path(r'^selectiongproteintoggle', views.SelectionGproteinToggle, name='selectiongproteintoggle'),
    re_path(r'^targetformread', views.ReadTargetInput, name='targetformread'),
]