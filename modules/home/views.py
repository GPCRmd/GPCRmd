from django.shortcuts import render
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.db.models import F
from modules.dynadb.models import DyndbDynamics, DyndbFilesDynamics
from modules.news.models import News
from modules.common.models import ReleaseNotes, ReleaseStatistics
from modules.dynadb.views import obtain_domain_url
from django.http import HttpResponse
from modules.covid19.models import CovidDynamics
import pandas as pd
import json
import os
import pickle
import copy

def search_in_treeData(classifli,myslug):#gpcrclassif_fams,myfam_slug
    namefound=False
    for nlevel in range(0,len(classifli)):
        thisslug= classifli[nlevel]["slug"]
        if myslug==thisslug:
            namefound=True
            return(nlevel)
    return(False)

def json_dict(path):
    """
    Converts json file to pyhton dict.
    """
    json_file=open(path)
    json_str = json_file.read()
    json_data = json.loads(json_str)
    return json_data

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

def open_json(filepath):
    json_file=open(filepath)
    json_str = json_file.read()
    json_data=pd.io.json.loads(json_str)
    return json_data

def gpcrmd_home(request):
    context = {}

    # title of the page
    context['site_title'] = settings.SITE_TITLE
    context['documentation_url'] = settings.DOCUMENTATION_URL
    context['logo_path'] = 'home/logo/' + settings.SITE_NAME + '/main.png';
    context['logo_text_path'] = 'home/logo/' + settings.SITE_NAME + '/text.png';
    gpcrmdtree_path=settings.MEDIA_ROOT + "Precomputed/Summary_info/gpcrmdtree.data"
    with open(gpcrmdtree_path, 'rb') as filehandle:  
        tree_data = pickle.load(filehandle)
    context['tree_data']=json.dumps(tree_data)
    dynall=DyndbDynamics.objects.filter(is_published=True) #all().exclude(id=5) #I think dyn 5 is wrong

    ################ Precompute & import    
    dynclass=dynall.annotate(subm_date=F('creation_timestamp'))
    dynclass=dynclass.annotate(is_traj=F('dyndbfilesdynamics__id_files__id_file_types__is_trajectory'))
    dynclass=dynclass.annotate(file_id=F('dyndbfilesdynamics__id_files__id'))
    dynclass=dynclass.annotate(fam_slug=F('id_model__id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein__receptor_id_protein__family_id__slug'))
    dynclass=dynclass.annotate(fam_slug2=F('id_model__id_protein__receptor_id_protein__family_id__slug'))
    dynclass=dynclass.annotate(dyn_id=F('id'))
    dynclass = dynclass.annotate(pdb_namechain=F("id_model__pdbid"))
    dynall_values=dynclass.values("dyn_id","subm_date","fam_slug","fam_slug2","is_published","is_traj","file_id","pdb_namechain")

    dyn_dict = {}
    #fam_d={"001":"A","002":"B1","003":"B2","004":"C","005":"F","006":"Taste 2","007":"Others"}

    pdb_id_set=set()
    fam_set=set()
    subtype_set=set()
    for dyn in dynall_values:
        dyn_id=dyn["dyn_id"]
        pdbid=dyn["pdb_namechain"].split(".")[0]
        if pdbid:
            if pdbid != "HOMO":
                pdb_id_set.add(pdbid)
        fam_slug=dyn["fam_slug"]
        if not fam_slug:
            fam_slug=dyn["fam_slug2"]
        fam=False
        if fam_slug:
            if pdbid != "HOMO":
                subtype_set.add(fam_slug)
                fam_set.add(fam_slug[:-4])
            fam_code=fam_slug.split("_")[0]
            #fam=fam_d[fam_code]            
        if dyn_id not in dyn_dict:
            dyn_dict[dyn_id]={}
            dyn_dict[dyn_id]["subm_date"]=dyn["subm_date"]
            dyn_dict[dyn_id]["fam"]=fam
            if dyn["is_traj"]:
                dyn_dict[dyn_id]["trajs"]={dyn["file_id"]}
            else:
                dyn_dict[dyn_id]["trajs"]=set()
        else:
            if not dyn_dict[dyn_id]["fam"]:
                dyn_dict[dyn_id]["fam"]=fam
            if dyn["is_traj"]:
                dyn_dict[dyn_id]["trajs"].add(dyn["file_id"])

    # Submisisons by date
    date_d={}
    syst_c=0
    traj_c=0
    for d in sorted(dyn_dict.values(),key=lambda x:x["subm_date"]):
        subm_date_obj=d["subm_date"]
        subm_date=subm_date_obj.strftime("%b %Y")
        syst_c+=1
        traj_c+=len(d["trajs"])
        if not subm_date in date_d:
            date_d[subm_date]={}
        date_d[subm_date]["Systems"]=syst_c
        date_d[subm_date]["Trajectories"]=traj_c
        #date_d[subm_date]["Dateobj"]=subm_date_obj

    st=pd.DataFrame.from_dict(date_d,orient="index")
    st.index=pd.to_datetime(st.index).to_period('m')
    st = st.reindex(pd.period_range(st.index.min(), st.index.max(), freq='m'), fill_value=0)
    st.index= [st.strftime("%b %Y") for st in st.index]

    last_s=0
    last_t=0
    subm_data=[]
    for index, row in st.iterrows():
        sys=row["Systems"]
        traj=row["Trajectories"]
        if sys ==0:
            sys=last_s
            traj=last_t
            leg_s=""
            leg_t=""
        else:
            last_s=sys
            last_t=traj
            leg_s=str(sys)
            leg_t=str(traj)
        subm_data.append([index,int(sys),leg_s,int(traj),leg_t])

    context["subm_data"] =json.dumps(subm_data)
    ################
    fam_count=0
    subt_count=0
    pdb_count=0
    for nclasstmp in range(0,len(tree_data["children"])):
        fam=tree_data["children"][nclasstmp]["children"]
        len_fam=len(fam)
        fam_count+=len_fam
        for nfamtmp in range(0,len_fam):            
            st=tree_data["children"][nclasstmp]["children"][nfamtmp]["children"]
            len_st=len(st)
            subt_count+=len_st
            for nsubt in range(0,len_st):
                pdbli=tree_data["children"][nclasstmp]["children"][nfamtmp]["children"][nsubt]["children"]
                pdb_count+=len(pdbli)

    #Fams sumulated
    sim_fams=len(fam_set)
    total_fams=fam_count #missing=["Melatonin",
                           #"Parathyroid hormone receptors", 
                           #'Prostanoid receptors' ,"Tachykinin"]
                   #GPCRdb: 34
                   #GPCRmd:30
    missing_fams= total_fams - sim_fams
    if missing_fams < 0: 
        missing_fams = 0
    fam_stats= [['Class', 'Num'],
                ['Simulated', sim_fams],
                ['Pending',missing_fams]
                ]
    context["fam_stats"]=json.dumps(fam_stats)
    context["total_fam_stats"] = total_fams

    #Subtypes sumulated
    sim_subtyppes=len(subtype_set)
    total_subtyppes=subt_count
                   #GPCRdb: 64
                   #GPCRmd: 52
    missing_subtypes=total_subtyppes - sim_subtyppes
    if missing_subtypes < 0: 
        missing_subtypes = 0
    subtype_stats= [['Class', 'Num'],
                ['Simulated', sim_subtyppes],
                ['Pending',missing_subtypes]
                ]
    context["subtype_stats"]=json.dumps(subtype_stats)
    context["total_subtype_stats"] = total_subtyppes

    #PDB ids sumulated
    pdb_id_sim=len(pdb_id_set)
    pdb_id_total=pdb_count
                   #GPCRdb: 346
                   #GPCRmd: 270
    missing_pdb_ids=pdb_id_total - pdb_id_sim
    if missing_pdb_ids < 0: 
        missing_pdb_ids = 0
    pdb_stats= [['Class', 'Num'],
                ['Simulated', pdb_id_sim],
                ['Pending',missing_pdb_ids]
                ]
    context["pdb_stats"]=json.dumps(pdb_stats)
    context["total_pdb_stats"] = pdb_id_total

    gpcrmdtree_path= settings.MEDIA_ROOT+"Precomputed/Summary_info/gpcrmdtree.data"

    mdsrv_url=obtain_domain_url(request)
    context["mdsrv_url"]=mdsrv_url

    return render(request, 'home/index_gpcrmd.html', context)

