from sys import argv,exit
import pandas as pd
from  numpy import array
from json import loads, dump
from  plotly.figure_factory import create_dendrogram
import numpy as np
import os
import re
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import Label, HoverTool, TapTool, CustomJS, BasicTicker, ColorBar, ColumnDataSource, LinearColorMapper, PrintfTickFormatter
from bokeh.transform import transform
from math import ceil
from scipy.cluster.hierarchy import linkage, fcluster, cut_tree

print("functions imported")

# Be careful with this!!! Put here only because some false-positive warnings from pandas
import warnings
warnings.filterwarnings('ignore')

#############
### Functions
#############


def json_dict(path):
    """Converts json file to pyhton dict."""
    json_file=open(path)
    json_str = json_file.read()
    json_data = loads(json_str)
    return json_data

def improve_receptor_names(df_ts,compl_data):
    """
    Parses the dataframe to create the data source of the plot. When defining a name for each dynamics entry: if there is any other dynamics in the 
    datadrame that is created fromt he same pdb id and ligand, all these dynamics will indicate the dynamics id
    """
    recept_info={}
    recept_info_order={
        "upname":0,
        "lig_sname":1,
        "dyn_id":2,
        "prot_id":3,
        "comp_id":4,
        "prot_lname":5,
        "pdb_id":6,
        "lig_lname":7,
        "struc_fname":8,
        "struc_f":9,
        "traj_fnames":10,
        "traj_f":11,
        "delta":12,
        "receptor_unique_name":13,
        'gpcr_class':14
    }
    dyns_by_receptor={}
    index_dict={}
    dyn_gpcr_pdb={}
    for recept_id in df_ts['Id']:
        dyn_id=recept_id
        upname=compl_data[recept_id]["up_name"]
        lig_sname=compl_data[recept_id]["lig_sname"]
        lig_lname=compl_data[recept_id]["lig_lname"]
        prot_id=compl_data[recept_id]["prot_id"]
        comp_id=compl_data[recept_id]["comp_id"]
        prot_lname=compl_data[recept_id]["prot_lname"]
        pdb_id=compl_data[recept_id]["pdb_id"]
        struc_fname=compl_data[recept_id]["struc_fname"]
        struc_f=compl_data[recept_id]["struc_f"]
        traj_fnames=compl_data[recept_id]["traj_fnames"]
        traj_f=compl_data[recept_id]["traj_f"]
        delta=compl_data[recept_id]["delta"]
        sim__fullname="%s (%s) (%s)" % (upname,pdb_id,dyn_id)
        gpcr_class = compl_data[recept_id]["class"]
        
        if pdb_id:
            prot_lig=(pdb_id,lig_sname)
        else:
            prot_lig=(upname,lig_sname)

        recept_name=prot_lname+" ("+prot_lig[0]+")"
        recept_info[dyn_id]=[upname, lig_sname,dyn_id,prot_id,comp_id,prot_lname,pdb_id,lig_lname,struc_fname,struc_f,traj_fnames,traj_f,delta,sim__fullname,gpcr_class]
        index_dict[recept_id]=recept_name 
        dyn_gpcr_pdb[recept_name]=compl_data[recept_id]["gpcr_pdb"]

    df_ts['Name'] = list(map(lambda x: index_dict[x], df_ts['Id']))
    df_ts['shortName'] = list(map(lambda x: recept_info[x][13], df_ts['Id']))
    return(recept_info,recept_info_order,df_ts,dyn_gpcr_pdb,index_dict)

def filter_same_helix(df):
    """
    Remove same-helix interaction pairs from dataframe. Returns same dataframe
    """
    helixpattern = re.compile(r"""^(..)\w+\s+\1""")#For detecting same-helix contacts, the ones like 1.22x22 1.54x54
    helixfilter = df['Position'].str.contains(helixpattern)
    df = df[~helixfilter]
    return(df)

def split_by_standard(df, compl_data):
    """
    Return two dataframes, one with standard simulations and one with no-standard 
    """
    gpcrmd_people = ['Amoralpa11', 'mariona_tf', 'david', 'tste','ismresp']
    nonstandard_simulations = set(('dyn4', 'dyn5', 'dyn6', 'dyn7', 'dyn8', 'dyn9', 'dyn10'))

    #Find non-standard simulations
    for dyn in compl_data:
        if 'user' not in compl_data[dyn]:#To avoid obsolete entries
            nonstandard_simulations.add(dyn)            
        elif compl_data[dyn]['user'] not in gpcrmd_people:
            nonstandard_simulations.add(dyn)
            
    df_standard = df[df.columns[~df.columns.isin(nonstandard_simulations)]]
    
    return(df, df_standard)

def filter_lowfreq(df, main_itype):
    """
    Filter low-frequency interactions. Remove all position pairs not having at least 2 simulations
    with more than 50% interaction frequency
    """
    df_purged = df.drop(['itype','Position','Position1','Position2'], 1)
    df['above_30perc'] = (df_purged > 50).sum(1)
    pos_topreserve = set(df['Position'][ (df['above_30perc'] > 1) & (df['itype'] == main_itype) ])
    df.drop('above_30perc', 1, inplace = True)
    df = df[df['Position'].isin(pos_topreserve)]
     
    return(df)

def set_new_axis(df):
    """
    Substitute the original position 3-nomenclatures single line format (1x23x23x24x24 1x23x23x24x24)
    to 3-nomenclatures multiline format (1x\n23\n23\n24\n24\n\n1x\n23\n23\n24\n24)(similar to gpcrdb).
    """
    def new_cell(cell):
        cell = cell.replace(' ','\n\n')
        cell = cell.replace('x','\n')
        cell = re.sub(pattern_pos1, r"\1x\n", cell)
        cell = re.sub(pattern_pos2, r"\n\n\1x\n", cell)
        return cell
    
    pattern_pos1 = re.compile(r"^(\d+)\n")
    pattern_pos2 = re.compile(r"\n\n(\d+)\n")
    df['Position'] = df['Position'].apply(new_cell)
    return df

def stack_matrix(df, itypes):
    """
    Converts matrix in a stacked version: columns now are Position, dynid and itypes and rows all 
    frequencies by position and dyind
    """
    df_ts = 1
    for itype in itypes:
        df_type = df[df["itype"] == itype]
        df_type.drop('itype', 1, inplace = True)
        df_type.set_index('Position', inplace = True)
        df_ts_type = df_type.transpose().stack().rename(itype).reset_index()
        if type(df_ts) == int:
            df_ts = df_ts_type
        else:
            df_ts = pd.merge( df_ts, df_ts_type, how ='outer', on=["level_0", 'Position'])        
    
    df_ts = df_ts.fillna("0.0") # Fill posible NaN in file

    df_ts.rename(columns={"level_0": "Id"}, inplace=True)

    return df_ts
    
def adapt_to_marionas(df):
    """
    This function comprises a series of operations to adapt the new tsv format to Mariona's original scripts.
    Also returns a dictionary
    """

    #Merging toghether both contacting aminoacid Ids
    df['Position'] = df.Position1.str.cat(df.Position2, sep = " ")

    # Passing frequencies from decimal to percentage
    nocols = (("Position1","Position2","itype","Position"))
    for colname in df:
        if colname not in nocols:
            df[colname] = df[[colname]].apply(lambda x: x*100)

    return(df)

