from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
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
import datetime
import numbers

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
    context["tabledata"]=sorted(dyndata.values(),key=lambda x:x["dyn_id"])
    return context


def index_allprot(request,genome_id):
    error_msn=False
    if CovidIsolate.objects.filter(isolate_id=genome_id).exists():
        seqgen=CovidSequencedGene.objects.filter(id_sequence__is_wt=False,id_isolate__isolate_id=genome_id)
        is_filtered=sorted(list({e.id_final_protein.name for e in seqgen}))
        mydyn=CovidDynamics.objects.filter(id_model__final_proteins__name__in=is_filtered,id_model__proteins__species="Severe acute respiratory syndrome coronavirus 2 (2019-nCoV) (SARS-CoV-2)")
    else:
        mydyn=CovidDynamics.objects.all()
        is_filtered=False
        error_msn="Isolate %s not found" % genome_id
        genome_id=False
    context=extract_table_info(request,mydyn)
    context["is_filtered"]=is_filtered
    context["variant_genome"]=genome_id
    context["error_msn"]=error_msn
    return render(request, 'covid19/index.html', context)


def index(request,prot_name=None,genome_id=None):
    pre_search=""
    if 'pre' in request.GET:
        pre_search = request.GET['pre']
    is_filtered=False
    if genome_id and not CovidIsolate.objects.filter(isolate_id=genome_id).exists():
        error_msn="Isolate %s not found" % genome_id
        genome_id=False
    if prot_name:
        mydyn=CovidDynamics.objects.filter(id_model__final_proteins__name=prot_name)
        if genome_id:
            mydyn=mydyn.filter(id_model__proteins__species="Severe acute respiratory syndrome coronavirus 2 (2019-nCoV) (SARS-CoV-2)")
        is_filtered=[prot_name]
    else:  
        mydyn=CovidDynamics.objects.all()
        is_filtered=False
    error_msn=""
    context=extract_table_info(request,mydyn)
    context["is_filtered"]=is_filtered
    context["variant_genome"]=genome_id
    context["error_msn"]=error_msn
    context["pre_search"]=pre_search
    return render(request, 'covid19/index.html', context)

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




def recursive_prepare_json_dump(myvar):
    if type(myvar)==dict:
        for k,v in myvar.items():
            myvar[k]=recursive_prepare_json_dump(v)
    elif type(myvar)==set:
        myvar= list(myvar)
    return myvar


def load_mutfunc_mutationeffect_data(mutfunc_o):
    #mutfunc_o=CovidMutfuncData.objects.filter(id_final_protein__name=protein)
    mutfunc_o=mutfunc_o.annotate(int_uniprot=F("covidmutfuncdatainterface__int_uniprot"))
    mutfunc_o=mutfunc_o.annotate(interaction_energy=F("covidmutfuncdatainterface__interaction_energy"))
    mutfunc_o=mutfunc_o.annotate(diff_interface_residues=F("covidmutfuncdatainterface__diff_interface_residues"))
    mutfunc_o=mutfunc_o.annotate(int_name=F("covidmutfuncdatainterface__int_name"))
    mutfunc_o=mutfunc_o.annotate(int_template=F("covidmutfuncdatainterface__int_template"))
    mutfunc_o=mutfunc_o.annotate(diff_interaction_energy=F("covidmutfuncdatainterface__diff_interaction_energy"))
    mutfunc_o=mutfunc_o.annotate(finprot_name=F("id_final_protein_id__name"))
    mutfunc_values=mutfunc_o.values()
    #sort mutfunc data in a dictionary
    mutfunc_data={}
    for mutfunc in mutfunc_values:
        protname=mutfunc["finprot_name"]
        if protname not in mutfunc_data:
            mutfunc_data[protname]={}
        position=mutfunc["position"]
        if position not in mutfunc_data[protname]:
            mutfunc_data[protname][position]={}
        varname="%s%s%s"%(mutfunc["wt"],position,mutfunc["mut"])
        if varname not in mutfunc_data[protname][position]:
            mutfunc_data[protname][position][varname]={}
            for k in ["freqpermille", "ptm", "sift_score", "sift_median", "relative_surface_accessibility", "foldx_ddg", "mut_escape_mean", "mut_escape_max", "annotation", "template"]:
                mutfunc_data[protname][position][varname][k]=mutfunc[k]
            mutfunc_data[protname][position][varname]["interface"]=[]
        has_interface_data=False
        int_d={}
        for k in ["int_uniprot" , "interaction_energy" , "diff_interface_residues" , "int_name" , "int_template" , "diff_interaction_energy" ]:
            if mutfunc[k]:
                has_interface_data=True
            int_d[k]=mutfunc[k]
        if has_interface_data:
            mutfunc_data[protname][position][varname]["interface"].append(int_d)

    return mutfunc_data





def get_variant_impact_parameters():
    mutant_effect_params=[
        (
            "Substitution scores",
            [
                {"name": "BLOSUM90 score", "ref":"variant_blosum90", "is_mutfunc":False, "include_in_score":True},
                {"name": "&Delta; charge","ref": "variant_charge", "is_mutfunc":False, "include_in_score":True},        
                {"name": "Epstein's coefficient of difference","ref": "variant_epstein", "is_mutfunc":False, "include_in_score":True, "details":"Based on the differences in polarity and size between replaced pairs of amino acids (<a target='_blank' href='doi.org/10.1038/215355a0'>Epstein, 1967</a>)."},        
                {"name": "Experimental exchangeability","ref": "variant_exex", "is_mutfunc":False, "include_in_score":True , "details":"Measure of the mean effect of exchanging one amino acid into a different amino acid (<a  target='_blank' href='doi.org/10.1534/genetics.104.039107'>Yampolsky and Stoltzfus, 2005</a>)."},
                {"name": "Grantham's distance","ref": "variant_grantham", "is_mutfunc":False, "include_in_score":True, "details":"Grantham's distance depends on three  properties: composition, polarity and molecular volume (<a target='_blank' href='doi.org/10.1126/science.185.4154.862'>Grantham, 1974</a>)."},        
                {"name": "Miyata's distance","ref": "variant_miyata", "is_mutfunc":False, "include_in_score":True, "details":"Miyata's distance is based on 2 physicochemical properties: volume and polarity (<a target='_blank' href='doi.org/10.1007/BF01732340'>Miyata et al., 1979</a>)."},        
                {"name": "Sneath's index","ref": "variant_sneath", "is_mutfunc":False, "include_in_score":True, "details":"Sneath's index takes into account 134 categories of activity and structure. Dissimilarity index D is a percentage value of the sum of all properties not shared between two replaced amino acids (<a target='_blank' href='doi.org/10.1016/0022-5193(66)90112-3'>Sneath et al., 1966</a>)."},                        
                {"name": "&Delta; hydrophobicity","ref": "variant_dhydro", "is_mutfunc":False, "include_in_score":True, 
                    "multiple_options": [('Kyte Doolittle scale', 'variant_hp_kyte_doolittle'),
                                         ('Kyte Doolittle 2 scale', 'variant_hp_kyte_doolittle_2'),
                                         ('Eisenberg Weiss scale', 'variant_hp_eisenberg_weiss'),
                                         ('Engelman scale', 'variant_hp_engleman'),
                                         ('Hessa scale', 'variant_hp_hessa'),
                                         ('Hopp Woods scale', 'variant_hp_hoop_woods'),
                                         ('Janin scale', 'variant_hp_janin'),
                                         ('Moon Fleming scale', 'variant_hp_moon_fleming'),
                                         ('Wimley White scale', 'variant_hp_wimley_white'),
                                         ('Zhao London scale', 'variant_hp_zhao_london')]

                },
            ]
        ),
        #Mutfunc Conservation
        (
            "Conservation",
            [
                {"name": "Frequency (&permil;)",
                    "ref": "variant_mutfunc_freqpermille", 
                    "is_mutfunc":True, 
                    "relevant_values":[
                        {
                            "threshold": 10, 
                            "threshold_type": ">", 
                            "text": "The variant has been observed in > 1% of samples taken since the start of the pandemic.", 
                        }
                    ],
                    "include_in_score":True,
                    "details":"Overall frequency a variant has been observed since the start of the pandemic, across a large library of samples. It does not reflect current global or regional prevalence. Data from <a href='http://sars.mutfunc.com' target='_blank'>Mutfunc: SARS-CoV-2</a>."},
                {"name": "SIFT4G Score",
                    "ref": "variant_mutfunc_sift_score", 
                    "is_mutfunc":True, 
                    "relevant_values":[ {
                            "threshold": 0.05, 
                            "threshold_type": "<", 
                            "text": "Scores <0.05 are considered deleterious."
                        }
                    ],
                    "include_in_score":True,
                    "details":"Score generated by SIFT4G. Scores <0.05 are considered deleterious. Data from <a href='http://sars.mutfunc.com' target='_blank'>Mutfunc: SARS-CoV-2</a>."},
                {"name": "SIFT4G Median IC",
                    "ref": "variant_mutfunc_sift_median", 
                    "is_mutfunc":True, 
                    "relevant_values":[{
                        "threshold": 3.25, 
                        "threshold_type": "<=", 
                        "text": "Median IC > 3.25 indicate a potentially suboptimal alignment."
                    }],
                    "include_in_score":True,
                    "details":"Describes the reliability of SIFT4G scores. Median IC scores are ideally between 2.75 and 3.5. Scores >3.25 and especially >3.5 indicate potentially poor alignment quality.  Data from <a href='http://sars.mutfunc.com' target='_blank'>Mutfunc: SARS-CoV-2</a>."},

            ]
        ),
        #Structure
        (
            "Structure",
             [
                {"name": "Post-translational modification",
                    "ref": "variant_mutfunc_ptm", 
                    "is_mutfunc":True, 
                    "relevant_values":None,
                    "include_in_score":True,
                    "details":"Data from <a href='http://sars.mutfunc.com' target='_blank'>Mutfunc: SARS-CoV-2</a>."},
                {"name": "Surface accessibility",
                    "ref": "variant_mutfunc_relative_surface_accessibility", 
                    "is_mutfunc":True, 
                    "relevant_values":None,
                    "include_in_score":True,
                    "mod_tooltip":True,
                    "details":"Data from <a href='http://sars.mutfunc.com' target='_blank'>Mutfunc: SARS-CoV-2</a>. Template: <span class='variant_mutfunc_template'></span>"},
                {"name": "FoldX &Delta;&Delta;G",
                    "ref": "variant_mutfunc_foldx_ddg", 
                    "is_mutfunc":True, 
                    "relevant_values":[
                        {
                        "threshold": 1, 
                        "threshold_type": ">", 
                        "text": "Value > 1 indicate the variant destabilises the protein."
                        },
                        {
                        "threshold": -1, 
                        "threshold_type": "<", 
                        "text": "Value < -1 indicate the variant stabilises the protein."
                        },
                    ],
                    "include_in_score":True,
                    "mod_tooltip":True,
                    "details":"Predicted change in the protein's folding Gibbs Free Energy change caused by this mutation. Values greater than 1 are considered significantly destabilising and those less than -1 stabilising. Data from <a href='http://sars.mutfunc.com' target='_blank'>Mutfunc: SARS-CoV-2</a>. Template: <span class='variant_mutfunc_template'></span>"},
            ]
        ),
        #Experimental Antibody escape
        (
            "Experimental",
            [
                {"name": "Mean Experimental Antibody Escape",
                    "ref": "variant_mutfunc_mut_escape_mean", 
                    "is_mutfunc":True, 
                    "relevant_values":[
                        {
                        "threshold": 0.05, 
                        "threshold_type": ">", 
                        "text": "Mean proportion > 0.05."
                        },
                    ],
                    "include_in_score":True,
                    "details":"Mean escape proportion accross a mix of antibodies, calculated from Greaney et al. (2020). Data from <a href='http://sars.mutfunc.com' target='_blank'>Mutfunc: SARS-CoV-2</a>."},
                {"name": "Max. Experimental Antibody Escape",
                    "ref": "variant_mutfunc_mut_escape_max", 
                    "is_mutfunc":True, 
                    "relevant_values":[
                        {
                        "threshold": 0.2, 
                        "threshold_type": ">", 
                        "text": "Max. proportion > 0.2."
                        },
                    ],
                    "include_in_score":True,
                    "details":"Maximum escape proportion accross a mix of antibodies, calculated from Greaney et al. (2020). Data from <a href='http://sars.mutfunc.com' target='_blank'>Mutfunc: SARS-CoV-2</a>."},
            ]
        ),
        (
            "Others",[
                {"name": "Annotation",
                    "ref": "variant_mutfunc_annotation", 
                    "is_mutfunc":True, 
                    "relevant_values":None,
                    "include_in_score":False,
                    "details":"Data from <a href='http://sars.mutfunc.com' target='_blank'>Mutfunc: SARS-CoV-2</a>."},
            ]
        )
    ]


    time_dep_params=[
        {"name": "RMSD", "ref":"analysis_mut_rmsd"},
        {"name": "RMSF", "ref":"analysis_mut_rmsf"},
        {"name": "SASA", "ref":"analysis_mut_sasa"},
        {"name": "CHI1", "ref":"analysis_mut_chi1"},
        #{"name": "Contact number", "ref":"analysis_contnum"}
        {"name":"All contacts", "ref":"analysis_mut_contact_all" , "short_name": "contact_all", "is_contact":True},
        {"name":"Hydrogen bond contacts", "ref":"analysis_mut_contact_hb" , "short_name": "contact_hb", "is_contact":True},
        {"name":"Salt bridge contacts", "ref":"analysis_mut_contact_sb" , "short_name": "contact_sb", "is_contact":True},
        {"name":"Hydrophobic contacts", "ref":"analysis_mut_contact_hp" , "short_name": "contact_hp", "is_contact":True},
        {"name":"Pi-cation contacts", "ref":"analysis_mut_contact_pc" , "short_name": "contact_pc", "is_contact":True},
        {"name":"Pi-stacking contacts", "ref":"analysis_mut_contact_ps" , "short_name": "contact_ps", "is_contact":True},
        {"name":"T-stacking contacts", "ref":"analysis_mut_contact_ts" , "short_name": "contact_ts", "is_contact":True},
        {"name":"Van der Waals contacts", "ref":"analysis_mut_contact_vdw" , "short_name": "contact_vdw", "is_contact":True},
        {"name":"Water bridge contacts", "ref":"analysis_mut_contact_wb" , "short_name": "contact_wb", "is_contact":True},
        {"name":"Extended water bridge contacts", "ref":"analysis_mut_contact_wb2" , "short_name": "contact_wb2", "is_contact":True},
    ]

    return mutant_effect_params,time_dep_params

