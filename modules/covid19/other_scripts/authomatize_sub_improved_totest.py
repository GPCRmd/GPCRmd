import requests
import math
import urllib
import os
import mdtraj as md

from covid19.models import *
from modules.dynadb.models import DyndbFileTypes
from django.conf import settings

def get_prot_from_pdb(pdbid):
    pdb_url="https://data.rcsb.org/rest/v1/core/entry/%s"%pdbid
    pdb_data=requests.get(pdb_url).json()
    if pdb_data and "status" not in pdb_data:
        prot_name=pdb_data["struct"]["pdbx_descriptor"]
        return prot_name
    else:
        return None

def get_prot_tag(pdbid):
    name_to_tag={
         '2019-ncov receptor-binding domain': 'RBD',
         'angiotensin-converting enzyme 2 (e.c.3.4.17.23)': 'ACE2',
         'antitoxin hicb': 'NSP3',
         'non-structural polyprotein 1ab': 'NSP1',
         'non-structural protein 3': 'NSP3',
         'nsp12': 'NSP12',
         'nsp7': 'NSP7',
         'nsp8': 'NSP8',
         'nsp9 replicase protein': 'NSP9',
         'papain-like proteinase': 'NSP3',
         'sars-cov-2 chimeric rbd': 'RBD',
         'spike glycoprotein': 'Spike'
     }
    prot_tag=None
    prot_name= get_prot_from_pdb(pdbid)
    if prot_name:
        prot_li=prot_name.split(", ")
        for myprot in prot_li:
            myprot=myprot.lower()
            if myprot in name_to_tag:
                prot_tag=name_to_tag[myprot]
    if not prot_tag:
        print("No prot tag for %s (%s)"% (pdbid,prot_name))
    return prot_tag

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

def save_download_file(save_data,download_data,dynobj,filename,projID,filt_atoms,total_numframes):
    db_filepath=False
    if save_data:
        (db_filepath,covidfile_dyn_obj,subtype)=save_bioexcel_file_data(dynobj,filename,total_numframes)
    if download_data:
        download_bioexcel_file(filename,projID,db_filepath)
        if save_data:
            ext=filename.split(".")[-1]
            if subtype == "pdb":
                if not filt_atoms:
                    if ext=="pdb":
                        traj = md.load_pdb(db_filepath)
                    else:
                        traj = md.load(db_filepath)
                    atom_num = traj.n_atoms
                    dynobj.atom_num=atom_num
                    dynobj.save()
            elif subtype=="trajectory":
                if not total_numframes:
                    t=md.open(db_filepath)
                    framenum=t.__len__()
                    covidfile_dyn_obj.framenum=framenum
                    covidfile_dyn_obj.save()


def download_bioexcel_file(filename,projID,db_filepath=False,overwrite=False):
    #Download traj test
    #url = 'https://bioexcel-cv19.bsc.es/api/rest/v1/projects/%s/files/trajectory' % projid
    #urllib.request.urlretrieve(url, '/home/mariona/testtraj')
    url="https://bioexcel-cv19.bsc.es/api/rest/current/projects/%s/files/%s"%(projID,filename)
    if not db_filepath:
        db_filepath=os.path.join(settings.MEDIA_ROOT + "Covid19Dynamics/bioexcel",filename)
    if overwrite or not os.path.isfile(db_filepath):
        print("Downloading file: %s"% filename)
        urllib.request.urlretrieve(url, db_filepath)

def save_bioexcel_file_data(dynobj,filename,total_numframes,sub_file_num=0,db_path=settings.MEDIA_ROOT + "Covid19Dynamics/",db_fileURL='/dynadb/files/Covid19Dynamics/'):
    dyn_id=dynobj.id
    ext=filename.split(".")[-1]
    tmp_db_filename ="tmp_%s_dyn_%s.%s"%(sub_file_num,dyn_id,ext)
    tmp_db_filepath =  os.path.join(db_path,tmp_db_filename)
    tmp_db_url =  os.path.join(db_fileURL,tmp_db_filename)
    
    filetype=DyndbFileTypes.objects.get(extension=ext)
    if filetype.is_trajectory:
        type_val=2
        subtype="trajectory"
    elif filetype.is_coordinates:
        type_val=0
        subtype="pdb"
    elif filetype.is_topology:
        type_val=1
        subtype="topology"
    elif filetype.is_anytype:
        type_val=4
        subtype="other"


    covidfileobj=CovidFiles(
        filename=tmp_db_filename,
        id_file_types=filetype,
        filepath=tmp_db_filepath,
        url=tmp_db_url
        )
    covidfileobj.save()

    file_id=covidfileobj.id
    db_filename ="%s_dyn_%s.%s"%(file_id,dyn_id,ext)
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
        framenum=total_numframes,
        )
    covidfile_dyn_obj.save()

    return (db_filepath,covidfile_dyn_obj,subtype)

allprojects=requests.get('https://bioexcel-cv19.bsc.es/api/rest/v1/projects').json()

num_proj=allprojects["totalCount"]


check_up=True
save_data=False
download_data=False
i=2 #The 1st ID is 2, for some reason

bex_data={}

