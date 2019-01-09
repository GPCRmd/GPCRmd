import matplotlib# MANDATORY TO BE IN FIRST PLACE!!
matplotlib.use('Agg')# MANDATORY TO BE IN SECOND PLACE!!
from math import pi
from sys import argv,exit
import pandas as pd
import numpy as np
from json import loads
from re import sub,compile
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, leaves_list, dendrogram, fcluster
import mpld3
import os

# Be careful with this!!! Put here only because some false-positive warnings from pandas
import warnings
warnings.filterwarnings('ignore')

# Mariona's functions

def json_dict(path):
    """Converts json file to pyhton dict."""
    json_file=open(path)
    json_str = json_file.read()
    json_data = loads(json_str)
    return json_data

def improve_receptor_names(df_ts,compl_data):
    """Parses the dataframe to create the data source of the plot. When defining a name for each dynamics entry: if there is any other dynamics in the datadrame that is created fromt he same pdb id and ligand, all these dynamics will indicate the dynamics id"""
    recept_info={}
    recept_info_order={"upname":0, "resname":1,"dyn_id":2,"prot_id":3,"comp_id":4,"prot_lname":5,"pdb_id":6,"lig_lname":7,"struc_fname":8,"traj_fnames":9,"delta":10}
    taken_protlig={}
    index_dict={}
    dyn_gpcr_pdb={}
    for recept_id in df_ts['Id']:
        dyn_id=recept_id
        upname=compl_data[recept_id]["up_name"]
        resname=compl_data[recept_id]["lig_sname"]
        prot_id=compl_data[recept_id]["prot_id"]
        comp_id=compl_data[recept_id]["comp_id"]
        lig_lname=compl_data[recept_id]["lig_lname"]
        prot_lname=compl_data[recept_id]["prot_lname"]
        pdb_id=compl_data[recept_id]["pdb_id"]
        struc_fname=compl_data[recept_id]["struc_fname"]
        traj_fnames=compl_data[recept_id]["traj_fnames"]
        delta=compl_data[recept_id]["delta"]
        if pdb_id:
            prot_lig=(pdb_id,resname)
        else:
            prot_lig=(upname,resname)
        
        if prot_lig in taken_protlig:
            name_base=taken_protlig[prot_lig]["recept_name"]
            recept_name=name_base+" (id:"+str(dyn_id)+")"
            #Add the dyn id at recept_info for the original dyn as well, if necessary:
            if not taken_protlig[prot_lig]["id_added"]:
                orig_recept_name=name_base
                orig_dyn_id=recept_info[orig_recept_name][recept_info_order["dyn_id"]]
                orig_recept_name_upd=orig_recept_name+" (id:"+str(orig_dyn_id)+")"
                recept_info[orig_recept_name_upd] = recept_info.pop(orig_recept_name)
                taken_protlig[prot_lig]["id_added"]=True
        else:
            recept_name=prot_lname+" ("+prot_lig[0]+") + "+prot_lig[1]
            taken_protlig[prot_lig]={"recept_name":recept_name,"id_added":False}
        recept_info[recept_name]=[upname, resname,dyn_id,prot_id,comp_id,prot_lname,pdb_id,lig_lname,struc_fname,traj_fnames,delta]
        index_dict[recept_id]=recept_name
        dyn_gpcr_pdb[recept_name]=compl_data[recept_id]["gpcr_pdb"]
    df_ts['Id'] = list(map(lambda x: index_dict[x], df_ts['Id']))
    return(recept_info,recept_info_order,df_ts,dyn_gpcr_pdb,index_dict)

def removing_entries_and_freqsdict(df, itypes, main_itype):
    """
    Create dict_freqs dictionary, filter same-helix interaction, filter low-frequency interactions
    """    
    positions = dict()
    counter = 0
    dict_freqs = {}
    pos_topreserve = set()
    
    #Filtering same-helix contacts
    helixpattern = compile(r"""^(..)\w+\s+\1""")#For detecting same-helix contacts, the ones like 1.22x22 1.54x54
    helixfilter = df['Position'].str.contains(helixpattern)
    df = df[~helixfilter]

    # Storing interaction-specific frequencies in a dictionary
    for itype in itypes:
        df_type = df[df["itype"] == itype]
        df_type.drop('itype', 1, inplace = True)
        df_type.set_index('Position', inplace = True)
        dict_freqs[itype] = df_type.to_dict()
    
    # Preserve positions which interaction frequency for this type reach, at mean, 0.1 (or 10 if working on percentages)
    df['mean_row'] = df.mean(axis = 1, numeric_only = True)
    pos_topreserve = set(df['Position'][ (df['mean_row'] > 10) & (df['itype'] == main_itype) ])
    df.drop('mean_row', 1, inplace = True)
    df = df[df['Position'].isin(pos_topreserve)]
    
    # Once type-specific frequencies are stored apart, set main frequency value to main_itype (the option selected)
    df = df[df['itype'] == main_itype]
    
    #Dropping away interaction type colum
    df.drop('itype', 1, inplace = True)
     
    # Set position as row index of the dataframe
    df = df.set_index('Position')

    return(df,dict_freqs)
        