def flareplot_template(df, jsonpath):
    """
    Create a pseudoflareplot input json with no interactions, but with all avalible positions.
    It will be used later as a template to create the top interactions flareplots.  
    """
    #'track' entry for json file: each track is a node (position) in the flareplot
    helix_colors = {'1':"#78C5D5",'12':"#5FB0BF",'2':"#459BA8",'23':"#5FAF88",'3':"#79C268",'34':"#9FCD58",'4':"#C5D747",'45':"#DDD742",'5':"#F5D63D",'56':"#F3B138",'6':"#F18C32",'67':"#ED7A6A",'7':"#E868A1",'78':"#D466A4",'8':"#BF63A6",'Ligand--1':'#FF5050', 'Ligand': '#FF5050'}        
    allpos = set(df['Position1']).union(set(df['Position2']))
    tracks = [{
        'trackLabel': 'Degree centrality',
        "trackProperties": []
    }]
    trees = [{
        'treeLabel': 'Helices',
        'treePaths': []
    }]
    
    #Add ligand
    tracks[0]['trackProperties'].append({
        'color' : "#FF5050",
        'size' : 1.0,
        'nodeName': 'Ligand'
    })
    trees[0]['treePaths'].append([1, 'Ligand'])
    
    setpos = set()
    for multipos in allpos:
        if multipos.startswith('Ligand'):
            continue
            
        split_pos = multipos.split('x')
        for pos in split_pos:
            if split_pos.index(pos) == 0:
                helix = pos
                color = helix_colors[helix]
            else:                
                real_pos = helix+'x'+pos
                if real_pos not in setpos:
                    trackprop = {
                        'color' : color,
                        'size' : 1.0,
                        'nodeName': real_pos
                    }
                    if len(helix) == 2:
                        newhelix = int(helix[0]) + int(helix[1])
                        trees[0]['treePaths'].append([newhelix, real_pos])
                    else:
                        newhelix = int(helix)*2
                        trees[0]['treePaths'].append([newhelix, real_pos])

                    tracks[0]['trackProperties'].append(trackprop)
                    setpos.add(real_pos)

    #Sort trees
    treePaths_sorted = sorted(list(trees[0]['treePaths']), key=lambda l: (l[0],l[1]))
    treePaths_sorted = [ str(x[0])+"."+x[1] for x in treePaths_sorted ]
    trees[0]['treePaths'] = treePaths_sorted
    
    #Output jsondict to store
    jsondict = { 'trees' : trees, 'tracks' : tracks }
    
    # Store json file
    jsonpath = basepath + "template.json" 
    with open(jsonpath, 'w') as jsonfile:
        dump(jsondict, jsonfile, ensure_ascii=False, indent = 4)


def dyn_flareplots(df, folderpath, dyn_list, itype, flare_template = False):
    """
    Create top20 interaction jsons for each simulation. Needed for customized selection flareplots.
    """
    os.makedirs(folderpath, exist_ok = True)
    colors = ['#800000', '#860000', '#8c0000', '#930000', '#990000', '#9f0000', '#a60000', '#ac0000', '#b20000', '#b90000', '#bf0000', '#c50000', '#cc0000', '#d20000', '#d80000', '#df0000', '#e50000', '#eb0000', '#f20000', '#f80000', '#ff0000', '#ff0700', '#ff0e00', '#ff1500', '#ff1c00', '#ff2300', '#ff2a00', '#ff3100', '#ff3800', '#ff3f00', '#ff4600', '#ff4d00', '#ff5400', '#ff5b00', '#ff6200', '#ff6900', '#ff7000', '#ff7700', '#ff7e00', '#ff8500', '#ff8c00', '#ff9100', '#ff9700', '#ff9d00', '#ffa300', '#ffa800', '#ffae00', '#ffb400', '#ffba00', '#ffbf00', '#ffc500', '#ffcb00', '#ffd100', '#ffd600', '#ffdc00', '#ffe200', '#ffe800', '#ffed00', '#fff300', '#fff900', '#ffff00', '#f2ff00', '#e5ff00', '#d8ff00', '#ccff00', '#bfff00', '#b2ff00', '#a5ff00', '#99ff00', '#8cff00', '#7fff00', '#72ff00', '#66ff00', '#59ff00', '#4cff00', '#3fff00', '#33ff00', '#26ff00', '#19ff00', '#0cff00', '#00ff00', '#0afc0a', '#15fa15', '#1ff81f', '#2af62a', '#34f434', '#3ff13f', '#49ef49', '#54ed54', '#5eeb5e', '#69e969', '#74e674', '#7ee47e', '#89e289', '#93e093', '#9ede9e', '#a8dba8', '#b3d9b3', '#bdd7bd', '#c8d5c8', '#d3d3d3']
    for dyn in dyn_list:

        # Select top interactions based on its mean frequency. Also asign color based on mean value
        df_clust = df.filter(items = [dyn, 'APosition1', 'APosition2', 'BPosition1', 'BPosition2','CPosition1', 'CPosition2','FPosition1', 'FPosition2',])
        df_clust['color'] = df_clust[dyn].apply(lambda x: colors[100-round(x*100/100)]) #There are 101 colors avalible in list

        #Filter top 5 in df_clust
        df_clust = df_clust.nlargest(20, dyn)

        # 'Edge' entry for json file
        df_dict = pd.DataFrame(columns = ["name1", "name2", "frames"])
        df_dict['name1'] = df_clust['APosition1'] 
        df_dict['name2'] = df_clust['APosition2']
        df_dict['frames'] = [[1]]*len(df_dict)
        df_dict['color'] = df_clust['color']
        df_dict['value'] = df_clust[dyn]
        edges = df_dict.to_dict(orient="records")

        # Appending edges to flare plot template, if any submitted
        if flare_template:
            flare_template['edges'] = edges
            jsondict = flare_template
        else:
            jsondict = { 'edges' : edges }

        #'Edge' multi-entries, based on the 4 GPCR nomenclatures
        for leter in ['A', 'B', 'C', 'F']:
            df_dict = pd.DataFrame(columns = ["name1", "name2", "frames"])
            df_dict['name1'] = df_clust[leter+'Position1'] 
            df_dict['name2'] = df_clust[leter+'Position2']
            df_dict['frames'] = [[1]]*len(df_dict)
            df_dict['color'] = df_clust['color']
            df_dict['value'] = df_clust[dyn]
            leter_edges = df_dict.to_dict(orient="records")

            #Appending edges
            if flare_template:
                flare_template[leter+'edges'] = leter_edges
                jsondict = flare_template
            else:
                jsondict = { leter+'edges' : leter_edges }

        #Writing json
        jsonpath = folderpath + dyn + "_top.json"
        with open(jsonpath, 'w') as jsonfile:
            dump(jsondict, jsonfile, ensure_ascii=False, indent = 4)

        
def frequencies(df):
    """
    Creates an interaction frequency numpy matrix from 
    """

    # Transpose matrix
    df_t = df.transpose() 
    
    # Create dictionary table with position tuple as keys and interaction-by-simulation-freq array as value
    freq_table = { tuple(col.split("\n\n")):list(df_t[col].values) for col in df_t }
        
    # Convert previous dictionary to numpy array, and traspose it
    freq_matrix = (array([freq_table[(r1, r2)] for (r1, r2) in freq_table])).T

    # Reorder according to clustering
    return freq_matrix

