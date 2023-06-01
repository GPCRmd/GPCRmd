from modules.dynadb.models import DyndbDynamics, DyndbFilesDynamics
from django.db.models import F
from django.core.management.base import BaseCommand, CommandError
import gc
import os
import mdtraj as md
from modules.dynadb.views import  get_precomputed_file_path
import json
from django.conf import settings

######################################
#dynfiles = DyndbFilesDynamics.objects.filter(id_dynamics__is_published=True)
#dynfiles = DyndbFilesDynamics.objects.all()
#dynfiles = DyndbFilesDynamics.objects.filter(id_dynamics__id__in=[4, 7, 9, 10, 145, 147, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 56, 64, 65, 83, 88, 96, 100, 101, 103, 104, 105, 106, 107, 111, 112, 113, 114, 115, 116, 117, 121])
#dynfiles = DyndbFilesDynamics.objects.filter(id_dynamics__id__in=[31])
#dynfiles = dynfiles.annotate(file_name=F("id_files__filename"),file_path=F("id_files__filepath"),file_id=F('id_files__id'),dyn_id=F("id_dynamics__id"))
#dynfiles_traj = dynfiles.filter(type=2)
#dynfiles_traj_d = dynfiles_traj.values("file_name","file_path","file_id","dyn_id")
#
#dyntraj_d={}
#for dyn in dynfiles_traj_d:
    #dyn_id=dyn["dyn_id"]
    #if dyn_id not in dyntraj_d:
        #dyntraj_d[dyn_id]=dict()
        #dyntraj_d[dyn_id]["dyn_id"]=dyn_id
        #dyntraj_d[dyn_id]["traj"]=[]
    #traj_info={"file_name":dyn["file_name"],
               #"file_path":dyn["file_path"],
               #"file_id":dyn["file_id"]}
    #dyntraj_d[dyn_id]["traj"].append(traj_info)
#
#r=obtain_dyn_files_from_id(False,True)
#
#
#
#for gcdyn_id, gcdyn_info in r.items():
    #gc_trajli=gcdyn_info["trajectory"]
    #gc_trajids=[e["id_files"] for e in gc_trajli]
#    
    #dynfiles = DyndbFilesDynamics.objects.filter(id_dynamics__id=gcdyn_id)
    #dynfiles = dynfiles.annotate(file_name=F("id_files__filename"),file_path=F("id_files__filepath"),file_id=F('id_files__id'))
    #dynfiles_traj = dynfiles.filter(type=2)
    #dynfiles_li=[e.file_id for e in dynfiles_traj]
#    
    #if gcdyn_id in dyntraj_d:
        #db_trajli=dyntraj_d[gc    json_file=open(path+filename)
        #db_trajids=[e["file_id"] for e in db_trajli]
#
        #if gc_trajids!=db_trajids:
            #print(gcdyn_id)