def adapt_to_marionas(df):
    """
    This function comprises a series of operations to adapt the new tsv format to Mariona's original scripts.
    Also returns a dictionary
    """

    #Merging toghether both contacting aminoacid Ids
    df['Position'] = df.Position1.str.cat(df.Position2, sep = " ")
    df = df.drop(df.columns[[0, 1]], axis=1)

    # Passing frequencies from decimal to percentage
    nocols = (("Position1","Position2","itype","Position"))
    for colname in df:
        if colname not in nocols:
            df[colname] = df[[colname]].apply(lambda x: x*100)

    return(df)

def add_itype_freqs(df_ts, set_itypes, dict_freqs):
    """
    Adds interaction-type specific frequencies to the dataframe as new columns
    """
    # Creating dictionary for frequencies by interaction type
    type_freqs = { itype:[] for itype in set_itypes}

    # Filling dictionary for frequencies by interaction type
    for row in df_ts.iterrows():
        dyn = row[1]['Id']
        position = row[1]['Position']
        for itype in set_itypes:
            if position in dict_freqs[itype][dyn]:
                type_freqs[itype].append(dict_freqs[itype][dyn][position])
            else:
                type_freqs[itype].append(0.0)
        
        
    # Joining dictionary for frequencies by interaction type to main dataframe
    df_ts = df_ts.join(pd.DataFrame(type_freqs))
    
    return(df_ts)

def clustering(df_t):
    """
    Clusters simulations by their total accumulated interaction frequencies.
    Returns the simulation order according to their clustering
    """
    dyn_labels = list(df_t.index)
    
    # Create dictionary table with position tuple as keys and interaction-by-simulation-freq array as value
    freq_table = { tuple(col.split(" ")):list(df_t[col].values) for col in df_t }
        
    # Convert previous dictionary to numpy array
    freq_matrix = np.array([freq_table[(r1, r2)] for (r1, r2) in freq_table])

    # Using scipy to cluster. Copied from get_contacts scripts
    l = linkage(freq_matrix.T, method='single')
    
    col_ordering = leaves_list(l)
    
    # New Column labels
    new_order = [dyn_labels[i] for i in col_ordering]
        
    # Reorder according to clustering
    return (new_order,l)


def flat_clusters(labels, colors, clusters, dflt_col, dend_matrix):
    """
    Returns an array with the cluster number to which every element belongs to 
    """
    # flat_clusters
    T = fcluster(dend_matrix, t=clusters, criterion='maxclust')
    leaf_colors = { num_leaf : colors[clust_leaf-1] for num_leaf,clust_leaf in zip(labels,T) }
    link_cols = {}
    for i, i12 in enumerate(dend_matrix[:,:2].astype(int)):
        c1, c2 = (link_cols[x] if x > len(dend_matrix) else leaf_colors[x] for x in i12)
        link_cols[i+1+len(dend_matrix)] = c1 if c1 == c2 else dflt_col
    return(link_cols, T)

def anotate_cluster(x, y, cluster_num, color):
    """
    Annotates a point in a dendrogram with a cluster_(cluster_num) label, in position x y with
    a small circle of color (color) 
    """
    plt.plot(x, y, 'ro', c = color)
    plt.text(int(x-20),(y+1),cluster_num,fontsize=14) # Note the minus five is for not having the text directly over the node, but at its side

