import matplotlib# MANDATORY TO BE IN FIRST PLACE!!
matplotlib.use('Agg')# MANDATORY TO BE IN SECOND PLACE!!
from math import pi
from sys import argv,exit
import pandas as pd
from  numpy import array
from json import loads
from re import sub,compile
from  plotly.figure_factory import create_dendrogram
from  plotly.offline import plot
import os
from math import pi
from bokeh.palettes import cividis
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool, TapTool, CustomJS, DataRange1d, Range1d, BasicTicker, ColorBar, ColumnDataSource, LinearColorMapper, PrintfTickFormatter
from bokeh.transform import transform

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
    """
    Parses the dataframe to create the data source of the plot. When defining a name for each dynamics entry: if there is any other dynamics in the 
    datadrame that is created fromt he same pdb id and ligand, all these dynamics will indicate the dynamics id
    """
    recept_info={}
    recept_info_order={
        "upname":0,
        "resname":1,
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
        "delta":12
    }
    taken_protlig={}
    index_dict={}
    dyn_gpcr_pdb={}
    for recept_id in df_ts['Id']:
        dyn_id=recept_id
        upname=compl_data[recept_id]["up_name"]
        resname=compl_data[recept_id]["lig_sname"]
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
                #recept_info[orig_recept_name_upd] = recept_info.pop(orig_recept_name)
                taken_protlig[prot_lig]["id_added"]=True
        else:
            recept_name=prot_lname+" ("+prot_lig[0]+")"

            if bool(prot_lig[1]):
                recept_name = recept_name + " + "+prot_lig[1]
            taken_protlig[prot_lig]={"recept_name":recept_name,"id_added":False}
        recept_info[recept_name]=[upname, resname,dyn_id,prot_id,comp_id,prot_lname,pdb_id,lig_lname,struc_fname,struc_f,traj_fnames,traj_f,delta]
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
    Creates an interaction frequency numpy matrix from 
    """

    # Create dictionary table with position tuple as keys and interaction-by-simulation-freq array as value
    freq_table = { tuple(col.split(" ")):list(df_t[col].values) for col in df_t }
        
    # Convert previous dictionary to numpy array, and traspose it
    freq_matrix = (array([freq_table[(r1, r2)] for (r1, r2) in freq_table])).T

    # Reorder according to clustering
    return freq_matrix

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
    plt.text(x,y,"_Cluster %d" % (cluster_num),fontsize=16) 

def annotate_cluster_nodes(dn, T, colors):
    """
    annotates the clusters obtained in T in the dendgrogram (dn) with colors (colors). Currently not operative
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


def dendrogram_clustering(dend_matrix, labels, height, width, filename): 

    # Setting figures
    fig = create_dendrogram(dend_matrix, orientation='right', labels=labels)

    fig['layout'].update({
        'width':600, 
        'height':height,
        'autosize' : False,
        })

    fig['layout']['margin'].update({
        'r' : 400,
        'l' : 20,
        't' : 0,
        'b' : 0,
        'pad' : 0
        })
    fig['layout']['xaxis'].update({
        'showline': False,
        'showticklabels': False,
        'ticks' : '',
        })

    fig['layout']['yaxis'].update({
        'side' : 'right',
        'showline': False,
        'ticks' : '',
        'tickfont' : {
            'size' : 15,
            'color' : 'black'
            }
        })

    # Taking order for plot rows
    dendro_leaves = fig['layout']['yaxis']['ticktext']

    # Writing dendrogram on file
    plot(fig, filename=filename, auto_open=False, config={'staticPlot' : True })

    return list(dendro_leaves)

def sort_simulations(df_ts, dyn_dend_order):
    """
    Sorts the simulations in the dataframe according to the order in the list dyn_dend_order
    """

    # Create a dictionary with the order of each simulation row in the plot 
    dyn_dend_order_dict = { dyn_name : dyn_dend_order.index(dyn_name) for dyn_name in dyn_dend_order }

    # Adding column based in new order recieved from clustering
    df_ts['clust_order'] =  df_ts['Id'].apply(lambda x: dyn_dend_order_dict[x])

    #Sorting by ballesteros Id's (helixloop column) and clustering order
    df_ts['helixloop'] = df_ts['Position'].apply(lambda x: sub(r'^(\d)x',r'\g<1>0x',x)) 
    df_ts = df_ts.sort_values(["helixloop",'clust_order'])

    #Drop sort columns once used
    df_ts.drop(['helixloop','clust_order'], axis = 1, inplace = True)

    return df_ts

