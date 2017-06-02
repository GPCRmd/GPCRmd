

import os.path
import mdtraj as md
from collections import defaultdict


def create_json(trj_file,trj_name,top_file,resi_to_group,resi_to_name):
    print("\nTraj to flare\n")
    out_file   = os.path.basename(trj_name)+"_fp.json"
    print("Reading md-trajectory ..")
    it=md.iterload(filename=trj_file,chunk=50, top=top_file)
    f=0

    print("Analyzing hbond network ..")
    hbond_frames = defaultdict(set)
    for t in it:
        for fnum,frame in enumerate(t[:]):
          hbonds = md.baker_hubbard(frame, periodic=True)
          print("Frame %d .. %d hbonds"%(f,hbonds.shape[0]))
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

    print("Writing hbonds to %s .."%out_file)
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
      edge_entries.append("    {\"name1\":\"%s\", \"name2\":\"%s\", \"frames\":%s}"%(resn1,resn2,str(framelist)))

      tree_paths.add(resi_to_group[resi1]+"."+resn1)
      tree_paths.add(resi_to_group[resi2]+"."+resn2)


    #Collect entries for tracks (coloring of nodes)
    track_entries = []
    #helix_colors = ["#1500D6","#003D97","#00E600","#00E600","#FEE200","#FF9000","#FF3B00","#FF0000"]
    #helix_colors = ["#78C5D5","#459BA8","#79C268","#C5D747","#F5D63D","#F18C32","#E868A1","#BF63A6"]
    helix_colors = {1:"#78C5D5",12:"#5FB0BF",2:"#459BA8",23:"#5FAF88",3:"#79C268",34:"#9FCD58",4:"#C5D747",45:"#DDD742",5:"#F5D63D",56:"#F3B138",6:"#F18C32",67:"#ED7A6A",7:"#E868A1",78:"#D466A4",8:"#BF63A6"}
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
    json_path="/protwis/sites/protwis/view/static/view/fplot/json_files/"
    with open(json_path+out_file,"w") as of:
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



def create_json_GPCR(trj_file,trj_name,top_file,resi_to_group,resi_to_name):
    print("\nTraj to flare, GPCR version\n")
    out_file   = os.path.basename(trj_name)+"_fp.json"
    print("Reading md-trajectory ..")
    it=md.iterload(filename=trj_file,chunk=50, top=top_file)
    f=0

    print("Analyzing hbond network ..")
    hbond_frames = defaultdict(set)
    for t in it:
        for fnum,frame in enumerate(t[:]):
          hbonds = md.baker_hubbard(frame, periodic=True)
          print("Frame %d .. %d hbonds"%(f,hbonds.shape[0]))
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


    print("Writing hbonds to %s .."%out_file)
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
      edge_entries.append("    {\"name1\":\"%s\", \"name2\":\"%s\", \"frames\":%s}"%(resn1,resn2,str(framelist)))

      tree_paths.add(resi_to_group[resi1]+"."+resn1)
      tree_paths.add(resi_to_group[resi2]+"."+resn2)


    #Collect entries for tracks (coloring of nodes)
    track_entries = []
    #helix_colors = ["#1500D6","#003D97","#00E600","#00E600","#FEE200","#FF9000","#FF3B00","#FF0000"]
    #helix_colors = ["#78C5D5","#459BA8","#79C268","#C5D747","#F5D63D","#F18C32","#E868A1","#BF63A6"]
    helix_colors = {1:"#78C5D5",12:"#5FB0BF",2:"#459BA8",23:"#5FAF88",3:"#79C268",34:"#9FCD58",4:"#C5D747",45:"#DDD742",5:"#F5D63D",56:"#F3B138",6:"#F18C32",67:"#ED7A6A",7:"#E868A1",78:"#D466A4",8:"#BF63A6"}
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
    json_path="/protwis/sites/protwis/view/static/view/fplot/json_files/"
    print(json_path+out_file)
    with open(json_path+out_file,"w") as of:
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
      

