from django.shortcuts import render
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.db.models import F
from dynadb.models import DyndbDynamics, DyndbFilesDynamics
from news.models import News
from common.models import ReleaseNotes, ReleaseStatistics
from dynadb.views import obtain_domain_url
import pandas as pd
import json
import os
import pickle

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
    context['logo_text_path'] = 'home/logo/' + settings.SITE_NAME + '/text.png';
    
#    #latest entry
#    latest=DyndbDynamics.objects.filter(is_published=True).latest("creation_timestamp")
#    dynfiles = DyndbFilesDynamics.objects.filter(id_dynamics__id=latest.id)
#    #dynfiles = dynfiles.annotate(file_name=F("id_files__filename"),file_path=F("id_files__filepath"),file_id=F('id_files__id'))
#    dynfiles = dynfiles.annotate(file_path=F("id_files__filepath"));
#    model_path = dynfiles.get(id_files__id_file_types__is_model=True).file_path;
#    context["model_path"]= model_path[model_path.index("Dynamics"):] 
#########
    dynall=DyndbDynamics.objects.filter(is_published=True) #all().exclude(id=5) #I think dyn 5 is wrong

    ################ Precompute & import
    #dynclass=dynall.annotate(is_published=F('is_published'))
    

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
            pdb_id_set.add(pdbid)
        fam_slug=dyn["fam_slug"]
        if not fam_slug:
            fam_slug=dyn["fam_slug2"]
        fam=False
        if fam_slug:
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


#    # Submissions by class    
#    dynall_fam_data=[d["fam"] for d in dyn_dict.values()]
#    class_li=[]
#    for gclass in ["A","B1","B2","C","F"]:
#        class_count=dynall_fam_data.count(gclass)
#        class_li.append([gclass,class_count])
#    context["class_data"]=json.dumps(class_li)


    # Submisisons by date
    date_d={}
    syst_c=0
    traj_c=0
    for d in dyn_dict.values():
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
    #Fams sumulated
    sim_fams=len(fam_set)
    missing_fams=64 - sim_fams
    fam_stats= [['Class', 'Num'],
                ['Simulated', sim_fams],
                ['Pending',missing_fams]
                ]
    context["fam_stats"]=json.dumps(fam_stats)


    #Subtypes sumulated
    sim_subtyppes=len(subtype_set)
    missing_subtypes=64 - sim_subtyppes
    subtype_stats= [['Class', 'Num'],
                ['Simulated', sim_subtyppes],
                ['Pending',missing_subtypes]
                ]
    context["subtype_stats"]=json.dumps(subtype_stats)


    #PDB ids sumulated
    pdb_id_sim=len(pdb_id_set)
    missing_pdb_ids=346 - pdb_id_sim
    pdb_stats= [['Class', 'Num'],
                ['Simulated', pdb_id_sim],
                ['Pending',missing_pdb_ids]
                ]
    context["pdb_stats"]=json.dumps(pdb_stats)



#    # Activation state
#    stats_precomp_file="/protwis/sites/files/Precomputed/Summary_info/dyn_stats.data"
#    exists=os.path.isfile(stats_precomp_file)
#    act_li=False
#    if exists:
#        with open(stats_precomp_file, 'rb') as filehandle:  
#            act_li = pickle.load(filehandle)
#    context["act_data"]=json.dumps(act_li)


    # Entry of the month
    dyn_id=4
    context["dyn_id"]=dyn_id
    dynobj=dynall.filter(id=dyn_id)#.latest("creation_timestamp")
    t=dynobj.annotate(dyn_id=F('id'))
    t = t.annotate(comp_resname=F("id_model__dyndbmodelcomponents__resname"))
    t = t.annotate(comp_type=F("id_model__dyndbmodelcomponents__type"))
    t = t.annotate(protname=F('id_model__id_protein__uniprotkbac'))
    t = t.annotate(protname2=F('id_model__id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein__name'))
    t = t.annotate(ligname=F("id_model__dyndbmodelcomponents__id_molecule__dyndbcompound__name"))
    t = t.annotate(pdb_namechain=F("id_model__pdbid"))
    dyndata=t.values("id","comp_resname","comp_type","protname","protname2","ligname","pdb_namechain")

    lig_li=[d["comp_resname"].capitalize() for d in dyndata if d["comp_type"]==1]
    context["lig_li"]=" or ".join(lig_li)
    
    ligname_li=[d["ligname"].capitalize() for d in dyndata if d["comp_type"]==1] 
    context["lig_name"]=" and ".join(ligname_li)
    
    prot_name=" and ".join(list({d["protname"] if d["protname"] else d["protname2"] for d in dyndata}))
    context["prot_name"]=prot_name

    pdb_namechain=dyndata[0]["pdb_namechain"]
    if dyn_id ==4 and not pdb_namechain:
        pdb_namechain="4N6H"
    context["pdb_id"]=pdb_namechain.split(".")[0]

    dynfiles = DyndbFilesDynamics.objects.filter(id_dynamics__id=dyn_id)
    dynfiles = dynfiles.annotate(file_path=F("id_files__filepath"))
    dynfiles = dynfiles.annotate(is_model=F("id_files__id_file_types__is_model"))
    #dynfiles = dynfiles.annotate(is_traj=F("id_files__id_file_types__is_trajectory"));
    filesdata= dynfiles.values("file_path","is_model")
    #foundstr=False
    #foundtraj=False
    for f in filesdata:
        if f["is_model"]==True:
            model_path=f["file_path"]
            context["model_path"]= model_path[model_path.index("Dynamics"):].split(".")[0] + "_filtered.gro"
            break
#            foundstr=True
#        if f["is_traj"]==True:
#            traj_path=f["file_path"]
#            context["traj_path"]= traj_path[traj_path.index("Dynamics"):] 
#            foundtraj=True
#        if (foundtraj and foundstr):
#            break

    #prot_info = dynfiles.annotate(file_path=F("id_model__name"));

    mdsrv_url=obtain_domain_url(request)
    context["mdsrv_url"]=mdsrv_url



    return render(request, 'home/index_gpcrmd.html', context )

def contact(request):
    context = {}
    return render(request, 'home/contact.html', context )

def community(request):
    context = {}
    return render(request, 'home/community.html', context )

def gpcrtree(request):
    context = {}
    return render(request, 'home/gpcrtree.html', context )