def reverse_positions(df):
    """
    Appends a copy of the dataframe with the Position pair of the interaction being reversed (5x43-7x89 for 7x89-5x43)
    """
    df_rev = df.copy(deep = True)
    df_rev['Position'] = df_rev['Position'].replace({r'(\w+)\s+(\w+)' : r'\2 \1'}, regex=True)
    df_double = pd.concat([df, df_rev])
    return df_double    

def create_hovertool(itype, itypes_order, hb_itypes, typelist):
    """
    Creates a list in hovertool format from the two dictionaries above
    """

    #Creating hovertool list
    hoverlist = [('Id', '@Id'), ('PDB id', '@pdb_id'), ('Position', '@Position')]
    if itype == "all":
        for group,type_tuple in itypes_order:
            for itype_code,itype_name in type_tuple:
                hoverlist.append((itype_name, "@{" + itype_code + '}{0.00}%'))
                if itype_code == "hb":
                    for hb_code,hb_name in hb_itypes.items():
                        hoverlist.append((hb_name, "@{" + hb_code + '}{0.00}%'))
    else:
        hoverlist.append((typelist[itype], "@{" + itype + '}{0.00}%'))
    hoverlist.append(('Total interaction frequency', '@{all}{0.00}%'))

    #Hover tool:
    hover = HoverTool(
        tooltips=hoverlist
    )

    return hover


def define_figure(width, height, tool_list, dataframe, hover):
    """
    Prepare bokeh figure heatmap as intended
    """

    # Mapper
    colors = ['#FF0000','#FF0800','#FF1000','#FF1800','#FF2000','#FF2800','#FF3000','#FF3800','#FF4000','#FF4800','#FF5000','#FF5900','#FF6100','#FF6900','#FF7100','#FF7900','#FF8100','#FF8900','#FF9100','#FF9900','#FFA100','#FFAA00','#FFB200','#FFBA00','#FFC200','#FFCA00','#FFD200','#FFDA00','#FFE200','#FFEA00','#FFF200','#FFFA00','#FAFF00','#F2FF00','#EAFF00','#E2FF00','#DAFF00','#D2FF00','#CAFF00','#C2FF00','#BAFF00','#B2FF00','#AAFF00','#A1FF00','#99FF00','#91FF00','#89FF00','#81FF00','#79FF00','#71FF00','#69FF00','#61FF00','#59FF00','#50FF00','#48FF00','#40FF00','#38FF00','#30FF00','#28FF00','#20FF00','#18FF00','#10FF00','#08FF00','#00FF00']
    colors.reverse()
    mapper = LinearColorMapper(palette=colors, low=0, high=100)

    p = figure(
        plot_width= width, 
        plot_height=height,
        #title="Example freq",
        y_range=list(dataframe.Id.drop_duplicates()),
        x_range=list(dataframe.Position.drop_duplicates()),
        tools=tool_list, 
        x_axis_location="above",
        active_drag=None,
        toolbar_location="right",
        toolbar_sticky = False,
        min_border_top = round(height * 0.045) # The proportion of margin to be left on top of matrix to align with dendrogram
        )

    # Rotate angle of x-axis labels
    p.xaxis.major_label_orientation = pi/3

    # Create rectangle for heatmap
    mysource = ColumnDataSource(dataframe)
    p.rect(
        y="Id", 
        x="Position", 
        width=1, 
        height=1, 
        source=mysource,
        line_color="white", 
        fill_color=transform('value', mapper),

        # set visual properties for selected glyphs
        selection_line_color="black",
        selection_fill_color=transform('value', mapper),
        # set visual properties for non-selected glyphs
        nonselection_fill_color=transform('value', mapper),
        nonselection_fill_alpha=1,
        nonselection_line_alpha=1,
        nonselection_line_color="white"
        )

    # Add legend
    color_bar = ColorBar(
        color_mapper=mapper,
        location=(0, 0),
        label_standoff = 12,
        ticker=BasicTicker(desired_num_ticks=2),
        formatter=PrintfTickFormatter(format="%d%%"),
        major_label_text_font_size="11pt"
        )
    p.add_layout(color_bar, 'left')

    # Setting axis
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.xaxis.major_label_text_font_size = "10pt"
    p.yaxis.major_label_text_font_size = "10pt"
    p.yaxis.visible = False
    p.axis.major_label_standoff = 0
    p.xaxis.major_label_orientation = 1#"vertical"

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
                var recept_id=data["Id"][sel_ind];
                var pos=data["Position"][sel_ind];
                var freq_total=data["all"][sel_ind];
                var freq_type=data[itype][sel_ind];
                var pos_array = pos.split(" ");
                var pos_string = pos_array.join("_")
                var pos_ind_array = pos_array.map(value => { return gnum_data['index'].indexOf(value); });
                var pdb_pos_array = pos_ind_array.map(value => { return gnum_data[recept_id][value]; });
                var lig=ri_data[recept_id][rio_data['resname']];
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

                //Setting type specific frequencies
                if (itype == "all") {
                    for (my_type in typelist) {
                        if (my_type == "all"){ // Total frequency shall not be displayed twice
                            continue;
                        }
                        var freq_type = data[my_type][sel_ind];
                        $( "#freq_" + my_type).html(freq_type.toFixed(2) + "%");
                    }
                }
                else {
                    $( "#freq_" + itype).html(freq_type.toFixed(2) + "%");
                }

                $("#freqtotal_val").html(freq_total.toFixed(2) + "%");
                $("#recept_val").html(prot_lname + " ("+recept+")");
                $("#pos_val").html(pos);
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