def clustering(clusters, dend_matrix, labels, linkagefun):
    """
    Find the color threshold needed for the dendrogram to have "clusters" number of clusters. 
    Also define to which cluster each simulation belongs
    """
    Z = linkagefun(dend_matrix)
    color_threshold = Z[-1*clusters][2]+0.0000000001 #Cut slightly above the tree node
    
    # Defining to which cluster belongs to each simulation
    T = fcluster(Z, t=clusters, criterion='maxclust')
    clustdict = { "cluster" + str(clust) : [] for clust in T }
    for sim,clust in zip(labels,T):
         clustdict["cluster" + str(clust)].append(sim)

    return(color_threshold, clustdict)

def black_or_white(bgcolor):
    """
    Text with this color background should be in black or white font?
    """
    ary_bgcolors = re.findall(r"[\w']+", bgcolor)
    R = int(ary_bgcolors[1])
    G = int(ary_bgcolors[2])
    B = int(ary_bgcolors[3])
    Lumi = (sum([R,G,B])/3)

    if Lumi > 125:
        colorfont = 'rgb(0,0,0)'
    else:
        colorfont = 'rgb(255,255,255)'

    return colorfont

def hoverlabels_axis(fig, recept_info, recept_info_order, default_color, annotations = []):
    """
    Makes hover labels from figure correspond to Y-axis labels, and make Y-axis labels correspond to dendrogram
    colors.
    """
    
    def define_annotation_list(y_pos, bgcolor, text, colorfont, name, hovertext):
        """
        Create a list of annotation objects. This annotations are meant to replace the axis labels as names of simulations
        """
        return dict(
            x = -0,
            y = y_pos,
            xanchor = 'left',
            text = text,
            hovertext = hovertext,
            showarrow = False,
            captureevents = True,
            bgcolor = bgcolor,
            font = { 'size' : 12, 'color' : colorfont },
            height = 14
        )

    def prepare_entry(hoverentry, fig, ypos, name_index, ligname_index, recept_info, pdb_index):
        """
        Creates xaxis-annotations and hoverlabels based on the information contained by this dendrogram branch
        """                
        dynid = dendro_leaves[int((ypos-5)/10)]
        nodyn_id = dynid.replace('dyn','')
        pdbcode = recept_info[dynid][pdb_index]
        simname = recept_info[dynid][name_index]
        ligname = recept_info[dynid][ligname_index]
        bgcolor = hoverentry['marker']['color']
        anot_text = "%s (%s)<b style='display: none'>%s</b>" % (simname, pdbcode, dynid)
        hovertext = str("complex with %s (dynID: %s)" % (ligname, nodyn_id)) if (ligname) else  str("apoform (dynID: %s)" % (nodyn_id))

        # Annotation to corresponding simulation
        colorfont = black_or_white(bgcolor)
        annotations.append(define_annotation_list(ypos, bgcolor, anot_text, colorfont, dynid, hovertext))

        return(fig, annotations)
    
    dendro_leaves = fig['layout']['yaxis']['ticktext']

    # Adapting hovertool to what I want from it
    name_index = recept_info_order['upname']
    pdb_index = recept_info_order['pdb_id']
    ligname_index = recept_info_order['lig_sname']
    occuped_positions = dict()
    for hoverentry in fig['data']:

        # Silenciate all default hover entries. 
        hoverentry['hoverinfo'] = 'none'
        
        # If entry reaches end of plot (not intermediate node)
        if (hoverentry['x'][0] == -0) and (int(hoverentry['y'][0])%10 == 5):
            
            #If entry Y-corodinate is not already occuped by another one, or if it's wrongly occuped by a middle dendrogram which reaches bottom of plot
            if (hoverentry['y'][0] not in occuped_positions) or (hoverentry['marker']['color'] != default_color):

                occuped_positions[hoverentry['y'][0]] = hoverentry['marker']['color']
                (fig, annotations) = prepare_entry(hoverentry, fig, hoverentry['y'][0], name_index, ligname_index, recept_info, pdb_index)

                #If this entry reaches two labels at the same time (terminal U node), create yet another entry
                if (hoverentry['x'][3] == -0) and (int(hoverentry['y'][3])%10 == 5): 
                    (fig, annotations) = prepare_entry(hoverentry, fig, hoverentry['y'][3], name_index, ligname_index, recept_info, pdb_index)

    fig['layout']['annotations'] = annotations

    return fig

def annotate_clusters(fig, default_color = ""):
    """
    Put an annotation the nodes on top of clusters
    """
    prevcolor = ""
    min_x = 0
    clustcount = -1
    clustcoords = []
    xcords = []
    annotations = []
    taken_ycords = set()
    
    # Sorting by y coordenate (needed for later)
    fig['data'] = sorted(fig['data'], key=lambda x: x['y'][0])
    
    #Iterate over all vector forms in the figure and find the ones that are cluster tops
    for entry in fig['data']:

        currentcolor = entry['marker']['color']
        current_min_x = min(entry['x'])
        current_max_x = max(entry['x'])
        # For skipping upper-dendrogram, non-cluster branches
        if (currentcolor == default_color) and ((max(entry['x']) != -0.0) or (entry['y'][0]%10 == 0)):
            continue

        #Check for false 'single-node, default color' clusters
        if ((entry['y'][0] in taken_ycords) or (entry['y'][0] in taken_ycords)) and (currentcolor == default_color):
            continue
            
        # If there has been a color change ...
        #... OR it is a single-node cluster
        if (prevcolor != currentcolor) or ((currentcolor == default_color) and (max(entry['x']) == -0.0) ):
            clustcount += 1
            xcords.append("")
            min_x = 0
            clustcoords.append({})
            
        # If new entry is higher (inside the tree) than previous, select as candidate for cluster node        
        if current_min_x <= min_x:

            min_x = current_min_x
            clustcoords[clustcount]['clusnode_x'] = entry['x'][1]
            xcords[clustcount] = (clustcoords[clustcount]['clusnode_x'])
            clustcoords[clustcount]['clusnode_y'] = (entry['y'][1] + entry['y'][2])/2
            clustcoords[clustcount]['clustnumber'] = clustcount
            clustcoords[clustcount]['color'] = currentcolor
            clustcoords[clustcount]['xanchor'] = 'right'
            
            #For single-branch clusters
            if (currentcolor == default_color) and (current_max_x == -0): 
                index_x = np.where(entry['x'] == current_max_x) 
                clustcoords[clustcount]['clusnode_y'] = entry['y'][index_x][0]
                #If the branch contains two single-node clusters(very rare case), append another cluster label
                if (entry['x'][0] == -0) and (entry['x'][3] == -0) and (entry['y'][2]%10 != 0):
                    clustcount += 1
                    clustcoords.append({
                        'clusnode_x' : entry['x'][2],
                        'clusnode_y' : entry['y'][2],
                        'clustnumber' : clustcount,
                        'color' : currentcolor,
                        'xanchor' : 'right'
                   })
                    xcords.append(clustcoords[clustcount]['clusnode_x'])
        
        #Add occuped y-coords
        for ycord in entry['y']:
            if ycord%10 == 5:
                taken_ycords.add(ycord)

        prevcolor = currentcolor
    
    # Annotate with "clusterN" the vector forms found in previous loop
    for clust in clustcoords:
        colorfont = black_or_white(clust['color'])
        annotations.append(dict(
            x = clust['clusnode_x'],
            y = clust['clusnode_y'],
            xanchor = clust['xanchor'],
            text = "cluster " + str(clust['clustnumber']+1),
            showarrow = False,
            bgcolor = clust['color'],
            font = { 'size' : 12, 'color' : colorfont },
            height = 14
        ))

    return annotations

