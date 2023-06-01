from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import CharField,TextField as V, F
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

from modules.view.views import obtain_domain_url
from modules.covid19.models import *
from modules.dynadb.models import DyndbFileTypes

from modules.covid19.forms import *
from django.forms.forms import NON_FIELD_ERRORS

import json
import mdtraj as md
import numpy as np
import math
import re
import os
import copy
import csv
import requests
import pickle
import pandas as pd
import statistics

from django.conf import settings

def extract_table_info(request,mydyn):
    context={}
    if request.user.is_authenticated():
        if request.user.has_privilege_covid:
            context["user_accepted"]=True
    dyndata={}
    mydyn=mydyn.annotate(file_id=F("covidfilesdynamics__id_files__id"))
    mydyn=mydyn.annotate(file_is_traj=F('covidfilesdynamics__id_files__id_file_types__is_trajectory'))
    mydyn=mydyn.annotate(pdbid=F('id_model__pdbid'))
    mydyn=mydyn.annotate(finalprot=F('id_model__final_proteins__name'))
    mydyn=mydyn.annotate(model_source=F('id_model__source'))
    
    #Added:
    #mydyn=mydyn.annotate(model_type=F('id_model__type'))
    mydyn=mydyn.annotate(is_ligand=F('coviddynamicscomponents__is_ligand'))
    mydyn=mydyn.annotate(is_membrane=F('coviddynamicscomponents__is_membrane'))
    mydyn=mydyn.annotate(molecule_name=F('coviddynamicscomponents__molecule_name'))
    #mydyn=mydyn.annotate(ligand_type=F('coviddynamicscomponents__ligand_type'))
    
    mydyn=mydyn.annotate(prot_name=F('id_model__covidmodelprotein__id_protein__name'))
    mydyn=mydyn.annotate(uniprotkbac=F('id_model__covidmodelprotein__id_protein__uniprotkbac'))
    mydyn=mydyn.annotate(uniprot_entry=F('id_model__covidmodelprotein__id_protein__uniprot_entry'))
    mydyn=mydyn.annotate(species=F('id_model__covidmodelprotein__id_protein__species'))

    mydynvalues=mydyn.values("dyn_name","id","author_institution","file_id","file_is_traj","pdbid","is_published","is_ligand","is_membrane","molecule_name","prot_name","uniprotkbac","uniprot_entry","species","atom_num","software" , "sversion" , "ff" , "ffversion" ,"model_source", "finalprot")
    model_source_data=CovidModel.MODEL_SOURCE
#"is_ligand","is_membrane","molecule_name","prot_name","uniprotkbac","uniprot_entry","species","atom_num","software" , "sversion" , "ff" , "ffversion" 
    for dynval in mydynvalues:
        if not dynval["is_published"]:
            continue
        dyn_id=dynval["id"]
        if dyn_id not in dyndata:
            dyndata[dyn_id]={}
            dyndata[dyn_id]["dyn_id"]=dyn_id
            dyndata[dyn_id]["dyn_name"]=dynval["dyn_name"]
            dyndata[dyn_id]["prot_name"]=list()#dynval["prot_name"]
            dyndata[dyn_id]["uniprotkbac"]=list()#dynval["uniprotkbac"]
            dyndata[dyn_id]["uniprot_entry"]=list()#dynval["uniprot_entry"]
            dyndata[dyn_id]["species"]=set()#dynval["species"]
            dyndata[dyn_id]["author_institution"]=dynval["author_institution"]
            dyndata[dyn_id]["pdbid"]=dynval["pdbid"]
            dyndata[dyn_id]["included_prot"]=set()
            model_source=dynval["model_source"]
            if model_source==1:
                dyndata[dyn_id]["model_source"]= model_source_data[1][1]
            dyndata[dyn_id]["traj_ids"]=set()
            dyndata[dyn_id]["ligands"]=set()
            dyndata[dyn_id]["membrane_comp"]=set()
            dyndata[dyn_id]["atom_num"]=dynval["atom_num"]
            dyndata[dyn_id]["software"]=dynval["software"]
            dyndata[dyn_id]["sversion"]=dynval["sversion"]
            dyndata[dyn_id]["ff"]=dynval["ff"]
            dyndata[dyn_id]["ffversion" ]=dynval["ffversion" ]
        if dynval["prot_name"] and dynval["prot_name"] not in dyndata[dyn_id]["prot_name"]:
            dyndata[dyn_id]["prot_name"].append(dynval["prot_name"])
        if dynval["uniprotkbac"] and dynval["uniprotkbac"] not in dyndata[dyn_id]["uniprotkbac"]:
            dyndata[dyn_id]["uniprotkbac"].append(dynval["uniprotkbac"])
        if dynval["uniprot_entry"] and dynval["uniprot_entry"] not in dyndata[dyn_id]["uniprot_entry"]:
            dyndata[dyn_id]["uniprot_entry"].append(dynval["uniprot_entry"])
        if dynval["species"]:
            mysp=dynval["species"]
            if mysp=="Severe acute respiratory syndrome coronavirus 2 (2019-nCoV) (SARS-CoV-2)":
                mysp="SARS-CoV-2"
            elif mysp=="Severe acute respiratory syndrome coronavirus (SARS-CoV)":
                mysp="SARS-CoV"
            else:
                mysp=mysp.split(" (")[0]
            dyndata[dyn_id]["species"].add(mysp)
        if dynval["file_is_traj"]:
            dyndata[dyn_id]["traj_ids"].add(dynval["file_id"])
        if dynval["is_ligand"]:
            dyndata[dyn_id]["ligands"].add(dynval["molecule_name"])
        elif dynval["is_membrane"]:
            dyndata[dyn_id]["membrane_comp"].add(dynval["molecule_name"])
        if dynval["finalprot"]:
            dyndata[dyn_id]["included_prot"].add(dynval["finalprot"])
    #context["tabledata"]=dyndata.values()
    context["tabledata"]=sorted(dyndata.values(), key=lambda x:x["dyn_id"])
    return context


#def index_allprot(request,genome_id):
#    error_msn=False
#    if CovidIsolate.objects.filter(isolate_id=genome_id).exists():
#        seqgen=CovidSequencedGene.objects.filter(id_sequence__is_wt=False,id_isolate__isolate_id=genome_id)
#        is_filtered=sorted(list({e.id_final_protein.name for e in seqgen}))
#        mydyn=CovidDynamics.objects.filter(id_model__final_proteins__name__in=is_filtered,id_model__proteins__species="Severe acute respiratory syndrome coronavirus 2 (2019-nCoV) (SARS-CoV-2)")
#    else:
#        mydyn=CovidDynamics.objects.all()
#        is_filtered=False
#        error_msn="Isolate %s not found" % genome_id
#        genome_id=False
#    context=extract_table_info(request,mydyn)
#    context["is_filtered"]=is_filtered
#    context["variant_genome"]=genome_id
#    context["error_msn"]=error_msn
#    return render(request, 'sc2md/index.html', context)


