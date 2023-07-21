import re
import os.path
import mdtraj as md
import numpy as np
from collections import defaultdict
import gc

def get_num_frames(trj_file,stride):
    t=md.open(trj_file , mode="r",  force_overwrite=False)
    res=t.read(stride=stride)
    num_frames=np.shape(res[0])[0]

    #t=md.open(trj_file)
    #num_frames=t.__len__()
    
    del t
    gc.collect()
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

def create_json(self,isGPCR,trj_file,top_file,resi_to_group,resi_to_name,newpath,stride,seg_to_chain):
    out_file  = re.search("(\w*)(\.\w*)$" , newpath).group()
    self.stdout.write(self.style.NOTICE("Reading MD trajectory..."))
    num_frames=get_num_frames(trj_file,stride)
    it=md.iterload(filename=trj_file,chunk=(50/stride), top=top_file , stride=stride)
    f=0
    
    self.stdout.write(self.style.NOTICE("Analyzing Hbond network. It may take a while..."))
    hbond_frames = defaultdict(set)

    for t in it:
        hbonds_allframes = md.wernet_nilsson(t)
        for fnum,frame in enumerate(t[:]):
            hbonds= hbonds_allframes[fnum]
            for hbond in hbonds:
                resi_1 = t.topology.atom(hbond[0]).residue
                resi_2 = t.topology.atom(hbond[2]).residue
                if ((resi_1 != resi_2) and (resi_1.is_protein) and (resi_2.is_protein)):
                    if (resi_1.index < resi_2.index):
                        key = ((str(resi_1.resSeq),seg_to_chain[resi_1.segment_id]),(str(resi_2.resSeq),seg_to_chain[resi_2.segment_id]))
                    else:
                        key = ((str(resi_2.resSeq),seg_to_chain[resi_2.segment_id]),(str(resi_1.resSeq),seg_to_chain[resi_1.segment_id]))
                    hbond_frames[key].add(f)
            f+=1
        self.stdout.write(self.style.NOTICE("%d%% completed"%((f/(num_frames/stride))*100)))
    

    self.stdout.write(self.style.NOTICE("Analyzing network centrality .."))

    #Build networkx graph
    centrality = defaultdict(int)
    for resi1,resi2 in hbond_frames:
        if not resi1 in resi_to_name: continue
        if not resi2 in resi_to_name: continue
        resn1 = resi_to_name[resi1] if resi1 in resi_to_name else resi1[0]
        resn2 = resi_to_name[resi2] if resi2 in resi_to_name else resi2[0]
        if resn1=="None" or resn2=="None": 
            continue
        else:
            resn1=resn1.rsplit(".")[1]
            resn2=resn2.rsplit(".")[1]

        interaction_count = len(hbond_frames[(resi1,resi2)])
        weight = interaction_count/num_frames
        centrality[resn1] += weight
        centrality[resn2] += weight

    #Normalize centrality to the range [0:1]
    min_centrality = min([centrality[v] for v in centrality]) 
    max_centrality = max([centrality[v] for v in centrality]) 
    for v in centrality:
        centrality[v] = (centrality[v]-min_centrality)/(max_centrality-min_centrality)


    self.stdout.write(self.style.NOTICE("Writing hbonds to %s .."%out_file))
    #Collect entries for edges and trees (grouping of nodes)
    edge_entries = []
    tree_paths   = set()
    for resi1,resi2 in hbond_frames:
        if not resi1 in resi_to_name: continue
        if not resi2 in resi_to_name: continue
        resn1 = resi_to_name[resi1] if resi1 in resi_to_name else resi1[0]
        resn2 = resi_to_name[resi2] if resi2 in resi_to_name else resi2[0]
        if resn1=="None" or resn2=="None": 
            continue
        else:
            resn1=resn1.rsplit(".")[1]
            resn2=resn2.rsplit(".")[1]

        framelist = sorted(list(hbond_frames[(resi1,resi2)]))
        helixinfo=get_cont_type(self,trj_file,resn1,resn2)
        if (helixinfo):
            edge_entries.append("    {\"name1\":\"%s\", \"name2\":\"%s\", \"frames\":%s, \"helixpos\":\"%s\"}"%(resn1,resn2,str(framelist),helixinfo))
        else:
            edge_entries.append("    {\"name1\":\"%s\", \"name2\":\"%s\", \"frames\":%s}"%(resn1,resn2,str(framelist)))

        tree_paths.add(resi_to_group[resi1]+"."+resn1)
        tree_paths.add(resi_to_group[resi2]+"."+resn2)



    #Collect entries for the helix track (coloring of nodes)
    helix_track_entries = []
    helix_colors = {1:"#78C5D5",12:"#5FB0BF",2:"#459BA8",23:"#5FAF88",3:"#79C268",34:"#9FCD58",4:"#C5D747",45:"#DDD742",5:"#F5D63D",56:"#F3B138",6:"#F18C32",67:"#ED7A6A",7:"#E868A1",78:"#D466A4",8:"#BF63A6"}
    if isGPCR:
        for tp in tree_paths:
            try:
                #res_name = tp[tp.rfind("x")+1:]
                res_name = tp.split(".",1)[1]
                res_helix = int(tp[tp.rfind(".")+1:tp.find("x")])
                helix_track_entries.append("      { \"nodeName\": \"%s\", \"color\": \"%s\", \"size\":\"1.0\" }"%(res_name,helix_colors[res_helix]))
            except ValueError: pass
            except IndexError: pass
            except KeyError: pass


        #Collect entries for the centrality track
        centrality_track_entries = []
        def ccol(val):
            col1 = (255,127,80)
            col2 = (255,255,255)
            rgb = tuple([int(c1*val+c2*(1-val)) for c1,c2 in zip(col1,col2)])
            return '#%02x%02x%02x' % rgb

        for tp in tree_paths:
            try:
                res_name = tp[tp.rfind(".")+1:]
                res_helix = int(tp[tp.rfind(".")+1:tp.find("x")])
                cent_val = centrality[res_name]
                centrality_track_entries.append("      { \"nodeName\": \"%s\", \"color\": \"%s\", \"size\":\"%s\" }"%(res_name,ccol(cent_val), cent_val))
            except ValueError: pass
            except IndexError: pass


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
            of.write(",\n".join(helix_track_entries))
            of.write("\n")
            of.write("    ]},\n")
            of.write("    {\n")
            of.write("    \"trackLabel\": \"Degree centrality\",\n")
            of.write("    \"trackProperties\": [\n")
            of.write(",\n".join(centrality_track_entries))
            of.write("\n")
            of.write("    ]}\n")
            of.write("  ],\n")
            of.write("  \"defaults\":{\"edgeColor\":\"rgba(50,50,50,100)\", \"edgeWidth\":2 }\n")
            of.write("}\n")


#############################################  
          
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