def flareplot_json(df, clustdict, folderpath, flare_template = False):
    """
    Create json entries for significative positions (top10 mean frequency) of each cluster produced
    """
    os.makedirs(folderpath,  exist_ok = True)
    colors = ['#800000', '#860000', '#8c0000', '#930000', '#990000', '#9f0000', '#a60000', '#ac0000', '#b20000', '#b90000', '#bf0000', '#c50000', '#cc0000', '#d20000', '#d80000', '#df0000', '#e50000', '#eb0000', '#f20000', '#f80000', '#ff0000', '#ff0700', '#ff0e00', '#ff1500', '#ff1c00', '#ff2300', '#ff2a00', '#ff3100', '#ff3800', '#ff3f00', '#ff4600', '#ff4d00', '#ff5400', '#ff5b00', '#ff6200', '#ff6900', '#ff7000', '#ff7700', '#ff7e00', '#ff8500', '#ff8c00', '#ff9100', '#ff9700', '#ff9d00', '#ffa300', '#ffa800', '#ffae00', '#ffb400', '#ffba00', '#ffbf00', '#ffc500', '#ffcb00', '#ffd100', '#ffd600', '#ffdc00', '#ffe200', '#ffe800', '#ffed00', '#fff300', '#fff900', '#ffff00', '#f2ff00', '#e5ff00', '#d8ff00', '#ccff00', '#bfff00', '#b2ff00', '#a5ff00', '#99ff00', '#8cff00', '#7fff00', '#72ff00', '#66ff00', '#59ff00', '#4cff00', '#3fff00', '#33ff00', '#26ff00', '#19ff00', '#0cff00', '#00ff00', '#0afc0a', '#15fa15', '#1ff81f', '#2af62a', '#34f434', '#3ff13f', '#49ef49', '#54ed54', '#5eeb5e', '#69e969', '#74e674', '#7ee47e', '#89e289', '#93e093', '#9ede9e', '#a8dba8', '#b3d9b3', '#bdd7bd', '#c8d5c8', '#d3d3d3']    
    for clust in clustdict.keys():

        # Select top interactions based on its mean frequency. Also asign color based on mean value
        df_clust = df.filter(items = clustdict[clust] + ['APosition1', 'APosition2', 'BPosition1', 'BPosition2','CPosition1', 'CPosition2','FPosition1', 'FPosition2',])
        df_clust['mean'] = df_clust.mean(axis = 1, numeric_only = True)
        mean_threshold = min(df_clust['mean'].nlargest(20).tolist())
        df_clust['color'] = df_clust['mean'].apply(lambda x: colors[100-round(x*100/100)]) #There are 101 colors avalible in list

        #Filter top 5 in df_clust
        df_clust = df_clust.nlargest(20,'mean')

        # 'Edge' entry for json file
        df_dict = pd.DataFrame(columns = ["name1", "name2", "frames"])
        df_dict['name1'] = df_clust['APosition1'] 
        df_dict['name2'] = df_clust['APosition2']
        df_dict['frames'] = [[1]]*len(df_dict)
        df_dict['color'] = df_clust['color']
        df_dict['value'] = df_clust['mean']
        edges = df_dict.to_dict(orient="records")

        # Appending edges to flare plot template, if any submitted
        if flare_template:
            flare_template['edges'] = edges
            jsondict = flare_template
        else:
            jsondict = { 'edges' : edges }

        #'Edge' multi-entries, based on the 4 GPCR nomenclatures
        for leter in ['A', 'B', 'C', 'F']:
            df_dict = pd.DataFrame(columns = ["name1", "name2", "frames"])
            df_dict['name1'] = df_clust[leter+'Position1'] 
            df_dict['name2'] = df_clust[leter+'Position2']
            df_dict['frames'] = [[1]]*len(df_dict)
            df_dict['color'] = df_clust['color']
            df_dict['value'] = df_clust['mean']
            leter_edges = df_dict.to_dict(orient="records")

            #Appending edges
            if flare_template:
                flare_template[leter+'edges'] = leter_edges
                jsondict = flare_template
            else:
                jsondict = { leter+'edges' : leter_edges }

        #Writing json
        jsonpath = folderpath + clust + ".json"
        with open(jsonpath, 'w') as jsonfile:
            dump(jsondict, jsonfile, ensure_ascii=False, indent = 4)

def dendrogram_clustering(dend_matrix, labels, height, width, filename, clusters, recept_info, recept_info_order): 

    # Define linkage function (we'll be using the default one for plotly). 
    linkagefun=lambda x: linkage(x, 'complete')
    (thres,clustdict) = clustering(clusters, dend_matrix, labels, linkagefun)

    # Create color scale from the "category20" color scale. Not working because color_scale plotly option is inoperative
    colors_category20 = ['rgb(31, 119, 180)', 'rgb(174, 199, 232)', 'rgb(255, 127, 14)', 'rgb(255, 187, 120)', 'rgb(44, 160, 44)', 'rgb(152, 223, 138)', 'rgb(214, 39, 40)', 'rgb(255, 152, 150)', 'rgb(148, 103, 189)', 'rgb(197, 176, 213)', 'rgb(140, 86, 75)', 'rgb(196, 156, 148)', 'rgb(227, 119, 194)', 'rgb(247, 182, 210)', 'rgb(127, 127, 127)', 'rgb(199, 199, 199)', 'rgb(188, 189, 34)', 'rgb(219, 219, 141)', 'rgb(23, 190, 207)', 'rgb(158, 218, 229)']
    colors = colors_category20[0:clusters]

    # Setting figures
    fig = create_dendrogram(
        dend_matrix,
        orientation='right',
        labels=labels,
        linkagefun=linkagefun,
        color_threshold = thres,
        hovertext = labels,
    )

    fig['layout'].update({
        'width':width, 
        'height':height,
        'hoverdistance' : 10,
        'plot_bgcolor' : "#FFFFFF"
        })

    fig['layout']['margin'].update({
        'r' : 150,
        'l' : 100,
        't' : 200,#This problem with the phantom margin has to be solved at some point
        'b' : 0,
        'pad' : 0,
        'autoexpand' : False,
        })

    fig['layout']['xaxis'].update({
        'showline': False,
        'showticklabels': False,
        'ticks' : '',
        'fixedrange' : True,
        'automargin' : False
        })

    fig['layout']['yaxis'].update({
        'side' : 'right',
        'showline': False,
        'ticks' : '',
        'tickfont' : {
            'size' : 15,
            'color' : 'white'
            },
        'fixedrange' : True,
        'automargin' : False
        })

    #Annotating cluster nodes
    annotations = annotate_clusters(fig, 'rgb(0,116,217)') # Default color for tree

    # Correcting hoverlabels
    fig = hoverlabels_axis(fig, recept_info, recept_info_order, 'rgb(0,116,217)', annotations)

    # Taking order for plot rows
    dendro_leaves = fig['layout']['yaxis']['ticktext']

    # Writing dendrogram on file
    fig.write_html(filename, auto_open=False,config={
        "displayModeBar": "hover",
        "showAxisDragHandles": False,
        "showAxisRangeEntryBoxes": False,
        "scrollZoom": False,
        "showTips" : False,
        "modeBarButtons": [["toImage"]]
    })
    return (list(dendro_leaves),clustdict)