while i <= num_proj+1:
    projid_base="MCV1900000"
    projid= projid_base[:- len(str(i))] + str(i)
    this_proj=requests.get('https://bioexcel-cv19.bsc.es/api/rest/v1/projects/%s' % projid).json()
    if this_proj["published"]:
        print("ID: ",projid)
        if save_data and CovidDynamics.objects.filter(extracted_from_db="BioExcel",extracted_from_db_entry=projid).exists():
            print("Already exists in the database - skipping")
            i+=1
            continue
        proj_meta=this_proj['metadata']
        sim_name=proj_meta["NAME"]
        prot_name=proj_meta["UNIT"]
        #simulation
        total_numframes=proj_meta["frameCount"]
        delta_ps=proj_meta["FREQUENCY"]
        stride=False
        if total_numframes>10000:
            stride=10
            total_numframes=math.ceil(total_numframes/stride)
            delta_ps=delta_ps*stride
        delta_ns=delta_ps*0.001
        timestep_fs=proj_meta["TIMESTEP"]
        #total_syst_atoms=proj_meta["SYSTATS"]
        filt_atoms=proj_meta["atomCount"]
        software=proj_meta["PROGRAM"]
        software_version=proj_meta["VERSION"]
        force_field=proj_meta["FF"]
        force_field_version=""
        description=proj_meta.get("DESCRIPTION")
        if description:
            description=description +" | BioExcel ID: "+projid
        else:
            description="BioExcel ID: "+projid
        #molecules
        #molecules=set()
        #for mymol in ['DPPC', 'SOL', 'NA', 'CL']:
        #    if proj_meta[mymol]>0:
        #        molecules.add(mymol)
        membrane=proj_meta["MEMBRANE"]
        has_membrane=membrane=="Yes"
        if has_membrane:
            print("%s has membrane, add code to save it? - Membrane: %s"% (projid,membrane))

        lig_li=[]
        model_type=0
        if "LIGANDS" in proj_meta:
            lig_li=proj_meta["LIGANDS"]
            model_type=1
        #authors
        authors=proj_meta["AUTHORS"]
        citation=proj_meta["CITATION"]
        #Protein
        pdbid=proj_meta["PDBID"].upper()
        prot_tag=get_prot_tag(pdbid)
        #pdbinfo=proj_meta["pdbInfo"]
        #prot_data=proj_meta["pdbInfo"]["uniprotRefs"]
        prot_data=[]
        simchains=this_proj['chains']
        for pdbchain in proj_meta["pdbInfo"]["chains"]:
            pdbchain_id=pdbchain["_id"].split("_")[1]
            if pdbchain_id in simchains:
                prot_name=pdbchain["header"].split("  ")[2]
                uniprotkbac=pdbchain['swpHit']["idHit"]
                prot_data.append({'_id':uniprotkbac, 'header':prot_name})

                fields=["entry_name","protein_names","organism"]
                if check_up:
                    results_dict=query_uprot(uniprotkbac,fields)
                    if results_dict:
                        prot_names_all=results_dict["Protein names"]
                        prot_name=prot_names_all[:prot_names_all.find("(")].strip()
                        uniprot_entry = results_dict["Entry name"]
                        species =results_dict["Organism"]
                    else:
                        print("ERROR extracting data from uniprot")
                        uniprot_entry = "-"
                        species ="-"
        bex_data[projid]=prot_data
        #SAVE DATA
        if save_data:
            #Save protein
            protobj, created_protobj = CovidProtein.objects.get_or_create(
                uniprotkbac=uniprotkbac,
                uniprot_entry=uniprot_entry,
                name=prot_name,
                species=species
            )
            modelobj,created_modelobj=CovidModel.objects.get_or_create(
                type=model_type,
                pdbid=pdbid,
                #id_protein=protobj
            )
            modprotobj,created_modprotobj=CovidModelProtein.objects.get_or_create(
                id_model=modelobj,
                id_protein=protobj
            )
            #Save dynamics
            dynobj,created_dynobj=CovidDynamics.objects.get_or_create(
                author_first_name="x",
                author_last_name="x",
                author_institution=authors,
                citation=citation,
                delta=delta_ns,
                dyn_name=sim_name,
                id_model=modelobj,
                timestep=timestep_fs,
                atom_num=filt_atoms,
                software=software,
                sversion=software_version,
                ff=force_field,
                ffversion=force_field_version,
                description=description,
                extracted_from_db="BioExcel",
                extracted_from_db_entry=projid,
                is_published=True
            )
            #Save molecules
            for lig in lig_li:
                dyncompobj,created_dyncompobj=CovidDynamicsComponents.objects.get_or_create(
                    id_dynamics=dynobj,
                    resname=lig["ngl_selection"],
                    molecule_name=lig["name"],
                    is_ligand=True,
                    ligand_type=0
            )
        #files
        proj_files=requests.get('https://bioexcel-cv19.bsc.es/api/rest/v1/projects/%s/files' % projid).json()
        for thisfile in proj_files:
            filename=thisfile["filename"]
            if filename.startswith("md.imaged.rot"):
                ext=filename.split(".")[-1]
                projID=thisfile["metadata"]['project']
                if ext=="pdb":
                    save_download_file(save_data,download_data,dynobj,filename,projID,filt_atoms,total_numframes)
                elif ext =="xtc":
                    if stride:
                        if "100" in filename:
                            #Download TRAJ file
                            save_download_file(save_data,download_data,dynobj,filename,projID,filt_atoms,total_numframes)
                    else:
                        if "100" not in filename:
                            #Download TRAJ file
                            save_download_file(save_data,download_data,dynobj,filename,projID,filt_atoms,total_numframes)

    i+=1