def contact(request):
    context = {}
    return render(request, 'home/contact.html', context )

# LEGAL TERMS
def disclaimer(request):
    context = {}
    return render(request, 'home/disclaimer.html', context )

def cookies_policy(request):
    context = {}
    return render(request, 'home/cookies_policy.html', context )

def privacy_policy(request):
    context = {}
    return render(request, 'home/privacy_policy.html', context )

def terms(request):
    context = {}
    return render(request, 'home/terms.html', context )

def community(request):
    context = {}
    return render(request, 'home/community.html', context )

def gpcrtree(request):
    context = {}
    gpcrmdtree_path=settings.MEDIA_ROOT + "Precomputed/Summary_info/gpcrmdtree.data"
    with open(gpcrmdtree_path, 'rb') as filehandle:  
        tree_data = pickle.load(filehandle)
    context['tree_data']=json.dumps(tree_data)
    dynall=DyndbDynamics.objects.filter(is_published=True) #all().exclude(id=5) #I think dyn 5 is wrong

    ################ Precompute & import
    dynclass=dynall.annotate(subm_date=F('creation_timestamp'))
    dynclass=dynclass.annotate(is_traj=F('dyndbfilesdynamics__id_files__id_file_types__is_trajectory'))
    dynclass=dynclass.annotate(file_id=F('dyndbfilesdynamics__id_files__id'))
    dynclass=dynclass.annotate(fam_slug=F('id_model__id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein__receptor_id_protein__family_id__slug'))
    dynclass=dynclass.annotate(fam_slug2=F('id_model__id_protein__receptor_id_protein__family_id__slug'))
    dynclass=dynclass.annotate(dyn_id=F('id'))
    dynclass = dynclass.annotate(pdb_namechain=F("id_model__pdbid"))
    dynall_values=dynclass.values("dyn_id","subm_date","fam_slug","fam_slug2","is_published","is_traj","file_id","pdb_namechain")


    dyn_dict = {}
    #fam_d={"001":"A","002":"B1","003":"B2","004":"C","005":"F","006":"Taste 2","007":"Others"}

    pdb_id_set=set()
    fam_set=set()
    subtype_set=set()
    for dyn in dynall_values:
        dyn_id=dyn["dyn_id"]
        pdbid=dyn["pdb_namechain"].split(".")[0]
        if pdbid:
            if pdbid != "HOMO":
                pdb_id_set.add(pdbid)
        fam_slug=dyn["fam_slug"]
        if not fam_slug:
            fam_slug=dyn["fam_slug2"]
        fam=False
        if fam_slug:
            if pdbid != "HOMO":
                subtype_set.add(fam_slug)
                fam_set.add(fam_slug[:-4])
            fam_code=fam_slug.split("_")[0]
            #fam=fam_d[fam_code]            
        if dyn_id not in dyn_dict:
            dyn_dict[dyn_id]={}
            dyn_dict[dyn_id]["subm_date"]=dyn["subm_date"]
            dyn_dict[dyn_id]["fam"]=fam
            if dyn["is_traj"]:
                dyn_dict[dyn_id]["trajs"]={dyn["file_id"]}
            else:
                dyn_dict[dyn_id]["trajs"]=set()
        else:
            if not dyn_dict[dyn_id]["fam"]:
                dyn_dict[dyn_id]["fam"]=fam
            if dyn["is_traj"]:
                dyn_dict[dyn_id]["trajs"].add(dyn["file_id"])

    # Submisisons by date
    date_d={}
    syst_c=0
    traj_c=0
    for d in sorted(dyn_dict.values(),key=lambda x:x["subm_date"]):
        subm_date_obj=d["subm_date"]
        subm_date=subm_date_obj.strftime("%b %Y")
        syst_c+=1
        traj_c+=len(d["trajs"])
        if not subm_date in date_d:
            date_d[subm_date]={}
        date_d[subm_date]["Systems"]=syst_c
        date_d[subm_date]["Trajectories"]=traj_c
        #date_d[subm_date]["Dateobj"]=subm_date_obj

    st=pd.DataFrame.from_dict(date_d,orient="index")
    st.index=pd.to_datetime(st.index).to_period('m')
    st = st.reindex(pd.period_range(st.index.min(), st.index.max(), freq='m'), fill_value=0)
    st.index= [st.strftime("%b %Y") for st in st.index]

    last_s=0
    last_t=0
    subm_data=[]
    for index, row in st.iterrows():
        sys=row["Systems"]
        traj=row["Trajectories"]
        if sys ==0:
            sys=last_s
            traj=last_t
            leg_s=""
            leg_t=""
        else:
            last_s=sys
            last_t=traj
            leg_s=str(sys)
            leg_t=str(traj)
        subm_data.append([index,int(sys),leg_s,int(traj),leg_t])

    context["subm_data"] =json.dumps(subm_data)
    ################
    fam_count=0
    subt_count=0
    pdb_count=0
    for nclasstmp in range(0,len(tree_data["children"])):
        fam=tree_data["children"][nclasstmp]["children"]
        len_fam=len(fam)
        fam_count+=len_fam
        for nfamtmp in range(0,len_fam):            
            st=tree_data["children"][nclasstmp]["children"][nfamtmp]["children"]
            len_st=len(st)
            subt_count+=len_st
            for nsubt in range(0,len_st):
                pdbli=tree_data["children"][nclasstmp]["children"][nfamtmp]["children"][nsubt]["children"]
                pdb_count+=len(pdbli)

    #Fams sumulated
    sim_fams=len(fam_set)
    total_fams=fam_count #missing=["Melatonin",
                           #"Parathyroid hormone receptors", 
                           #'Prostanoid receptors' ,"Tachykinin"]
                   #GPCRdb: 34
                   #GPCRmd:30
    missing_fams= total_fams - sim_fams
    if missing_fams < 0: # Error with negative numbers
        missing_fams = 0
    fam_stats= [['Class', 'Num'],
                ['Simulated', sim_fams],
                ['Pending',missing_fams]
                ]
    context["fam_stats"]=json.dumps(fam_stats)


    #Subtypes sumulated
    sim_subtyppes=len(subtype_set)
    total_subtyppes=subt_count
                   #GPCRdb: 64
                   #GPCRmd: 52
    missing_subtypes=total_subtyppes - sim_subtyppes
    subtype_stats= [['Class', 'Num'],
                ['Simulated', sim_subtyppes],
                ['Pending',missing_subtypes]
                ]
    context["subtype_stats"]=json.dumps(subtype_stats)


    #PDB ids sumulated
    pdb_id_sim=len(pdb_id_set)
    pdb_id_total=pdb_count
                   #GPCRdb: 346
                   #GPCRmd: 270
    missing_pdb_ids=pdb_id_total - pdb_id_sim
    if missing_pdb_ids < 0: 
        missing_pdb_ids = 0
    pdb_stats= [['Class', 'Num'],
                ['Simulated', pdb_id_sim],
                ['Pending',missing_pdb_ids]
                ]
    context["pdb_stats"]=json.dumps(pdb_stats)
    mdsrv_url=obtain_domain_url(request)
    context["mdsrv_url"]=mdsrv_url

    return render(request, 'home/gpcrtree.html', context)