def count_available_descriptors(descript_obj,description_type):
    if description_type=="mutant_effect":
        me_c=0
        for section,opt_li in descript_obj:
            for opt in opt_li:
                if opt["include_in_score"]:
                    me_c+=1
    else:
        me_c=len(descript_obj)*2
    return me_c

def param_long_to_short(param_long):
    param_long_to_short_d={
         'BLOSUM90' : 'blosum90',
        '|d hydrophobicity| (Kyte Doolittle score)' : 'hp_kyte_doolittle',
        'd hydrophobicity (Kyte Doolittle)' : 'hp_kyte_doolittle',
        '|d charge|' : 'charge',
        'Frequency (mutfunc)' : 'mutfunc_freqpermille',
        'd charge' : 'charge',
        'PTM (yes/no) (mutfunc)' : 'mutfunc_ptm',
        'SIFT4G Score (mutfunc)' : 'mutfunc_sift_score',
        'SIFT4G Median IC (mutfunc)' : 'mutfunc_sift_median',
        'Surface accessibility (mutfunc)' : 'mutfunc_relative_surface_accessibility',
        'FoldX ddG (mutfunc)' : 'mutfunc_foldx_ddg',
        'Mean Experimental Antibody Escape (mutfunc)' : 'mutfunc_mut_escape_mean',
        'Max. Experimental Antibody Escape (mutfunc)' : 'mutfunc_mut_escape_max',
        'RMSD average (Time-dependent)' : 'rmsd_average',
        'RMSD SD (Time-dependent)' : 'rmsd_sd',
        'RMSF average (Time-dependent)' : 'rmsf_average',
        'RMSF SD (Time-dependent)' : 'rmsf_sd',
        'SASA average (Time-dependent)' : 'sasa_average',
        'SASA SD (Time-dependent)' : 'sasa_sd',
        'Chi1 average (Time-dependent)' : 'chi1_average',
        'Chi1 SD (Time-dependent)' : 'chi1_sd',
        'contact_hb average (Time-dependent)' : 'contact_hb_average',
        'contact_hb SD (Time-dependent)' : 'contact_hb_sd',
        'contact_sb average (Time-dependent)' : 'contact_sb_average',
        'contact_sb SD (Time-dependent)' : 'contact_sb_sd',
        'contact_pc average (Time-dependent)' : 'contact_pc_average',
        'contact_pc SD (Time-dependent)' : 'contact_pc_sd',
        'contact_ps average (Time-dependent)' : 'contact_ps_average',
        'contact_ps SD (Time-dependent)' : 'contact_ps_sd',
        'contact_ts average (Time-dependent)' : 'contact_ts_average',
        'contact_ts SD (Time-dependent)' : 'contact_ts_sd',
        'contact_vdw average (Time-dependent)' : 'contact_vdw_average',
        'contact_vdw SD (Time-dependent)' : 'contact_vdw_sd'    ,
        "Contacts H bond average (Time-dependent)" :"contact_hb_average", 
        "Contacts H bond SD (Time-dependent)" : "contact_hb_sd", 
        "Contacts salt bridge average (Time-dependent)" : "contact_sb_average", 
        "Contacts salt bridge SD (Time-dependent)":"contact_sb_sd", 
        "Contacts hydrophobic average (Time-dependent)":"contact_hp_average", 
        "Contacts hydrophobic SD (Time-dependent)":"contact_sd", 
        "Contacts pi-stacking average (Time-dependent)":"contact_ps_average", 
        "Contacts pi-stacking SD (Time-dependent)":"contact_ps_sd", 
        "Contacts T-stacking average (Time-dependent)":"contact_ts_average", 
        "Contacts T-stacking SD (Time-dependent)":"contact_ts_sd", 
        "Contacts Van der Waals average (Time-dependent)":"contact_vdw_average", 
        "Contacts Van der Waals SD (Time-dependent)":"contact_vdw_sd",
        "Contacts water bridge average (Time-dependent)":"contact_wb_average", 
        "Contacts water bridge SD (Time-dependent)":"contact_wb_sd", 
        "Contacts extended water bridge average (Time-dependent)":"contact_wb2_average", 
        "Contacts extended water bridge SD (Time-dependent)":"contact_wb2_sd"
    }
    param_long=param_long.strip("`")
    return param_long_to_short_d.get(param_long,None)


def get_variant_impact_param_weights_fitted_ab_escape(filename):
    weights_path_pre=settings.MEDIA_ROOT + "Precomputed/covid19/variant_impact/param_weights/"
    weights_path=os.path.join(weights_path_pre,filename)
    params_d=None
    if os.path.isfile(weights_path):
        params_d={}
        df=pd.read_csv(weights_path,index_col=0)
        for index,row in df.iterrows():
            short_nm=param_long_to_short(index)
            if short_nm:
                #params_d[short_nm]=row["Estimate"]
                params_d[short_nm]=row["s1"]
    return params_d