def annotate_cluster_nodes(dn, T, colors):
    """
    annotates the clusters obtained in T in the dendgrogram (dn) with colors (colors)
    """
    pos = 0
    len_col_list = len(dn['color_list'])
    cluster_counter = 0
    for i, d in zip(dn['icoord'], dn['dcoord']):

        #Select y and x coordenates for our node
        y = 0.5 * sum(i[1:3])
        x = d[1]

        #Check colors, and set_true if this node is a just before a change of color (thus, a cluster node)
        node_color = dn['color_list'][pos]
        if pos == len_col_list-1:
            nextnode_color = dn['color_list'][pos]
        else:
            nextnode_color = dn['color_list'][pos + 1]

        #Annotating node if its a cluster node
        if (nextnode_color != node_color) and ('b' != node_color):
            cluster_num = (colors.index(node_color) + 1)
            anotate_cluster(x,y,cluster_num, node_color)        

        #Annotating side of single-leaf clusters
        elif (node_color == "b") and (d[0] == 0.0):

            #Taking cluster number.  Based on dendrogram coordenate system, in which leafs are separated each other by 10 and from bottom by 5
            single_leaf_position = int((i[1] - 5) / 10) # Position on dendrogram
            single_leaf_num = dn['leaves'][single_leaf_position] # Position on input array
            cluster_num = T[single_leaf_num]

            y = i[1]
            x = d[1]
            anotate_cluster(x,y,cluster_num, node_color)

            if (d[3] == 0.0):

                #Taking cluster number.  Based on dendrogram coordenate system, in which leafs are separated each other by 10 and from bottom by 5
                single_leaf_position = int((i[3] - 5) / 10) # Position on dendrogram
                single_leaf_num = dn['leaves'][single_leaf_position] # Position on input array
                cluster_num = T[single_leaf_num]

                y = i[3]
                x = d[1]
                anotate_cluster(x,y,cluster_num, node_color)

        pos += 1

def dendrogram_clustering(dend_matrix, labels, height, width, clusters): 
    """
    dendrogram time, my dudes
    """
    arbitrary_dpi = 50 # Arbitrary. Don't pay attention to it
    inch_height = height / arbitrary_dpi
    inch_width = width / arbitrary_dpi

    #Setting matplotlib figure
    plt.figure(dpi = arbitrary_dpi, figsize = [inch_width, inch_height],facecolor = "white")
   
    colors = ['g', 'r', 'k', 'y', 'm', 'c']
    leaves_nums_list = list(range(0,len(labels)))
    
    # Asigning clusters and colors to each leaf
    (link_cols,T) = flat_clusters(leaves_nums_list, colors, clusters, 'b', dend_matrix)
    
    # Creating dendrogram
    dn = dendrogram(
        dend_matrix,
        labels=labels,
        orientation = 'left',
        link_color_func = lambda x: link_cols[x] 
    )
        
    # Annotate cluster nodes in dendrogram
    annotate_cluster_nodes(dn, T, colors)
        
    # Setting labels font size and color
    ax = plt.gca()
    ax.tick_params(axis='both', which='both', labelsize=16, colors="black", right= False, bottom=False)
    
    # Rendering html figure with mpld3 module from our matplotlib figure
    html_dendrogram = mpld3.fig_to_html(plt.gcf())
    return html_dendrogram    