def create_dyntoname_file(dyn_dend_order, recept_info, recept_info_order, options_path):
    """
    Creates a list of tuples, each one containing dynID-receptor names pairs
    Needed to display menu dropdown's receptor names in same order as dendrogram
    """
    unique_name_index = recept_info_order['receptor_unique_name']
    dyn_names = [ recept_info[dyn][unique_name_index] for dyn in dyn_dend_order ]
    dyn_to_names = list(zip(dyn_dend_order, list(dyn_names)))
    dyn_to_names.reverse()
    with open(options_path+"name_to_dyn_dict.json", "w") as dyn_names_file:
        dump(dyn_to_names, dyn_names_file, ensure_ascii=False, indent = 4)

def add_restypes(df, compl_data, recept_info, recept_info_order):
    """
    Add a new column with the residue type (ARG, CYS, TRP) of each position in each simulation
    """
    AAs =  {'C': 'CYS', 'D': 'ASP', 'S': 'SER', 'Q': 'GLN', 'K': 'LYS',
     'I': 'ILE', 'P': 'PRO', 'T': 'THR', 'F': 'PHE', 'N': 'ASN', 
     'G': 'GLY', 'H': 'HIS', 'L': 'LEU', 'R': 'ARG', 'W': 'TRP', 
     'A': 'ALA', 'V': 'VAL', 'E': 'GLU', 'Y': 'TYR', 'M': 'MET'}
    GPCRclass_numbers = {'A':1, 'B':2, 'C':3, 'F':4}
    class_index = recept_info_order['gpcr_class']

    def get_restype_and_realpos(dynid_col, pos_col):
        """
        Return residue type of position and the position identifier for this position in this protein
        It's a bit complex, for I need to distinguish which GPCR class nomenclature uses this protein
        """
        restype_list = []
        prot_pos = []
        for dynid,pos in zip(dynid_col, pos_col):
            if pos == 'Ligand':
                restype_list.append('')
                prot_pos.append('Ligand')
            else: 
                GPCRclass_number = GPCRclass_numbers[recept_info[dynid][class_index]] 
                class_pos_array = pos.split('\n')
                class_pos = class_pos_array[0]+class_pos_array[GPCRclass_number]

                if class_pos in compl_data[dynid]['gpcr_pdb']: 
                    restype = compl_data[dynid]['gpcr_pdb'][class_pos][-1]
                    restype_list.append(restype)
                    prot_pos.append(class_pos)
                else:
                    #print("Position %s not found in %s" %(class_pos, dynid)) #Too much output
                    restype_list.append("(N/A)")
                    prot_pos.append(class_pos)

        return(restype_list,prot_pos)

    #Split Position column
    new = df['Position'].str.split("\n\n", n = 1, expand = True)
    df['Position 1'] = new[0]
    df['Position 2'] = new[1]

    #Add residue type and protein position column
    (restype_1, protein_Position_1) = get_restype_and_realpos(df['Id'], df['Position 1'].values)
    df['restype_1'] = restype_1
    df['protein_Position 1'] = protein_Position_1
    (restype_2, protein_Position_2) = get_restype_and_realpos(df['Id'], df['Position 2'].values)
    df['restype_2'] = restype_2
    df['protein_Position 2'] = protein_Position_2
    
    df['restypes'] = df['restype_1'] +" "+ df['restype_2']  
    df['protein_Position'] = df['protein_Position 1'] +" "+ df['protein_Position 2']
    df['restypePosition'] = df['restype_1'] + df['protein_Position 1'] + " " + df['restype_2'] + df['protein_Position 2']
    
    #Drop Position, proteinPosition and restype columns once they are not needed
    df.drop(columns = ['Position 1','Position 2','restype_1','restype_2','protein_Position 1','protein_Position 2'], inplace = True)
  
    return df

def new_columns(df, itype):
    """
    Adding Position1 and Position2 columns from A nomenclature system to dataframe, in subsitution of
    Position column, which included both.
    """

    def split_by_class(position_col):
        """
        Split 2x\n26\n12\n12\n12 into 2x26 2x12 2x12 2x12 2x12
        """
        name = position_col.name
        positions = position_col.values
        pos_by_class = {"A"+name :[], "B"+name :[], "C"+name :[], "F"+name :[]}
        number_letter = ["0",'A','B', 'C', 'F']
        for pos in positions:
            splited_pos = pos.split("x")
            for i in [1,2,3,4]:
                if pos == "Ligand":
                    pos_by_class[number_letter[i]+name].append("Ligand")
                else:
                    pos_by_class[number_letter[i]+name].append(splited_pos[0]+"x"+splited_pos[i])

        return(pd.DataFrame.from_dict(pos_by_class))

    #Delete non-main itypes
    df = df[df['itype']==itype]
    
    df.reset_index(drop = True, inplace = True)
    df_newcols1 =  split_by_class(df["Position1"])
    df_newcols2 =  split_by_class(df["Position2"])
    df = pd.concat([df, df_newcols1, df_newcols2], axis = 1)

    return df

def sort_simulations(df_ts, dyn_dend_order):
    """
    Sorts the simulations in the dataframe according to the order in the list dyn_dend_order
    """

    # Create a dictionary with the order of each simulation row in the plot 
    dyn_dend_order_dict = { dyn_name : dyn_dend_order.index(dyn_name) for dyn_name in dyn_dend_order }

    # Adding column based in new order recieved from clustering
    df_ts['clust_order'] =  df_ts['Id'].apply(lambda x: dyn_dend_order_dict[x])

    #Sorting by ballesteros Id's (helixloop column) and clustering order
    df_ts['helixloop'] = df_ts['Position'].apply(lambda x: re.sub(r'^(\d)x',r'\g<1>0x',x)) 
    df_ts = df_ts.sort_values(["helixloop",'clust_order'])

    #Drop sort columns once used
    df_ts.drop(['helixloop','clust_order'], axis = 1, inplace = True)
    
    return df_ts

def reverse_positions(df):
    """
    Appends a copy of the dataframe with the Position pair of the interaction being reversed (5x43-7x89 for 7x89-5x43)
    """
    df_rev = df.copy(deep = True)
    divided_positions = df_rev['Position'].str.split('\n\n',expand = True)
    df_rev['Position'] = divided_positions[1] + "\n\n" + divided_positions[0]
    df_double = pd.concat([df, df_rev])
    return df_double

def create_hovertool(itype, itypes_order, hb_itypes, typelist):
    """
    Creates a list in hovertool format from the two dictionaries above
    """

    #Creating hovertool listzzzz
    hoverlist = [('Name', '@Name'),
                 ('PDB id', '@pdb_id'),
                 ('Position', '@restypePosition'),
                 (typelist[itype], "@{" + itype + '}{0.00}%')
                ]

    #Hover tool:
    hover = HoverTool(
        tooltips=hoverlist
    )

    return hover
  