def news(request):
    context = {}
    return render(request, 'home/news.html', context )

def ndround(request):
    context = {}
    return render(request, 'home/news/2ndround.html', context )


def is_updating(request):
    """
    Check out if a load-all-simulations-after-updating thing is going on
    """
    print(os.path.exists(settings.MEDIA_ROOT + "config/isloading.txt"))
    isloading = os.path.exists(settings.MEDIA_ROOT + "config/isloading.txt")
    return(HttpResponse(isloading))

def remove_marker(request): 
    """
    Delete the load-all-simulations-after-updating once quickloading is done
    """
    if os.path.exists(settings.MEDIA_ROOT + "config/isloading.txt"):
        os.remove(settings.MEDIA_ROOT + "config/isloading.txt")
    return(HttpResponse())

def quickloadall_both(request):

    """
    Quickload both covid and gpcrmd
    """

    # Create uploading file
    f = open(settings.MEDIA_ROOT + 'config/isloading.txt','w')
    f.close()

    #DyndbFiles.objects.filter(dyndbfilesdynamics__id_dynamics=dyn_id, id_file_types__is_trajectory=True)
    mdsrv_url=obtain_domain_url(request)
    dynobj=DyndbDynamics.objects.all()
    dynfiledata = dynobj.annotate(dyn_id=F('id'))
    dynfiledata = dynfiledata.annotate(file_path=F('dyndbfilesdynamics__id_files__filepath'))
    dynfiledata = dynfiledata.annotate(file_is_traj=F('dyndbfilesdynamics__id_files__id_file_types__is_trajectory'))
    dynfiledata = dynfiledata.annotate(file_ext=F('dyndbfilesdynamics__id_files__id_file_types__extension'))
    dynfiledata = dynfiledata.values("dyn_id","file_path","file_is_traj","file_ext")
    dyn_dict = {}
    for dyn in dynfiledata:
        dyn_id=dyn["dyn_id"]
        if dyn_id not in dyn_dict:
            dyn_dict[dyn_id]={}
            dyn_dict[dyn_id]["traj"]=[]
            dyn_dict[dyn_id]["pdb"]=[]
        file_info=dyn["file_path"]
        if not file_info:
            continue
        file_short=file_info[file_info.index("Dynamics"):]
        if dyn["file_is_traj"]:
            dyn_dict[dyn_id]["traj"].append(file_short)
        elif dyn["file_ext"]=="pdb":
            dyn_dict[dyn_id]["pdb"].append(file_short)

    del dynfiledata

    dynobj=CovidDynamics.objects.filter(is_published=True)
    dynfiledata = dynobj.annotate(dyn_id=F('id'))
    dynfiledata = dynfiledata.annotate(file_path=F('covidfilesdynamics__id_files__filepath'))
    dynfiledata = dynfiledata.annotate(file_is_traj=F('covidfilesdynamics__id_files__id_file_types__is_trajectory'))
    dynfiledata = dynfiledata.annotate(file_ext=F('covidfilesdynamics__id_files__id_file_types__extension'))
    dynfiledata = dynfiledata.values("dyn_id","file_path","file_is_traj","file_ext")

    for dyn in dynfiledata:
        dyn_id=dyn["dyn_id"]
        if dyn_id not in dyn_dict:
            dyn_dict[dyn_id]={}
            dyn_dict[dyn_id]["traj"]=[]
            dyn_dict[dyn_id]["pdb"]=[]
        file_info=dyn["file_path"]
        if not file_info:
            continue
        file_short=file_info[file_info.index("Covid19Dynamics"):]
        if dyn["file_is_traj"]:
            dyn_dict[dyn_id]["traj"].append(file_short)
        elif dyn["file_ext"]in {"pdb","gro"}:
            dyn_dict[dyn_id]["pdb"].append(file_short)

    filesli=[[d["pdb"][0],d["traj"]] for d in dyn_dict.values() if d["pdb"]]
    context={
        "mdsrv_url":mdsrv_url,
        "filesli":json.dumps(filesli)
            }
    return render(request, 'home/quickloadall.html', context)