def get_variant_impact_param_weights(has_spike):
    predef_weights=[]
    if has_spike:
        coefs_li=[
                {"filename":"param_weights_escape.csv",
                 "name":"Fitted to Ab. escape",
                 "description":"Weights fitted to data of antibody escape variants (<a target='_blank' href='doi.org/10.1016/j.chom.2020.11.007'>Greaney et al., 2020</a>)."
                },
                {"filename":"param_weights_binding.csv",
                 "name":"Fitted to binding",
                 "description":"Weights fitted to data of change in binding affinity between SARS-CoV-2’s Spike receptor-binding domain (RBD) and the ACE2 receptor (<a target='_blank' href='doi.org/10.1016/j.cell.2020.08.012'>Starr et al., 2020</a>)."
                },
                {"filename":"param_weights_expression.csv",
                 "name":"Fitted to expression",
                 "description":"Weights fitted to data of change in expression of the RBD on yeast cells (<a target='_blank' href='doi.org/10.1016/j.cell.2020.08.012'>Starr et al., 2020</a>)."
                }
            ]
        for coefs in coefs_li:
            params_abesc=get_variant_impact_param_weights_fitted_ab_escape(coefs["filename"])
            if params_abesc:
                params_abesc_d={"name":coefs["name"], "weights":json.dumps(params_abesc), "description":coefs["description"]}
                predef_weights.append(params_abesc_d)
    #rmsf_param_weights=[('rmsf_average', 1), ('rmsf_sd', 1), ('contact_hb_average', 1), ('contact_hb_sd', 1), ('contact_sb_average', 1), ('contact_sb_sd', 1), ('contact_pc_average', 1), ('contact_pc_sd', 1), ('contact_ps_average', 1), ('contact_ps_sd', 1), ('contact_ts_average', 1), ('contact_ts_sd', 1), ('contact_vdw_average', 1), ('contact_vdw_sd', 1),]
    params_rmsf_contacts={'rmsf_average': 1, 'rmsf_sd': 1, 'contact_hb_average': 1, 'contact_hb_sd': 1, 'contact_sb_average': 1, 'contact_sb_sd': 1, 'contact_pc_average': 1, 'contact_pc_sd': 1, 'contact_ps_average': 1, 'contact_ps_sd': 1, 'contact_ts_average': 1, 'contact_ts_sd': 1, 'contact_vdw_average': 1, 'contact_vdw_sd': 1,}
    params_rmsf_contacts_d={"name":"RMSF & contacts", "weights":json.dumps(params_rmsf_contacts)}
    predef_weights.append(params_rmsf_contacts_d)
    return predef_weights

def extract_report_data(dyn_id):
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
    

    mydynvalues=mydyn.values("file_id", "file_type", "file_url", "framenum", "uniprotkbac", "uniprot_entry", "species", "pdbid", "model_source", "finalprot", "is_ligand", "is_membrane", "molecule_name", "ligand_type", "author_first_name", "author_last_name", "author_institution","citation","doi","dyn_name","delta", "timestep", "atom_num", "software", "sversion", "ff", "ffversion", "description", "extracted_from_db" , "extracted_from_db_entry","solvent_type","solvent_is_filtered","creation_timestamp")
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
        dyndata["doi"]=dbdata["doi"]
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
        solvent_types_d={sid:val for sid,val in CovidDynamics.solvent_types}
        solvent_type=solvent_types_d[dbdata["solvent_type"]]
        dyndata["solvent_type"]= a=solvent_type if solvent_type!="Unknown" else None
        dyndata["solvent_is_filtered"]=dbdata["solvent_is_filtered"]        
        creation_time_obj=dbdata["creation_timestamp"]
        if creation_time_obj:
            dyndata["submission_date"]=creation_time_obj.strftime("%B %d, %Y")

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

    return dyndata


def add_if_exists(dbdata,dyndata,myvar):
    if dbdata[myvar]:
        dyndata[myvar]=dbdata[myvar]
    return dyndata

def obtain_sel_from_chain_ressegments(chainres_d):
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

def detect_consecutive_res_segments(posli):
    seg_li=[]
    seg_from=posli[0]
    seg_to=posli[0]
    pre_pos=posli[0]
    for pos in posli:
        if pos >pre_pos+1:
            seg_li.append([seg_from,pre_pos])
            seg_from=pos
        pre_pos=pos
    seg_li.append([seg_from,pre_pos])
    return seg_li



def nglsel_from_chainsandpos(chainpos):
    chain_seg_d={}
    for chain,posli in chainpos.items():
        posli=sorted(list(set(posli)))
        pos_segments=detect_consecutive_res_segments(posli)
        chain_seg_d[chain]={}
        chain_seg_d[chain]["seg_li"]=pos_segments
    mysel=obtain_sel_from_chain_ressegments(chain_seg_d)
    return mysel



def get_time():
    mytime=datetime.datetime.today()
    myhour=mytime.hour
    mymin=mytime.minute
    return (myhour,mymin)


def get_mut_data(found_mut,prot_to_finalprot,upseq_to_model):
    """
    Takes a dictionary from iterating queryobject.values() and creates a dictionary with info on the mutation
    """
    prot_name=found_mut["prot_name"]        
    thismut_d={}
    resid_fp=found_mut["resid"]

    pos_from_up=prot_to_finalprot[prot_name]["finalprot_seq_start"]
    resid_up=resid_fp+(pos_from_up-1)
    thismut_d["resid_up"]=resid_up
    mut_model_pos=upseq_to_model.get(resid_up,None)

    mut_name="%s%s%s"%(found_mut["resletter_from"],resid_fp,found_mut["resletter_to"])
    thismut_d["mut_name"]=mut_name
    thismut_d["resid_finprot"]=resid_fp
    thismut_d["resletter_to"]=found_mut["resletter_to"]
    thismut_d["resletter_from"]=found_mut["resletter_from"]
    if mut_model_pos:
        thismut_d["model_sel"]="%s:%s"%(mut_model_pos["seqpos"],mut_model_pos["chain"])
    else:
        thismut_d["model_sel"]=False
    return thismut_d


def get_mutations_in_isolate(sel_genome_id,included_prots,prot_to_finalprot,upseq_to_model):
    """
    mutations in the selected isolate (for the viewer)
    """
    mut_in_sel_isolate={}
    some_mut_in_struc=False
    if sel_genome_id:
#        found_muts=CovidMutatedPos.objects.filter(id_sequence__covidsequencedgene__id_isolate__isolate_id=sel_genome_id)

        if type(sel_genome_id)== list:
            found_muts=CovidMutatedPos.objects.filter(covidsequence__covidsequencedgene__id_isolate__isolate_id__in=sel_genome_id)

        else:
            found_muts=CovidMutatedPos.objects.filter(covidsequence__covidsequencedgene__id_isolate__isolate_id=sel_genome_id)
#        found_muts=found_muts.annotate(prot_name=F("id_sequence__covidsequencedgene__id_final_protein__name")).filter(prot_name__in=included_prots).distinct()
        found_muts=found_muts.annotate(prot_name=F("id_final_protein__name")).filter(prot_name__in=included_prots).distinct()
        found_muts_vals=found_muts.values("resid","resletter_from","resletter_to","prot_name")



        for found_mut in found_muts_vals:
            prot_name=found_mut["prot_name"]
            thismut_d=get_mut_data(found_mut,prot_to_finalprot,upseq_to_model)
            if prot_name not in mut_in_sel_isolate:
                mut_in_sel_isolate[prot_name]={}
            mut_resid_finprot=thismut_d["resid_finprot"]
            if mut_resid_finprot not in mut_in_sel_isolate[prot_name]:
                mut_in_sel_isolate[prot_name][mut_resid_finprot]={}
            mut_name=thismut_d["mut_name"]
            mut_in_sel_isolate[prot_name][mut_resid_finprot][mut_name]=thismut_d
            if thismut_d["model_sel"]:
               some_mut_in_struc=True 
    return mut_in_sel_isolate,some_mut_in_struc

def load_mutated_isolates_in_finalprot(finprot):
    finp_iso_path=settings.MEDIA_ROOT + "Precomputed/covid19/finprot_to_isolates"
    isolates_in_prot=set()
    finprot_nm=finprot.lower().replace(" ","_")
    finp_iso_file=os.path.join(finp_iso_path,"%s.data"%finprot_nm)
    if os.path.isfile(finp_iso_file):
        with open(finp_iso_file,"rb") as fh:
            isolates_in_prot=pickle.load(fh)
    else:
        print("Precomp. file with isolates in %s not found. Extracting from db (slower option)" % finprot)
        iter_iso=CovidIsolate.objects.filter(covidsequencedgene__id_final_protein__name=finprot).values_list("isolate_id",flat=True).iterator()
        isolates_in_prot=set()
        for iso in iter_iso:
            isolates_in_prot.add(iso)

    return (isolates_in_prot)



#def save_isolates_in_prots_session(request,dyn_id,included_prots):
#    if request.session.get('isolates_in_seq', False):
#        session_isolates=request.session["isolates_in_seq"]
#        print("\n\n")
#        print(session_isolates.keys())
#        print("\n\n")
#    else:
#        session_isolates={}
#    if dyn_id in session_isolates:
#        sess_isolates_in_seq=session_isolates[dyn_id]
#    else:
#        sess_isolates_in_seq=load_mutated_isolates_in_finalprot(included_prots)
#
#        session_isolates[dyn_id]= sess_isolates_in_seq
#        request.session['isolates_in_seq']=session_isolates
#    return sess_isolates_in_seq