def define_figure(width, height, dataframe, hover, itype):
    """
    Prepare bokeh figure heatmap as intended
    """

    # Mapper
    colors = ['#800000', '#860000', '#8c0000', '#930000', '#990000', '#9f0000', '#a60000', '#ac0000', '#b20000', '#b90000', '#bf0000', '#c50000', '#cc0000', '#d20000', '#d80000', '#df0000', '#e50000', '#eb0000', '#f20000', '#f80000', '#ff0000', '#ff0700', '#ff0e00', '#ff1500', '#ff1c00', '#ff2300', '#ff2a00', '#ff3100', '#ff3800', '#ff3f00', '#ff4600', '#ff4d00', '#ff5400', '#ff5b00', '#ff6200', '#ff6900', '#ff7000', '#ff7700', '#ff7e00', '#ff8500', '#ff8c00', '#ff9100', '#ff9700', '#ff9d00', '#ffa300', '#ffa800', '#ffae00', '#ffb400', '#ffba00', '#ffbf00', '#ffc500', '#ffcb00', '#ffd100', '#ffd600', '#ffdc00', '#ffe200', '#ffe800', '#ffed00', '#fff300', '#fff900', '#ffff00', '#f2ff00', '#e5ff00', '#d8ff00', '#ccff00', '#bfff00', '#b2ff00', '#a5ff00', '#99ff00', '#8cff00', '#7fff00', '#72ff00', '#66ff00', '#59ff00', '#4cff00', '#3fff00', '#33ff00', '#26ff00', '#19ff00', '#0cff00', '#00ff00', '#0afc0a', '#15fa15', '#1ff81f', '#2af62a', '#34f434', '#3ff13f', '#49ef49', '#54ed54', '#5eeb5e', '#69e969', '#74e674', '#7ee47e', '#89e289', '#93e093', '#9ede9e', '#a8dba8', '#b3d9b3', '#bdd7bd', '#c8d5c8', '#d3d3d3']
    colors.reverse()
    mapper = LinearColorMapper(palette=colors, low=0, high=100)

    #Bokeh figure
    p = figure(
        plot_width= width,
        plot_height=height,
        #title="Example freq",
        y_range=list(dataframe.Id.drop_duplicates()),
        x_range=list(dataframe.Position.drop_duplicates()),
        tools=["hover","tap","save","reset","wheel_zoom"], 
        x_axis_location="above",
        active_drag=None,
        toolbar_location="right",
        toolbar_sticky = False,
        min_border_top = 200,#leave some space for x-axis artificial labels
        min_border_bottom = 0,
    )

    # Create rectangle for heatmap
    mysource = ColumnDataSource(dataframe)
    p.rect(
        y="Id", 
        x="Position",
        width=1, 
        height=1, 
        source=mysource,
        line_color="white", 
        fill_color=transform(itype, mapper),

        # set visual properties for selected glyphs
        selection_line_color="black",
        selection_fill_color=transform(itype, mapper),
        # set visual properties for non-selected glyphs
        nonselection_fill_color=transform(itype, mapper),
        nonselection_fill_alpha=1,
        nonselection_line_alpha=1,
        nonselection_line_color="white"
        )

    #Very poor way of creating X-axis labels. Necessary for having linejumps inside the axis labels
    x_cord = 0
    y_cord = len(list(dataframe.Id.drop_duplicates()))+11#Position: 11 spaces above the plot's top border
    foolabel = Label(x=-1,
                     y=y_cord,
                     text='\nA: \nB: \nC: \nF: \n\n\nA: \nB: \nC: \nF: \n',
                     render_mode='css', 
                     border_line_alpha=1.0,
                     text_font_size = "10pt",
                     background_fill_color = "#FFFFFF")
    p.add_layout(foolabel)

    #Fore every unique position in the set, add a label in axis
    for position in list(dataframe.Position.drop_duplicates()):
        position = position.replace("Ligand","Lig\n\n\n\n\n")
        foolabel = Label(x=x_cord,
                         y=y_cord,
                         text=position,
                         render_mode='css', 
                         border_line_alpha=1.0,
                         background_fill_color = "#FFFFFF",
                         text_font_size = "10pt")
        p.add_layout(foolabel)
        x_cord +=1

    # Setting axis
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.xaxis.major_label_text_font_size = "10pt"
    p.yaxis.major_label_text_font_size = "10pt"
    p.yaxis.visible = False
    p.xaxis.visible = False
    p.axis.major_label_standoff = 0
    p.xaxis.major_label_orientation = 1

    # Adding hover
    p.add_tools(hover)

    # Needed later
    return(mysource,p)

def select_tool_callback(recept_info, recept_info_order, dyn_gpcr_pdb, itype, typelist, mysource):
    """
    Prepares the javascript script necessary for the side-window
    """
    
    #Create data source
    df_ri=pd.DataFrame(recept_info)
    ri_source=ColumnDataSource(df_ri)
    df_rio=pd.DataFrame(recept_info_order, index=[0])
    rio_source=ColumnDataSource(df_rio)
    df_gnum=pd.DataFrame(dyn_gpcr_pdb)
    gnum_source=ColumnDataSource(df_gnum)

    #Select tool and callback: (SIMPLIFIED)
    mysource.callback = CustomJS(
        args={"r_info":ri_source,"ro_info":rio_source,"gnum_info":gnum_source,"itype":itype, "typelist" : typelist},
        code="""
            var sel_ind = cb_obj.selected["1d"].indices;
            var plot_bclass=$("#retracting_parts").attr("class");
            if (sel_ind.length != 0){
                var data = cb_obj.data;
                var ri_data=r_info.data;
                var rio_data=ro_info.data;
                var gnum_data=gnum_info.data;
                var recept_name=data["Name"][sel_ind];
                var recept_id=data["Id"][sel_ind];
                var pos = data["protein_Position"][sel_ind];
                var restypepos = data["restypePosition"][sel_ind];
                var freq_type=data[itype][sel_ind];
                var pos_array = pos.split(" ");
                var pos_string = pos_array.join("_")
                var pos_ind_array = pos_array.map(value => { return gnum_data['index'].indexOf(value); });
                var pdb_pos_array = pos_ind_array.map(value => { return gnum_data[recept_name][value]; });
                var lig=ri_data[recept_id][rio_data['lig_sname']];
                var lig_lname=ri_data[recept_id][rio_data['lig_lname']];
                var recept=ri_data[recept_id][rio_data['upname']];
                var dyn_id_pre=ri_data[recept_id][rio_data['dyn_id']];
                var dyn_id=dyn_id_pre.match(/\d*$/)[0];
                var prot_id=ri_data[recept_id][rio_data['prot_id']];
                var prot_lname=ri_data[recept_id][rio_data['prot_lname']];
                var comp_id=ri_data[recept_id][rio_data['comp_id']];
                var struc_fname=ri_data[recept_id][rio_data['struc_fname']];
                var struc_file=ri_data[recept_id][rio_data['struc_f']];
                var traj_fnames=ri_data[recept_id][rio_data['traj_fnames']];
                var traj_f=ri_data[recept_id][rio_data['traj_f']];
                var pdb_id=ri_data[recept_id][rio_data['pdb_id']];
                var pdb_id_nochain = pdb_id.split(".")[0];
                var delta=ri_data[recept_id][rio_data['delta']];
                $('#ngl_iframe')[0].contentWindow.$('body').trigger('createNewRef', [struc_file, traj_fnames, traj_f ,lig, delta, pos, pdb_pos_array]);
             
                if (plot_bclass != "col-xs-9"){
                    $("#retracting_parts").attr("class","col-xs-9");
                    $("#first_col").attr("class","col-xs-7");
                    $("#second_col").attr("class","col-xs-5");
                    $("#info").css({"visibility":"visible","position":"relative","z-index":"auto"});
                }
                
                //Show NA comment if there is a NA in the position
                if(/N\/A/.test(restypepos)){
                    $('#na_comment').show();
                }

                //Setting type specific frequencies
                $( "#freq_" + itype).html(freq_type.toFixed(2) + "%");
                if (itype == "all") {
                    for (my_type in typelist) {
                        freq_type = data[my_type][sel_ind];
                        $( "#freq_" + my_type).html(parseFloat(freq_type).toFixed(2) + "%");
                    }
                }

                $("#recept_val").html(prot_lname + " ("+recept+")");
                $("#pos_val").html(restypepos);
                $("#pdb_id").html(pdb_id);
                $("#pdb_link").attr("href","https://www.rcsb.org/structure/" + pdb_id_nochain)
                if (Boolean(lig)) {
                    $("#lig_val").html(lig_lname + " ("+lig+")");
                    $("#lig_link").show();
                    $("#lig_link").attr("href","../../../dynadb/compound/id/"+comp_id);
                }
                else {
                    $("#lig_val").html("None");
                    $("#lig_link").hide();
                }
                $("#viewer_link").attr("href","../../../view/"+dyn_id+"/"+pos_string);
                $("#recept_link").attr("href","../../../dynadb/protein/id/"+prot_id);
                

            } else {
                if (plot_bclass != "col-xs-12"){
                    $("#retracting_parts").attr("class","col-xs-12");
                    $("#info").css({"visibility":"hidden","position":"absolute","z-index":"-1"});
                } 
            }           
        """)

    return mysource

