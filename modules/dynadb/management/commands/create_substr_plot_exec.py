#python create_substr_plot_exec.py -i "/home/mariona/gpcrmd_vagrant/shared/sites/files/tests/cb2r/json/average/" -o "/home/mariona/gpcrmd_vagrant/shared/sites/files/tests/cb2r/json/average/substest/" -p [["giunaffected","barr1unaffected"],["giunaffected","barr2unaffected"],["gobunaffected","barr1unaffected"],["gobunaffected","barr2unaffected"]]
from os import listdir
import json
import argparse
import pandas as pd


def json_dict_wnodes(filepath):
    json_file=open(filepath)
    json_str = json_file.read()
    json_data=pd.io.json.loads(json_str)
    allpos_li=[ noded["name"] for noded in json_data["nodes"]]
    json_data=json_data["edges"]
    json_d={}
    num_fr=0
    for (int_d) in json_data:
        json_d[(int_d['name1'],int_d['name2'])]=int_d['frames']
        edg_max=max(int_d['frames'])
        if (edg_max > num_fr):
            num_fr=edg_max
    return(json_d,allpos_li)
    

def create_new_json(mypath,json_name,edge_entries,node_entries):
    newpath=mypath+json_name
    print(newpath)
    with open(newpath,"w") as of:
        of.write("{\n")
        of.write("  \"edges\": [\n")
        of.write(",\n".join(edge_entries))
        of.write("\n")
        of.write("  ],\n")
        of.write("  \"nodes\": [\n")
        of.write(",\n".join(node_entries))
        of.write("\n")
        of.write("  ]\n")      
        of.write("}\n")   

def substr_plot_together(owt_filename,omt_filename,helix_colors,in_path,out_path,out_json):
    """Creates one plot with the difference data instead of a plot with interactions only in case A + a plot with interactions only in case B"""
    (owt,allpos_li)=json_dict_wnodes(in_path+owt_filename)
    (omt,allpos_li)=json_dict_wnodes(in_path+omt_filename)
    
    edge_entries=[]
    node_entries=set()
    wt_set=set(owt.keys())
    mt_set=set(omt.keys())
    all_set=wt_set.union(mt_set);

    numfr=len(all_set)
    i=0
    for intpair in all_set:
        if intpair in owt:
            wt_n=len(owt[intpair])
        else:
            wt_n=0
        if intpair in omt:
            mt_n=len(omt[intpair])
        else:
            mt_n=0            
        diff=wt_n - mt_n
        if diff != 0:
            framelist=list(range(0,abs(diff)))
            edge_entries.append("    {\"name1\":\"%s\", \"name2\":\"%s\", \"frames\":%s}"%(intpair[0],intpair[1],str(framelist)))
            node_entries.add("      { \"name\": \"%s\", \"color\": \"%s\" }"%(intpair[0],helix_colors[int(intpair[0].split(".",1)[0])]))
            node_entries.add("      { \"name\": \"%s\", \"color\": \"%s\" }"%(intpair[1],helix_colors[int(intpair[1].split(".",1)[0])]))
        if ((i/numfr)*100 in [10,20,30,40,50,60,70,80,90]):
            print((i/numfr)*100)
        
        i+=1
    create_new_json(out_path,out_json,edge_entries,node_entries)
   
