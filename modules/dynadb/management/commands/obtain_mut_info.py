from django.core.management.base import BaseCommand, CommandError
import requests
from modules.dynadb.models import DyndbDynamics
from modules.view.views import obtain_DyndbProtein_id_list
from bioservices import UniProt
import os
from pathlib import Path
import pandas as pd
import json
import urllib
import re
from modules.dynadb.pipe4_6_0 import d as aa_short
from django.db.models import F
from django.conf import settings

class Command(BaseCommand):
    help = "Obtains data on known mutations and/or variants for the GPCRs stored in the database from GPCRdb"
    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            dest='update',
            default=False,
            help='Overwrites already stored data.',
        )
        parser.add_argument(
            '--sel',
            dest='sel_mv', 
            nargs='?',
            choices=["var_only","mut_only","all"],
            action='store',
            default='var_only',
            help = "Download info for variants only, mutants only, or all. In principle we only need varian info because the mutant info is aleady in our database.")

#        parser.add_argument(
#            '-r',
#            dest='restrict', 
#            nargs='?',
#            choices=['mut','var'],
#            action='store',
#            default='all',
#            help='Define if only mutational or only variant info is retrieved..'
#        )
        
    def handle(self, *args, **options):
        def open_json(json_filepath):
            json_file=open(json_filepath)
            json_str = json_file.read()
            json_dict=pd.io.json.loads(json_str)
            return json_dict
        def open_dict_or_new(filepath):
            filepath_obj = Path(filepath)
            try:
                filepath_res = filepath_obj.resolve()
                mydict=open_json(filepath)
            except FileNotFoundError:
                mydict={}
            return mydict
        def uniprot_mapping(fromtype, totype, identifier):
            """Takes an identifier, and types of identifier 
            (to and from), and calls the UniProt mapping service
            Abbrebiations of Uniprot identifier types can be found here: https://www.uniprot.org/help/api_idmapping
            """
            base = 'http://www.uniprot.org'
            tool = 'mapping'
            params = {'from':fromtype,
                        'to':totype,
                        'format':'tab',
                        'query':identifier,
            }
            #urllib turns the dictionary params into an encoded url suffix
            data = urllib.parse.urlencode(params)
            #construct the UniProt URL
            url = base+'/'+tool+'?'+data
            #and grab the mapping
            response =  urllib.request.urlopen(url)
            #response.read() provides tab-delimited output of the mapping
            return (response.read())
        def calc_foldcgange(wt_val,mut_val):
            if mut_val >= wt_val:
                fchange=str(round(mut_val/wt_val,3))
            else:
                fchange=str(- round(wt_val/mut_val,3))
            return fchange
        def obtain_mut_info(muts_dict,uprot,entry):
            mut_info=requests.get('http://gpcrdb.org/services/mutants/'+entry).json()
            if entry not in muts_dict:
                if mut_info:
                    muts_dict[entry]={}
                    for pos_mut in mut_info:
                        seqpos=pos_mut["mutation_pos"]
                        if float(pos_mut["exp_wt_value"])==0 or float(pos_mut["exp_mu_effect_value"])==0:
                            fchange=False
                        else:
                            fchange=calc_foldcgange(pos_mut["exp_wt_value"],pos_mut["exp_mu_effect_value"])
                        #fchange=str(round(pos_mut["exp_mu_effect_value"]/pos_mut["exp_wt_value"],2))
                        pos_mut_d={
                            "from":pos_mut["mutation_from"],
                            "to":pos_mut["mutation_to"],
                            "fchange":fchange,
                            "measure":pos_mut["exp_type"],
                            "unit":pos_mut["exp_wt_unit"],
                            "exp":pos_mut["exp_func"],
                            "lig":pos_mut["ligand_name"],
                            "pub_ref":pos_mut["reference"],
                            "qual":pos_mut["exp_mu_effect_qual"]
                            }
                        if seqpos in muts_dict[entry]:
                            muts_dict[entry][seqpos].append(pos_mut_d)
                        else:
                            muts_dict[entry][seqpos]=[pos_mut_d]
                else:
                    muts_dict[entry]={}

            return muts_dict
        def obtain_var_info(vars_dict,uprot,entry):
            uprot_map=uniprot_mapping('ACC+ID', 'ENSEMBL_ID', uprot)
            if len(uprot_map)<= 8:
                return vars_dict
            ens_id= uprot_map.decode().strip("\n").split("\t")[-1]
            exac=requests.get("http://exac.hms.harvard.edu/rest/gene/variants_in_gene/"+ens_id).json()
            if entry not in vars_dict:
                vars_dict[entry]={}
                for exac_var in exac:
                    consequence=exac_var["major_consequence"]
                    if consequence in ["frameshift_variant","missense_variant","stop_gained","synonymous_variant"]:
                        #frameshift_variant: p.Val152SerfsTer3
                        #stop_gained: p.Trp32Ter
                        #missense_variant: p.Leu340Pro
                        #synonymous_variant: p.Thr384Thr
                        var_info=exac_var["HGVSp"]
                        mymatch=re.match("p\.([A-Za-z]*)(\d*)(([A-Za-z]*).*)",var_info)
                        fromAA=mymatch.group(1)
                        seqNum=mymatch.group(2)
                        toAA=mymatch.group(3)
                        allele_freq=exac_var["allele_freq"]
                        if consequence == "missense_variant" or consequence=="synonymous_variant":                            
                            from_sAA=aa_short[fromAA.upper()]
                            to_sAA=aa_short[toAA.upper()]
                        elif consequence=="stop_gained":
                            from_sAA=aa_short[fromAA.upper()]
                            to_sAA=toAA
                        elif consequence=="frameshift_variant":
                            from_sAA=aa_short[fromAA.upper()]
                            mymatch2=re.match("^([A-Za-z]*)(fsTer.*)$",toAA)
                            to_AAnm=mymatch2.group(1)
                            to_rest=mymatch2.group(2)
                            to_AAnm=aa_short[to_AAnm.upper()]
                            to_sAA=to_AAnm+to_rest
                        exac_var_id=exac_var["variant_id"]
                        pos_vars={
                                    "from":from_sAA,
                                    "to":to_sAA,
                                    "consequence":consequence,
                                    "exac_var_id":exac_var_id,
                                    "allele_freq":allele_freq
                                }
                        if seqNum in vars_dict[entry]:
                            vars_dict[entry][seqNum].append(pos_vars)
                        else:
                            vars_dict[entry][seqNum]=[pos_vars]
            return vars_dict

        mypath=settings.MEDIA_ROOT + "Precomputed/muts_vars_info"
        if not os.path.isdir(mypath):
            os.makedirs(mypath)
        vars_filepath=os.path.join(mypath,"gpcr_vars.json")
        muts_filepath=os.path.join(mypath,"gpcr_muts.json")
        if options['update']:
            vars_dict={}
            muts_dict={}
        else:
            vars_dict=open_dict_or_new(vars_filepath)
            muts_dict=open_dict_or_new(muts_filepath)

        dyn_li=DyndbDynamics.objects.filter(is_published=True)


        dynobj=dyn_li.annotate(dyn_id=F('id'))
        dynobj=dynobj.annotate(uniprot=F('id_model__id_protein__uniprotkbac'))
        dynobj=dynobj.annotate(uniprot2=F('id_model__id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein__uniprotkbac'))
        dynprotdata = dynobj.values("dyn_id","uniprot","uniprot2")
        
        dyn_dict = {}
        for dyn in dynprotdata:
            dyn_id=dyn["dyn_id"]
            up=dyn["uniprot"]
            if not up:
                up=dyn["uniprot2"]
            if not up:
                self.stdout.write(self.style.NOTICE("UniProt ID not found for dyn %s" % (dyn_id)))
                continue
            if dyn_id not in dyn_dict:
                dyn_dict[dyn_id]=[up]
            else:
                dyn_dict[dyn_id].append(up)
        u = UniProt()
        for dyn_id,uprot_li in dyn_dict.items():
            for uprot in uprot_li:
                data=u.quick_search("id:%s" % uprot)
                if data:
                    entry=data[uprot]['Entry name'].lower()
                    if options["sel_mv"] =="var_only" or options["sel_mv"] =="all":
                        vars_dict=obtain_var_info(vars_dict,uprot,entry)
                    elif options["sel_mv"] =="mut_only" or options["sel_mv"] =="all":
                        muts_dict=obtain_mut_info(muts_dict,uprot,entry)
                else:
                    self.stdout.write(self.style.NOTICE("No uniprot id found for %s (dyn id:%i)." % (uprot,dyn_id)))
        if options["sel_mv"] =="var_only" or options["sel_mv"] =="all":        
            with open(vars_filepath, 'w') as outfile:
                json.dump(vars_dict, outfile)
        elif options["sel_mv"] =="mut_only" or options["sel_mv"] =="all":
            with open(muts_filepath, 'w') as outfile:
                json.dump(muts_dict, outfile)





#        




        #_vars or _muts
            #uniptoy_id : [
          #      {"from":"V","to":"A","fchange":"1.35","measure":"k(i)","exp_type":"Binding - Radioligand competition/displacement","ref":"https://www.ncbi.nlm.nih.gov" },
          #      {"from":"V","to":"S","fchange":"1.23","measure":"k(i)","exp_type":"Binding - Radioligand competition/displacement","ref":"https://www.ncbi.nlm.nih.gov" }
          #  ]