def create_csvfile(options_path, recept_info,df):
    """
    This function creates the CSV file to be donwloaded from web
    """
    df_csv = df.copy()
    df_csv.index.names = ['Interacting positions']

    #Change dynX by full name of receptor, adding the dynid if there is more than a simulation for that receptor
    df_csv.columns = df_csv.columns.map(lambda x: recept_info[x][13])

    #Sorting by ballesteros Id's (helixloop column) and clustering order
    df_csv['Interacting positions'] = df_csv.index
    df_csv['helixloop'] = df_csv['Interacting positions'].apply(lambda x: re.sub(r'^(\d)x',r'\g<1>0x',x)) 
    df_csv = df_csv.sort_values(["helixloop"])

    #Change jumplines by 'x' to avoid formatting problems
    def new_index(cell):
        cell = cell.replace('\n\n', '  ')
        cell = cell.replace('\n', 'x')
        cell = cell.replace('xx', 'x')
        return cell

    df_csv['Interacting positions'] =  df_csv['Interacting positions'].apply(lambda x: new_index(x))
    df_csv.index = df_csv['Interacting positions']

    #Drop columns
    df_csv.drop(columns = ['helixloop','Interacting positions'], inplace = True)

    #Store dataframe as csv
    df_csv.to_csv(path_or_buf = options_path+"dataframe.csv", float_format='%.1f')

############
## Variables
############

#itype sets
itypes = set(("wb", "wb2", "sb","hp","pc","ps","ts","vdw", "hb", "hbbb","hbsb","hbss","hbls","hblb","all"))
nolg_itypes = set(("sb","pc","ts","ps","hbbb","hbsb","hbss","hp"))
noprt_itypes = set(("hbls","hblb"))
ipartners = set(("lg","prt","prt_lg"))

# Basepath for files
basepath = "/protwis/sites/files/Precomputed/get_contacts_files/"

typelist =  {
    'sb' : 'salt bridge',
    "pc" : 'pi-cation',
    "ps" : 'pi-stacking',
    'ts' : 't-stacking',
    "vdw" : 'van der waals',
    'hp' : 'hydrophobic',
    "hbbb" : 'backbone to backbone HB',
    "hbsb" : 'sidechain to backbone HB',
    "hbss" : 'sidechain to sidechain HB',
    "hbls" : 'ligand to sidechain HB',
    "hblb" : 'ligand to backbone HB',
    "wb" : 'water bridge',
    "wb2" : 'extended water bridge',
    "hb" : 'hydrogen bonds',
    'all' : 'all types',
}
hb_itypes = {
    "hbbb" : 'backbone to backbone',
    "hbsb" : 'sidechain to backbone',
    "hbss" : 'sidechain to sidechain',
    "hbls" : 'ligand to sidechain',
    "hblb" : 'ligand to backbone',
}
other_itypes = {
    'hp' : 'hydrophobic',
    'sb' : 'salt bridge',
    "pc" : 'pi-cation',
    "ps" : 'pi-stacking',
    'ts' : 't-stacking',
    "vdw" : 'van der waals',
    "wb" : 'water bridge',
    "wb2" : 'extended water bridge',

}

itypes_order = [
    ("Non-polar", 
        (
            ("vdw","van der waals"),
            ('hp', "hydrophobic")
        )
    ),
    ("Polar/Electrostatic", 
        (
            ("hb", "hydrogen bond"),
            ("wb", "water bridge"),
            ("wb2", "extended water bridge"),
            ('sb', "salt bridge"),
            ("pc", "pi-cation")
        )
    ),
    ("Stacking",
        (
            ("ps", "pi-stacking"),
            ('ts', "t-stacking")
        )
    )
]

###############
# Main function 
###############

