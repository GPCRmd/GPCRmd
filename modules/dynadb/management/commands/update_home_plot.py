from django.core.management.base import BaseCommand, CommandError
from django.db.models import F
from modules.dynadb.models import DyndbDynamics
import pickle
import requests
from django.conf import settings

class Command(BaseCommand):
    help = "Retrieves info from the database to complete the dicitonary used to create the GPCRmd tree (tree_data)."
    def add_arguments(self, parser):
#        parser.add_argument(
#            '--overwrite',
#            action='store_true',
#            dest='overwrite',
#            default=False,
#            help='Overwrites already generated json files.',
#        )
        parser.add_argument(
           '-i',
            dest='gpcrmdtree_path',
            default=settings.MEDIA_ROOT + "Precomputed/Summary_info/gpcrmdtree.data",
            action='store',
            type=str,
            help='Path to the input file,'
        )
        parser.add_argument(
           '-o',
            dest='gpcrmdtree_path_out',
            default=settings.MEDIA_ROOT + "Precomputed/Summary_info/gpcrmdtree.data",
            action='store',
            type=str,
            help='Path to the output file.'
        )
        parser.add_argument(
           '--dyn',
            dest='dynamics_id',
            nargs='*',
            action='store',
            default=False,
            help='Specify dynamics id(s) of simulations to include in the plot. Otherwise all new simulations will be added.'
        )
        parser.add_argument(
            '--force_find_pdb',
            action='store_true',
            dest='force_find_pdb',
            default=False,
            help='Looks for the PDB id of dynamics to be added without considering the class, family and sbtype of the receptor. This means that if our receptor is class F, it will iterate through all families, subtypes and PDBs of the rest of the classes to find the PDB inf in tree_data. Use when for some reason there is a missmatch with a class/family/subtype name (or longname) in tree_data with respect to GPCRdb (But rather than forcing it, you should fix the name in tree_data!)',
        )
        
    def handle(self, *args, **kwargs):
        def search_in_treeData(childrenli,myname,nameLongname):
            namefound=False
            for nlevel in range(0,len(childrenli)):
                thisname= childrenli[nlevel][nameLongname]
                if myname==thisname:
                    namefound=True
                    return(nlevel)
            return(False)
    
        def appendocreate(mystr,element):
            if mystr:
                mylist=mystr.split("|")
                mylist.append(element)
                mystr=("|").join(mylist)
            else:
                mystr=element
            return mystr

        # args = parser.parse_args() # Get the arguments

        #Dowbload data from GPCRdb
        strucpcrdb=requests.get('http://gpcrdb.org/services/structure/').json()
        prot_info={d["protein"]:d for d in strucpcrdb}
        famgpcrdb=requests.get('http://gpcrdb.org/services/proteinfamily/').json()
        slugtofamdata={d["slug"]:d for d in famgpcrdb}

        #Load input dict
        gpcrmdtree_path=kwargs["gpcrmdtree_path"]
        with open(gpcrmdtree_path, 'rb') as filehandle:  
            tree_data = pickle.load(filehandle)

        #Obtain dyn to be considered
        if kwargs['dynamics_id']:
            dynobj=dynobj.filter(id__in=kwargs['dynamics_id'])
        else:
            dynobj=DyndbDynamics.objects.filter(is_published=True)
        if dynobj == []:
            self.stdout.write(self.style.NOTICE("No dynamics found with specified conditions."))
            return
        #Retrieve data from dyn
        dynmods = dynobj.annotate(dyn_id=F('id'))
        dynmods = dynmods.annotate(pdb_namechain=F("id_model__pdbid"))
        dynmods=dynmods.annotate(entry_name=F('id_model__id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein__receptor_id_protein__entry_name'))
        dynmods=dynmods.annotate(entry_name2=F('id_model__id_protein__receptor_id_protein__entry_name'))
        dynmods=dynmods.annotate(prot_name=F('id_model__id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein__name'))
        dynmods=dynmods.annotate(comp_type=F("id_model__dyndbmodelcomponents__type"))
        dynmods=dynmods.annotate(ligname=F("id_model__id_complex_molecule__dyndbcomplexmoleculemolecule__id_molecule__id_compound__name"))
        vals_dynmods=dynmods.values("dyn_id","pdb_namechain","entry_name","entry_name2","prot_name","comp_type","ligname")

        dyn_dict = {}
        for dyn in vals_dynmods:
            dyn_id=dyn["dyn_id"]
            if dyn_id not in dyn_dict:
                dyn_dict[dyn_id]={}
                dyn_dict[dyn_id]["lig_li"]=set()
            pdbid=dyn["pdb_namechain"]
            if not pdbid:
                #self.stdout.write(self.style.NOTICE("!!! missing pdb in dyn %s" % dyn_id))
                print("!!! missing pdb in dyn %s" % dyn_id)
                continue
            if pdbid =="HOMO":
                continue
            pdbid=pdbid.split(".")[0].upper()

            entry_name=dyn["entry_name"]
            if not entry_name:
                entry_name=dyn["entry_name2"]
            if not entry_name:
                if dyn["prot_name"]:
                    dyn_dict[dyn_id]["lig_li"].add(dyn["prot_name"])#It's a prot ligand
                continue
            if entry_name not in prot_info:
                print("!!! entry name not in GPCRdb in dyn %s" % dyn_id)
                continue
            myprotd=prot_info[entry_name]
            fam_slug=myprotd["family"]
            class_slug=fam_slug.split("_")[0]
            myclass=slugtofamdata[class_slug]["name"]
            if myclass not in ['Class A (Rhodopsin)', 'Class B1 (Secretin)', 'Class C (Glutamate)', 'Class F (Frizzled)']:
                continue
            myclass=myclass[:myclass.index("(")-1]
            subtype=slugtofamdata[fam_slug]["name"]
            famname=slugtofamdata[fam_slug]["parent"]["name"]
            dyn_dict[dyn_id]["pdbid"]=pdbid
            dyn_dict[dyn_id]["class"]=myclass
            dyn_dict[dyn_id]["subtype"]=subtype
            dyn_dict[dyn_id]["fam"]=famname
            if dyn["comp_type"]==1:
                dyn_dict[dyn_id]["lig_li"].add(dyn["ligname"])

        force_find_pdb=kwargs["force_find_pdb"]
        for dyn_id,dyn_data in dyn_dict.items():
            if len(dyn_data.keys())<=1:
                print("No data found for dyn %s"%dyn_id)
                continue
            myclass=dyn_data["class"]
            myfam=dyn_data["fam"]
            mysubt=dyn_data["subtype"]
            pdbid=dyn_data["pdbid"]
            if force_find_pdb:
                break_all=False
                for nclasstmp in range(0,len(tree_data["children"])):
                    if break_all:
                        break
                    fam=tree_data["children"][nclasstmp]["children"]
                    for nfamtmp in range(0,len(fam)):
                        if break_all:
                            break
                        st=tree_data["children"][nclasstmp]["children"][nfamtmp]["children"]
                        for nsubt in range(0,len(st)):
                            pdbli=tree_data["children"][nclasstmp]["children"][nfamtmp]["children"][nsubt]["children"]
                            npdb=search_in_treeData(pdbli,pdbid,"name")
                            if not npdb is False:
                                break_all=True
                                nclass=nclasstmp
                                nfam=nfamtmp
                                break

            else:
                print(pdbid)
                nclass=search_in_treeData(tree_data["children"],myclass,"name")
                if nclass is False:
                    print("Class not found in tree_data for dyn %s" %dyn_id)
                    continue
                try:
                    nfam=search_in_treeData(tree_data["children"][nclass]["children"],myfam,"longname")
                    if nfam is False:
                        print("nfam %s not found in tree_data for dyn %s" %(myfam,dyn_id))
                        continue
                except:
                    continue
                try:
                    nsubt=search_in_treeData(tree_data["children"][nclass]["children"][nfam]["children"],mysubt,"longname")
                    if nsubt is False:
                        print("Subtype %s not found in tree_data for dyn %s (%s %s %s)" %(mysubt,dyn_id,nclass,nfam,nsubt))
                        continue
                except:
                    continue
                npdb=search_in_treeData(tree_data["children"][nclass]["children"][nfam]["children"][nsubt]["children"],pdbid,"name")
                if npdb is False:
                    print("PDB %s not found in tree_data for dyn %s." % (pdbid,dyn_id))
                    continue
            pdbdata=tree_data["children"][nclass]["children"][nfam]["children"][nsubt]["children"][npdb]
            if dyn_data["lig_li"]:
                apocomp="Complex"
            else:
                apocomp="Apo"
            tree_dyn_orig=pdbdata[apocomp]
            tree_dyn_li=tree_dyn_orig.split("|")
            if str(dyn_id) not in tree_dyn_li:
                print("Adding dyn %s in pdb %s %s (%s %s %s %s))"%(dyn_id,pdbid,apocomp,nclass,nfam,nsubt,npdb))
                tree_dyn_fin=appendocreate(tree_dyn_orig,str(dyn_id))
                pdbdata[apocomp]=tree_dyn_fin
                pdbdata["Simulated"]="Yes"
                if apocomp=="Complex":
                    mylig="+".join(dyn_data["lig_li"])
                    treelig=pdbdata["Ligand"]
                    treelig_fin=appendocreate(treelig,mylig)
                    pdbdata["Ligand"]=treelig_fin
                    treetransd=pdbdata["Transducer"]
                    treetransd_fin=appendocreate(treetransd,"-")
                    pdbdata["Transducer"]=treetransd_fin

        gpcrmdtree_path_out=kwargs["gpcrmdtree_path_out"]
        with open(gpcrmdtree_path_out, 'wb') as filehandle:  
            # store the data as binary data stream
            pickle.dump(tree_data, filehandle)