###################################
class Command(BaseCommand):
    help = "Converts ContactMaps data in FP."
    def add_arguments(self, parser):
        parser.add_argument(
           '--dyn',
            dest='dynamics_id',
            nargs='*',
            action='store',
            default=False,
            help='Specify dynamics id(s) for which the matrix will be precomputed. '
        )
        parser.add_argument(
            '--ignore_publication',
            action='store_true',
            dest='ignore_publication',
            default=False,
            help='Consider both published and unpublished dynamics.',
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            dest='overwrite',
            default=False,
            help='Overwrites already generated matrices.',
        )
    def handle(self, *args, **options):
        def create_pos_to_gnum(dyn_id):
            gcdata_path=settings.MEDIA_ROOT + "Precomputed/get_contacts_files/dynamic_symlinks/dyn%(dynid)s/dyn%(dynid)s_labels.tsv" % {"dynid" :dyn_id}
            if os.path.isfile(gcdata_path):
                pos_to_gnum={}
                with open(gcdata_path) as infile:
                    for line in infile: 
                        if len(line) == 0 or line[0] == "#":
                            continue
                        (pos,gnum) = line.split("\t")
                        pos_to_gnum[pos]=gnum.rstrip("\n")
                return pos_to_gnum
            else:
                return False

        def extract_res_info(res1):
            helix_to_treep={"1" :"2",
                            "12":"3",
                            "2" :"4" ,
                            "23":"5"  ,
                            "3" :"6" ,
                            "34":"7"  ,
                            "4" :"8" ,
                            "45":"9"  ,
                            "5" :"10" ,
                            "56":"11"  ,
                            "6" :"12" ,
                            "67":"13"  ,
                            "7" :"14" ,
                            "78":"15" ,
                            "8" :"16"}
            nodecolor = {'1': '#78C5D5',
                         '12': '#5FB0BF',
                         '2': '#459BA8',
                         '23': '#5FAF88',
                         '3': '#79C268',
                         '34': '#9FCD58',
                         '4': '#C5D747',
                         '45': '#DDD742',
                         '5': '#F5D63D',
                         '56': '#F3B138',
                         '6': '#F18C32',
                         '67': '#ED7A6A',
                         '7': '#E868A1',
                         '78': '#D466A4',
                         '8': '#BF63A6'}

            res1=res1[:res1.rfind(":")]
            if res1 in pos_to_gnum:
                gnum1=pos_to_gnum[res1]
                h1=gnum1.split("x")[0]
                if h1=="Ligand":
                    return False
                treep1=helix_to_treep[h1] + "." + gnum1
                nodecolor1 = nodecolor[h1]
                return (gnum1,treep1,nodecolor1,h1)
            else:
                return False


        def create_p_jsons(dynfiles_traj,pos_to_gnum):
            frame_ends_bytraj=[]
            accum_frames=0
            all_int_d=dict()
            hb_list=["hbbb","hbsb","hbss"]
            for traj in dynfiles_traj:
                n_frames=traj["n_frames"]
                frame_ends_bytraj.append(n_frames+accum_frames -1) #Starts by 0
                accum_frames+=n_frames

                cont_li=['sb', 'pc', 'ps', 'ts', 'vdw', 'hb', 'wb', 'wb2', 'hp']
                
                traj_int_d={e:dict() for e in cont_li}
                
                for int_d in traj_int_d.values():
                    int_d['defaults']={'edgeColor': 'rgba(50,50,50,100)', 'edgeWidth': 2}
                    int_d["trees"]=[{
                            "treeLabel" :'Helices',
                            "treePaths":set(), # ex. '2.1x30'
                        }]
                    int_d["edges"]=dict() #list of {'name1':, 'frames':, 'name2':, 'helixpos':} -> helixpos can be Intra or Inter
                                    #ex: {"frames": [ 0, 10, 12],  'helixpos': 'Intra', 'name1': '5x38', 'name2': '5x39'}
                    int_d["tracks"]=[
                                {"trackLabel":"Helices",
                                 "trackProperties" :list() # {'color': '#79C268', 'nodeName': '3x25', 'size': '1.0'}
                                }
                                ]
                all_int_d[traj["file_id"]]=traj_int_d
            gcdata_path=settings.MEDIA_ROOT + "Precomputed/get_contacts_files/dynamic_symlinks/dyn%(dynid)s/dyn%(dynid)s_dynamic.tsv" % {"dynid" :dynfiles_traj[0]["dyn_id"]}

            traj_rep=0    
            pre_frame=False
            accum_frames=0
            if os.path.isfile(gcdata_path):
                with open(gcdata_path) as infile:
                    for line in infile:
                        line = line.strip()
                        if "total_frames" in line:
                            el = line.split(" ")
                            file_total_frames=int(el[1].split(":")[1])

                        if len(line) == 0 or line[0] == "#":
                            continue

                        allinfo = line.split("\t")
                        if len(allinfo)==4:
                            (frame,int_type,res1,res2)=allinfo
                        elif len(allinfo)==5:
                            (frame,int_type,res1,res2,res3)=allinfo
                        elif len(allinfo)==6:
                            (frame,int_type,res1,res2,res3,res4)=allinfo
                        else:
                            self.stdout.write(self.style.NOTICE("Incorrect number of elements in line. Skipping. Line: %s"%line))
                            continue
                        if frame != pre_frame:
                            if int(pre_frame) == frame_ends_bytraj[traj_rep]:
                                traj_rep+=1                            
                                accum_frames=int(frame)
                                self.stdout.write(self.style.NOTICE("\tTraj id: %s"%dynfiles_traj[traj_rep]["file_id"]))
                        frame_corr=str(int(frame)-accum_frames)
                        traj_id=dynfiles_traj[traj_rep]["file_id"]
                        traj_int_d=all_int_d[traj_id]
                        #add all res:
                        resinfo1=extract_res_info(res1)
                        resinfo2=extract_res_info(res2)
                        if resinfo1 and resinfo2:
                            (gnum1,treep1,nodecolor1,h1)=resinfo1
                            (gnum2,treep2,nodecolor2,h2)=resinfo2
                        else:
                            continue
                        for int_typeid, int_data in traj_int_d.items():
                            if treep1 not in int_data["trees"][0]["treePaths"]:
                                int_data["trees"][0]["treePaths"].add(treep1) # ex. '2.1x30'
                                int_data["tracks"][0]["trackProperties"].append({'color': nodecolor1, 'nodeName': gnum1, 'size': '1.0'})
                            if treep2 not in int_data["trees"][0]["treePaths"]:
                                int_data["trees"][0]["treePaths"].add(treep2)
                                int_data["tracks"][0]["trackProperties"].append({'color': nodecolor2, 'nodeName': gnum2, 'size': '1.0'})
                        #add this particular inteaction
                        if int_type in hb_list:
                            int_type="hb"
                        if int_type in traj_int_d:
                            edge_d=traj_int_d[int_type]["edges"]
                            if (gnum1,gnum2) in edge_d:
                                edge_d[(gnum1,gnum2)]["frames"].append(frame_corr)
                            elif (gnum2,gnum1) in edge_d:
                                edge_d[(gnum2,gnum1)]["frames"].append(frame_corr)
                            else:
                                if (h1==h2):
                                    hpos="Intra"
                                else:
                                    hpos="Inter"
                                edge_d[(gnum1,gnum2)] = {'name1':gnum1 , 'name2':gnum2 , 'frames':[frame_corr],  'helixpos':hpos}

                        pre_frame=frame

                for traj_id,traj_int_d in all_int_d.items():
                    for int_type, int_data in traj_int_d.items():
                        int_data["trees"][0]["treePaths"] = list(int_data["trees"][0]["treePaths"])
                        int_data["edges"] = [v for k,v in int_data["edges"].items()]
                        save_json(dynfiles_traj,traj_id,int_type,int_data)
                return True
            else:
                return False
                            
        def save_json(dynfiles_traj,traj_id,int_type,int_data):
            traj_filename=[e["file_name"] for e in dynfiles_traj if e['file_id']==traj_id][0]
            json_filename=traj_filename.split(".")[0] + "_" + int_type +".json"
            filpath=get_precomputed_file_path('flare_plot',int_type,url=False)
            if not os.path.isdir(filpath):
                os.makedirs(filpath)
            with open(os.path.join(filpath,json_filename), 'w') as outfile:
                json.dump(int_data, outfile)




        if options['ignore_publication']:
            dynobj=DyndbDynamics.objects.all()
        else:
            dynobj=DyndbDynamics.objects.filter(is_published=True)
        if options['dynamics_id']:
            dynobj=dynobj.filter(id__in=options['dynamics_id'])
        if dynobj == []:
            self.stdout.write(self.style.NOTICE("No dynamics found with specified conditions."))

        dynobj = dynobj.annotate(dyn_id=F('id'))
        dynobj_d = dynobj.values("id")
        dyn_id_li=[d["id"] for d in dynobj_d]

        dyn_traj_d={}
        i=0
        tot=len(dyn_id_li)
        for dyn_id in sorted(dyn_id_li):
            try:
                self.stdout.write(self.style.NOTICE("dyn %s - %.1f%% completed"%(dyn_id , (i/tot)*100) ))
                dynfiles = DyndbFilesDynamics.objects.filter(id_dynamics__id=dyn_id)
                dynfiles = dynfiles.annotate(file_name=F("id_files__filename"),file_path=F("id_files__filepath"),file_id=F('id_files__id'))
                dynfiles_traj = dynfiles.filter(type=2)
                dynfiles_traj = dynfiles_traj.values("file_name","file_path","file_id")
                for traj in dynfiles_traj:
                    traj_path=traj["file_path"]
                    traj["dyn_id"]=dyn_id
                    if os.path.isfile(traj_path):
                        t=md.open(traj_path)
                        n_frames=t.__len__()
                        del t
                        gc.collect()
                        traj["n_frames"]=n_frames
                    else:
                        traj["n_frames"]=False
                pos_to_gnum=create_pos_to_gnum(dyn_id)
                if not pos_to_gnum:
                    self.stdout.write(self.style.ERROR("Labels file not found. Skipping." ))
                    continue
                result=create_p_jsons(dynfiles_traj,pos_to_gnum)
                if not result:
                    self.stdout.write(self.style.ERROR("GetContacts results file not found. Skipping." ))
                    continue
                dyn_traj_d[dyn_id]=dynfiles_traj
                i+=1
            except Exception as e:
                self.stdout.write(self.style.ERROR(e))
        self.stdout.write(self.style.NOTICE("100%" ))