def get_contacts_plots(itype, ligandonly):

    """
    Create and save dataframe, dendrogram, and other data necessary for computing get_contacts online plots
        - itype: any of the codes from below typelist.
        - ligandonly: lg (only residue-ligand contacts), prt (only intraprotein contacts), all 
    """    

    # Creating set_itypes and loading data
    if itype == "all":
        set_itypes =  set(("sb", "pc", "ps", "ts", "vdw", "hp", "hb", "hbbb", "hbsb", "hbss", "wb", "wb2", "hbls", "hblb", "all"))
        df_raw = None
        for itype_df in set_itypes:
            df_raw_itype = pd.read_csv(str(basepath + "contact_tables/compare_" + itype_df + ".tsv"), sep="\s+")
            df_raw = pd.concat([df_raw, df_raw_itype])
    else: 
        set_itypes = { itype }
        df_raw = pd.read_csv(str(basepath + "contact_tables/compare_" + itype + ".tsv"), sep="\s+")

    print("Computing contmaps inputs for %s-%s" % (itype, ligandonly))

    #Loading files
    compl_data = json_dict(str(basepath + "compl_info.json"))
    flare_template = json_dict(basepath + "template.json")

    # Adapting to Mariona's format
    df_original = adapt_to_marionas(df_raw)

    # If is working with total frequency and all interaction partners, create a new flareplot template file
    if (itype=='all') and (ligandonly=='prt_lg'):
        flareplot_template(df_original, basepath)
        
    # Filtering out non-ligand interactions if option ligandonly is True
    if ligandonly == "lg":
        ligandfilter = df_original['Position'].str.contains('Ligand')
        df_original = df_original[ligandfilter]
    elif ligandonly == "prt":
        ligandfilter = ~df_original['Position'].str.contains('Ligand')
        df_original = df_original[ligandfilter]

    df_original = filter_same_helix(df_original)

    #Removing low-frequency contacts
    df_original = filter_lowfreq(df_original, itype)

    #Add \n between GPCR nomenclatures, to show it multiline in the heatmap axis   
    df_original = set_new_axis(df_original)

    # Excluding non-standard (and by standard I'm saying "made by us") simulations
    (df_complete, df_standard) = split_by_standard(df_original, compl_data)
    
    #Repeat everything for standartd and non-standard dataframes (our simulations and the simulations from everone in GPCRmd)
    for (stnd,df) in (("cmpl", df_complete), ("stnd", df_standard)):
        
        #If doesn't exists yet, create base input folder
        options_path = "%scontmaps_inputs/%s/%s/%s/" %(basepath, itype, stnd, ligandonly)
        os.makedirs(options_path, exist_ok=True)

        # If there are no interactions with this ligandonly-itype combination
        if df.empty:
            print("No interactions avalible for this molecular partners and interaction type: %s and %s" % (ligandonly, itype) )
            return

        # Setting columns 'Position', 'leter+Position1' and 'leter+Position2' in df for jsons files    
        df_columned = new_columns(df, itype)
        df_columned.to_pickle(options_path+"dataframe_customflareplot.pkl")

        #Dropping away Position columns, once they are not needed
        df_drop = df.drop(['Position1','Position2'], 1)
        
        # Stack matrix (one row for each interaction pair and dynamic. Colnames are position, dynid and itypes)
        df_ts = stack_matrix(df_drop, set_itypes)
        
        #Dropping away non main-type interaction rows.
        df_drop = df_drop[df_drop['itype'] == itype]
        df_drop.drop('itype',axis=1, inplace=True)

        # Set position as row index of the dataframe
        df_drop = df_drop.set_index('Position')    

        # Labels for dendogram
        dendlabels_dyns = list(df_drop.columns)
        
        # Making one-simulation flareplots. Only done in cmpl to avoid repeating same Simulations
        if stnd == "cmpl":
            sim_jsons_path = '%scontmaps_inputs/%s/simulation_jsons/%s/' % (basepath, itype, ligandonly)
            dyn_flareplots(df_columned, sim_jsons_path, dendlabels_dyns, itype,  flare_template)

        #Computing frequency matrix
        dend_matrix = frequencies(df_drop)
        (recept_info,recept_info_order,df_ts,dyn_gpcr_pdb,index_dict)=improve_receptor_names(df_ts,compl_data)
        
        # Apending column with PDB ids
        pdb_id = recept_info_order['pdb_id']
        df_ts['pdb_id'] = df_ts['Id'].apply(lambda x: recept_info[x][pdb_id])
        
        #Storing dataframe with results in a CSV file, downloadable from web
        create_csvfile(options_path, recept_info,df_drop)

        # Add residue types to dataframe
        df_ts = add_restypes(df_ts, compl_data, recept_info, recept_info_order)

        #Preparing dendrogram folders and parameters
        dendfolder = options_path + "dendrograms/" 
        os.makedirs(dendfolder, exist_ok = True)
        dend_height = int( int(df.shape[1]) * 17)
        dend_width = 450

        # Computing several dendrograms and corresponding json files
        for cluster in list(range(2,21)):
            print('      computing dendrogram with '+str(cluster)+' clusters')
            dendfile = ("%s%iclusters_dendrogram.html" % (dendfolder, cluster))
            (dyn_dend_order, clustdict) = dendrogram_clustering(dend_matrix, dendlabels_dyns, dend_height, dend_width, dendfile, cluster, recept_info, recept_info_order)
            # Write dynamicID-cluster dictionary on a json
            clustdir = "%sflarejsons/%sclusters/" % (options_path, cluster)
            os.makedirs(clustdir, exist_ok= True)
            with open(clustdir + "clustdict.json", 'w') as clusdictfile:
                dump(clustdict, clusdictfile, ensure_ascii=False, indent = 4)

            #Jsons for the flareplots of this combinations of clusters
            flareplot_json(df_columned, clustdict, clustdir, flare_template)
        
        #Store Simulation names and dyn on file
        create_dyntoname_file(dyn_dend_order, recept_info, recept_info_order, options_path)
        
        for rev in ["norev","rev"]:

            # If rev option is setted to rev, duplicate all lines with the reversed-position version 
            #(4x32-2x54 duplicates to 2x54-4x32)
            if rev == "rev":
                df_ts_rev = reverse_positions(df_ts)
            else:
                df_ts_rev = df_ts
            
            df_ts_rev = sort_simulations(df_ts_rev, dyn_dend_order)

            #Taking some variables for dataframe slicing
            max_columns = 45
            pairs_number = df_drop.shape[0]
            inter_number = df_ts_rev.shape[0]
            inter_per_pair = (inter_number/pairs_number)/2 if rev == "rev" else inter_number/pairs_number 
            number_heatmaps = ceil((inter_number/inter_per_pair)/max_columns)
            
            #Create heatmap folder if not yet exists
            heatmap_path_jupyter = "/protwis/sites/files/Precomputed/get_contacts_files/contmaps_inputs/%s/%s/%s/heatmaps/%s/" % (itype,stnd,ligandonly,rev)
            heatmap_path = "%sheatmaps/%s/" % (options_path,rev)
            os.makedirs(heatmap_path, exist_ok=True)

            #Saving dataframe for future uses in customized heatmaps
            df_ts_rev.to_pickle(heatmap_path+"dataframe_for_customized.pkl")
            
            #Make heatmaps each 50 interacting pairs
            div_list = []
            heatmap_filename_list = []
            number_heatmap_list = []
            prev_slicepoint = 0
            for i in range(1,number_heatmaps+1):
                number_heatmap_list.append(str(i))

                #Slice dataframe. Also definig heigth and width of the heatmap
                slicepoint = int(i*inter_per_pair*max_columns)
                if i == number_heatmaps:
                    df_slided = df_ts_rev[prev_slicepoint:]
                else:
                    df_slided = df_ts_rev[prev_slicepoint:slicepoint]
                w = int(df_slided.shape[0]/inter_per_pair*20+40)
                prev_slicepoint = slicepoint
                h=dend_height

                # Define bokeh figure and hovertool
                
                hover = create_hovertool(itype, itypes_order, hb_itypes, typelist)
                mysource,p = define_figure(w, h, df_slided, hover, itype)

                # Creating javascript for side-window
                mysource = select_tool_callback(recept_info, recept_info_order, dyn_gpcr_pdb, itype, typelist, mysource)

                # Extract bokeh plot components and store them in lists
                script, div = components(p)
                div_list.append(div.lstrip())
                heatmap_filename = "%s%iheatmap.html" % (heatmap_path_jupyter,i)
                heatmap_filename_list.append(heatmap_filename)

                # Write heatmap on file
                heatmap_filename = "%s%iheatmap.html" % (heatmap_path,i)
                with open(heatmap_filename, 'w') as heatmap:
                    heatmap.write(script)

            # Write lists as python variables in a python file
            variables_file = "%svariables.py" % (heatmap_path)
            with open(variables_file, 'w') as varfile:
                varfile.write("div_list = [\'%s\']\n" % "\',\'".join(div_list))
                varfile.write("heatmap_filename_list = [\'%s\']\n" % "\',\'".join(heatmap_filename_list))
                varfile.write("number_heatmaps_list = [\'%s\']\n" % "\',\'".join(number_heatmap_list))

###################
## Calling function
###################

if len(argv) == 1:
    print(exit("""

##############table_to_dataframe.py#####################

This script creates dataframes, dendrogram and other
auxiliary files which serve as main inputs for contact_maps
application.

table_to_dataframe.py <INTERACTION_TYPE> <INTERACTION_PARTNERS>
table_to_dataframe.py --all

    - INTERACTION TYPE: any of the interaction types avalible for the web 
    - INTERACTION PARTNERS: lg, prt or prt_lg 

    --all: all combinations of itype and interaction partners are computed
"""))

if argv[1] == "--all":
    for itype in itypes:
        for ipartner in ipartners:
            if (itype in nolg_itypes) and (ipartner == "lg"):
                continue
            if (itype in noprt_itypes) and (ipartner == "prt"):
                continue
            get_contacts_plots(itype, ipartner)
else:
    get_contacts_plots(argv[1], argv[2])