def index(request,prot_name=None,genome_id=None):
    is_filtered=False
    if genome_id and not CovidIsolate.objects.filter(isolate_id=genome_id).exists():
        error_msn="Isolate %s not found" % genome_id
        genome_id=False
    if prot_name:
        mydyn=CovidDynamics.objects.filter(id_model__final_proteins__name=prot_name,is_shared_sc2md=True)
        if genome_id:
            mydyn=mydyn.filter(id_model__proteins__species="Severe acute respiratory syndrome coronavirus 2 (2019-nCoV) (SARS-CoV-2)")
        is_filtered=[prot_name]
    else:  
        mydyn=CovidDynamics.objects.filter(is_shared_sc2md=True)
        is_filtered=False
    error_msn=""
    context=extract_table_info(request,mydyn)
    context["is_filtered"]=is_filtered
    context["variant_genome"]=genome_id
    context["error_msn"]=error_msn
    return render(request, 'sc2md/index.html', context)

def getstrideval(framenum):
    if framenum < 5000:
        strideto=10
    elif framenum < 10000:
        strideto=50
    else:
        strideto=100
    return strideto

def get_fplot_data(dyn_id,traj_id):
    show_fp=False
    int_type_l=['hb', 'sb', 'pc', 'ps', 'ts', 'vdw', 'wb', 'wb2',"hp"]
    int_name_d={"hb":"Hydrogen bonds",
                "sb": "Salt bridges",
                "pc": "Pi-cation",
                "ps": "Pi-stacking",
                "ts": "T-stacking",
                "vdw": "Van der Waals",
                "wb": "Water bridges",
                "wb2": "Extended water bridges",
                "hp" : "Hydrophobic"}    
    fp_data=[]
    for int_type in int_type_l:
        fpfilename= "%(traj_id)s_trj_%(dyn_id)s_%(int_type)s.json"%{"dyn_id":dyn_id,"traj_id":traj_id,"int_type":int_type}
        fpdir = settings.MEDIA_ROOT + "Precomputed/covid19/flare_plot/%s" % int_type
        fppath = os.path.join(fpdir,fpfilename)
        exists=os.path.isfile(fppath)
        if exists:
            fpdir_url = "/dynadb/files/Precomputed/covid19/flare_plot/%s" % int_type
            fppath_url = os.path.join(fpdir_url,fpfilename)
            fp_data.append([int_type,int_name_d[int_type],fppath_url])
            show_fp=True
        else:
            fp_data.append([int_type,int_name_d[int_type],""])
    return (fp_data, show_fp)


def obtain_dom_res_sel(chainres_d):
    res_sel_li=[]
    for (chainn,chaind) in chainres_d.items():
        extremes_li=[]
        for extremes in chaind["seg_li"]:
            if extremes[0]!= extremes[1]:
                pairsel="%s-%s"%(extremes[0],extremes[1])
            else:
                pairsel=str(extremes[0])
            extremes_li.append(pairsel)
        if chainn and chainn!= " ":
            res_sel_ch=":%s and (%s)"%(chainn," or ".join(extremes_li))
        else:
            res_sel_ch=" or ".join(extremes_li)
        res_sel_li.append(res_sel_ch)

        
        #[":%s and (%s)"%(chainn," or ".join( ["%s-%s" %(e[0],e[1]) if e[0]!= e[1] else str(e[0]) for e in chaind["seg_li"]])) for (chainn,chaind) in chainres_d.items()]

    #res_sel_li=["%s:%s"%(r["seqpos"],r["chain"]) if (r["chain"] and r["chain"]!=" ") else str(r["seqpos"])  for r in mydom_resli]
    if len(res_sel_li) >1:
        res_sel_li=["(%s)"%e for e in res_sel_li]
    res_sel=" or ".join(res_sel_li)
    res_sel_fin="protein and (%s)"%res_sel
    return res_sel_fin


def dynanalysis(request,dyn_id,sel_genome_id=None):
    context={}

    # TO ADD: 
        #light sel and heavy sel
    #####

    d=CovidDynamics.objects.select_related("id_model__pdbid","id_model__source").prefetch_related("covidfilesdynamics_set__id_files__id_file_types","coviddynamicscomponents_set","id_model__covidmodelprotein_set__id_protein__coviduniprotseqpositions_set","id_model__final_proteins").get(id=dyn_id,is_published=True)
    if not d.is_shared_sc2md:
        raise Exception("Simulation not found")
    context["dyn_id"]=dyn_id
    delta=d.delta
    if not delta:
        delta=0.2

    context["delta"]=delta
    context["dyn_name"]=d.dyn_name
    context["pdbid"]=d.id_model.pdbid
    model_source=d.id_model.source
    if model_source==1:
        model_source_data=CovidModel.MODEL_SOURCE
        context["model_source"]= model_source_data[1][1]
    context["files"]={}
    context["files"]["traj"]=[]
    show_fp=False
    trajidToFramenum={}
    modelfileobj=None
    for f in d.covidfilesdynamics_set.all():
        fileobj=f.id_files
        filetype=fileobj.id_file_types
        if filetype.is_trajectory:
            filedata={}
            framenum=f.framenum
            traj_id=fileobj.id
            filedata["id"]=traj_id
            filedata["name"]=fileobj.filename
            filedata["path"]=fileobj.filepath.replace(settings.MEDIA_ROOT + "","")
            (fp_data, fp_avail)=get_fplot_data(dyn_id,traj_id)
            show_fp=show_fp or fp_avail
            filedata["fplot"]=fp_data
            filedata["strideval"]=getstrideval(framenum)
            context["files"]["traj"].append(filedata)
            trajidToFramenum[traj_id]=framenum
        elif filetype.is_coordinates:
            modelfileobj=fileobj
            filedata={}
            filedata["id"]=fileobj.id
            filedata["name"]=fileobj.filename
            filedata["path"]=fileobj.filepath.replace(settings.MEDIA_ROOT + "","")
            context["files"]["pdb"]=filedata
    context["trajidToFramenum"]=json.dumps(trajidToFramenum)
    context["show_fp"]=show_fp

    context["molecules"]=[]
    for m in d.coviddynamicscomponents_set.all():
        molinfo={}
        molinfo["resname"]=m.resname
        molinfo["molecule_name"]=m.molecule_name
        #molinfo["number"]=m.numberofmol
        molinfo["is_ligand"]=m.is_ligand
        molinfo["is_membrane"]=m.is_membrane
        context["molecules"].append(molinfo)

    included_prots={e.name for e in d.id_model.final_proteins.all()}
    prot_to_finalprot_obj=CovidProteinFinalprotein.objects.annotate(prot_name=F("id_finalprotein__name")).filter(prot_name__in=included_prots,id_protein__in=d.id_model.proteins.all())
    prot_to_finalprot_obj_val=prot_to_finalprot_obj.values("finalprot_seq_start","finalprot_seq_end","prot_name")
    prot_to_finalprot={e["prot_name"]:e for e in prot_to_finalprot_obj_val}
    seq_intervals_finalprot={(e["finalprot_seq_start"],e["finalprot_seq_end"]):e["prot_name"] for e in prot_to_finalprot_obj_val}


    #domains info
    model_prots=CovidProtein.objects.filter(covidmodelprotein__id_model=d.id_model)
    uniprotkbac_li=[p.uniprotkbac for p in model_prots if p.uniprotkbac]
    protdomains=CovidDomains.objects.filter(uniprotkbac__in=uniprotkbac_li)
    model_pos_obj=CovidModelSeqPositions.objects.select_related("id_uniprotpos").filter(id_file=modelfileobj)

   # upseq_to_model={m.id_uniprotpos.seqpos: {"seqpos":m.seqpos,"aa":m.aa,"chain":m.chainid} for m in model_pos_obj}
    upseq_to_model={}
    finpseq_to_model={}
    for m in model_pos_obj:
        up_pos=m.id_uniprotpos.seqpos
        model_details={"seqpos":m.seqpos,"aa":m.aa,"chain":m.chainid}
        upseq_to_model[up_pos]=model_details
        for interval,protname in seq_intervals_finalprot.items():
            if up_pos >=interval[0] and up_pos <=interval[1]:
                if protname not in finpseq_to_model:
                    finpseq_to_model[protname]={}
                fp_pos=(up_pos - interval[0]) +1
                finpseq_to_model[protname][fp_pos]=model_details

    alldominfo={}
    for mydom in protdomains:
        dominfo={}
        region_name=mydom.region_name.capitalize()
        dominfo["uniprotkbac"]=mydom.uniprotkbac
        domnote=mydom.note
        if not domnote:
            domnote=region_name
        dominfo["note"]=domnote
        evidence_str=mydom.evidence
        evidence_li_pre=evidence_str.split(", ")
        pm_evidence_li=[]
        for thisev in evidence_li_pre:
            thisevdata=thisev.split("|")
            for evd in thisevdata:
                evd_sp=evd.split(":")
                if len(evd_sp)==2:
                    (evd_from, evd_id)=evd_sp
                    if evd_from=="PubMed":
                        pm_evidence_li.append(evd_id)
        dominfo["pm_evidence"]=pm_evidence_li
        dominfo["domain_seq"]=mydom.domain_seq
        frompos_up=mydom.frompos
        topos_up=mydom.topos
        dominfo["seq_positions"]=(frompos_up,topos_up)
        dom_residues_up=range(frompos_up,topos_up+1)
        dom_residues_result=[]
        for dom_pos_up in dom_residues_up:
            dompos_model_info=upseq_to_model.get(dom_pos_up,None)
            if dompos_model_info:
                dom_residues_result.append(dompos_model_info)
        if dom_residues_result:
            if region_name not in alldominfo:
                alldominfo[region_name]=[]
            dominfo["residues"]=dom_residues_result
            domid=region_name.replace(" ","_")
            dominfo["domainid"]=domid
            alldominfo[region_name].append(dominfo)
    for domname,domtype in alldominfo.items():
        for mydom in domtype:
            mydom_resli=mydom["residues"]
            chainres_d={}
            for r in sorted(mydom_resli,key=lambda x:(x["chain"],x["seqpos"])):
                rchain=r["chain"]
                rseqpos=r["seqpos"]
                if rchain not in chainres_d:
                    chainres_d[rchain]={"segi":0,"seg_li":[[rseqpos,rseqpos]]}
                else:
                    segi=chainres_d[rchain]["segi"]
                    last_seqpos=chainres_d[rchain]["seg_li"][segi][1]
                    if rseqpos == last_seqpos+1:
                        chainres_d[rchain]["seg_li"][segi][1]=rseqpos
                    else:
                        chainres_d[rchain]["segi"]+=1
                        chainres_d[rchain]["seg_li"].append([rseqpos,rseqpos])
            res_sel_fin=obtain_dom_res_sel(chainres_d)
            mydom["selection"]=res_sel_fin
        alldominfo[domname]=sorted(domtype,key=lambda x:x["note"])
    context["domains"]=alldominfo

    # Extract variants in the protein(s). If selected isolate, make a list of variants in it
    context["var_data"]=False
    context["variant_genome"]=sel_genome_id
    
    mdsrv_url=obtain_domain_url(request)
    
        

    context["mdsrv_url"]=mdsrv_url
    if request.session.get('warning_load', False):
        warning_load=request.session["warning_load"]
    else:
        warning_load={"trajload":True,"heavy":True}
    context["warning_load"]=json.dumps(warning_load)

    return render(request, 'sc2md/dynanalysis.html', context)