def get_contacts_plots(itype, ligandonly, rev):

    """
    Create and save dataframe, dendrogram, and other data necessary for computing get_contacts online plots
        - itype: any of the codes from below typelist.
        - ligandonly: lg (only residue-ligand contacts), prt (only intraprotein contacts), all 
    """

    # Basepath for files
    basepath = "/protwis/sites/files/Precomputed/get_contacts_files/"

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


    print(str("computing dataframe and dendrogram for %s-%s-%s") % (itype, ligandonly, rev))

    # Creating set_itypes, with all in case it is not still in it
    if itype == "all":
        set_itypes =  set(("sb", "pc", "ps", "ts", "vdw", "hp", "hb", "hbbb", "hbsb", "hbss", "wb", "wb2", "hbls", "hblb", "all"))
    else: 
        set_itypes = set(itype.split("_"))
        set_itypes.add('all')

    #Creating itypes dictionary for selected types
    selected_itypes = { x:typelist[x] for x in set_itypes }

    #Loading files
    df_raw = pd.read_csv("/protwis/sites/files/Precomputed/get_contacts_files/contact_tables/compare_all.tsv", sep="\s+")
    for itype_df in set_itypes:
        if itype_df == "all": 
            continue
        df_raw_itype = pd.read_csv("/protwis/sites/files/Precomputed/get_contacts_files/contact_tables/compare_" + itype_df + ".tsv", sep="\s+")
        df_raw = pd.concat([df_raw, df_raw_itype])
    compl_data = json_dict("/protwis/sites/files/Precomputed/get_contacts_files/compl_info.json")

    # Adapting to Mariona's format
    df = adapt_to_marionas(df_raw)

    # Filtering out non-ligand interactions if option ligandonly is True
    if ligandonly == "lg":
        ligandfilter = df['Position'].str.contains('Ligand')
        df = df[ligandfilter]
    elif ligandonly == "prt":
        ligandfilter = ~df['Position'].str.contains('Ligand')
        df = df[ligandfilter]

    #Removing helix-to-helix, low-frequency pairs and merging same residue-pair interaction frequencies
    df,dict_freqs = removing_entries_and_freqsdict(df, set_itypes, itype)

    # If rev option is setted to rev, duplicate all lines with the reversed-position version (4x32-2x54 duplicates to 2x54-4x32)
    if rev == "rev":
        df = reverse_positions(df)

    # If there are no interactions with this ligandonly-itype combination
    if df.empty:
        exit("No interactions avalible for this molecular partners and interaction type: %s and %s" % (ligandonly, itype) )

    # Set position as row index of the dataframe
    df = df.set_index('Position')    

    #Transposing dataframe
    df_t = df.transpose()
    dynlist = list(df_t.index)

    #Clustering of simulations
    dend_matrix = clustering(df_t)

    # Converting to df_ts table, 
    df_ts = df_t.stack().rename("value").reset_index()
    df_ts.rename(columns={"level_0": "Id"}, inplace=True)

    # Appending to the data-frame type-specific frequencies (will be needed for the hovertool)
    df_ts = add_itype_freqs(df_ts, set_itypes, dict_freqs)

    #Changing ID names by simulation names
    (recept_info,recept_info_order,df_t,dyn_gpcr_pdb,index_dict)=improve_receptor_names(df_ts,compl_data)

    # Apending column with PDB ids
    pdb_id = recept_info_order['pdb_id']
    df_ts['pdb_id'] = df_ts['Id'].apply(lambda x: recept_info[x][pdb_id])

    # Labels for dendogram
    dendlabels_names = [ index_dict[dyn] for dyn in dynlist ]

    #Creating dendrogram
    dendfile = basepath + "view_input_dataframe" + "/" + itype + "_" + ligandonly + "_dendrogram_figure.html"
    dend_height = int( int(df.shape[1]) * 16 + 20)
    dend_width = 160 #Same width as two square column
    dyn_dend_order = dendrogram_clustering(dend_matrix, dendlabels_names, dend_height, dend_width, dendfile)

    df_ts = sort_simulations(df_ts, dyn_dend_order)

    # Defining height and width of the future figure from columns (simulations) and rows (positions) of the df dataframe
    # I use df instead of df_ts because of its structure. I know it's kind of strange
    h=dend_height
    w=16300 if int(df.shape[0]*20 + 130) > 16300 else int(df.shape[0]*20 + 130)

    # Save dataframe in csv (without row indexes)
    csvfile =  basepath + "view_input_dataframe" + "/" + itype + "_" + ligandonly + "_" + rev + "_dataframe.csv"
    df_ts.to_csv(path_or_buf = csvfile, index = False)

    # Define a figure
    hover = create_hovertool(itype, itypes_order, hb_itypes, typelist)
    mytools = ["hover","tap","save","reset","wheel_zoom"]
    mysource,p = define_figure(w, h, mytools, df_ts, hover)

    # Creating javascript for side-window
    mysource = select_tool_callback(recept_info, recept_info_order, dyn_gpcr_pdb, itype, typelist, mysource)

    # Find path to files 
    plotdiv_w= w + 275
    script, div = components(p)

    ###################
    ## Printing outputs
    ###################

    # Creating directory if it doesn't exist
    if not os.path.exists(basepath + "view_input_dataframe"):
        os.makedirs(basepath + "view_input_dataframe")

    # Write heatmap on file
    with open(basepath + "view_input_dataframe" + "/" + itype + "_" + ligandonly + "_" + rev + "_heatmap.html", 'w') as heatmap:
        heatmap.write(script)

    # Write div and plotdiv as python variables in a python file
    with open(basepath + "view_input_dataframe" + "/" + itype + "_" + ligandonly + "_" + rev + "_variables.py", 'w') as varfile:
        varfile.write("div = \'%s\'\n" % div.lstrip())
        varfile.write("plotdiv_w = " + str(plotdiv_w))

###################
## Calling function
###################

if len(argv) == 1:
    print(exit("""

##############table_to_dataframe.py#####################

This script creates dataframes, dendrogram and other
auxiliary files which serve as main inputs for contact_maps
application.

table_to_dataframe.py <INTERACTION_TYPE> <INTERACTION_PARTNERS> <REV_OPTION>

    - INTERACTION TYPE: any of the interaction types avalible for the web.
    - INTERACTION PARTNERS: lg, prt or prt_lg
    - REVERSE OPTION: rev or norev. Show (or not) reversed residue pairs

"""))
get_contacts_plots(argv[1], argv[2], argv[3])