def save_isolates_in_prots_session(request,included_prots):
    if request.session.get('isolates_in_seq', False):
        session_isolates=request.session["isolates_in_seq"]
    else:
        session_isolates={}
    example_iso=""
    for fin_prot in included_prots:
        if fin_prot in session_isolates:
            sess_isolates_in_seq=session_isolates[fin_prot]
        else:
            sess_isolates_in_seq=load_mutated_isolates_in_finalprot(fin_prot)
        session_isolates[fin_prot]= sess_isolates_in_seq
        request.session['isolates_in_seq']=session_isolates

        for e in sess_isolates_in_seq:#just to collect 1 example
            example_iso=e
            break
    return example_iso  


def search_isolate_autocomp(request):
    q=request.GET.get('search', '').upper()
    #dyn_id=str(request.GET.get('dyn_id'))
    prots_s=str(request.GET.get('prots'))
    final_prots=prots_s.split(",")
    isolates_in_seq=set()
    if request.session.get('isolates_in_seq', False):
        session_isolates=request.session["isolates_in_seq"]
        for prot in final_prots:
            if prot in session_isolates:
                isolates_in_thisprot=session_isolates[prot]  
                if isolates_in_thisprot:
                    isolates_in_seq=isolates_in_seq.union(isolates_in_thisprot)
    isolates_in_seq.add("ALL")
    max_len=10
    added_n=0
    results=[]
    for e in isolates_in_seq:
        if e.startswith(q):
            results.append(e)
            added_n+=1
        if added_n>max_len:
            break
    return results


