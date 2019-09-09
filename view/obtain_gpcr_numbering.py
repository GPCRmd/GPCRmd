from view.views import *
from dynadb.pipe4_6_0 import *
from dynadb.models import DyndbDynamics
from django.db.models import F

def generate_gpcr_pdb (dyn_id, structure_file, retrieve_rel_dict=False):
    """Obtain GPCR num. of  structure file"""
    pdb_name = structure_file
    chain_name_li=obtain_prot_chains(pdb_name)
    multiple_chains=False
    if len(chain_name_li) > 1:
        multiple_chains=True
    (prot_li_gpcr, dprot_li_all,dprot_li_all_info,pdbid)=obtain_DyndbProtein_id_list(dyn_id)            
    dprot_chains={}
    chains_taken=set()
    gpcr_chains=[]
    non_gpcr_chains=[]
    prot_seq_pos={}
    seq_pos_n=1
    all_chains=[]
    all_prot_names=[]
    for prot_id, prot_name, prot_is_gpcr, prot_seq in dprot_li_all_info: #To classify chains by protein (dprot_chains is a dict:for each protein, has a list of each chain with its matchpdbfa results + the protein seq_pos)
        all_prot_names.append(prot_name)
        seq_pos=[]
        dprot_chains[prot_id]=[[],[]]  
        for chain_name in chain_name_li:
            checkpdb_res=checkpdb_ngl(pdb_name, segid="",start=-1,stop=9999999999999999999, chain=chain_name)
            if isinstance(checkpdb_res, tuple):
                tablepdb,pdb_sequence,hexflag=checkpdb_res
                result=matchpdbfa_ngl(prot_seq,pdb_sequence, tablepdb, hexflag)
                if isinstance(result, list):
                    #chain_results[chain_name]=result
                    if chain_name not in chains_taken:
                        chains_taken.add(chain_name)
                        dprot_chains[prot_id][0].append((chain_name,result))
                        seq_pos,seq_pos_n=(seq_pos,seq_pos_n)=obtain_seq_pos_info(result,seq_pos,seq_pos_n,chain_name,multiple_chains)
                        dprot_chains[prot_id][1]=seq_pos
                        all_chains.append(chain_name)
                        if prot_is_gpcr:
                            gpcr_chains.append(chain_name)
                        else:
                            non_gpcr_chains.append(chain_name)
        prot_seq_pos[prot_id]=(prot_name,seq_pos)
    keys_to_rm=set()
    for key, val in dprot_chains.items():
        if val==([],[]):
            keys_to_rm.add(key)
    for key in keys_to_rm:
        del dprot_chains[key]

    if chains_taken: # To check if some result have been obtained
        all_gpcrs_info=[]
        seg_li_all={}
        gpcr_pdb_all={}
        gpcr_id_name={}
        for gpcr_DprotGprot in prot_li_gpcr:
            gpcr_Dprot=gpcr_DprotGprot[0]
            gpcr_Gprot=gpcr_DprotGprot[1]
            dprot_id=gpcr_Dprot.id
            dprot_name=gpcr_Dprot.name
            gen_num_res=obtain_gen_numbering(dyn_id, gpcr_Dprot,gpcr_Gprot)  #warning!! the problem is here
            if len(gen_num_res) > 2:
                (numbers, num_scheme, db_seq, current_class) = gen_num_res
                gpcr_n_ex=""
                for pos_gnum in numbers[current_class].values():
                    if pos_gnum[1]: #We take the 1st instance of gpcr num as example, and check in which format it is (n.nnxnn or nxnn)
                        gpcr_n_ex=pos_gnum[1]
                        break
                if "." in gpcr_n_ex: #For the moment we only accept n.nnxnn format
                    seq_pos_index=0
                    gpcr_pdb={}
                    gpcr_aa={}
                    gnum_classes_rel={}
                    (dprot_chain_li, dprot_seq) = dprot_chains[dprot_id] 
                    for chain_name, result in dprot_chain_li:
                        (gpcr_pdb,gpcr_aa,gnum_classes_rel,other_classes_ok,dprot_seq,seq_pos_index,seg_li)=obtain_rel_dicts(result,numbers,chain_name,current_class,dprot_seq,seq_pos_index, gpcr_pdb,gpcr_aa,gnum_classes_rel,multiple_chains,simplified=True,add_aa=True,all_struc_num=True)
                                                        
                    gnum_classes_rel_ok={}
                    for (gclass,pos_d) in gnum_classes_rel.items():
                        for changed,current in pos_d.items():
                            if not current in gnum_classes_rel_ok:
                                gnum_classes_rel_ok[current]={}
                            gnum_classes_rel_ok[current][gclass]=changed



                    prot_seq_pos[dprot_id]=(dprot_name, dprot_seq)
                    gpcr_pdb_all[dprot_id]=(gpcr_pdb)
                    gpcr_id_name[dprot_id]=dprot_name
                    seg_li_all[dprot_id]=seg_li #[!] For the moment I don't use this, I consider only 1 GPCR
    if retrieve_rel_dict:
        return(gpcr_pdb,gnum_classes_rel_ok,current_class) #[!] For now I only consider 1 GPCR, so I only need this dict
    else:
        return(gpcr_pdb) #[!] For now I only consider 1 GPCR, so I only need this dict



def obtain_class(dyn_id):
    dynobj=DyndbDynamics.objects.filter(id=dyn_id)
    dynprot=dynobj.annotate(fam_slug=F('id_model__id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein__receptor_id_protein__family_id__slug'))
    fam_slug=dynprot.values("fam_slug")[0]["fam_slug"]
    if not fam_slug:
        dynprot=dynobj.annotate(fam_slug=F('id_model__id_protein__receptor_id_protein__family_id__slug'))
        fam_slug=dynprot.values("fam_slug")[0]["fam_slug"]
    fam_code=fam_slug.split("_")[0]
    fam_d={"001":"A","002":"B","003":"B","004":"C","005":"F","006":"Taste 2","007":"Others"}
    fam=fam_d[fam_code]
    return fam
