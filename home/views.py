from django.shortcuts import render
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.db.models import F
from dynadb.models import DyndbDynamics, DyndbFilesDynamics
from news.models import News
from common.models import ReleaseNotes, ReleaseStatistics
from dynadb.views import obtain_domain_url

@cache_page(60 * 60 * 24)
def index(request):
    request.session.flush()

    context = {}

    # title of the page
    context['site_title'] = settings.SITE_TITLE
    context['documentation_url'] = settings.DOCUMENTATION_URL

    # analytics
    context['google_analytics_key'] = settings.GOOGLE_ANALYTICS_KEY

    # get news
    context['news'] = News.objects.order_by('-date').all()[:3]

    # get release notes
    try:
        context['release_notes'] = ReleaseNotes.objects.all()[0]
        context['release_statistics'] = ReleaseStatistics.objects.filter(release=context['release_notes'])
    except IndexError:
        context['release_notes'] = ''
        context['release_statistics'] = []

    return render(request, 'home/index_{}.html'.format(settings.SITE_NAME), context)

def gpcrmd_home(request):
    context = {}

    # title of the page
    context['site_title'] = settings.SITE_TITLE
    context['documentation_url'] = settings.DOCUMENTATION_URL
    context['logo_path'] = 'home/logo/' + settings.SITE_NAME + '/main.png';
    
    context["style"]={"header":"img",# plain or img
                      "sub_header":False,
                      "columns":"info", #carousel, info, False
                      "buttons":"pannels", #pannels, links, all
    }

#    #latest entry
#    latest=DyndbDynamics.objects.filter(is_published=True).latest("creation_timestamp");
#    dynfiles = DyndbFilesDynamics.objects.filter(id_dynamics__id=latest.id)
#    #dynfiles = dynfiles.annotate(file_name=F("id_files__filename"),file_path=F("id_files__filepath"),file_id=F('id_files__id'))
#    dynfiles = dynfiles.annotate(file_path=F("id_files__filepath"));
#    model_path = dynfiles.get(id_files__id_file_types__is_model=True).file_path;
#    mdsrv_url=obtain_domain_url(request)
#    context["model_path"]= model_path[model_path.index("Dynamics"):] 
#    context["mdsrv_url"]=mdsrv_url



    return render(request, 'home/index_gpcrmd.html', context )


def gpcrmd_hometest(request):
    context = {}

    # title of the page
    context['site_title'] = settings.SITE_TITLE
    context['documentation_url'] = settings.DOCUMENTATION_URL
    context['logo_path'] = 'home/logo/' + settings.SITE_NAME + '/main.png';
    


    return render(request, 'home/index_gpcrmd_t.html', context )