import re
import os.path
import mdtraj as md
import numpy as np
from collections import defaultdict


def get_num_frames(trj_file,stride):
    t=md.open(trj_file , mode="r",  force_overwrite=False)
    res=t.read(stride=stride)
    num_frames=np.shape(res[0])[0]
    return num_frames

def get_cont_type(self,jsonfile,n1,n2):
    if(len(n1.split("x")) != 2):
        self.stdout.write(self.style.NOTICE("GPCR num %s not understood in %s." % (n1 , jsonfile)))
        return False
    chain1=n1.split("x")[0]
    chain2=n2.split("x")[0]
    if (chain1==chain2):
        group="1"
        info="Intra"
    else:
        group="2"
        info="Inter"
    return (info)

def create_json(self,isGPCR,trj_file,top_file,resi_to_group,resi_to_name,newpath,stride):
    out_file  = re.search("(\w*)(\.\w*)$" , newpath).group()
    self.stdout.write(self.style.NOTICE("Reading MD trajectory..."))
    num_frames=get_num_frames(trj_file,stride)
    it=md.iterload(filename=trj_file,chunk=(50/stride), top=top_file , stride=stride)
    f=0
    
    self.stdout.write(self.style.NOTICE("Analyzing Hbond network. It may take a while..."))
    hbond_frames = defaultdict(set)
    for t in it:
        for fnum,frame in enumerate(t[:]):
            hbonds = md.baker_hubbard(frame, periodic=True)
            for hbond in hbonds:
                resi_1 = t.topology.atom(hbond[0]).residue
                resi_2 = t.topology.atom(hbond[2]).residue
                if ((resi_1 != resi_2) and (resi_1.is_protein) and (resi_2.is_protein)):
                    if (resi_1.index < resi_2.index):
                        key = ((str(resi_1.resSeq),str(resi_1.chain.index)),(str(resi_2.resSeq),str(resi_2.chain.index)))
                    else:
                        key = ((str(resi_2.resSeq),str(resi_2.chain.index)),(str(resi_1.resSeq),str(resi_1.chain.index)))
                    hbond_frames[key].add(f)
            f+=1
        self.stdout.write(self.style.NOTICE("%d%% completed"%((f/num_frames)*100)))
    
    self.stdout.write(self.style.NOTICE("Writing hbonds to %s .."%out_file))
    #Collect entries for edges and trees (grouping of nodes)
    edge_entries = []
    tree_paths   = set()
    for resi1,resi2 in hbond_frames:
        if not resi1 in resi_to_name: continue
        if not resi2 in resi_to_name: continue
        resn1 = resi_to_name[resi1] if resi1 in resi_to_name else resi1[0]
        resn2 = resi_to_name[resi2] if resi2 in resi_to_name else resi2[0]
        if resn1=="None" or resn2=="None": continue

        framelist = sorted(list(hbond_frames[(resi1,resi2)]))
        helixinfo=get_cont_type(self,trj_file,resn1,resn2)
        if (helixinfo):
            edge_entries.append("    {\"name1\":\"%s\", \"name2\":\"%s\", \"frames\":%s, \"helixpos\":%s}"%(resn1,resn2,str(framelist),helixinfo))
        else:
            edge_entries.append("    {\"name1\":\"%s\", \"name2\":\"%s\", \"frames\":%s}"%(resn1,resn2,str(framelist)))

        tree_paths.add(resi_to_group[resi1]+"."+resn1)
        tree_paths.add(resi_to_group[resi2]+"."+resn2)


    #Collect entries for tracks (coloring of nodes)
    track_entries = []
    #helix_colors = ["#1500D6","#003D97","#00E600","#00E600","#FEE200","#FF9000","#FF3B00","#FF0000"]
    #helix_colors = ["#78C5D5","#459BA8","#79C268","#C5D747","#F5D63D","#F18C32","#E868A1","#BF63A6"]
    helix_colors = {1:"#78C5D5",12:"#5FB0BF",2:"#459BA8",23:"#5FAF88",3:"#79C268",34:"#9FCD58",4:"#C5D747",45:"#DDD742",5:"#F5D63D",56:"#F3B138",6:"#F18C32",67:"#ED7A6A",7:"#E868A1",78:"#D466A4",8:"#BF63A6"}
    if isGPCR:
        for tp in tree_paths:
            try:
                #res_name = tp[tp.rfind("x")+1:]
                res_name = tp.split(".",1)[1]
                res_helix = int(tp[tp.rfind(".")+1:tp.find("x")])
                track_entries.append("      { \"name\": \"%s\", \"color\": \"%s\" }"%(res_name,helix_colors[res_helix]))
            except ValueError: pass
            except IndexError: pass
            except KeyError: pass


        #Write everything
        with open(newpath,"w") as of:
            of.write("{\n")
            of.write("  \"edges\": [\n")
            of.write(",\n".join(edge_entries))
            of.write("\n")
            of.write("  ],\n")
            of.write("  \"nodes\": [\n")
            of.write(",\n".join(track_entries))
            of.write("\n")
            of.write("  ]\n")      
            of.write("}\n")      
          
    else:
        for tp in tree_paths:
            try:
                #res_name = tp[tp.rfind("x")+1:]
                res_name = tp[tp.rfind(".")+1:]
                res_helix = int(tp[tp.rfind(".")+1:tp.find("x")])
                track_entries.append("      { \"nodeName\": \"%s\", \"color\": \"%s\", \"size\":\"1.0\" }"%(res_name,helix_colors[res_helix]))
            except ValueError: pass
            except IndexError: pass
            except KeyError: pass


        #Write everything
        with open(newpath,"w") as of:
            of.write("{\n")
            of.write("  \"edges\": [\n")
            of.write(",\n".join(edge_entries))
            of.write("\n")
            of.write("  ],\n")
            of.write("  \"trees\": [\n")
            of.write("    {\n")
            of.write("      \"treeLabel\":\"Helices\",\n")
            of.write("      \"treePaths\": [\n")
            of.write(",\n".join(["        \""+tp+"\"" for tp in tree_paths]))
            of.write("\n")
            of.write("      ]\n")
            of.write("    }\n")
            of.write("  ],\n")
            of.write("  \"tracks\": [\n")
            of.write("    {\n")
            of.write("    \"trackLabel\": \"Helices\",\n")
            of.write("    \"trackProperties\": [\n")
            of.write(",\n".join(track_entries))
            of.write("\n")
            of.write("    ]}\n")
            of.write("  ],\n")
            of.write("  \"defaults\":{\"edgeColor\":\"rgba(50,50,50,100)\", \"edgeWidth\":2 }\n")
            of.write("}\n")


