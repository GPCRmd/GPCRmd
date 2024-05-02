#Script to clean files that are not usefull on GPCRmd

# Imports
import os
import glob

from django.core.management.base import BaseCommand, CommandError

from modules.dynadb.models import DyndbSubmissionDynamicsFiles, DyndbFiles

class Command(BaseCommand):
    help = "Clean files that are not useful on GPCRmd. "
    
    def handle(self, *args, **kwargs):  
        ftypes = ["_dyn_", "_trj_", "_prm_", "_oth_", "_prt_"]
        DSDF_files, dir_files = [], []
        out_files = {
                    "_dyn_":[],
                    "_trj_":[],
                    "_prm_":[],
                    "_oth_":[],
                    "_prt_":[]
                    }
        secr_files = {
                    "_dyn_":[],
                    "_trj_":[],
                    "_prm_":[],
                    "_oth_":[],
                    "_prt_":[]
                    }
        for dir_f in glob.glob("/GPCRmd/media/files/Dynamics/*.*"):
            dir_files.append(os.path.relpath(dir_f, "/GPCRmd/media/files")) # Dynamics...
            
        for DSDF in DyndbSubmissionDynamicsFiles.objects.all(): #Reference list /Dynamics
            if "Dynamics" in DSDF.filepath:
                DSDF_files.append(DSDF.filepath)
                
        # for DF in DyndbFiles.objects.all():
        #     filepath = DF.filepath
        #     if "//" in filepath:
        #         filepath = filepath.replace("//","/")
        #     if "Dynamics" in filepath:
        #         if filepath not in DSDF_files or filepath[1:] not in dir_files:
        #             if "1063" in filepath:
        #                 print(filepath)
        #             out_files.append(filepath)
        #         else:
        #             # if "1063" in filepath:
        #             #     print(filepath)
        #             in_files.append(filepath)
        
        for d_file in dir_files:
            filepath = "/" + d_file 
            if filepath not in DSDF_files:
                # if "_1063" in filepath:
                #     print(filepath)
                for ft in ftypes:
                    if ft in filepath:
                        out_files[ft].append(filepath)
                        l_file = filepath.split("_")
                        l_sub = l_file[-1].split(".")
                        sub_id = l_sub[0]
                        try:
                            if int(sub_id) >= 815 and int(sub_id) <= 1251:
                                secr_files[ft].append(filepath)
                        except: #Include in the name filtered, 4hbonds, notprotein, 4saltbridges, mdpocket
                            break
                        break
        
        # DSDF_files.sort() #Sort the list
        # out_files.sort()
        print(len(out_files["_dyn_"])+ len(out_files["_trj_"])+ len(out_files["_oth_"])+ len(out_files["_prm_"])+ len(out_files["_prt_"]) , len(out_files["_dyn_"]), len(out_files["_trj_"]), len(out_files["_oth_"]), len(out_files["_prm_"]), len(out_files["_prt_"]))
        print(len(secr_files["_dyn_"])+ len(secr_files["_trj_"])+ len(secr_files["_oth_"])+ len(secr_files["_prm_"])+ len(secr_files["_prt_"]) , len(secr_files["_dyn_"]), len(secr_files["_trj_"]), len(secr_files["_oth_"]), len(secr_files["_prm_"]), len(secr_files["_prt_"]))
        
        # for f in 