def ajax_autocomp_isolates(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        results=search_isolate_autocomp(request)
        return HttpResponse(json.dumps(results), 'application/json')

def dynanalysis(request,dyn_id,sel_genome_id=None,variantimpact_def=False):
    request.session.set_expiry(0) 
    context={}

    # TO ADD: 
        #light sel and heavy sel
    #####

    context["mdsrv_url"]=obtain_domain_url(request)
    if "8000" in context["mdsrv_url"]:
        context["mdsrv_url"]=context["mdsrv_url"].replace("8000","8081")(request)

    if request.session.get('warning_load', False):
        warning_load=request.session["warning_load"]
    else:
        warning_load={"trajload":True,"heavy":True}
    context["warning_load"]=json.dumps(warning_load)
    context["variantimpact_def"]=variantimpact_def


    dyndata_report=extract_report_data(dyn_id)

    d=CovidDynamics.objects.select_related("id_model__pdbid","id_model__source").prefetch_related("covidfilesdynamics_set__id_files__id_file_types","coviddynamicscomponents_set","id_model__covidmodelprotein_set__id_protein__coviduniprotseqpositions_set","id_model__final_proteins").get(id=dyn_id,is_published=True)
    context["dyn_id"]=dyn_id
    delta=dyndata_report["delta"]
    if not delta:
        dyndata_report["delta"]=0.2
    context["dyndata_report"]=dyndata_report

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
            filedata["path"]=fileobj.filepath.replace(settings.MEDIA_ROOT,"")
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
            filedata["path"]=fileobj.filepath.replace(settings.MEDIA_ROOT,"")
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
    context["included_prots"]=json.dumps(list(included_prots))
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
    finp_sel={}
    for m in model_pos_obj:
        up_pos_obj=m.id_uniprotpos
        up_pos=up_pos_obj.seqpos
        up_aa=up_pos_obj.aa
        model_details={"seqpos":m.seqpos,"aa":m.aa,"chain":m.chainid,"aa_uniprot":up_aa}
        upseq_to_model[up_pos]=model_details
        pos_in_covid_finprot=False
        for interval,protname in seq_intervals_finalprot.items():
            if up_pos >=interval[0] and up_pos <=interval[1]:
                pos_in_covid_finprot=protname
                if protname not in finpseq_to_model:
                    finpseq_to_model[protname]={}
                fp_pos=(up_pos - interval[0]) +1
                finpseq_to_model[protname][fp_pos]=model_details
        #Obtain all chains and resids of each final protein
        if pos_in_covid_finprot:
            pos_protname=pos_in_covid_finprot
        else:
            pos_protname="Others"
        if pos_protname not in finp_sel:
            finp_sel[pos_protname]={}
        if model_details["chain"] not in finp_sel[pos_protname]:
            finp_sel[pos_protname][model_details["chain"]]=[]
        finp_sel[pos_protname][model_details["chain"]].append(model_details["seqpos"])
    #Obtain selection for each final protein:
    #[!] Not used at the moment 
    for finprotname,chainpos in finp_sel.items():
        nglsel=nglsel_from_chainsandpos(chainpos) 





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
            res_sel_fin=obtain_sel_from_chain_ressegments(chainres_d)
            mydom["selection"]=res_sel_fin
        alldominfo[domname]=sorted(domtype,key=lambda x:x["note"])
    context["domains"]=alldominfo

    # Extract variants in the protein(s). If selected isolate, make a list of variants in it
    context["selected_var_data"]=False
    context["variant_genome"]=sel_genome_id

########################

#   mut_in_sel_isolate - mutations in the selected isolate (for the viewer)
#   isolates_in_seq - set of all isolates involving the modeled part of this protein
#   finpseq_to_model - for each finprot. residue, data of mutations involved
#       all_isolates contains the list of isolates involving each position
#           I would instead generate a dict of isolates to involved pos


    (mut_in_sel_isolate,some_mut_in_struc)=get_mutations_in_isolate(sel_genome_id,included_prots,prot_to_finalprot,upseq_to_model)
    context["some_mut_in_struc"]=some_mut_in_struc
    example_iso=save_isolates_in_prots_session(request,included_prots)
    context["isolates_in_seq_placeholder"]=example_iso

#        test_gupdate=True
#        if test_gupdate:
#            isolates_in_seq=['EPI_ISL_1097311', 'EPI_ISL_1109968', 'EPI_ISL_1210530', 'EPI_ISL_1210531', 'EPI_ISL_1210532', 'EPI_ISL_1210533', 'EPI_ISL_1210534', 'EPI_ISL_1210536', 'EPI_ISL_1210537', 'EPI_ISL_1210538']#[!]
#
#        else:
#            isolates_in_seq=CovidIsolate.objects.filter(covidsequencedgene__id_final_protein__name__in=included_prots).distinct().values_list("isolate_id",flat=True)
#        context["isolates_in_seq"]=isolates_in_seq



#found_muts=CovidMutatedPos.objects.filter(id_sequence__covidsequencedgene__id_final_protein__name__in=included_prots).distinct()
#for mut in found_muts:
#    mut_seq_gene_li=mut.id_sequence.covidsequencedgene_set.all()
#    mut_isolates=CovidIsolate.objects.filter(covidsequencedgene__id_sequence=mut.id_sequence)
#    isolates_w_mut=[iso.isolate_id for iso in mut_isolates]

    ####

    ####

    found_muts=CovidMutatedPos.objects.annotate(prot_name=F("id_final_protein__name")).filter(prot_name__in=included_prots).distinct()
    #found_muts=CovidMutatedPos.objects.annotate(prot_name=F("id_sequence__covidsequencedgene__id_final_protein__name")).filter(prot_name__in=included_prots).distinct()
    #found_muts=found_muts.annotate(isolate_id=F("id_sequence__covidsequencedgene__id_isolate__isolate_id"))#[!]
    #found_muts=found_muts[:500]
    found_muts_vals=found_muts.values("resid","resletter_from","resletter_to","prot_name")# isolate_id #[!]

    #mut_in_seq={}
    muts_in_model=False
    for found_mut in found_muts_vals:
        #isolate_id=found_mut["isolate_id"]#[!]

        thismut_d=get_mut_data(found_mut,prot_to_finalprot,upseq_to_model)
        if thismut_d["model_sel"]: #if mutation is in the model
            muts_in_model=True
            prot_name=found_mut["prot_name"]
            resid_fp=thismut_d["resid_finprot"]
            resid_up=thismut_d["resid_up"]
            thisres_data=finpseq_to_model[prot_name][resid_fp]
            if "pos_variants" not in thisres_data:
                thisres_data["pos_variants"]={}
            mut_name=thismut_d["mut_name"]
            if mut_name not in thisres_data["pos_variants"]:
                thisres_data["pos_variants"][mut_name]=thismut_d
                wt_aa=upseq_to_model[resid_up]["aa_uniprot"]
                pdb_aa=thisres_data["aa"]
                if wt_aa != pdb_aa:
                    thisres_data["wt_aa"]=wt_aa
            #if "all_isolates" not in thisres_data:
            #    thisres_data["all_isolates"]=set()
            #thisres_data["all_isolates"].add(isolate_id) #[!]

            found_mut["resid"]

    mut_in_sel_isolate_mutpos={}
    for prot,posvar_d in mut_in_sel_isolate.items():
        mut_in_sel_isolate_mutpos[prot]=list(posvar_d.keys())
    
    context["selected_var_data"]=mut_in_sel_isolate
    context["selected_var_positions"]=mut_in_sel_isolate_mutpos


    context["muts_in_model"]=muts_in_model
    context["finpseq_to_model"]=finpseq_to_model
    context["finpseq_to_model_json"]=json.dumps(recursive_prepare_json_dump( copy.deepcopy(finpseq_to_model)))
    #context["mut_in_seq"]=mut_in_seq
                


    #context["contact_types"]=[("contact_all","All contacts"), ("contact_hb","Hydrogen bond"), ("contact_sb","Salt bridge"), ("contact_hp","Hydrophobic"), ("contact_pc","Pi-cation"), ("contact_ps","Pi-stacking"), ("contact_ts","T-stacking"), ("contact_vdw","Van der Waals"), ("contact_wb","Water bridge"), ("contact_wb2","Extended water bridge")]
    
#    mut_impact_path=settings.MEDIA_ROOT + "Precomputed/covid19/variant_impact/mut_impact/dyn_%s.data" % dyn_id
#    if os.path.isfile(mut_impact_path):
#        with open(mut_impact_path,"rb") as fh:
#            mut_impact_d=pickle.load(fh)
        

    impact_per_variant_path_pre=settings.MEDIA_ROOT + "Precomputed/covid19/variant_impact/summary"
    impact_per_variant_all={}
    for mytraj in context["files"]["traj"]:
        traj_id =mytraj["id"]
        impact_per_variant_path=os.path.join(impact_per_variant_path_pre,"dyn_%s_traj_%s.data"%(dyn_id,traj_id))

        if os.path.isfile(impact_per_variant_path):
            with open(impact_per_variant_path,"rb") as fh:
                impact_per_variant_traj=pickle.load(fh)

            impact_per_variant_all[traj_id]=impact_per_variant_traj

    if impact_per_variant_all:

        # Mutfunc data
        #Extract from DB
        mutfunc_o=CovidMutfuncData.objects.filter(id_final_protein__name__in=included_prots)
        mutfunc_data=load_mutfunc_mutationeffect_data(mutfunc_o)
        #merge  mutfunc_data with our data on parameters per position
        for traj_id,mut_impact_data in impact_per_variant_all.items():
            for finprot,protdata in mut_impact_data.items():
                for protpos,posdata in protdata.items():
                    posvars=posdata["variants"]
                    for varname, vardict in posvars.items():
                        try:
                            vardict["mutfunc"]=mutfunc_data[finprot][protpos][varname]
                        except KeyError:
                            pass
                    
        context["impact_per_var"]=json.dumps(impact_per_variant_all)

    (mutant_effect_params,time_dep_params)=    get_variant_impact_parameters()


    context["mutant_effect_params"]=mutant_effect_params
    context["time_dep_params"]=time_dep_params
    context["count_mutant_effect_params"]=count_available_descriptors(mutant_effect_params,"mutant_effect")
    context["count_time_dep_params"]=count_available_descriptors(time_dep_params,"time_dep")

    #variant impact weights
    has_spike="Spike" in included_prots
    param_weights=get_variant_impact_param_weights(has_spike)
    context["variant_impact_param_weights"]=param_weights#json.dumps(param_weights)


    print("\n\nSend!\n\n")
    return render(request, 'covid19/dynanalysis.html', context)


def ajax_notshow_warn(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.POST:
        warning_type=request.POST.get("warning_type")
        if request.session.get('warning_load', False):
            warning_load=request.session["warning_load"]
        else:
            warning_load={"trajload":True,"heavy":True}
        warning_load[warning_type]=False;
        request.session['warning_load']=warning_load
        return HttpResponse(json.dumps(True), content_type='covid19/1')

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
            return HttpResponse(json.dumps(data_rmsd), content_type='covid19/'+dyn_id)   

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
            return HttpResponse(json.dumps(data_rmsf), content_type='covid19/'+dyn_id)   

def load_var_impact_data(filepath,position,is_pandas,analysis,stride=False,delta=False):
    if is_pandas:
        df=pd.read_csv(filepath,usecols=[str(position)])
        df.index.name = 'Frame'
        df.reset_index(inplace=True)
        if stride:
            num_frames=int(df.iloc[-1]["Frame"])
            stride_val=round(num_frames/5000)
            if stride_val:
                df=df.iloc[::stride_val, :]
        col1="Frame"
        if delta:
            df["Frame"]=df["Frame"].apply(lambda x:(x+1)*delta)
            col1="Time (ns)"
        myresult=df.values.tolist()
        values=df[str(position)].values
        myresult.insert(0,[col1,analysis]) 
    else:
        with open(filepath, 'rb') as filehandle:     
            myresult=pickle.load(filehandle)
#        myresult=[[float(a),float(b)] for (a,b) in myresult]
        myhead=["Atom",analysis]
        values=[e[1] for e in myresult]
        myresult.insert(0,myhead) 
    return (myresult,values)

def average(lst): 
    return sum(lst) / len(lst) 




def ajax_muts_in_isolate(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.POST:
        dyn_id= request.POST.get("dyn_id")
        sel_genome_id= request.POST.get("isolate")

        d=CovidDynamics.objects.get(id=dyn_id)
        #obtain included_prots
        included_prots={e.name for e in d.id_model.final_proteins.all()}
        #obtain prot_to_finalprot
        prot_to_finalprot_obj=CovidProteinFinalprotein.objects.annotate(prot_name=F("id_finalprotein__name")).filter(prot_name__in=included_prots,id_protein__in=d.id_model.proteins.all())
        prot_to_finalprot_obj_val=prot_to_finalprot_obj.values("finalprot_seq_start","finalprot_seq_end","prot_name")
        prot_to_finalprot={e["prot_name"]:e for e in prot_to_finalprot_obj_val}
        #obtain upseq_to_model
        model_pos_obj=CovidModelSeqPositions.objects.select_related("id_uniprotpos").filter(id_file__covidfilesdynamics__id_dynamics=dyn_id,id_file__covidfilesdynamics__type=0)
        upseq_to_model={}
        for m in model_pos_obj:
            up_pos=m.id_uniprotpos.seqpos
            model_details={"seqpos":m.seqpos,"aa":m.aa,"chain":m.chainid}
            upseq_to_model[up_pos]=model_details
        (mut_in_sel_isolate,some_mut_in_struc)=get_mutations_in_isolate(sel_genome_id,included_prots,prot_to_finalprot,upseq_to_model)


        data_var = {"result":mut_in_sel_isolate,"some_mut_in_struc":some_mut_in_struc}
        return HttpResponse(json.dumps(data_var), content_type='covid19/'+dyn_id)   

def ajax_variant_impact(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.POST:
        dyn_id= request.POST.get("dyn_id")
        traj_id= request.POST.get("traj_id")
        delta= float(request.POST.get("delta"))
        position= request.POST.get("position")

        var_input_res_path=settings.MEDIA_ROOT + "Precomputed/covid19/variant_impact/"

        var_result={}
        for myel in os.listdir(var_input_res_path):
            myelpath=os.path.join(var_input_res_path,myel)
            if os.path.isdir(myelpath):
                analysys_dyn_file=os.path.join(myelpath,"dyn_%s_traj_%s.csv"% (dyn_id,traj_id))
                if os.path.isfile(analysys_dyn_file):
                    try:
                        (myresult,values)=load_var_impact_data(analysys_dyn_file,position,True,myel,delta=delta)
                    except:
                        continue

                else:
                    analysys_dyn_file=os.path.join(myelpath,"dyn_%s_traj_%s_pos_%s_.data" % (dyn_id,traj_id,position))
                    if os.path.isfile(analysys_dyn_file):
                        (myresult,values)=load_var_impact_data(analysys_dyn_file,position,False,myel)
                    else:
                        continue
                var_result[myel]={}
                var_result[myel]["result"]=myresult
                var_result[myel]["average"]=average(values)
                var_result[myel]["sd"]=statistics.pstdev(values)                        

        data_var = {"result":var_result}

        return HttpResponse(json.dumps(data_var), content_type='covid19/'+dyn_id)   

def load_timedep_results(dyn_id,traj_id,position,td_param):
    #corrections
    var_input_res_path=settings.MEDIA_ROOT + "Precomputed/covid19/variant_impact/"
    delta=CovidDynamics.objects.get(id=dyn_id).delta
    myelpath=os.path.join(var_input_res_path,td_param)
    param_result=False
    if os.path.isdir(myelpath):
        analysys_dyn_file=os.path.join(myelpath,"dyn_%s_traj_%s.csv"% (dyn_id,traj_id))
        if os.path.isfile(analysys_dyn_file):
            (myresult,values)=load_var_impact_data(analysys_dyn_file,position,True,td_param,delta=delta)
            param_result=myresult

        else:
            analysys_dyn_file=os.path.join(myelpath,"dyn_%s_traj_%s_pos_%s_.data" % (dyn_id,traj_id,position))
            if os.path.isfile(analysys_dyn_file):
                (myresult,values)=load_var_impact_data(analysys_dyn_file,position,False,td_param)
                param_result=values
    return param_result


def load_precomp_mutationeffect_results(dyn_id,traj_id,protein=False,position=False,variant=False):
    impact_per_variant_path_pre=settings.MEDIA_ROOT + "Precomputed/covid19/variant_impact/summary"
    impact_per_variant_path=os.path.join(impact_per_variant_path_pre,"dyn_%s_traj_%s.data"%(dyn_id,traj_id))
    if os.path.isfile(impact_per_variant_path):
        with open(impact_per_variant_path,"rb") as fh:
            impact_per_variant_traj=pickle.load(fh)
        if protein:
            if position:
                if variant:
                    return impact_per_variant_traj[protein][position]["variants"][variant]
                else:
                    return impact_per_variant_traj[protein][position]
            else:
                return impact_per_variant_traj[protein]
        else:
            return impact_per_variant_traj

def obtain_varscores_traj(dyn_id,traj_id,position,variant,protein,parameters_me_li,parameters_td_li):    
    sum_dep_li=False
    sum_dep_extra=0 #for time-dependent params. that are not obtained per frame i.e. RMSF

    for td_param, weight in parameters_td_li:
        param_result=load_timedep_results(dyn_id,traj_id,position,td_param)
        if param_result:
            weight=float(weight)
            if td_param =="rmsf":
                sum_dep_extra+=average(param_result)*weight
            else:
                if sum_dep_li:
                    for pn, pointval in enumerate(sum_dep_li):
                        pointval_score=pointval[1]
                        if (type(pointval_score)==int or type(pointval_score)==float):
                            sum_dep_li[pn][1]=pointval_score+(param_result*weight)
                else:
                    sum_dep_li=[["Time (ns)","Score"]]
                    for pointval in param_result:
                        if (type( pointval[1])==int or type(pointval[1])==float):               
                            toadd=[pointval[0],(pointval[1]*weight)]
                            sum_dep_li.append(toadd)

        else:
            print("Error with %s" %td_param)

    precomp_me_res=load_precomp_mutationeffect_results(dyn_id,traj_id,protein,position,variant)
    mutfunc_o=CovidMutfuncData.objects.filter(id_final_protein__name=protein)
    mutfunc_data_all=load_mutfunc_mutationeffect_data(mutfunc_o)
    try:
        mutfunc_data=mutfunc_data_all[protein][position][variant]
    except KeyError:
        mutfunc_data={}

    sum_nodep=0
    for me_param, weight in parameters_me_li:
        weight=float(weight)
        if me_param in precomp_me_res:
            param_result=precomp_me_res[me_param]
        elif me_param in mutfunc_data:
            param_result=mutfunc_data[me_param]
        elif me_param=="ptm":
            if param_result:
                param_result=1
            else:
                param_result=0
        sum_nodep+=param_result*weight

    for pn,(pointval_time,pointval_score) in enumerate(sum_dep_li):
        if (type(pointval_score)==int or type(pointval_score)==float):
            fin_val=pointval_score + sum_dep_extra + sum_nodep
            sum_dep_li[pn]=[pointval_time,fin_val]
    return sum_dep_li

def format_param_description(parameters_li):
    parameters_li_f=["%s (weight=%s)"%(par,weight) for par,weight in parameters_li]
    return ", ".join(parameters_li_f)

def download_varscores_traj(request,dyn_id,traj_id,position,variant,protein,parameters_me,parameters_td):
    parameters_td_li=[e.split(";") for e in parameters_td.split(",")]
    parameters_me_li=[e.split(";") for e in parameters_td.split(",")]

    sum_dep_li=obtain_varscores_traj(dyn_id,traj_id,position,variant,protein,parameters_me_li,parameters_td_li)

    response = HttpResponse(content_type='text/csv')        
    response['Content-Disposition'] = 'attachment; filename="dyn_%s_traj_%s_pos_%s_%s.csv"' % (dyn_id,traj_id,position,variant)
    
    writer = csv.writer(response)
    writer.writerow(["#Dyn ID: "+dyn_id])
    writer.writerow(["#Traj ID: "+traj_id])
    writer.writerow(["#Protein: "+protein])
    writer.writerow(["#Position in the protein sequence: "+position])
    writer.writerow(["#Mutation effect parameters in the score and weight: "+format_param_description(parameters_td_li)])
    writer.writerow(["#Time-dependent parameters in the score and weight: "+format_param_description(parameters_me_li)])
    for e in sum_dep_li:
        writer.writerow(e)
    return response


def download_varimpact(request,dyn_id,traj_id,position,analysis):
    var_input_res_path=settings.MEDIA_ROOT + "Precomputed/covid19/variant_impact/%s/" % analysis
    if analysis=="rmsf":
        filename="dyn_%s_traj_%s_pos_%s_.data"%(dyn_id,traj_id,position)
        is_pandas=False
        delta=False
    else:
        filename="dyn_%s_traj_%s.csv" % (dyn_id,traj_id)
        is_pandas=True
        delta=CovidDynamics.objects.get(id=int(dyn_id)).delta

    filepath=os.path.join(var_input_res_path,filename)
    (results,values)=load_var_impact_data(filepath,position,is_pandas,analysis,delta)

    response = HttpResponse(content_type='text/csv')        
    response['Content-Disposition'] = 'attachment; filename="dyn_%s_traj_%s_pos_%s_%s.csv"' % (dyn_id,traj_id,position,analysis)
    
    writer = csv.writer(response)
    writer.writerow(["#Dyn ID: "+dyn_id])
    writer.writerow(["#Position in the protein sequence: "+position])
    writer.writerow(["#Analysis type: "+analysis])
    header=[]
    for name in results[0]:
        header.append("'"+name+"'")
    writer.writerow(header)
    for row in results[1:]:
        rowcol=[]
        for col in row:
            rowcol.append(col)
        writer.writerow(rowcol) 
 
    return response


def write_variantscore_data_values(writer,mut_impact_data,include_dyn_id,include_traj_id,ptm_binary):
    for prot,protdata in sorted(mut_impact_data.items(),key=lambda x:x[0]):
        for protpos,posdata in sorted(protdata.items(),key=lambda x:x[0]): 
            pos_timedep=posdata["time_dep"]
            pos_variants=posdata["variants"]
            for varname,vardata in sorted(pos_variants.items(),key=lambda x:x[0]):
                (x,wtaa,pos,mutaa,y)=re.split("(\w)(\d+)(\w)",varname)
                line=[prot,protpos,wtaa,mutaa]
                if include_traj_id:
                    line.insert(0,include_traj_id)
                if include_dyn_id:
                    line.insert(0,include_dyn_id)
                for param in ['variant_blosum90', 'variant_charge', 'variant_grantham', 'variant_miyata', 'variant_epstein', 'variant_exex', 'variant_sneath']:
                    line.append(vardata[param])
                for param in ['variant_hp_eisenberg_weiss', 'variant_hp_engleman', 'variant_hp_hessa', 'variant_hp_hoop_woods', 'variant_hp_janin', 'variant_hp_kyte_doolittle', 'variant_hp_kyte_doolittle_2', 'variant_hp_moon_fleming', 'variant_hp_wimley_white', 'variant_hp_zhao_london']:
                    line.append(vardata["hydrophobicity"][param])
                for param in ["freqpermille", "sift_score", "sift_median", "ptm", "relative_surface_accessibility", "foldx_ddg", "mut_escape_mean", "mut_escape_max", "annotation"]:
                    paramval=vardata["mutfunc"][param]
                    if ptm_binary and param=="ptm":
                        if paramval:
                            paramval=1
                        else:
                            paramval=0
                    line.append(paramval)
                for param in ["rmsd", "rmsf", "sasa", "chi1", "contact_all", "contact_hb", "contact_sb", "contact_hp", "contact_pc", "contact_ps", "contact_ts", "contact_vdw", "contact_wb", "contact_wb2"]:
                    if param in pos_timedep:
                        line.append(pos_timedep[param]["average"])
                        line.append(pos_timedep[param]["sd"])
                    else:
                        line.append("")
                        line.append("")
                writer.writerow(line)

def write_variantscore_data(writer,all_notes,mut_impact_data_all,include_dyn_id=False,include_traj_id=False,ptm_binary=False,multiple_traj=False):
    for note in all_notes:
        writer.writerow(note)
    header=["Protein","Position","WT","Mut","BLOSUM90", "d charge", "d Grantham", "d Miyata", "d Epstein", "d Exex", "d Sneath", "d hydrophobicity (Eisenberg Weiss)", "d hydrophobicity (Engleman)", "d hydrophobicity (Hessa)", "d hydrophobicity (Hoop Woods)", "d hydrophobicity (Janin)", "d hydrophobicity (Kyte Doolittle)", "d hydrophobicity (Kyte Doolittle 2)", "d hydrophobicity (Moon Fleming)", "d hydrophobicity (Wimley White)", "d hydrophobicity (Zhao London)","Frequency (per mille) (mutfunc)","SIFT4G Score (mutfunc)", "SIFT4G Median IC (mutfunc)", "PTM (mutfunc)", "Surface accessibility (mutfunc)", "FoldX ddG (mutfunc)", "Mean Experimental Antibody Escape (mutfunc)", "Max. Experimental Antibody Escape (mutfunc)", "Annotation (mutfunc)","RMSD average (Time-dependent)", "RMSD SD (Time-dependent)", "RMSF average (Time-dependent)", "RMSF SD (Time-dependent)", "SASA average (Time-dependent)", "SASA SD (Time-dependent)", "Chi1 average (Time-dependent)", "Chi1 SD (Time-dependent)", "All contacts average (Time-dependent)", "All contacts SD (Time-dependent)", "Contacts H bond average (Time-dependent)", "Contacts H bond SD (Time-dependent)", "Contacts salt bridge average (Time-dependent)", "Contacts salt bridge SD (Time-dependent)", "Contacts hydrophobic average (Time-dependent)", "Contacts hydrophobic SD (Time-dependent)", "contact_pc average (Time-dependent)", "contact_pc SD (Time-dependent)", "Contacts pi-stacking average (Time-dependent)", "Contacts pi-stacking SD (Time-dependent)", "Contacts T-stacking average (Time-dependent)", "Contacts T-stacking SD (Time-dependent)", "Contacts Van der Waals average (Time-dependent)", "Contacts Van der Waals SD (Time-dependent)", "Contacts water bridge average (Time-dependent)", "Contacts water bridge SD (Time-dependent)", "Contacts extended water bridge average (Time-dependent)", "Contacts extended water bridge SD (Time-dependent)"]
    if include_traj_id:
        header.insert(0,"Traj ID")
    if include_dyn_id:
        header.insert(0,"Dyn ID")
    if ptm_binary:
        header[header.index("PTM (mutfunc)")]="PTM (yes/no) (mutfunc)"
    writer.writerow(header)

    if multiple_traj:
        for traj_id, mut_impact_data in sorted(mut_impact_data_all.items(), key=lambda x:x[0]):
            if include_traj_id:
                include_traj_id=traj_id
            write_variantscore_data_values(writer,mut_impact_data,include_dyn_id,include_traj_id,ptm_binary)
    else:
        include_traj_id=False
        write_variantscore_data_values(writer,mut_impact_data_all,include_dyn_id,include_traj_id,ptm_binary)



def download_variantscores_all(request,dyn_id):
    dyn=CovidDynamics.objects.get(id=dyn_id)
    traj_ids=[tfd.id_files.id for tfd in dyn.covidfilesdynamics_set.filter(type=2)]

    mut_impact_data_all={}
    for traj_id in traj_ids:
        mut_impact_data=load_precomp_mutationeffect_results(dyn_id,traj_id)
        mutfunc_o=CovidMutfuncData.objects.filter(id_final_protein__covidmodel__coviddynamics__id=dyn_id)
        mutfunc_data=load_mutfunc_mutationeffect_data(mutfunc_o)

        #merge  mutfunc_data with our data on precomputed parameters 
        for finprot,protdata in mut_impact_data.items():
            for protpos,posdata in protdata.items():
                posvars=posdata["variants"]
                for varname, vardict in posvars.items():
                    try:
                        vardict["mutfunc"]=mutfunc_data[finprot][protpos][varname]
                    except KeyError:
                        pass
        mut_impact_data_all[traj_id]=mut_impact_data
   
    response = HttpResponse(content_type='text/csv')        
    response['Content-Disposition'] = 'attachment; filename="dyn_%s_variant_impact_scores.csv"' % (dyn_id)
    
    writer = csv.writer(response)

    all_notes=[
        ["#Time-dependent data is computed on the wild type, and this is not mutation-dependent."],
        ["#Time-dependent data is calculated for each trajectory frame. Here we provide the average value and the SD. RMSF is an exception: it is calculated for each residue atom, not frame, and here we provide average and SD of atom RMSF"],
        ["#Data labeled as 'mutfunc' is obtained from sars.mutfunc.com (Alistair Dunham, Gwendolyn M Jang, Monita Muralidharan, Danielle Swaney & Pedro Beltrao. 2021. A missense variant effect prediction and annotation resource for SARS-CoV-2. bioRxiv: 2021.02.24.432721 doi: https://doi.org/10.1101/2021.02.24.432721)"]
        ]
    write_variantscore_data(writer,all_notes,mut_impact_data_all,include_dyn_id=dyn_id,include_traj_id=True,multiple_traj=True)


    return response



def obtain_finpseq_to_model(dyn_id):
    modelfileobj=CovidFiles.objects.get(covidfilesdynamics__id_dynamics=dyn_id,covidfilesdynamics__type=0)
    model_pos_obj=CovidModelSeqPositions.objects.select_related("id_uniprotpos").filter(id_file=modelfileobj)

    d=CovidDynamics.objects.get(id=dyn_id)
    included_prots={e.name for e in d.id_model.final_proteins.all()}
    prot_to_finalprot_obj=CovidProteinFinalprotein.objects.annotate(prot_name=F("id_finalprotein__name")).filter(prot_name__in=included_prots,id_protein__in=d.id_model.proteins.all())
    prot_to_finalprot_obj_val=prot_to_finalprot_obj.values("finalprot_seq_start","finalprot_seq_end","prot_name")
    prot_to_finalprot={e["prot_name"]:e for e in prot_to_finalprot_obj_val}
    seq_intervals_finalprot={(e["finalprot_seq_start"],e["finalprot_seq_end"]):e["prot_name"] for e in prot_to_finalprot_obj_val}


    finpseq_to_model={}
    for m in model_pos_obj:
        up_pos_obj=m.id_uniprotpos
        up_pos=up_pos_obj.seqpos
        model_details="%s:%s"%(m.seqpos,m.chainid)
        for interval,protname in seq_intervals_finalprot.items():
            if up_pos >=interval[0] and up_pos <=interval[1]:
                if protname not in finpseq_to_model:
                    finpseq_to_model[protname]={}
                fp_pos=(up_pos - interval[0]) +1
                finpseq_to_model[protname][fp_pos]=model_details
    return finpseq_to_model

def download_custom_descriptors_template(request,dyn_id):
    finpseq_to_model= obtain_finpseq_to_model(dyn_id)
    response = HttpResponse(content_type='text/csv')        
    response['Content-Disposition'] = 'attachment; filename="user_descriptors.csv"'
    
    writer = csv.writer(response)
    writer.writerow(["#Add one or more metrics with a numeric value for each residue."])
    writer.writerow(["#This should be uploaded as comma separated values (csv)."])
    writer.writerow(["Protein","Seq. pos.","PDB resID","metric 1","...","metric n"])
    for prot, prot_pos_d in finpseq_to_model.items():
        for seq,pdb in sorted(prot_pos_d.items(),key=lambda x:x[0]):
            writer.writerow([prot,seq,pdb])
    return response


def obtain_impact_per_variant_all(dyn_id):
    traj_id_li=[e.id for e in CovidFiles.objects.filter(covidfilesdynamics__id_dynamics=dyn_id,covidfilesdynamics__type=2)]

    impact_per_variant_path_pre=settings.MEDIA_ROOT + "Precomputed/covid19/variant_impact/summary"
    impact_per_variant_all={}
    for traj_id in traj_id_li:
        impact_per_variant_path=os.path.join(impact_per_variant_path_pre,"dyn_%s_traj_%s.data"%(dyn_id,traj_id))

        if os.path.isfile(impact_per_variant_path):
            with open(impact_per_variant_path,"rb") as fh:
                impact_per_variant_traj=pickle.load(fh)

            impact_per_variant_all[traj_id]=impact_per_variant_traj

    if impact_per_variant_all:

        # Mutfunc data
        #Extract from DB
        included_prots= {e.name for e in CovidFinalProtein.objects.filter(covidmodel__coviddynamics=dyn_id)}

        mutfunc_o=CovidMutfuncData.objects.filter(id_final_protein__name__in=included_prots)
        mutfunc_data=load_mutfunc_mutationeffect_data(mutfunc_o)
        #merge  mutfunc_data with our data on parameters per position
        for traj_id,mut_impact_data in impact_per_variant_all.items():
            for finprot,protdata in mut_impact_data.items():
                for protpos,posdata in protdata.items():
                    posvars=posdata["variants"]
                    for varname, vardict in posvars.items():
                        try:
                            vardict["mutfunc"]=mutfunc_data[finprot][protpos][varname]
                        except KeyError:
                            pass
    return impact_per_variant_all

def parse_str_to_html(mystr):
    mystr=mystr.replace(" ","_")
    mystr=mystr.replace(".","")
    mystr=mystr.replace(":","")
    mystr=mystr.replace(",","")
    if len(mystr)==0:
        mystr="x"
    return mystr


@csrf_protect
def upload_descriptors(request,dyn_id):

    context={}
    context["dyn_id"]=dyn_id
    if request.method == 'POST':
        form = UploadDescriptorsForm(request.POST, request.FILES)
        if form.is_valid():
            #pdb_id=form.cleaned_data['pdb_id']
            csv_file=request.FILES['csv_file']
            #print(csv_file.read())
            try:
                df = pd.read_csv(csv_file, delimiter = ',',comment='#')
            except Exception:
                return HttpResponse("Invalid form",status=422,reason='Invalid input format',content_type='text/plain; charset=UTF-8')
            if len(df.columns)>23:
                return HttpResponse("Invalid form",status=422,reason='Too many metrics defined, the maximum is 20.',content_type='text/plain; charset=UTF-8')
            elif len(df.columns)==1:
                return HttpResponse("Invalid form",status=422,reason='Columns not detected',content_type='text/plain; charset=UTF-8')
            for colname in df.columns:
                if not re.search("^[A-Za-z]", colname):
                    return HttpResponse("Invalid form",status=422,reason='Metric names must start with a letter.',content_type='text/plain; charset=UTF-8')
                if not re.search("^[\w\s\-\.\:\,]+$", colname):
                    return HttpResponse("Invalid form",status=422,reason='Invalid character in metric names.',content_type='text/plain; charset=UTF-8')
            df = df.dropna(axis=1, how='all')
            if len(df.columns)<=3:
                return HttpResponse("Invalid form",status=422,reason='No valid metrics found.',content_type='text/plain; charset=UTF-8')
            if len(df.columns)!=len(set(df.columns)):
                return HttpResponse("Invalid form",status=422,reason='Metric names cannot be repeated.',content_type='text/plain; charset=UTF-8')
            try:
                impact_per_variant_all=obtain_impact_per_variant_all(dyn_id)
                taken_column_names=set()
                for i,protpos in df.iterrows():
                    for traj_id,impact_per_variant_traj in impact_per_variant_all.items():
                        try:
                            impact_per_variant_pos=impact_per_variant_traj[protpos["Protein"]][protpos["Seq. pos."]]["variants"]
                        except KeyError:
                            continue
                        for var, impact_per_variant in impact_per_variant_pos.items():
                            for metricname in protpos.index.tolist()[3:]:
                                protposval=protpos[metricname]
                                if math.isnan(protposval):
                                    protposval=None
                                elif not isinstance( protposval, numbers.Number):
                                    protposval=None
                                metricname_ok=parse_str_to_html(metricname)
                                taken_column_names.add(metricname_ok)
                                impact_per_variant[metricname_ok]=protposval
            except Exception as e:
                print(e)
                return HttpResponse("Invalid form",status=422,reason='Server error',content_type='text/plain; charset=UTF-8')
            data={}
            data["impact_per_var"]=impact_per_variant_all
            data["added_metrics"]=list(taken_column_names)
            response = JsonResponse(data)
            return response

        return HttpResponse("Invalid form",status=422,reason='Invalid input',content_type='text/plain; charset=UTF-8')
    else:
        form = UploadDescriptorsForm()
    context["form"]=form
    return render(request, 'covid19/upload_descriptor.html', context)



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

def project(request):
    context={}
    return render(request, 'covid19/project.html', context)

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
    if not request.user.is_authenticated():
        #return redirect('accounts:login')
        #return HttpResponseRedirect('/accounts/logincovid/?next=/covid19/upload')
        return HttpResponseRedirect('/accounts/login/?next=/covid19/upload&is_covid=True')
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
                is_published=True
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

            return HttpResponseRedirect('/covid19/upload/success/%s' % dynobj.id)
        else:
            form._errors[NON_FIELD_ERRORS] = form.error_class(['Some fields are empty or contain errors'])
    else:
        form = UploadFileForm()
    context={}
    context["form"]=form
    return render(request, 'covid19/upload.html', context)



def upload_success(request,dyn_id):
    context={"dyn_id":dyn_id}
    return render(request, 'covid19/upload_success.html', context)

def data_ym(data_str):
    datespl=data_str.split("-")
    (year,month)=datespl[:2]
    d=datetime.datetime(int(year),int(month),1)
    return d.strftime("%B %Y")

def get_final_proteins_info():
    mydyn=CovidDynamics.objects.filter(is_published=True).annotate(finalprot=F('id_model__final_proteins__name'))
    protsdyn=mydyn.values("finalprot","id")

    finprot_d={}
    for p in protsdyn:    
        dyn_id=p["id"]
        protname=p["finalprot"]
        if protname not in finprot_d:
            finprot_d[protname]=set()
        finprot_d[protname].add(dyn_id)
    finprot={}
    for prot,dynli in finprot_d.items():
        if prot:
            protname_id=prot.lower().replace(" ","_")
            finprot[protname_id]={}
            finprot[protname_id]["numdyn"]=len(dynli)
            finprot[protname_id]["name"]=prot
    return finprot

def sort_list_mod(mylist):
    if mylist:
        any_not_number=[e for e in mylist if not str(e).isnumeric()]
        if any_not_number:
            return sorted(mylist)
        else:
            return sorted(mylist,key=lambda x:float(x))
    else: 
        return mylist

def home(request):    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
        context={}
        input_path=settings.MEDIA_ROOT + "Covid19Data/Data/tree.data"
        if os.path.isfile(input_path):
            with open(input_path, 'rb') as filehandle:  
                tree_data = pickle.load(filehandle)
        context["tree_data"]=tree_data

        genomes_d={}
#        genome_muts_path=settings.MEDIA_ROOT + "Covid19Data/Data/home_genome_muts.data"
#        with open(genome_muts_path,"rb") as fh:
#            genomes_d=pickle.load(fh)
        context["genome_mutations"]=genomes_d

#        genomes_d={}
#        testing=True 
#        if not testing:
#            #generates dict of {isolate: {protein : list of mutations}}
#                                                    # also includes sequence but we don't need this
#            # to do
#            #   - we don't need to check if sequence exists each time we want to provide a fasta link
#            #   - incorporate the dict of {mutated proteins : mutation list } in the input json
#            #   with this we won't need to generate this dict
#            seqgeneobj=CovidSequencedGene.objects.filter(id_sequence__is_wt=False)
#            myseqgene=seqgeneobj.annotate(genename=F("id_final_protein__name"))
#            myseqgene=myseqgene.annotate(isolateid=F("id_isolate__isolate_id"))
#            myseqgene=myseqgene.annotate(mut_pos=F("id_sequence__seq_mutations__resid"))
#            myseqgene=myseqgene.annotate(mut_from=F("id_sequence__seq_mutations__resletter_from"))
#            myseqgene=myseqgene.annotate(mut_to=F("id_sequence__seq_mutations__resletter_to"))
#            myseqgene=myseqgene.annotate(sequence=F("id_sequence__seq"))
#            genomes_vals=myseqgene.values("genename","isolateid","mut_pos","mut_from","mut_to","sequence")
#            for thisgenome in genomes_vals:
#                if thisgenome["mut_pos"]:
#                    isolateid=thisgenome["isolateid"]
#                    if isolateid not in genomes_d:
#                        genomes_d[isolateid]={}
#                    genename=thisgenome["genename"]
#                    if genename not in genomes_d[isolateid]:
#                        genomes_d[isolateid][genename]={}
#                        genomes_d[isolateid][genename]["mutations"]=set()
#                    mutseq=thisgenome["sequence"]
#                    if thisgenome["sequence"]:
#                        genomes_d[isolateid][genename]["sequence"]=thisgenome["sequence"]
#                    mutname="%s%s%s"%(thisgenome["mut_from"],thisgenome["mut_pos"],thisgenome["mut_to"])
#                    genomes_d[isolateid][genename]["mutations"].add(mutname)
#
#            for geno in genomes_d.values():
#                for prot, protdict in geno.items():
#                    protdict["mutations"]=list(protdict["mutations"])




        allprotobj=CovidFinalProtein.objects.all()
        ann_allprotobj=allprotobj.annotate(dyn_id=F("covidmodel__coviddynamics__id"))
        ann_allprotobj=ann_allprotobj.annotate(is_published=F("covidmodel__coviddynamics__is_published"))
        allprot_values=ann_allprotobj.values("dyn_id","name","is_published")

        simulated_prots=set()
        for prot_info in sorted(allprot_values,key=lambda x: x["dyn_id"] if x["dyn_id"] else 0 ):
            dyn_id=prot_info["dyn_id"]
            if not dyn_id: 
                continue
            if not prot_info["is_published"]:
                continue
            genename=prot_info["name"]
            simulated_prots.add(genename)

        context["simulated_prots"]=list(simulated_prots)
        #print(context)
        return HttpResponse(json.dumps(context), content_type='home/')   
    else:

        context={}
        input_path_colors=settings.MEDIA_ROOT + "Covid19Data/Data/colorscales.data"
        if os.path.isfile(input_path_colors):
            with open(input_path_colors, 'rb') as filehandle:  
                colors_dict = pickle.load(filehandle)
        context["colors_dict"]=json.dumps(colors_dict)
        #obtain sequenced perrion
        sorted_seq_dates=sorted(colors_dict["date"])
        context["sequenced_from"]=data_ym(sorted_seq_dates[0])
        context["sequenced_to"]=data_ym(sorted_seq_dates[-1])

        var_li=sorted((e,e.replace("_"," ").capitalize()) for e in colors_dict.keys())
        context["var_li"]=var_li

        colors_dict_selectopt={}
        for col_var,var_data in colors_dict.items():
            colors_dict_selectopt[col_var]={}
            colors_dict_selectopt[col_var]["name"]=col_var.replace("_"," ").capitalize()
            if col_var in ["date_list","author","submitting_lab","originating_lab"]:
                continue
            elif col_var in ["age","mutations"]:
                new_data_opt=[]
                date_pair_from=False
                last_color=last_date=False
                for dateval,color in sorted(var_data.items(),key=lambda x:x[0]):
                  if not date_pair_from and date_pair_from!=0:
                    date_pair_from=dateval
                  else :
                    if last_color and (color != last_color):
                      if not date_pair_from:
                        date_pair_from=0
                      date_pair_fromto="%s - %s"%(date_pair_from,last_date)
                      new_data_opt.append(date_pair_fromto)
                      date_pair_from=dateval              
                  last_color=color
                  last_date=dateval
                date_pair_fromto="%s - %s"%(date_pair_from,last_date)
                new_data_opt.append(date_pair_fromto)
            else:
                new_data_opt=sort_list_mod(var_data.keys())
            colors_dict_selectopt[col_var]["options"]=new_data_opt
        context["colors_dict_selectopt"]=colors_dict_selectopt
        context["finprot"]=get_final_proteins_info()
        context["num_dyn"]=CovidDynamics.objects.filter(is_published=True).count()
        context["num_traj"]=CovidFilesDynamics.objects.filter(type=2,id_dynamics__is_published=True).count()
    
        mdsrv_url=obtain_domain_url(request)
        
            
        context["mdsrv_url"]=mdsrv_url

        return render(request, 'covid19/home.html', context)


def hometest(request):    
    context={}
    input_path=settings.MEDIA_ROOT + "Covid19Data/Data/tree.data"
    if os.path.isfile(input_path):
        with open(input_path, 'rb') as filehandle:  
            tree_data = pickle.load(filehandle)
    context["tree_data"]=json.dumps(tree_data)
    return render(request, 'covid19/hometest.html', context)


def hometest2(request):    
    context={}
    input_path=settings.MEDIA_ROOT + "Covid19Data/Data/tree.data"
    if os.path.isfile(input_path):
        with open(input_path, 'rb') as filehandle:  
            tree_data = pickle.load(filehandle)
    context["tree_data"]=json.dumps(tree_data)
    return render(request, 'covid19/hometest2.html', context)

def quickloadall(request):

    # Create uploading file
    f = open(settings.MEDIA_ROOT + 'config/isloading.txt','w')
    f.close()

    #DyndbFiles.objects.filter(dyndbfilesdynamics__id_dynamics=dyn_id, id_file_types__is_trajectory=True)
    mdsrv_url=obtain_domain_url(request)
    
        
    dynobj=CovidDynamics.objects.filter(is_published=True)
    dynfiledata = dynobj.annotate(dyn_id=F('id'))
    dynfiledata = dynfiledata.annotate(file_path=F('covidfilesdynamics__id_files__filepath'))
    dynfiledata = dynfiledata.annotate(file_is_traj=F('covidfilesdynamics__id_files__id_file_types__is_trajectory'))
    dynfiledata = dynfiledata.annotate(file_ext=F('covidfilesdynamics__id_files__id_file_types__extension'))
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
        file_short=file_info[file_info.index("Covid19Dynamics"):]
        if dyn["file_is_traj"]:
            dyn_dict[dyn_id]["traj"].append(file_short)
        elif dyn["file_ext"]in {"pdb","gro"}:
            dyn_dict[dyn_id]["pdb"].append(file_short)

    del dynfiledata
    filesli=[[d["pdb"][0],d["traj"]] for d in dyn_dict.values() if d["pdb"]]
    context={
        "mdsrv_url":mdsrv_url,
        "filesli":json.dumps(filesli)
            }
    return render(request, 'covid19/quickloadall.html', context)


#def report(request,dyn_id):
#    dyndata=extract_report_data(dyn_id)
#    return render(request, 'covid19/report.html', dyndata )


#def plottest(request):    
#    context={}
#    return render(request, 'covid19/plottest3.html', context)