def ajax_notshow_warn(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.POST:
        warning_type=request.POST.get("warning_type")
        if request.session.get('warning_load', False):
            warning_load=request.session["warning_load"]
        else:
            warning_load={"trajload":True,"heavy":True}
        warning_load[warning_type]=False;
        request.session['warning_load']=warning_load
        return HttpResponse(json.dumps(True), content_type='sc2md/1')

def result_by_time(data_frame,delta):
    data_store=copy.deepcopy(data_frame)
    data_store[0].insert(1,"Time")
    data_time=[data_store[0][1:]]
    for row in data_store[1:]:
        frame=row[0]
        time=(frame+1)*delta
        row.insert(1,time)
        d_time=row[1:]
        data_time.append(d_time)  
    return (data_store,data_time)

def ajax_rmsd(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.POST:
        if request.POST.get("rmsdStr"):
            struc_p= request.POST.get("rmsdStr")
            traj_p= request.POST.get("rmsdTraj")
            traj_frame_rg= request.POST.get("rmsdFrames")
            ref_frame= request.POST.get("rmsdRefFr")
            ref_traj_p= request.POST.get("rmsdRefTraj")
            traj_sel= request.POST.get("rmsdSel")
            no_rv=request.POST.get("no_rv")
            strideVal=request.POST.get("stride")
            delta=float(request.POST.get("delta"))
            dyn_id=request.POST.get("dyn_id")
            if request.session.get('covid_rmsd_data', False):
                rmsd_data_all=request.session['covid_rmsd_data']
                if dyn_id in rmsd_data_all:
                    rmsd_data=rmsd_data_all[dyn_id]
                    rmsd_dict=rmsd_data["rmsd_dict"]
                    new_rmsd_id=rmsd_data["new_rmsd_id"]
                    no_rv_l=no_rv.split(",")
                    to_rv=[];
                    for r_id in rmsd_dict.keys():
                        if (r_id not in no_rv_l):
                            to_rv.append(r_id)
                    for r_id in to_rv:
                        del rmsd_dict[r_id]   
                else:
                    new_rmsd_id=1
                    rmsd_dict={}
            else:
                new_rmsd_id=1
                rmsd_dict={}
            if len(rmsd_dict) < 15:
                (success,data_fin, errors)=compute_rmsd(struc_p,traj_p,traj_frame_rg,ref_frame,ref_traj_p,traj_sel,int(strideVal))
                if success:
                    data_frame=data_fin
                    (data_store,data_time)=result_by_time(data_frame,delta)
                    struc_filename=os.path.basename(struc_p)
                    traj_filename=os.path.basename(traj_p)
                    rtraj_filename=os.path.basename(ref_traj_p)
                    rmsd_dict["rmsd_"+str(new_rmsd_id)]=(data_store,struc_filename,traj_filename,traj_frame_rg,ref_frame,rtraj_filename,traj_sel,strideVal)
                    rmsd_data_dyn={"rmsd_dict":rmsd_dict, "new_rmsd_id":new_rmsd_id+1}
                    if request.session.get('covid_rmsd_data', False):
                        rmsd_data_all=request.session["covid_rmsd_data"]
                    else:
                        rmsd_data_all={}
                    rmsd_data_all[dyn_id]= rmsd_data_dyn
                    request.session['covid_rmsd_data']=rmsd_data_all
                    data_rmsd = {"result_t":data_time,"result_f":data_frame,"rmsd_id":"rmsd_"+str(new_rmsd_id),"success": success, "msg":errors , "strided":strideVal}
                else: 
                    data_rmsd = {"result":data_fin,"rmsd_id":None,"success": success, "msg":errors , "strided":strideVal}

            else:
                data_rmsd = {"result":None,"rmsd_id":None,"success": False, "msg":"Please, remove some RMSD results to obtain new ones." , "strided":strideVal}
            return HttpResponse(json.dumps(data_rmsd), content_type='sc2md/'+dyn_id)   

def ajax_rmsf(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.POST:
        if request.POST.get("rmsfStr"):
            struc_p= request.POST.get("rmsfStr")
            traj_p= request.POST.get("rmsfTraj")
            traj_frame_rg= request.POST.get("rmsfFrames")
            traj_sel= request.POST.get("rmsfSel")
            no_rv=request.POST.get("no_rv")
            strideVal=request.POST.get("stride")
            delta=float(request.POST.get("delta"))
            dyn_id=request.POST.get("dyn_id")
            if request.session.get('covid_rmsf_data', False):
                rmsf_data_all=request.session['covid_rmsf_data']
                if dyn_id in rmsf_data_all:
                    rmsf_data=rmsf_data_all[dyn_id]
                    rmsf_dict=rmsf_data["rmsf_dict"]
                    new_rmsf_id=rmsf_data["new_rmsf_id"]
                    no_rv_l=no_rv.split(",")
                    to_rv=[];
                    for r_id in rmsf_dict.keys():
                        if (r_id not in no_rv_l):
                            to_rv.append(r_id)
                    for r_id in to_rv:
                        del rmsf_dict[r_id]   
                else:
                    new_rmsf_id=1
                    rmsf_dict={}
            else:
                new_rmsf_id=1
                rmsf_dict={}
            if len(rmsf_dict) < 15:
                (success,data_fin, errors)=compute_rmsf(struc_p,traj_p,traj_frame_rg,traj_sel,int(strideVal))
                if success:
                    data_rmsf = {}
                    struc_filename=os.path.basename(struc_p)
                    traj_filename=os.path.basename(traj_p)
                    rmsf_dict["rmsf_"+str(new_rmsf_id)]=(data_fin,struc_filename,traj_filename,traj_frame_rg,traj_sel,strideVal)
                    rmsf_data_dyn={"rmsf_dict":rmsf_dict, "new_rmsf_id":new_rmsf_id+1}
                    if request.session.get('covid_rmsf_data', False):
                        rmsf_data_all=request.session["covid_rmsf_data"]
                    else:
                        rmsf_data_all={}
                    rmsf_data_all[dyn_id]= rmsf_data_dyn
                    request.session['covid_rmsf_data']=rmsf_data_all
                    data_rmsf = {"result":data_fin,"rmsf_id":"rmsf_"+str(new_rmsf_id),"success": success, "msg":errors , "strided":strideVal}
                else: 
                    data_rmsf = {"result":data_fin,"rmsf_id":None,"success": success, "msg":errors , "strided":strideVal}

            else:
                data_rmsf = {"result":None,"rmsf_id":None,"success": False, "msg":"Please, remove some RMSF results to obtain new ones." , "strided":strideVal}
            return HttpResponse(json.dumps(data_rmsf), content_type='sc2md/'+dyn_id)   




def  apply_frame_limit(target_n_frames,frames_done,total_num_frames):
    frames_done_new=frames_done+target_n_frames
    limit_top_frame=target_n_frames
    stop_traj=False
    if frames_done_new >= total_num_frames:
        limit_top_frame=total_num_frames-(frames_done)
        stop_traj=True
    return (limit_top_frame,stop_traj)

def rmsf(atom_sel,struc_path,traj_path,fr_from,strideVal, total_num_frames,frame=0):
    first=True
    frames_done=0
    itertraj=md.iterload(filename=traj_path,chunk=10, skip =fr_from ,top=struc_path, stride =strideVal)
    mytop=None
    for target in itertraj:
        #itraj.center_coordinates()
        if first:
            atom_indices=target.topology.select_atom_indices(atom_sel)
            avg_xyz_frame = np.zeros_like(target.xyz[frame, atom_indices, :], order='C', dtype=np.float32)
            n_atoms = target.xyz.shape[1] if np.all(atom_indices == slice(None)) else len(
                atom_indices)
            fluctuations = np.zeros(n_atoms, dtype=np.float32)
            mytop=target.atom_slice(atom_indices).topology
            first=False
        # by frame num
        target_n_frames = target.xyz.shape[0]
        target_displaced_xyz = np.array(target.xyz[:, atom_indices, :], copy=True)
        #Apply frame limit
        (target_n_frames,stop_traj)=apply_frame_limit(target_n_frames,frames_done,total_num_frames)
        #frames_done
        frames_done+=target_n_frames
        print("Average: frame %s - %.6s %%\n"% (frames_done,(frames_done/total_num_frames)*100))
        #Obtain average position of each atom
        for i in range(target_n_frames):
            for j in range(n_atoms):
                avg_xyz_frame[j, 0] += target_displaced_xyz[i, j, 0] / total_num_frames
                avg_xyz_frame[j, 1] += target_displaced_xyz[i, j, 1] / total_num_frames
                avg_xyz_frame[j, 2] += target_displaced_xyz[i, j, 2] / total_num_frames
        if stop_traj:
            break

    itertraj=md.iterload(filename=traj_path,chunk=10, skip =fr_from ,top=struc_path, stride =strideVal)
    first=True
    frames_done=0
    for target in itertraj:
        #itraj.center_coordinates()
        target_n_frames = target.xyz.shape[0]
        target_displaced_xyz = np.array(target.xyz[:, atom_indices, :], copy=True)
        #Apply frame limit
        (target_n_frames,stop_traj)=apply_frame_limit(target_n_frames,frames_done,total_num_frames)
        frames_done+=target_n_frames
        print("Diff: frame %s - %.6s %%\n"% (frames_done,(frames_done/total_num_frames)*100))
        #Obtain diff between each atom position and average
        for i in range(target_n_frames):
            for j in range(n_atoms):
                fluctuations[j] += ((target_displaced_xyz[i, j, 0] - avg_xyz_frame[j, 0])**2 +
                                    (target_displaced_xyz[i, j, 1] - avg_xyz_frame[j, 1])**2 +
                                    (target_displaced_xyz[i, j, 2] - avg_xyz_frame[j, 2])**2) / total_num_frames
        if stop_traj:
            break
    for j in range(n_atoms):
        fluctuations[j] = math.sqrt(fluctuations[j])
    my_rmsf=list(np.array(fluctuations, copy=False, dtype=float))
    my_res_li=["%s%s"%(r.name,r.resSeq) for r in mytop.residues]
    rmsf_data=list(zip(my_res_li,my_rmsf))
    rmsf_data=[["Residue","RMSF"]]+rmsf_data
    return rmsf_data


def obtain_strided_filtered_fnum(traj_path,fr_from,max_n_frames,strideVal):
    error=False
    small_error=False
    t=md.open(traj_path)
    whole_num_frames=t.__len__()
    if fr_from >= whole_num_frames:
        error_msg ="The trajectory analysed has no frame " + str(fr_from) +"."
        return(None,True,False)
    if not  max_n_frames:
        max_n_frames=whole_num_frames
    if max_n_frames > whole_num_frames:
        small_error ="The trajectory analysed has no frame " + str(max_n_frames-1) +". The final frame has been set to the last frame of that trajectory."
        small_errors.append(small_error) 
        max_n_frames=False
    else:
        whole_num_frames=max_n_frames-fr_from
    total_num_frames=math.floor(whole_num_frames/strideVal)
    return (total_num_frames,error,small_error)

def compute_rmsf(rmsfStr,rmsfTraj,traj_frame_rg,traj_sel,strideVal):
    #remove reference traj option
    #manage seleciton
    i=0
    struc_path = settings.MEDIA_ROOT + "" + rmsfStr
    traj_path = settings.MEDIA_ROOT + "" + rmsfTraj
    small_errors=[]
    atom_sel=None
    if traj_sel == "bck":
        atom_sel="alpha"
    elif traj_sel == "noh":
        atom_sel="heavy"
    elif traj_sel == "min":
        atom_sel="minimal"
    if traj_frame_rg == "all_frames":
        fr_from=0
        max_n_frames=False
    else:
        fr_li=traj_frame_rg.split("-")
        fr_from=int(fr_li[0])
        max_n_frames=int(fr_li[1])+1
    (total_num_frames,error,small_error)=obtain_strided_filtered_fnum(traj_path,fr_from,max_n_frames,strideVal)
    if error:
        return (False,None, error_msg)
    if small_error:
        small_errors.append(small_error)
    try:
        my_rmsf=rmsf(atom_sel,struc_path,traj_path,fr_from,strideVal,total_num_frames)
    except Exception:
        error_msg="RMSF can't be calculated."
        return (False,None, error_msg)
    data_fin=my_rmsf
    return(True, data_fin, small_errors)



def compute_rmsd(rmsdStr,rmsdTraj,traj_frame_rg,ref_frame,rmsdRefTraj,traj_sel,strideVal):
    i=0
    struc_path = settings.MEDIA_ROOT + "" + rmsdStr
    traj_path = settings.MEDIA_ROOT + "" + rmsdTraj
    ref_traj_path = settings.MEDIA_ROOT + "" + rmsdRefTraj
    small_errors=[]
    set_sel=None
    if traj_sel == "bck":
        set_sel="alpha"
    elif traj_sel == "noh":
        set_sel="heavy"
    elif traj_sel == "min":
        set_sel="minimal"
    if traj_frame_rg == "all_frames":
        fr_from=0
        fr_to="num_frames"
    else:
        fr_li=traj_frame_rg.split("-")
        fr_from=int(fr_li[0])
        fr_to=int(fr_li[1])+1
    try:
        ref_traj_fr=md.load_frame(ref_traj_path,int(ref_frame),top=struc_path)
        itertraj=md.iterload(filename=traj_path,chunk=10, skip =fr_from ,top=struc_path, stride =strideVal)
    except Exception:
        return (False,None, ["Error loading input files."])
    if len(ref_traj_fr)==0:
        error_msg="Frame "+str(ref_frame)+" does not exist at refference trajectory."
        return (False,None, error_msg)          
    rmsd_all=np.array([])
    if fr_to=="num_frames":
        max_n_frames=False
    else:
        max_n_frames=fr_to
    fr_count=fr_from
    for itraj in itertraj:
        fr_count+=(itraj.n_frames)*strideVal
        if max_n_frames and fr_count > max_n_frames:
            if i == 0:
                fr_max=math.ceil(( max_n_frames-(fr_count - (itraj.n_frames)*strideVal))/strideVal)
            else:
                fr_max=max_n_frames-(fr_count - (itraj.n_frames)*strideVal)
        else:
            fr_max=itraj.n_frames
        i+=fr_max

        if traj_sel =="all_prot":
            selection=itraj.topology.select("protein")
        else:
            selection=itraj.topology.select_atom_indices(set_sel)
        try:
            rmsd = md.rmsd(itraj[:fr_max], ref_traj_fr, 0,atom_indices=selection)
            rmsd_all=np.append(rmsd_all,rmsd,axis=0)
        except Exception:
            error_msg="RMSD can't be calculated."
            return (False,None, error_msg)
        if max_n_frames and fr_from+ (i*strideVal) >= max_n_frames:
            break
    if fr_from >= fr_count:
        error_msg ="The trajectory analysed has no frame " + str(fr_from) +"."
        return (False,None, error_msg)
    if max_n_frames and max_n_frames > fr_count:
        small_error ="The trajectory analysed has no frame " + str(max_n_frames-1) +". The final frame has been set to "+ str(fr_count - 1) +", the last frame of that trajectory."
        small_errors.append(small_error)            
    rmsd_all=np.reshape(rmsd_all,(len(rmsd_all),1))
    frames=np.arange(fr_from,fr_from+(len(rmsd_all)*strideVal),strideVal,dtype=np.int32).reshape((len(rmsd_all),1))
    data=np.append(frames,rmsd_all, axis=1).tolist()
    data_fin=[["Frame","RMSD"]] + data
    return(True, data_fin, small_errors)

def selection_proper_name(traj_sel):
    if traj_sel == "bck":
        set_sel="protein CA"
    elif traj_sel == "noh":
        set_sel="non-hydrogen protein atoms"
    elif traj_sel == "min":
        set_sel="protein CA, CB, C, N, O"
    elif traj_sel == "all_prot":
        set_sel="all protein atoms"
    else:
        set_sel = traj_sel
    return set_sel  

def download_fasta(request,genome_id,prot_name):
    myseq=CovidSequence.objects.get(covidsequencedgene__id_isolate__isolate_id=genome_id, covidsequencedgene__id_final_protein__name=prot_name).seq
    genomeinfo=CovidIsolate.objects.get(isolate_id=genome_id)
    gdate=genomeinfo.isolate_date
    gdate_formated=gdate.strftime("%Y-%m-%d")
    header_info=[prot_name,genomeinfo.isolate_name,gdate_formated,genome_id,genomeinfo.history,genomeinfo.tloc,genomeinfo.host,genomeinfo.originating_lab,genomeinfo.submitting_lab,genomeinfo.submitter,genomeinfo.location,genomeinfo.isolate_type]
    header="|".join(header_info)
    content=">%s\n%s" % (header,myseq)
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="%s.fa"'  %prot_name

    return response



def download_data(request,dyn_id,obj_type,obj_id):
    save_error=False
    error_txt=" "
    if obj_type=="rmsd":
        obj_id="%s_%s"%(obj_type,obj_id)
        if request.session.get('covid_rmsd_data', False):
            rmsd_data_s_all=request.session['covid_rmsd_data']
            if dyn_id in rmsd_data_s_all:
                rmsd_data_s=rmsd_data_s_all[dyn_id]
                rmsd_dict=rmsd_data_s["rmsd_dict"]
                if obj_id in rmsd_dict:
                    rmsd_data_all=rmsd_dict[obj_id]
                    (rmsd_data,struc_filename,traj_filename,traj_frame_rg,ref_frame,rtraj_filename,traj_sel,strideVal)=rmsd_data_all        
                    response = HttpResponse(content_type='text/csv')
                    
                    response['Content-Disposition'] = 'attachment; filename="'+re.search("(\w*)\.\w*$",struc_filename).group(1)+"_"+obj_id+'.csv"'
                    writer = csv.writer(response)
                    writer.writerow(["#Structure: "+struc_filename])
                    writer.writerow(["#Trajectory: "+traj_filename])
                    if (int(strideVal) > 1):
                        writer.writerow(["#Strided: "+strideVal])
                    writer.writerow(["#Reference: frame "+ref_frame+" of trajectory "+rtraj_filename])
                    writer.writerow(["#Selection: "+selection_proper_name(traj_sel)])
                    header=[]
                    for name in rmsd_data[0]:
                        header.append("'"+name+"'")
                    writer.writerow(header)
                    for row in rmsd_data[1:]:
                        rowcol=[]
                        for col in row:
                            rowcol.append(col)
                        writer.writerow(rowcol) 
                else:
                    save_error=True
                    error_txt="Session data expired. Please re-load the page and try again."
            else:
                save_error=True
        else:
            save_error=True
    elif obj_type=="rmsf":
        obj_id="%s_%s"%(obj_type,obj_id)
        if request.session.get('covid_rmsf_data', False):
            rmsf_data_s_all=request.session['covid_rmsf_data']
            if dyn_id in rmsf_data_s_all:
                rmsf_data_s=rmsf_data_s_all[dyn_id]
                rmsf_dict=rmsf_data_s["rmsf_dict"]
                if obj_id in rmsf_dict:
                    rmsf_data_all=rmsf_dict[obj_id]
                    (rmsf_data,struc_filename,traj_filename,traj_frame_rg,traj_sel,strideVal)=rmsf_data_all        
                    response = HttpResponse(content_type='text/csv')
                    
                    response['Content-Disposition'] = 'attachment; filename="'+re.search("(\w*)\.\w*$",struc_filename).group(1)+"_"+obj_id+'.csv"'
                    writer = csv.writer(response)
                    writer.writerow(["#Structure: "+struc_filename])
                    writer.writerow(["#Trajectory: "+traj_filename])
                    if (int(strideVal) > 1):
                        writer.writerow(["#Strided: "+strideVal])
                    writer.writerow(["#Selection: "+selection_proper_name(traj_sel)])
                    header=[]
                    for name in rmsf_data[0]:
                        header.append("'"+name+"'")
                    writer.writerow(header)
                    for row in rmsf_data[1:]:
                        rowcol=[]
                        for col in row:
                            rowcol.append(col)
                        writer.writerow(rowcol) 
                else:
                    save_error=True
                    error_txt="Session data expired. Please re-load the page and try again."
            else:
                save_error=True
        else:
            save_error=True
    

    else:
        save_error=True
        error_txt="URL error."
    if save_error:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="x.csv"'
        writer = csv.writer(response)
        writer.writerow([error_txt])
    return response


############################### UPLOAD ##################################
def join_path(*args,relative=False,url=False):
    path = ''
    first_slashre = re.compile(r'^[/\\]+')
    if relative:
        first_slash = ''
    else:
        if url:
            first_slash = '/'
        else:
            first_slash = os.path.sep 
    for arg in args:
        arg_no_slash = first_slashre.sub('',arg)
        path = os.path.join(path,arg_no_slash)
    if url:
        path = path.replace(os.path.sep,'/')
    path = first_slash+path
    return path


def get_file_url_root():
    url_prefix = "/dynadb/"
    return join_path(url_prefix,settings.MEDIA_URL,relative=False,url=True)


def get_file_paths(url=False):
    ''' Function that defines file paths and URLs for served files.
    Edit to change file path and URLs.'''
    
    filefolder="Covid19Dynamics"
        
    if url:
        root = get_file_url_root()
    else:
        root = settings.MEDIA_ROOT
        
    path = join_path(root,filefolder,relative=False,url=url)
    if url:
        path += '/'
    else:
        path += os.path.sep
    return path

def save_uploadedfile(filepath,uploadedfile):
    with open(filepath,'wb') as f:
        if uploadedfile.multiple_chunks:
            for chunk in uploadedfile.chunks():
                f.write(chunk)
        else:
            f.write(uploadedfile.read())
    #uploaded_file.close()
    

#class SaveUploadedFileThread(threading.Thread):
#    def __init__(self, filepath, uploadedfile, *args, **kwargs):
#        self.filepath = filepath
#        self.uploadedfile = uploadedfile
#        super(SaveUploadedFileThread, self).__init__(*args, **kwargs)
#
#    def run(self):
#        save_uploadedfile(self.filepath,self.uploadedfile)


def get_file_name_dict():
    filenamedict = dict()
    #define objects
    filenamedict['dynamics'] = dict()

    #define part(icles)
    filenamedict['dynamics']['part'] = None
    #define subtypes    
    filenamedict['dynamics']['subtypes'] = dict()
    filenamedict['dynamics']['subtypes']["pdb"] = dict()
    filenamedict['dynamics']['subtypes']["topology"] = dict()
    filenamedict['dynamics']['subtypes']["trajectory"] = dict()
    filenamedict['dynamics']['subtypes']["parameters"] = dict()
    filenamedict['dynamics']['subtypes']["other"] = dict()
    filenamedict['dynamics']['subtypes']["log"] = dict()

    #define file ext(ensions)    
    filenamedict['dynamics']['subtypes']["pdb"]["ext"] = ["pdb","gro"]
    filenamedict['dynamics']['subtypes']["topology"]["ext"] = ["psf","prmtop","top"]
    filenamedict['dynamics']['subtypes']["trajectory"]["ext"] = ["xtc","dcd"]
    filenamedict['dynamics']['subtypes']["parameters"]["ext"] = ["prm","tar.gz"]
    filenamedict['dynamics']['subtypes']["other"]["ext"] = ["tar.gz"]
    filenamedict['dynamics']['subtypes']["log"]["ext"] = ["log"]
    
    #define subtype part(icles)
    filenamedict['dynamics']['subtypes']["pdb"]["part"] = "dyn"
    filenamedict['dynamics']['subtypes']["topology"]["part"] = "dyn"
    filenamedict['dynamics']['subtypes']["trajectory"]["part"] = "trj"
    filenamedict['dynamics']['subtypes']["parameters"]["part"] = "prm"
    filenamedict['dynamics']['subtypes']["other"]["part"] = "oth"
    filenamedict['dynamics']['subtypes']["log"]["part"] = "dyn"
    return filenamedict

filenamedict = get_file_name_dict()
def get_file_name_particles(objecttype,ext=None,forceext=False,subtype=None,imgsize=300):
    subtypes = filenamedict[objecttype]['subtypes'].keys()
    
    if subtype is None:
        subtypeslen = len(subtypes)
        if subtypeslen  > 1 :
            raise ValueError("a subtype must be specified for objecttype '"+objecttype+"'.")   
        elif subtypeslen == 1:
            subtype = subtypes.pop()
        else:
            raise ValueError("No subtypes found for objecttype '"+objecttype+\
        "'. Please, check get_file_name_dict() definition.")
        
    exts = filenamedict[objecttype]['subtypes'][subtype]["ext"]
    if filenamedict[objecttype]['part'] is None:
        part = filenamedict[objecttype]['subtypes'][subtype]['part']
    else:
        part = filenamedict[objecttype]['part']
    if ext is None:
        extslen = len(exts)
        if extslen  > 1:
            raise ValueError("a file extension must be specified for objecttype '"+objecttype+":"+subtype+"' using 'ext' keyword.")
        elif extslen == 1:
            extf = exts[0]
    else:
        extf = ext.lower()
        
    if not forceext and extf not in exts :
        raise ValueError(extf+" is not a valid file extension for objecttype '"+objecttype+":"+subtype+"'.\
        To force the use of this extension use the 'forceext' keyword.")
        
    if subtype == "image":
        sizepart='_'+str(imgsize)
    else:
        sizepart = ''
    return(part,sizepart,extf)

def get_file_name(objecttype,fileid,objectid,ext=None,forceext=False,subtype=None,imgsize=300):
    
    part,sizepart,extf = get_file_name_particles(objecttype,ext=ext,forceext=forceext,subtype=subtype,imgsize=imgsize)
    filename = str(fileid)+'_'+part+'_'+str(objectid)+sizepart+'.'+extf
    return filename

def manage_uploaded_file(dynobj,uploaded_file,sub_file_num=0):
    uploaded_file_name=uploaded_file.name
    ext=uploaded_file_name.split(".")[-1]
    if ext=="gz":
        ext="tar.gz"
    filetype=DyndbFileTypes.objects.get(extension=ext)
    if filetype.is_trajectory:
        subtype="trajectory"
        type_val=2
    elif filetype.is_coordinates:
        subtype="pdb"
        type_val=0
    elif filetype.is_topology:
        subtype="topology"
        type_val=1
    elif filetype.is_anytype:
        subtype="other"
        type_val=4

    db_path=get_file_paths()
    os.makedirs(db_path,exist_ok=True)
    db_fileURL=get_file_paths(url=True)
    dyn_id=dynobj.id
    tmp_db_filename ="tmp_"+ get_file_name(objecttype="dynamics",fileid=sub_file_num,objectid=dyn_id,ext=ext,subtype=subtype)
    tmp_db_filepath =  os.path.join(db_path,tmp_db_filename)
    tmp_db_url =  os.path.join(db_fileURL,tmp_db_filename)
    covidfileobj=CovidFiles(
        filename=tmp_db_filename,
        id_file_types=filetype,
        filepath=tmp_db_filepath,
        url=tmp_db_url
        )
    covidfileobj.save()
    file_id=covidfileobj.id
    db_filename =get_file_name(objecttype="dynamics",fileid=file_id,objectid=dyn_id,ext=ext,subtype=subtype)
    db_filepath =  os.path.join(db_path,db_filename)
    db_url =  os.path.join(db_fileURL,db_filename)
    covidfileobj.filename=db_filename
    covidfileobj.filepath=db_filepath
    covidfileobj.url=db_url
    covidfileobj.save()

    covidfile_dyn_obj=CovidFilesDynamics(
        id_dynamics=dynobj,
        id_files=covidfileobj,
        type=type_val,
        )
    covidfile_dyn_obj.save()
    #Store file
    save_uploadedfile(db_filepath,uploaded_file)
    #SaveUploadedFileThread(db_filepath,uploaded_file).start()
    testing=False #[!]
    if not testing:
        if subtype == "pdb":
            if ext=="pdb":
                traj = md.load_pdb(db_filepath)
            else:
                traj = md.load(db_filepath)
            atom_num = traj.n_atoms
            dynobj.atom_num=atom_num
            dynobj.save()
        elif subtype=="trajectory":
            t=md.open(db_filepath)
            framenum=t.__len__()
            covidfile_dyn_obj.framenum=framenum
            covidfile_dyn_obj.save()


def query_uprot(uniprotkbac,fields):
    payload = {'query': 'id:%s'%uniprotkbac,'format': 'tab','columns': ",".join(fields)}
    result = requests.get("http://www.uniprot.org/uniprot/", params=payload)
    if result.ok and result.text:
        result_str=result.text
        (headers,vals)=result_str.split("\n")[:2]
        results_dict=dict(zip(headers.split("\t"),vals.split("\t")))
    else:
        results_dict={}
    return results_dict


#@login_required
@csrf_protect
def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES,extra=(request.POST.get('ligand_count'),request.POST.get('membrane_count')))
        if form.is_valid():
            #Protein
            pdb_id=form.cleaned_data['pdb_id']
            final_prots=form.cleaned_data['final_prots']
            model_source=form.cleaned_data['model_source']
            uniprotkbac=form.cleaned_data['uniprotkbac']
            try:
                prot_name=form.cleaned_data['prot_name']
                uniprot_entry=form.cleaned_data['uniprot_entry']
                species=form.cleaned_data['species']
            except:
                prot_name=None
                uniprot_entry=None
                species=None
            #Author
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            institution=form.cleaned_data['institution']
            #Simulation
            dyn_name=form.cleaned_data['dyn_name']
            delta=form.cleaned_data['delta']
            timestep=form.cleaned_data['timestep']
            software=form.cleaned_data['software']
            sversion=form.cleaned_data['sversion']
            ff=form.cleaned_data['ff']
            ffversion=form.cleaned_data['ffversion']
            try:
                description=request.FILES['description']
            except:
                description=None

            has_lig=form.cleaned_data['has_lig']
            model_type=0
            if has_lig=="Yes":
                model_type=1
            #Save protein
            protobj, created_protobj = CovidProtein.objects.get_or_create(
                uniprotkbac=uniprotkbac,
                uniprot_entry=uniprot_entry,
                name=prot_name,
                species=species
                )
            #Save Model
            modelobj,created_modelobj=CovidModel.objects.get_or_create(
                type=model_type,
                pdbid=pdb_id,
                source=model_source
                #id_protein=protobj
                )
            for protlabel in final_prots:
                finprotobj, created_finprot = CovidFinalProtein.objects.get_or_create(
                    name=protlabel
                    )
                modFinprotobj , created_modFinprotobj = CovidModelFinalProtein.objects.get_or_create(
                    id_final_protein=finprotobj,
                    id_model= modelobj
                  )     
            modprotobj,created_modprotobj=CovidModelProtein.objects.get_or_create(
                id_model=modelobj,
                id_protein=protobj
            )
            #Save Dynamics
            dynobj,created_dynobj=CovidDynamics.objects.get_or_create(
                author_first_name=first_name,
                author_last_name=last_name,
                author_institution=institution,
                delta=delta,
                dyn_name=dyn_name,
                id_model=modelobj,
                timestep=timestep,
                #atom_num=atom_num,
                software=software,
                sversion=sversion,
                ff=ff,
                ffversion=ffversion,
                description=description,
                is_published=True,
                is_shared_sc2md=True
                )
            #Ligand
            if has_lig=="Yes":
                ligand_count=int(form.cleaned_data['ligand_count'])
                lig_id=0
                while lig_id < ligand_count:
                    ligand_name=form.cleaned_data['ligand_name_%s' % lig_id]
                    ligand_resname=form.cleaned_data['ligand_resname_%s' % lig_id]
                    ligand_type=form.cleaned_data['ligand_type_%s' % lig_id]
                    if ligand_type=="orthosteric":
                        ligand_type_val=1
                    else:
                        ligand_type_val=2

                    #Save ligands
                    dyncompobj,created_dyncompobj=CovidDynamicsComponents.objects.get_or_create(
                        id_dynamics=dynobj,
                        resname=ligand_resname,
                        molecule_name=ligand_name,
                        is_ligand=True,
                        ligand_type=ligand_type_val
                        )
                    lig_id+=1

            #Membrane
            has_membrane=form.cleaned_data['has_membrane']
            if has_membrane=="Yes":
                membrane_count=int(form.cleaned_data['membrane_count'])
                membmol_id=0
                while membmol_id < membrane_count:
                    membmol_name=form.cleaned_data['membmol_name_%s' % membmol_id]
                    membmol_resname=form.cleaned_data['membmol_resname_%s' % membmol_id]

                    #Save Membrane
                    dyncompobj,created_dyncompobj=CovidDynamicsComponents.objects.get_or_create(
                        id_dynamics=dynobj,
                        resname=membmol_resname,
                        molecule_name=membmol_name,
                        is_membrane=True
                        )
                    membmol_id+=1
            #Files
            coord_uploadedfile=request.FILES['coord_file']
            manage_uploaded_file(dynobj,coord_uploadedfile)
            traj_uploadedfiles= request.FILES.getlist('traj_files')
            traj_num_file=0
            for traj_uploadedfile in traj_uploadedfiles:
                manage_uploaded_file(dynobj,traj_uploadedfile,traj_num_file)
                traj_num_file+=1
            try:
                other_uploadedfile=request.FILES['other_files']
            except:
                other_uploadedfile=None
            if other_uploadedfile:
                manage_uploaded_file(dynobj,other_uploadedfile)

            return HttpResponseRedirect('/sc2md/upload/success/%s' % dynobj.id)
        else:
            form._errors[NON_FIELD_ERRORS] = form.error_class(['Some fields are empty or contain errors'])
    else:
        form = UploadFileForm()
    context={}
    context["form"]=form
    return render(request, 'sc2md/upload.html', context)



def upload_success(request,dyn_id):
    context={"dyn_id":dyn_id}
    return render(request, 'sc2md/upload_success.html', context)


def home(request):    
    context={}
    input_path_colors=settings.MEDIA_ROOT + "Covid19Data/Data/colorscales.data"
    if os.path.isfile(input_path_colors):
        with open(input_path_colors, 'rb') as filehandle:  
            colors_dict = pickle.load(filehandle)
    context["colors_dict"]=json.dumps(colors_dict)
    var_li=sorted((e,e.replace("_"," ").capitalize()) for e in colors_dict.keys())
    context["var_li"]=var_li
    return render(request, 'sc2md/home.html', context)

def contact(request):
    context = {}
    return render(request, 'sc2md/contact.html', context )
    
def add_if_exists(dbdata,dyndata,myvar):
    if dbdata[myvar]:
        dyndata[myvar]=dbdata[myvar]
    return dyndata

def report(request,dyn_id):
    mydyn=CovidDynamics.objects.filter(id=dyn_id)

    #files
    mydyn=mydyn.annotate(file_id=F("covidfilesdynamics__id_files__id"))
    mydyn=mydyn.annotate(file_type=F('covidfilesdynamics__type'))
    mydyn=mydyn.annotate(file_url=F('covidfilesdynamics__id_files__url'))

    #Simulation details
    mydyn=mydyn.annotate(framenum=F('covidfilesdynamics__framenum'))

    #genetal info
    mydyn=mydyn.annotate(uniprotkbac=F('id_model__covidmodelprotein__id_protein__uniprotkbac'))
    mydyn=mydyn.annotate(uniprot_entry=F('id_model__covidmodelprotein__id_protein__uniprot_entry'))
    mydyn=mydyn.annotate(species=F('id_model__covidmodelprotein__id_protein__species'))
    mydyn=mydyn.annotate(pdbid=F('id_model__pdbid'))
    mydyn=mydyn.annotate(model_source=F('id_model__source'))
    mydyn=mydyn.annotate(finalprot=F('id_model__final_proteins__name'))
    
    #System setup
    mydyn=mydyn.annotate(is_ligand=F('coviddynamicscomponents__is_ligand'))
    mydyn=mydyn.annotate(is_membrane=F('coviddynamicscomponents__is_membrane'))
    mydyn=mydyn.annotate(molecule_name=F('coviddynamicscomponents__molecule_name'))
    mydyn=mydyn.annotate(ligand_type=F('coviddynamicscomponents__ligand_type'))
    

    mydynvalues=mydyn.values("file_id", "file_type", "file_url", "framenum", "uniprotkbac", "uniprot_entry", "species", "pdbid", "model_source", "finalprot", "is_ligand", "is_membrane", "molecule_name", "ligand_type", "author_first_name", "author_last_name", "author_institution","citation","dyn_name","delta", "timestep", "atom_num", "software", "sversion", "ff", "ffversion", "description", "extracted_from_db" , "extracted_from_db_entry")
    dyndata={}
    filetypes_dict={
         0: 'Model',
         1: 'Topology',
         2: 'Trajectory',
         3: 'Parameters',
         4: 'Others'
    }

    dyndata["files_simulation"]={}
    dyndata["files_other"]={}
    dyndata["framenum"]=0
    dyndata["replicates"]=0
    dyndata["final_proteins"]=set()
    dyndata["ligands"]=set()
    dyndata["membrane"]=set()
    for dbdata in mydynvalues:
        if dbdata["file_id"]:
            file_id=dbdata["file_id"]
            filetypeid=dbdata["file_type"]
            if filetypeid in [0,1,2]:
                file_group="files_simulation"
            else:
                file_group="files_other"
            if file_id not in dyndata[file_group]:                
                filetype=filetypes_dict[filetypeid]
                filedata={
                    "type":filetype,
                    "url":dbdata["file_url"]
                }
                dyndata[file_group][file_id] = filedata
                if filetypeid ==2:
                    if dbdata["framenum"]:
                        dyndata["framenum"]+=dbdata["framenum"]
                    dyndata["replicates"]+=1
        dyndata=add_if_exists(dbdata,dyndata,"uniprotkbac")
        dyndata=add_if_exists(dbdata,dyndata,"uniprot_entry")
        dyndata=add_if_exists(dbdata,dyndata,"species")
        dyndata=add_if_exists(dbdata,dyndata,"pdbid")
        dyndata=add_if_exists(dbdata,dyndata,"model_source")
        if dbdata["finalprot"]:
            dyndata["final_proteins"].add(dbdata["finalprot"])
        if dbdata["is_ligand"]:
            ligtype_val=dbdata["ligand_type"]
            if ligtype_val==1:
                ligtype="Orthosteric"
            elif ligtype_val==2:
                ligtype="Allosteric"
            else:
                ligtype=None
            moldata=(dbdata["molecule_name"],ligtype)
            dyndata["ligands"].add(moldata)
        if dbdata["is_membrane"]:
            dyndata["membrane"].add(dbdata["molecule_name"])
        dyndata["author_first_name"]=dbdata["author_first_name"]
        dyndata["author_last_name"]=dbdata["author_last_name"]
        dyndata["author_institution"]=dbdata["author_institution"]
        dyndata["citation"]=dbdata["citation"]
        dyndata["dyn_name"]=dbdata["dyn_name"]
        dyndata["delta"]=dbdata["delta"]
        dyndata["timestep"]=dbdata["timestep"]
        dyndata["atom_num"]=dbdata["atom_num"]
        dyndata["software"]=dbdata["software"]
        dyndata["sversion"]=dbdata["sversion"]
        dyndata["ff"]=dbdata["ff"]
        dyndata["ffversion"]=dbdata["ffversion"]
        dyndata["description"]=dbdata["description"]
        dyndata["extracted_from_db"]=dbdata["extracted_from_db"]
        dyndata["extracted_from_db_entry"]=dbdata["extracted_from_db_entry"]
        
    if dyndata["delta"]:
        if dyndata["framenum"]:
            dyndata["accum_time"]=(dyndata["framenum"] * dyndata["delta"])/1000
    else:
        dyndata["framenum"]=False
    sub_name=""
    if dyndata["author_first_name"] or dyndata["author_last_name"]:
        sub_name="%s %s"%(dyndata["author_first_name"],dyndata["author_last_name"])
        if dyndata["author_institution"]:
            sub_name+=" (%s)"% dyndata["author_institution"]
    if dyndata["author_institution"]:
        sub_name=dyndata["author_institution"]
    dyndata["submitted_by"]=sub_name


    return render(request, 'sc2md/report.html', dyndata )