def get_contacts_plots(itype, ligandonly):
    """
    Create and save dataframe, dendrogram, and other data necessary for computing get_contacts online plots
        - itype: any of the codes from below typelist.
        - ligandonly: lg (only residue-ligand contacts), prt (only intraprotein contacts), all 
    """

    #Declaring dictionaries with types
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

    # Creating set_itypes, with all in case it is not still in it
    if not itype == "all":
        set_itypes = set(itype.split("_"))
        set_itypes.add('all')
    else: 
        set_itypes = (("sb", "pc", "ps", "ts", "vdw", "hp", "hb", "hbbb", "hbsb", "hbss", "wb", "wb2", "hbls", "hblb", "all"))

    #Creating itypes dictionary for selected types
    selected_itypes = { x:typelist[x] for x in set_itypes }

    #Loading files
    df_raw = pd.read_csv("/protwis/sites/files/Precomputed/get_contacts_files/contact_tables/compare_summary.tsv", sep="\s+")
    compl_data = json_dict("/protwis/sites/files/Precomputed/crossreceptor_analysis_files/compl_info.json")

    # Filtering out non-desired interaction types
    if itype != "all":
        df = df_raw[(df_raw['itype'].isin(set_itypes)) ]
    else:
        df = df_raw

    # Adapting to Mariona's format
    df = adapt_to_marionas(df)

    # Filtering out non-ligand interactions if option ligandonly is True
    if ligandonly == "lg":
        ligandfilter = df['Position'].str.contains('Ligand')
        df = df[ligandfilter]
    elif ligandonly == "prt":
        ligandfilter = ~df['Position'].str.contains('Ligand')
        df = df[ligandfilter]

    #Removing helix-to-helix, low-frequency pairs and merging same residue-pair interaction frequencies
    df,dict_freqs = removing_entries_and_freqsdict(df, set_itypes, itype)

    # If there are no interactions with this ligandonly-itype combination
    if df.empty:
        exit("No interactions avalible for this molecular partners and interaction type: %s and %s" % (ligandonly, itype) )

    #Transposing dataframe
    df_t = df.transpose()

    #Clustering of simulations
    (clust_order,dend_matrix) = clustering(df_t)

    # Labels for dendogram
    dendlabels = list(df_t.index)

    # Converting to df_ts table, 
    df_ts = df_t.stack().rename("value").reset_index()
    df_ts.rename(columns={"level_0": "Id"}, inplace=True)

    # Appending to the data-frame type-specific frequencies (will be needed for the hovertool)
    df_ts = add_itype_freqs(df_ts, set_itypes, dict_freqs)

    #Changing ID names by simulation names
    (recept_info,recept_info_order,df_t,dyn_gpcr_pdb,index_dict)=improve_receptor_names(df_ts,compl_data)

    # Changing ID names by simulation names in clust_order list
    clust_order_names = { index_dict[dyn]:clust_order.index(dyn) for dyn in clust_order }

    # Adding column based in new order recieved from clustering
    df_ts['clust_order'] =  df_ts['Id'].apply(lambda x: clust_order_names[x])

    #Changing denlabels to full name format
    dendlabels_names = [ index_dict[dyn] for dyn in dendlabels ]

    #Sorting by ballesteros Id's (helixloop column) and clustering order
    df_ts['helixloop'] = df_ts['Position'].apply(lambda x: sub(r'^(\d)x',r'\g<1>0x',x)) 
    df_ts = df_ts.sort_values(["helixloop",'clust_order'])

    #Drop sort columns once used
    df_ts.drop(['helixloop','clust_order'], axis = 1, inplace = True)

    #Creating dendrogram
    dend_height = int( int(df.shape[1]) * 80 + 20)
    dend_width = 180 #Same width as two square column
    dendr_figure = dendrogram_clustering(dend_matrix, dendlabels_names, dend_height-20, dend_width, 2) 

    # Defining height and width of the future figure from columns (simulations) and rows (positions) of the df dataframe
    sim_num = df.shape[1] 
    h=int(sim_num*80 + 20)# I use the df dataframe instead of df_ts because the last one has acopled itypes columns
    w=16300 if int(df.shape[0]*80 + 80) > 16300 else int(df.shape[0]*80 + 80)   
    figure_shape = {
        'width' : w,
        'height' : h
    }

    ###################
    ## Printing outputs
    ###################

    # Basepath for files
    basepath = "/protwis/sites/files/Precomputed/get_contacts_files/"

    # Creating directory if it doesn't exist
    if not os.path.exists(basepath + "view_input_dataframe"):
        os.makedirs(basepath + "view_input_dataframe")

    # Print daraframe and to_import variables in file in file
    df_ts.to_csv(basepath + "view_input_dataframe" + "/" + itype + "_" + ligandonly + "_dataframe.csv")

    # Printing dendrogram in file
    dendr_file = open(basepath + "view_input_dataframe" + "/" + itype + "_" + ligandonly + "_dendrogram_figure.txt", "w")
    dendr_file.write(dendr_figure)
    dendr_file.close()

    # Printing special variables
    var_file = open(basepath + "view_input_dataframe" + "/" + itype + "_" + ligandonly + "_variables.py", "w")
    var_file.write("recept_info = " + repr(recept_info) + "\n\n")
    var_file.write("recept_info_order = " + repr(recept_info_order) + "\n\n")
    var_file.write("dyn_gpcr_pdb = " + repr(dyn_gpcr_pdb) + "\n\n")
    var_file.write("figure_shape = " + repr(figure_shape))
    var_file.close()

###################
## Calling function
###################

if len(argv) == 1:
    print(exit("""

##############table_to_dataframe.py#####################

This script creates dataframes, dendrogram and other
auxiliary files which serve as main inputs for contact_plots
application.

table_to_dataframe.py <INTERACTION_TYPE> <INTERACTION_PARTNERS> <NUM_SIMULATIONS>

    - INTERACTION TYPE: any of the interaction types avalible for the web.
    - INTERACTION PARTNERS: lg, prt or prt_lg

"""))
get_contacts_plots(argv[1], argv[2])