def substr_plot_separated(owt_filename,omt_filename,helix_colors,in_path,out_path,out_jsonWT,out_jsonMT,threshold,correctMax=False):
    """Creates one plot a plot with interactions only in case A (ex: wt) + a plot with interactions only in case B (ex: mt)"""
    (owt,allpos_li)=json_dict_wnodes(in_path+owt_filename)
    (omt,allpos_li)=json_dict_wnodes(in_path+omt_filename)
    
    diff_dict_wt={}
    diff_dict_mt={}
    edge_entries_wt=[]
    edge_entries_mt=[]
    node_entries_wt=set()
    node_entries_mt=set()
    wt_set=set(owt.keys())
    mt_set=set(omt.keys())
    all_set=wt_set.union(mt_set);
    used_pos_wt=set()
    used_pos_mt=set()
    
    for intpair in all_set:
        if intpair in owt:
            wt_n=len(owt[intpair])
        else:
            wt_n=0
        if intpair in omt:
            mt_n=len(omt[intpair])
        else:
            mt_n=0            
        diff=wt_n - mt_n
        if diff > 0:
            diff_dict_wt[intpair]=abs(diff)
        elif diff < 0:
            diff_dict_mt[intpair]=abs(diff)
        (p1,p2)=intpair


    max_diff=max((max(diff_dict_wt.values()), max(diff_dict_mt.values()) ))
    for (intpair,diff) in diff_dict_wt.items():
        if correctMax:
            corr_diff= round((abs(diff)/max_diff)*100)
        else:
            corr_diff=diff
        if threshold and corr_diff < threshold*10:
            print("skipping position smaller than threshold")
            continue
        framelist=list(range(0,corr_diff))
        edge_entries_wt.append("    {\"name1\":\"%s\", \"name2\":\"%s\", \"frames\":%s}"%(intpair[0],intpair[1],str(framelist)))
        node_entries_wt.add("      { \"name\": \"%s\", \"color\": \"%s\" }"%(intpair[0],helix_colors[int(intpair[0].split(".",1)[0])]))
        node_entries_wt.add("      { \"name\": \"%s\", \"color\": \"%s\" }"%(intpair[1],helix_colors[int(intpair[1].split(".",1)[0])]))    
        (p1,p2)=intpair
        used_pos_wt.add(p1)
        used_pos_wt.add(p2)
        

    for (intpair,diff) in diff_dict_mt.items():
        if correctMax:
            corr_diff= round((abs(diff)/max_diff)*100)
        else:
            corr_diff=diff
        if threshold and corr_diff < threshold*10:
            print("skipping position smaller than threshold")
            continue
        framelist=list(range(0,corr_diff))
        edge_entries_mt.append("    {\"name1\":\"%s\", \"name2\":\"%s\", \"frames\":%s}"%(intpair[0],intpair[1],str(framelist)))
        node_entries_mt.add("      { \"name\": \"%s\", \"color\": \"%s\" }"%(intpair[0],helix_colors[int(intpair[0].split(".",1)[0])]))
        node_entries_mt.add("      { \"name\": \"%s\", \"color\": \"%s\" }"%(intpair[1],helix_colors[int(intpair[1].split(".",1)[0])]))        
        (p1,p2)=intpair
        used_pos_mt.add(p1)
        used_pos_mt.add(p2)
    
    missing_pos_wt=set(allpos_li) - used_pos_wt
    missing_pos_mt=set(allpos_li) - used_pos_mt
    for pos in missing_pos_wt:
        node_entries_wt.add("      { \"name\": \"%s\", \"color\": \"%s\" }"%(pos,helix_colors[int(pos[0].split(".",1)[0])]))
    for pos in missing_pos_mt:
        node_entries_mt.add("      { \"name\": \"%s\", \"color\": \"%s\" }"%(pos,helix_colors[int(pos[0].split(".",1)[0])]))
    
    create_new_json(out_path,out_jsonWT,edge_entries_wt,node_entries_wt)
    create_new_json(out_path,out_jsonMT,edge_entries_mt,node_entries_mt)
    
    
def restricted_lol(lol):
    for l in lol:
        if type(l)==list:
            if len(l) > 3:
                raise argparse.ArgumentTypeError("Inner lists must contain max 3 elements.")
            elif len(l) == 3:
                x=l[2]      
                x = float(x)
                if x < 0.0 or x > 1.0:
                    raise argparse.ArgumentTypeError("Threshold %r not in range [0.0, 1.0]"%(x,))
        else:
            raise argparse.ArgumentTypeError("Input must be a list of lists.")
    return lol

    
parser = argparse.ArgumentParser(description="""
This takes a list containing pairs of json files. For each pair (A and B) creates a new json showing:
The interactions found in A but not in B (freq A - freq B taking only positive values)
The interactions found in B but not in A (freq B - freq A taking only positive values)
""")
parser.add_argument('-i', '--input_path',
    dest = "mypath",
    action = "store",
    default = ".",
    type=str,
    help = "Input path of the directory where the input JSON files are.")
   
parser.add_argument('-o', '--output_path',
    dest = "outpath",
    action = "store",
    default = False,
    type=str,
    help = "Output path where the new JSON files will be created.")
    
parser.add_argument('-p', '--pairs',
    dest = "to_compare",
    action = "store",
    required=True,
    type=restricted_lol,
    help = "List of json pairs to be substracted. Ex: [['A','B'],['B','C']]. The elements of each pair must match the name of a json file in the input path (ex: element 'A' corresponds to 'A.json'). It is possible to add as third element in the list a threshold (float from 0 to 1) for each group, (Ex: [['A','B', 0.1],['B','C', 0.15]]) to filter out interaction differences below that threshold.")
    
options = parser.parse_args()
in_path = options.mypath
out_path = options.outpath

if not out_path:
    out_path=in_path+"substr/"
if not path.isdir(out_path):
    makedirs(out_path)

helix_colors = {1:"#78C5D5",12:"#5FB0BF",2:"#459BA8",23:"#5FAF88",3:"#79C268",34:"#9FCD58",4:"#C5D747",45:"#DDD742",5:"#F5D63D",56:"#F3B138",6:"#F18C32",67:"#ED7A6A",7:"#E868A1",78:"#D466A4",8:"#BF63A6"}


to_compare=options.to_compare

for pair_info in to_compare:
    if len(pair_info)==3:
        (group1,group2,threshold)=pair_info
    else:
        (group1,group2)=pair_info[:2]
        threshold=False
    owt_filename=group1+".json"
    omt_filename=group2+".json"
    out_jsonWT=group1+"-"+group2+".json"
    out_jsonMT=group2+"-"+group1+".json"

    substr_plot_separated(owt_filename,omt_filename,helix_colors,in_path,out_path,out_jsonWT,out_jsonMT,threshold)



    

