from sys import argv,exit
import pandas as pd
import json
from  plotly.figure_factory import create_dendrogram
import numpy as np
import os
import re
from math import ceil
from scipy.cluster.hierarchy import linkage, fcluster, cut_tree
import multiprocessing as mp
# from django.conf import settings
from bokeh.plotting import figure, save
from bokeh.embed import components
from bokeh.models import Label, HoverTool, TapTool, CustomJS, BasicTicker, ColorBar, ColumnDataSource, LinearColorMapper, PrintfTickFormatter
from bokeh.transform import transform
from bokeh.events import Tap
###########
##Functions
###########

def json_dict(path):
    """Converts json file to pyhton dict."""
    json_file=open(path)
    json_str = json_file.read()
    json_data = json.loads(json_str)
    return json_data

def improve_receptor_names(df_ts,compl_data):
    """
    Parses the dataframe to create the data source of the plot. When defining a name for each dynamics entry: if there is any other dynamics in the 
    datadrame that is created fromt he same pdb id and ligand, all these dynamics will indicate the dynamics id
    """

    # Simulation fullname
    gennums = {}
    partial_data = {}
    for dyn_id in df_ts['Id']:
        prot_lname = compl_data[dyn_id]['prot_lname']
        pdb_id = compl_data[dyn_id]['pdb_id']
        up_name = compl_data[dyn_id]['up_name']
        recept_name="%s (%s)" % (prot_lname,pdb_id) if pdb_id else "%s (%s)" % (prot_lname,up_name) 
        recept_name_dynid="%s (%s) (%s)" % (up_name,pdb_id,dyn_id)

        # In this dictionary, we will store part of the contents of compl_data for each dynamic
        dyn_data = {}
        dyn_data['recept_name'] = recept_name
        dyn_data['recept_name_dynid'] = recept_name_dynid
        for k in ["up_name","lig_sname","dyn_id","prot_id","comp_id",
        "prot_lname","pdb_id","lig_lname","struc_fname","struc_f",
        "traj_fnames","traj_f","delta",'class','peplig','gprot_name',
        'gprot_chain_a','gprot_chain_b','gprot_chain_g','gpcr_chain']:
            dyn_data[k] = compl_data[dyn_id][k]

        # Dictionary for generic numberings       
        gennums[dyn_id]=compl_data[dyn_id]["gpcr_pdb"]
        gennums[dyn_id].update(compl_data[dyn_id]["gprot_pdb"])

        partial_data[dyn_id] = dyn_data

    df_ts['pdb_id'] = df_ts['Id'].apply(lambda x: partial_data[x]['pdb_id'])
    df_ts['Name'] = df_ts['Id'].apply(lambda x: partial_data[x]['recept_name'])
    df_ts['gprot_name'] = df_ts['Id'].apply(lambda x: partial_data[x]['gprot_name'])

    return(partial_data,df_ts,gennums)

def set_new_axis(df):
    """
    Substitute the original Residue 3-nomenclatures single line format (1x23x23x24x24 1x23x23x24x24)
    to 3-nomenclatures multiline format (1x\n23\n23\n24\n24\n\n1x\n23\n23\n24\n24)(similar to gpcrdb).
    """
    def new_cell(cell):
        cell = cell.replace(' ','\n\n')
        cell = cell.replace('x','\n')
        cell = cell.replace('_','\n')
        cell = re.sub(pattern_pos1, r"\1x\n", cell)
        cell = re.sub(pattern_pos2, r"\n\n\1x\n", cell)
        return cell
    
    pattern_pos1 = re.compile(r"^(\d+)\n")
    pattern_pos2 = re.compile(r"\n\n(\d+)\n")
    df['Residue'] = df['Residue'].apply(new_cell)
    return df

def filter_lowfreq(df):
    """
    Filter out interaction pairs with no system reaching at least 30%
    """
    # Filter lowfrequency
    above_30perc = ((df > 0.30).sum(1)>1)
    df = df[above_30perc]
    return(df)

def prepare_table(df,compl_data):
    """
    This function comprises a series of operations to adapt the new tsv format to Mariona's original scripts.
    Also returns a dictionary
    """

    # Filter lowfrequency
    above_30perc = ((df > 0.30).sum(1)>1)
    df = df[above_30perc]

    # Passing frequencies from decimal to percentage
    df= df.apply(lambda x: x*100)

    # Get rid of multinidexes
    Residues = pd.Series([a for a in df.index.map(' '.join)])
    df['Residue'] = [a for a in df.index.map(' '.join)]

    # Introduce jumplines in Generic numberings 
    df = set_new_axis(df)
    df = df.set_index('Residue')

    #Find non-standard simulations
    standard_simulations = { dyn for (dyn,entry) in compl_data.items() if entry['is_gpcrmd_community']}
    df_standard = df[df.columns[df.columns.isin(standard_simulations)]]

    return(df,df_standard)


def flareplot_template_gpcrgprot(df, jsonpath):
    """
    Create a pseudoflareplot input json with no interactions, but with all avalible Residues.
    It will be used later as a template to create the top interactions flareplots.  
    """

    # G-protein numbering for each of its loops and helices
    gprot_ind = {
        'HN': 17,
        'hns1': 18,
        'S1': 19,
        's1h1': 20,
        'H1': 21,
        'h1ha': 22,
        'HA': 23,
        'hahb': 24,
        'HB': 25,
        'hbhc': 26,
        'HC': 27,
        'hchd': 28,
        'HD': 29,
        'hdhe': 30,
        'HE': 31,
        'hehf': 32,
        'HF': 33,
        'hfs2': 34,
        'S2': 35,
        's2s3': 36,
        'S3': 37,
        's3h2': 38,
        'H2': 39,
        'h2s4': 40,
        'S4': 41,
        's4h3': 42,
        'H3': 43,
        'h3s5': 44,
        'S5': 45,
        's5hg': 46,
        'HG': 47,
        'hgh4': 48,
        'H4': 49,
        'h4s6': 50,
        'S6': 51,
        's6h5': 52,
        'H5': 53
        }

    # Color patterns for G protein 2ndary structures
    gprot_colors = {
    's' : "#f7b0b5",# FOr loops
    'h' : "#f7b0b5",# FOr loops 
    'H' : "#cf0617",# FOr helices
    'S' : "#cf0617"# FOr sheets
    }

    # Colors for every helix in GPCR
    helix_colors = {'1':"#78C5D5",'12':"#5FB0BF",
                    '2':"#459BA8",'23':"#5FAF88",
                    '3':"#79C268",'34':"#9FCD58",
                    '4':"#C5D747",'45':"#DDD742",
                    '5':"#F5D63D",'56':"#F3B138",
                    '6':"#F18C32",'67':"#ED7A6A",
                    '7':"#E868A1",'78':"#D466A4",
                    '8':"#BF63A6"}
    allgennums = set(item for sublist in df.index for item in sublist)
    #'track' entry for json file: each track is a node (Residue) in the flareplot
    tracks = [{
        'trackLabel': 'Degree centrality',
        "trackProperties": []
    }]
    trees = [{
        'treeLabel': 'Helices',
        'treePaths': []
    }]
    
    # #Add ligand
    # tracks[0]['trackProperties'].append({
    #     'color' : "#FF5050",
    #     'size' : 1.0,
    #     'nodeName': 'Ligand'
    # })
    # trees[0]['treePaths'].append([1, 'Ligand'])
    unsorted_trees = []
    unsorted_tracks = []
    
    added_gennums = set()
    for gennum in allgennums:

        #Skip ligands
        if gennum.startswith('Ligand'):
            continue
        
        # If this is generic numbering of G protein, append tracks after those of GPCR
        elif (gennum.startswith('G') or gennum.startswith('H')) and (gennum not in added_gennums):
            
            gennum_split = gennum.split('_')
            helix = gennum_split[1]
            helix_id = gprot_ind[helix]
            gennum_noGH = '_'.join(gennum_split[1:3])
            color_gprot = gprot_colors[gennum_noGH[0]]
            # gennum = gennum.replace('_',':')  
            trackprop = {
                'color' : color_gprot,
                'size' : 1.0,
                'nodeName': gennum_noGH
            }

            trees[0]['treePaths'].append([helix_id, gennum_noGH])
            tracks[0]['trackProperties'].append(trackprop)

        # If this is generic numbering multi-class of GPCR
        else:
            split_gennum = gennum.split('x')
            # We'll iterate over all classes (e.g.: 1x34x32x31x35 so each pos is separated by x)
            for gennum_p in split_gennum:
                if split_gennum.index(gennum_p) == 0:# If first case
                    helix = gennum_p
                    color = helix_colors[gennum_p]
                else:                
                    real_gennum = helix+'x'+gennum_p
                    if real_gennum not in added_gennums:
                        trackprop = {
                            'color' : color,
                            'size' : 1.0,
                            'nodeName': real_gennum
                        }
                        # For each threepath, we'll put the generic numbering of the pos preced by a sorting number
                        # e.g. 1.1x51, 2.12x34, 3.3x64....
                        if len(helix) == 2:
                            newhelix = int(helix[0]) + int(helix[1])
                        else:
                            newhelix = int(helix)*2
                        trees[0]['treePaths'].append([newhelix, real_gennum])

                        tracks[0]['trackProperties'].append(trackprop)
                        added_gennums.add(real_gennum)

    #Sort trees
    treePaths_sorted = sorted(list(trees[0]['treePaths']), key=lambda l: (l[0],l[1]))
    treePaths_sorted = [ str(x[0])+"."+x[1] for x in treePaths_sorted ]
    trees[0]['treePaths'] = treePaths_sorted
    
    #Output jsondict to store
    jsondict = { 'trees' : trees, 'tracks' : tracks, "defaults": {"edgeColor": "rgba(50,50,50,100)", "edgeWidth": 2}}
    
    # Store json file
    with open(jsonpath, 'w') as jsonfile:
        json.dump(jsondict, jsonfile, ensure_ascii=False, indent = 4)
        

def find_resnames_resids(row,db_dict,three_to_one):
    """
    Find residue names and Ids of each interacting residue pair
    """
    dynid = row['Id']
    pos_array = row['Residue'].split('\n\n')

    # Find Generic numbering of this Residue according to the class of its GPCR
    number_letter = ["0",'A','B', 'C', 'F']
    gclass = db_dict[dynid]['class']
    class_index = number_letter.index(gclass)
    residues_ary = []
    resids_ary = []
    for pos in pos_array:
        # If Residue is from a GPCR, select gennum of this Residue and from there, its 
        if 'x' in pos: 
            prot = 'gpcr'
            gennum_multiclass = pos.split('\n')
            gennum = gennum_multiclass[0]+gennum_multiclass[class_index]
            
        # If from Gprot
        else:
            prot = 'gprot'
            gennum = pos.replace('_','.')
            gennum = pos.replace('\n','.')

        # 
        if gennum in db_dict[dynid][prot+'_pdb']:
            res_sel = db_dict[dynid][prot+'_pdb'][gennum]
            sel_split = res_sel.split('-') 
            resid = sel_split[0]
            resname3 = sel_split[2]
            resname = three_to_one[resname3] if resname3 in three_to_one else 'X'
        else:
            resname = "(N/A)"
            resid = "(N/A)"
        residues_ary.append(resname+gennum)
        resids_ary.append(resid)
    residues = ' '.join(residues_ary)
    resids = ' '.join(resids_ary)

    # Assign values to new columns
    row['resID'] = resids
    row['resname_gennum'] = residues

    return(row)
    

def create_csvfile(outputs_path, partial_db_dict, df):
    """
    This function creates the CSV file to be donwloaded from web
    """
    df_csv = df.copy()
    df_csv.index.names = ['Interacting Residues']

    #Change dynX by full name of receptor, adding the dynid if there is more than a simulation for that receptor
    df_csv.columns = df_csv.columns.map(lambda x: partial_db_dict[x]["recept_name_dynid"])

    #Sorting by ballesteros Id's (helixloop column) and clustering order
    df_csv['Interacting Residues'] = df_csv.index
    df_csv['helixloop'] = df_csv['Interacting Residues'].apply(lambda x: re.sub(r'^(\d)x',r'\g<1>0x',x)) 
    df_csv = df_csv.sort_values(["helixloop"])

    #Change jumplines by 'x' to avoid formatting problems
    def new_index(cell):
        cell = cell.replace('\n\n', '  ')
        cell = cell.replace('\n', 'x')
        cell = cell.replace('xx', 'x')
        return cell

    df_csv['Interacting Residues'] =  df_csv['Interacting Residues'].apply(lambda x: new_index(x))
    df_csv.index = df_csv['Interacting Residues']

    #Drop columns
    df_csv.drop(columns = ['helixloop','Interacting Residues'], inplace = True)

    #Store dataframe as csv
    df_csv.to_csv(path_or_buf = outputs_path+"dataframe.csv", float_format='%.1f')

def split_pos(index):
    """
    Divide generic numbering interaction index according to GPCR class (for GPCRs)
    Return Gprot gennums with '_' replaced by cannonical '.'
    """
    index_split = index.name.split('\n\n')
    for pos in index_split:
        if 'x' in pos:
            gpcr_pos = []
            pos_x = pos.split('\n')
            for i in range(1,5):
                gpcr_pos.append(pos_x[0]+pos_x[i])
        else:
            gprot_pos = [pos.replace('_','.')]
    allpos = gpcr_pos+gprot_pos
    return(allpos)

def dyn_flareplots(df_o, folderpath, flare_template = False):
    """
    Create top20 interaction jsons for each simulation. Needed for customized selection flareplots.
    """
    if df_o.empty:
        return
    
    # Folder for flareplots
    df = df_o.copy()
    os.makedirs(folderpath, exist_ok = True)
    # Colors, many of them
    colors_auld = ['#800000', '#860000', '#8c0000', '#930000', '#990000', '#9f0000', '#a60000', '#ac0000', '#b20000', '#b90000', '#bf0000', '#c50000', '#cc0000', '#d20000', '#d80000', '#df0000', '#e50000', '#eb0000', '#f20000', '#f80000', '#ff0000', '#ff0700', '#ff0e00', '#ff1500', '#ff1c00', '#ff2300', '#ff2a00', '#ff3100', '#ff3800', '#ff3f00', '#ff4600', '#ff4d00', '#ff5400', '#ff5b00', '#ff6200', '#ff6900', '#ff7000', '#ff7700', '#ff7e00', '#ff8500', '#ff8c00', '#ff9100', '#ff9700', '#ff9d00', '#ffa300', '#ffa800', '#ffae00', '#ffb400', '#ffba00', '#ffbf00', '#ffc500', '#ffcb00', '#ffd100', '#ffd600', '#ffdc00', '#ffe200', '#ffe800', '#ffed00', '#fff300', '#fff900', '#ffff00', '#f2ff00', '#e5ff00', '#d8ff00', '#ccff00', '#bfff00', '#b2ff00', '#a5ff00', '#99ff00', '#8cff00', '#7fff00', '#72ff00', '#66ff00', '#59ff00', '#4cff00', '#3fff00', '#33ff00', '#26ff00', '#19ff00', '#0cff00', '#00ff00', '#0afc0a', '#15fa15', '#1ff81f', '#2af62a', '#34f434', '#3ff13f', '#49ef49', '#54ed54', '#5eeb5e', '#69e969', '#74e674', '#7ee47e', '#89e289', '#93e093', '#9ede9e', '#a8dba8', '#b3d9b3', '#bdd7bd', '#c8d5c8', '#d3d3d3']
    colors_ylorrd = ['#800026', '#850026', '#8a0026', '#8f0026', '#940026', '#990026', '#9e0026', '#a30026', '#a80026', '#ad0026', '#b20026', '#b70026', '#bd0026', '#c00225', '#c30424', '#c60623', '#c90822', '#cc0a21', '#d00d21', '#d30f20', '#d6111f', '#d9131e', '#dc151d', '#df171c', '#e31a1c', '#e51e1d', '#e7221e', '#e9271f', '#eb2b20', '#ed2f21', '#ef3423', '#f13824', '#f33c25', '#f54126', '#f74527', '#f94928', '#fc4e2a', '#fc532b', '#fc582d', '#fc5d2e', '#fc6330', '#fc6831', '#fc6d33', '#fc7234', '#fc7836', '#fc7d37', '#fc8239', '#fc873a', '#fd8d3c', '#fd903d', '#fd933e', '#fd9640', '#fd9941', '#fd9c42', '#fd9f44', '#fda245', '#fda546', '#fda848', '#fdab49', '#fdae4a', '#feb24c', '#feb54f', '#feb853', '#febb56', '#febf5a', '#fec25d', '#fec561', '#fec864', '#fecc68', '#fecf6b', '#fed26f', '#fed572', '#fed976', '#feda79', '#fedc7d', '#fede80', '#fedf84', '#fee187', '#fee38b', '#fee48e', '#fee692', '#fee895', '#fee999', '#feeb9c', '#ffeda0', '#ffeea3', '#fff0a7', '#fff1ab', '#fff3ae', '#fff4b2', '#fff6b6', '#fff7b9', '#fff9bd', '#fffac1', '#fffcc4', '#fffdc8', '#ffffcc']
    colors_inferno = ['#000003', '#000004', '#000006', '#010007', '#010109', '#01010B', '#02010E', '#020210', '#030212', '#040314', '#040316', '#050418', '#06041B', '#07051D', '#08061F', '#090621', '#0A0723', '#0B0726', '#0D0828', '#0E082A', '#0F092D', '#10092F', '#120A32', '#130A34', '#140B36', '#160B39', '#170B3B', '#190B3E', '#1A0B40', '#1C0C43', '#1D0C45', '#1F0C47', '#200C4A', '#220B4C', '#240B4E', '#260B50', '#270B52', '#290B54', '#2B0A56', '#2D0A58', '#2E0A5A', '#300A5C', '#32095D', '#34095F', '#350960', '#370961', '#390962', '#3B0964', '#3C0965', '#3E0966', '#400966', '#410967', '#430A68', '#450A69', '#460A69', '#480B6A', '#4A0B6A', '#4B0C6B', '#4D0C6B', '#4F0D6C', '#500D6C', '#520E6C', '#530E6D', '#550F6D', '#570F6D', '#58106D', '#5A116D', '#5B116E', '#5D126E', '#5F126E', '#60136E', '#62146E', '#63146E', '#65156E', '#66156E', '#68166E', '#6A176E', '#6B176E', '#6D186E', '#6E186E', '#70196E', '#72196D', '#731A6D', '#751B6D', '#761B6D', '#781C6D', '#7A1C6D', '#7B1D6C', '#7D1D6C', '#7E1E6C', '#801F6B', '#811F6B', '#83206B', '#85206A', '#86216A', '#88216A', '#892269', '#8B2269', '#8D2369', '#8E2468', '#902468', '#912567', '#932567', '#952666', '#962666', '#982765', '#992864', '#9B2864', '#9C2963', '#9E2963', '#A02A62', '#A12B61', '#A32B61', '#A42C60', '#A62C5F', '#A72D5F', '#A92E5E', '#AB2E5D', '#AC2F5C', '#AE305B', '#AF315B', '#B1315A', '#B23259', '#B43358', '#B53357', '#B73456', '#B83556', '#BA3655', '#BB3754', '#BD3753', '#BE3852', '#BF3951', '#C13A50', '#C23B4F', '#C43C4E', '#C53D4D', '#C73E4C', '#C83E4B', '#C93F4A', '#CB4049', '#CC4148', '#CD4247', '#CF4446', '#D04544', '#D14643', '#D24742', '#D44841', '#D54940', '#D64A3F', '#D74B3E', '#D94D3D', '#DA4E3B', '#DB4F3A', '#DC5039', '#DD5238', '#DE5337', '#DF5436', '#E05634', '#E25733', '#E35832', '#E45A31', '#E55B30', '#E65C2E', '#E65E2D', '#E75F2C', '#E8612B', '#E9622A', '#EA6428', '#EB6527', '#EC6726', '#ED6825', '#ED6A23', '#EE6C22', '#EF6D21', '#F06F1F', '#F0701E', '#F1721D', '#F2741C', '#F2751A', '#F37719', '#F37918', '#F47A16', '#F57C15', '#F57E14', '#F68012', '#F68111', '#F78310', '#F7850E', '#F8870D', '#F8880C', '#F88A0B', '#F98C09', '#F98E08', '#F99008', '#FA9107', '#FA9306', '#FA9506', '#FA9706', '#FB9906', '#FB9B06', '#FB9D06', '#FB9E07', '#FBA007', '#FBA208', '#FBA40A', '#FBA60B', '#FBA80D', '#FBAA0E', '#FBAC10', '#FBAE12', '#FBB014', '#FBB116', '#FBB318', '#FBB51A', '#FBB71C', '#FBB91E', '#FABB21', '#FABD23', '#FABF25', '#FAC128', '#F9C32A', '#F9C52C', '#F9C72F', '#F8C931', '#F8CB34', '#F8CD37', '#F7CF3A', '#F7D13C', '#F6D33F', '#F6D542', '#F5D745', '#F5D948', '#F4DB4B', '#F4DC4F', '#F3DE52', '#F3E056', '#F3E259', '#F2E45D', '#F2E660', '#F1E864', '#F1E968', '#F1EB6C', '#F1ED70', '#F1EE74', '#F1F079', '#F1F27D', '#F2F381', '#F2F485', '#F3F689', '#F4F78D', '#F5F891', '#F6FA95', '#F7FB99', '#F9FC9D', '#FAFDA0', '#FCFEA4']
    colors_magma = ['#000003', '#000004', '#000006', '#010007', '#010109', '#01010B', '#02020D', '#02020F', '#030311', '#040313', '#040415', '#050417', '#060519', '#07051B', '#08061D', '#09071F', '#0A0722', '#0B0824', '#0C0926', '#0D0A28', '#0E0A2A', '#0F0B2C', '#100C2F', '#110C31', '#120D33', '#140D35', '#150E38', '#160E3A', '#170F3C', '#180F3F', '#1A1041', '#1B1044', '#1C1046', '#1E1049', '#1F114B', '#20114D', '#221150', '#231152', '#251155', '#261157', '#281159', '#2A115C', '#2B115E', '#2D1060', '#2F1062', '#301065', '#321067', '#341068', '#350F6A', '#370F6C', '#390F6E', '#3B0F6F', '#3C0F71', '#3E0F72', '#400F73', '#420F74', '#430F75', '#450F76', '#470F77', '#481078', '#4A1079', '#4B1079', '#4D117A', '#4F117B', '#50127B', '#52127C', '#53137C', '#55137D', '#57147D', '#58157E', '#5A157E', '#5B167E', '#5D177E', '#5E177F', '#60187F', '#61187F', '#63197F', '#651A80', '#661A80', '#681B80', '#691C80', '#6B1C80', '#6C1D80', '#6E1E81', '#6F1E81', '#711F81', '#731F81', '#742081', '#762181', '#772181', '#792281', '#7A2281', '#7C2381', '#7E2481', '#7F2481', '#812581', '#822581', '#842681', '#852681', '#872781', '#892881', '#8A2881', '#8C2980', '#8D2980', '#8F2A80', '#912A80', '#922B80', '#942B80', '#952C80', '#972C7F', '#992D7F', '#9A2D7F', '#9C2E7F', '#9E2E7E', '#9F2F7E', '#A12F7E', '#A3307E', '#A4307D', '#A6317D', '#A7317D', '#A9327C', '#AB337C', '#AC337B', '#AE347B', '#B0347B', '#B1357A', '#B3357A', '#B53679', '#B63679', '#B83778', '#B93778', '#BB3877', '#BD3977', '#BE3976', '#C03A75', '#C23A75', '#C33B74', '#C53C74', '#C63C73', '#C83D72', '#CA3E72', '#CB3E71', '#CD3F70', '#CE4070', '#D0416F', '#D1426E', '#D3426D', '#D4436D', '#D6446C', '#D7456B', '#D9466A', '#DA4769', '#DC4869', '#DD4968', '#DE4A67', '#E04B66', '#E14C66', '#E24D65', '#E44E64', '#E55063', '#E65162', '#E75262', '#E85461', '#EA5560', '#EB5660', '#EC585F', '#ED595F', '#EE5B5E', '#EE5D5D', '#EF5E5D', '#F0605D', '#F1615C', '#F2635C', '#F3655C', '#F3675B', '#F4685B', '#F56A5B', '#F56C5B', '#F66E5B', '#F6705B', '#F7715B', '#F7735C', '#F8755C', '#F8775C', '#F9795C', '#F97B5D', '#F97D5D', '#FA7F5E', '#FA805E', '#FA825F', '#FB8460', '#FB8660', '#FB8861', '#FB8A62', '#FC8C63', '#FC8E63', '#FC9064', '#FC9265', '#FC9366', '#FD9567', '#FD9768', '#FD9969', '#FD9B6A', '#FD9D6B', '#FD9F6C', '#FDA16E', '#FDA26F', '#FDA470', '#FEA671', '#FEA873', '#FEAA74', '#FEAC75', '#FEAE76', '#FEAF78', '#FEB179', '#FEB37B', '#FEB57C', '#FEB77D', '#FEB97F', '#FEBB80', '#FEBC82', '#FEBE83', '#FEC085', '#FEC286', '#FEC488', '#FEC689', '#FEC78B', '#FEC98D', '#FECB8E', '#FDCD90', '#FDCF92', '#FDD193', '#FDD295', '#FDD497', '#FDD698', '#FDD89A', '#FDDA9C', '#FDDC9D', '#FDDD9F', '#FDDFA1', '#FDE1A3', '#FCE3A5', '#FCE5A6', '#FCE6A8', '#FCE8AA', '#FCEAAC', '#FCECAE', '#FCEEB0', '#FCF0B1', '#FCF1B3', '#FCF3B5', '#FCF5B7', '#FBF7B9', '#FBF9BB', '#FBFABD', '#FBFCBF']
    colors_ylgnbl = ['#081d58', '#0a1e5d', '#0c2062', '#0f2267', '#11246c', '#142671', '#162876', '#182a7b', '#1b2c80', '#1d2e85', '#20308a', '#22328f', '#253494', '#243795', '#243b97', '#243e99', '#24429a', '#23459c', '#23499e', '#234c9f', '#2350a1', '#2253a3', '#2257a4', '#225aa6', '#225ea8', '#2162aa', '#2166ac', '#206aae', '#206fb0', '#1f73b2', '#1f77b4', '#1f7bb6', '#1e80b8', '#1e84ba', '#1d88bc', '#1d8cbe', '#1d91c0', '#2094c0', '#2397c0', '#269ac1', '#299dc1', '#2ca0c1', '#2fa3c2', '#32a6c2', '#35a9c2', '#38acc3', '#3bafc3', '#3eb2c3', '#41b6c4', '#46b7c3', '#4bb9c2', '#50bbc1', '#55bdc1', '#5abfc0', '#60c1bf', '#65c3be', '#6ac5be', '#6fc7bd', '#74c9bc', '#79cbbb', '#7fcdbb', '#85cfba', '#8bd1b9', '#91d4b9', '#97d6b8', '#9dd8b8', '#a3dbb7', '#a9ddb6', '#afdfb6', '#b5e2b5', '#bbe4b5', '#c1e6b4', '#c7e9b4', '#caeab3', '#cdebb3', '#d0ecb3', '#d3eeb3', '#d6efb2', '#daf0b2', '#ddf1b2', '#e0f3b2', '#e3f4b1', '#e6f5b1', '#e9f6b1', '#edf8b1', '#eef8b4', '#f0f9b7', '#f1f9bb', '#f3fabe', '#f4fac1', '#f6fbc5', '#f7fcc8', '#f9fccb', '#fafdcf', '#fcfdd2', '#fdfed5', '#ffffd9']
    colors_grlgrdgr = ['#0d2b17', '#0e2d17', '#0f2f17', '#103118', '#123318', '#133618', '#143819', '#153a19', '#173c1a', '#183e1a', '#19411a', '#1a431b', '#1c451b', '#1d471b', '#1e4a1c', '#1f4c1c', '#214e1d', '#22501d', '#23521d', '#24551e', '#26571e', '#27591e', '#285b1f', '#295e1f', '#2b6020', '#2c6220', '#2d6420', '#2f6621', '#306921', '#316b22', '#326d22', '#346f22', '#357223', '#367423', '#377623', '#397824', '#3a7a24', '#3b7d25', '#3c7f25', '#3e8125', '#3f8326', '#408626', '#418826', '#438a27', '#448c27', '#458e28', '#469128', '#489328', '#499529', '#4a9729', '#4c9a2a', '#4e9b2d', '#519c30', '#549d34', '#569e37', '#599f3a', '#5ca03e', '#5ea141', '#61a345', '#64a448', '#67a54b', '#69a64f', '#6ca752', '#6fa855', '#71a959', '#74ab5c', '#77ac60', '#79ad63', '#7cae66', '#7faf6a', '#82b06d', '#84b170', '#87b374', '#8ab477', '#8cb57b', '#8fb67e', '#92b781', '#94b885', '#97b988', '#9abb8c', '#9dbc8f', '#9fbd92', '#a2be96', '#a5bf99', '#a7c09c', '#aac1a0', '#adc3a3', '#afc4a7', '#b2c5aa', '#b5c6ad', '#b8c7b1', '#bac8b4', '#bdc9b7', '#c0cbbb', '#c2ccbe', '#c5cdc2', '#c8cec5', '#cacfc8', '#cdd0cc', '#d0d1cf', '#d3d3d3']
    colors = colors_grlgrdgr
    
    dyn_list = df.columns   
    # Split the interacting-residues-pairs in the index into different columns
    df[['APos','BPos','CPos','FPos','GprotPos',]] = df.apply(lambda x: split_pos(x), result_type='expand', axis=1)

    for dyn in dyn_list:

        # Select top interactions based on its mean frequency. Also asign color based on mean value
        color_len = len(colors) -1
        df['color'] = df[dyn].apply(lambda x: colors[color_len-round(x*color_len/100)]) #There are 101 colors avalible in list

        #Filter top 20 interaction freqeuncies
        df = df.nlargest(20, dyn)

        #'Edge' multi-entries, based on the 4 GPCR nomenclatures
        jsondict = {}
        for leter in ['', 'A', 'B', 'C', 'F']:
            df_dict = pd.DataFrame(columns = ["name1", "name2", "frames"])
            df_dict['name1'] = df[leter+'Pos'] if leter else df['APos'] # Class A comes as the default one
            df_dict['name2'] = df['GprotPos'].str.replace('\n','_').str.replace('G_','')
            df_dict['frames'] = [[1]]*len(df_dict)
            df_dict['color'] = df['color']
            df_dict['value'] = df[dyn]
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
            json.dump(jsondict, jsonfile, ensure_ascii=False, indent = 4)


####################
## dendrogram functions
####################    

def frequencies(df):
    """
    Creates an interaction frequency numpy matrix from 
    """

    # Transpose matrix
    df_t = df.transpose() 
    
    # Create dictionary table with Residue tuple as keys and interaction-by-simulation-freq array as value
    freq_table = { tuple(col.split("\n\n")):list(df_t[col].values) for col in df_t }
        
    # Convert previous dictionary to numpy array, and traspose it
    freq_matrix = (np.array([freq_table[(r1, r2)] for (r1, r2) in freq_table])).T

    # Reorder according to clustering
    return freq_matrix
    
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

def hoverlabels_axis(fig, partial_db_dict, default_color, annotations = []):
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

    def prepare_entry(hoverentry, fig, ypos, partial_db_dict):
        """
        Creates xaxis-annotations and hoverlabels based on the information contained by this dendrogram branch
        """                
        dynid = dendro_leaves[int((ypos-5)/10)]
        nodyn_id = dynid.replace('dyn','')
        pdbcode = partial_db_dict[dynid]['pdb_id']
        simname = partial_db_dict[dynid]['up_name']
        peplig = partial_db_dict[dynid]['peplig']
        ligsname = partial_db_dict[dynid]['lig_sname']
        liglname = partial_db_dict[dynid]['lig_lname']
        bgcolor = hoverentry['marker']['color']
        anot_text = "%s (%s)<b style='display: none'>%s</b>" % (simname, pdbcode, dynid)
        if (ligsname):
            # If peptide ligand, take long-name of ligand (regular name)
            if (peplig):
                hovertext = str("complex with %s (dynID: %s)" % (liglname, nodyn_id))
            else: # Else take short name (Residue ID)
                hovertext = str("complex with %s (dynID: %s)" % (ligsname, nodyn_id))
        else:
            hovertext = str("apoform (dynID: %s)" % (nodyn_id))            

        # Annotation to corresponding simulation
        colorfont = black_or_white(bgcolor)
        annotations.append(define_annotation_list(ypos, bgcolor, anot_text, colorfont, dynid, hovertext))

        return(fig, annotations)
    
    dendro_leaves = fig['layout']['yaxis']['ticktext']

    # Adapting hovertool to what I want from it
    occuped_Residues = dict()
    for hoverentry in fig['data']:

        # Silenciate all default hover entries. 
        hoverentry['hoverinfo'] = 'none'
        
        # If entry reaches end of plot (not intermediate node)
        if (hoverentry['x'][0] == -0) and (int(hoverentry['y'][0])%10 == 5):
            
            #If entry Y-corodinate is not already occuped by another one, or if it's wrongly occuped by a middle dendrogram which reaches bottom of plot
            if (hoverentry['y'][0] not in occuped_Residues) or (hoverentry['marker']['color'] != default_color):

                occuped_Residues[hoverentry['y'][0]] = hoverentry['marker']['color']
                (fig, annotations) = prepare_entry(hoverentry, fig, hoverentry['y'][0], partial_db_dict)

                #If this entry reaches two labels at the same time (terminal U node), create yet another entry
                if (hoverentry['x'][3] == -0) and (int(hoverentry['y'][3])%10 == 5): 
                    (fig, annotations) = prepare_entry(hoverentry, fig, hoverentry['y'][3], partial_db_dict)

    fig['layout']['annotations'] = annotations

    return fig

def dendrogram_clustering(dend_matrix, labels, height, width, filename, clusters, partial_db_dict): 

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
        })

    fig.update_layout(
        margin=dict(t=0, b=0, r=150, l=100),
    )

    #Annotating cluster nodes
    annotations = annotate_clusters(fig, 'rgb(0,116,217)') # Default color for tree

    # Correcting hoverlabels
    fig = hoverlabels_axis(fig, partial_db_dict, 'rgb(0,116,217)', annotations)

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

def create_dyntoname_file(dyn_dend_order, partial_db_dict, outputs_path):
    """
    Creates a list of tuples, each one containing dynID-receptor names pairs
    Needed to display menu dropdown's receptor names in same order as dendrogram
    """
    dyn_names = [ partial_db_dict[dyn]['recept_name_dynid'] for dyn in dyn_dend_order ]
    dyn_to_names = list(zip(dyn_dend_order, list(dyn_names)))
    dyn_to_names.reverse()
    with open(outputs_path+"name_to_dyn_dict.json", "w") as dyn_names_file:
        json.dump(dyn_to_names, dyn_names_file, ensure_ascii=False, indent = 4)


def cluster_flareplot(df, clustdict, folderpath, flare_template = False):
    """
    Create json entries for significative positions (top10 mean frequency) of each cluster produced
    """
    os.makedirs(folderpath,  exist_ok = True)
    colors_grlgrdgr = ['#0d2b17', '#0e2d17', '#0f2f17', '#103118', '#123318', '#133618', '#143819', '#153a19', '#173c1a', '#183e1a', '#19411a', '#1a431b', '#1c451b', '#1d471b', '#1e4a1c', '#1f4c1c', '#214e1d', '#22501d', '#23521d', '#24551e', '#26571e', '#27591e', '#285b1f', '#295e1f', '#2b6020', '#2c6220', '#2d6420', '#2f6621', '#306921', '#316b22', '#326d22', '#346f22', '#357223', '#367423', '#377623', '#397824', '#3a7a24', '#3b7d25', '#3c7f25', '#3e8125', '#3f8326', '#408626', '#418826', '#438a27', '#448c27', '#458e28', '#469128', '#489328', '#499529', '#4a9729', '#4c9a2a', '#4e9b2d', '#519c30', '#549d34', '#569e37', '#599f3a', '#5ca03e', '#5ea141', '#61a345', '#64a448', '#67a54b', '#69a64f', '#6ca752', '#6fa855', '#71a959', '#74ab5c', '#77ac60', '#79ad63', '#7cae66', '#7faf6a', '#82b06d', '#84b170', '#87b374', '#8ab477', '#8cb57b', '#8fb67e', '#92b781', '#94b885', '#97b988', '#9abb8c', '#9dbc8f', '#9fbd92', '#a2be96', '#a5bf99', '#a7c09c', '#aac1a0', '#adc3a3', '#afc4a7', '#b2c5aa', '#b5c6ad', '#b8c7b1', '#bac8b4', '#bdc9b7', '#c0cbbb', '#c2ccbe', '#c5cdc2', '#c8cec5', '#cacfc8', '#cdd0cc', '#d0d1cf', '#d3d3d3']
    colors = colors_grlgrdgr
    color_len = len(colors) -1
    
    # Split the interacting-residues-pairs in the index into different columns
    df[['APos','BPos','CPos','FPos','GprotPos',]] = df.apply(lambda x: split_pos(x), result_type='expand', axis=1)
    for clust in clustdict.keys():

        # Select top interactions based on its mean frequency. Also asign color based on mean value
        df_clust = df.filter(items = clustdict[clust] + ['APos','BPos','CPos','FPos','GprotPos'])
        df_clust['mean'] = df_clust.mean(axis = 1, numeric_only = True)
        mean_threshold = min(df_clust['mean'].nlargest(20).tolist())
        df_clust['color'] = df_clust['mean'].apply(lambda x: colors[color_len-round(x*color_len/100)]) #There are 101 colors avalible in list
        df_clust['frames'] = df_clust['mean'].apply(lambda x: [str(i) for i in list(range(0,int(x)))])

        #Filter top 20 in df_clust
        df_clust = df_clust.nlargest(20,'mean')

        #'Edge' multi-entries, based on the 4 GPCR nomenclatures
        for leter in ['', 'A', 'B', 'C', 'F']:
            df_dict = pd.DataFrame(columns = ["name1", "name2", "frames"])
            df_dict['name1'] = df[leter+'Pos'] if leter else df['APos'] # Class A comes as the default one
            df_dict['name2'] = df_clust['GprotPos'].str.replace('\n','_').str.replace('G_','')
            df_dict['width'] = (df_clust['mean']).astype(int)
            df_dict['frames'] = df_clust['frames']
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
            json.dump(jsondict, jsonfile, ensure_ascii=False, indent = 4)        
        
def dendrogramming(df,outputs_path,partial_db_dict):
    """
    A mishmash of functions to create and save the dendrogram files we'll use in 
    the web application
    """

    #Computing frequency matrix
    dend_matrix = frequencies(df)

    # Labels for dendogram
    dendlabels_dyns = list(df.columns)

    #Preparing dendrogram folders and parameters
    dendfolder = outputs_path + "dendrograms/" 
    os.makedirs(dendfolder, exist_ok = True)
    dend_height = int(df.shape[1]) * 18
    dend_width = 450

    # Computing several dendrograms and corresponding json files
    for cluster in range(2,4):# DEBUG
    #         for cluster in list(range(2,21)):
        print('      computing dendrogram with '+str(cluster)+' clusters')
        dendfile = ("%s%iclusters_dendrogram.html" % (dendfolder, cluster))
        (dyn_dend_order, clustdict) = dendrogram_clustering(
            dend_matrix,
            dendlabels_dyns, 
            dend_height, 
            dend_width, 
            dendfile, 
            cluster, 
            partial_db_dict, 
        )
        # Write dynamicID-cluster dictionary on a json
        clustdir = "%sflareplots_clusters/%sclusters/" % (outputs_path, cluster)
        os.makedirs(clustdir, exist_ok= True)
        with open(clustdir + "clustdict.json", 'w') as clusdictfile:
            json.dump(clustdict, clusdictfile, ensure_ascii=False, indent = 4)

        #Jsons for the flareplots of this combinations of clusters
        cluster_flareplot(df, clustdict, clustdir, flare_template)

    #Store Simulation names and dyn on file
    create_dyntoname_file(dyn_dend_order, partial_db_dict, outputs_path)

    return(dyn_dend_order,dend_height)

def sort_simulations(df, dyn_dend_order):
    """
    Sorts the simulations in the dataframe according to the order in the list dyn_dend_order
    """

    # Create a dictionary with the order of each simulation row in the plot 
    dyn_dend_order_dict = { dyn_name : dyn_dend_order.index(dyn_name) for dyn_name in dyn_dend_order }

    # Adding column based in new order recieved from clustering
    df['clust_order'] =  df['Id'].apply(lambda x: dyn_dend_order_dict[x])

    #Sorting by ballesteros Id's (helixloop column) and clustering order
    df['helixloop'] = df['Residue'].apply(lambda x: re.sub(r'^(\d)x',r'\g<1>0x',x)) 
    df = df.sort_values(["helixloop",'clust_order'])

    #Drop sort columns once used
    df.drop(['helixloop','clust_order'], axis = 1, inplace = True)
    
    return df


####################
## heatmap functions
####################

def find_itype_freqs(df_ts,typelist):
    """
    Find interaction frequencies of individual interaction types and append them to main df
    """

    for itype in typelist:

        def find_freq(row,int_dict):
            k = (row['Id'],row['Residue'])
            freq_i = int_dict[k] if k in int_dict else 0.0
            return(freq_i)

        # Load table of specific interaction type
        df_path = "%s%s.tsv"%(interta_path, itype)
        if not os.path.exists(df_path):
            continue
        df_raw = pd.read_csv(df_path, sep="\s+")

        # Prepare table: filter low-freq inters, pass freqs to percentage, ....
        (df_itype,df_standard) = prepare_table(df_raw,db_dict)
        df_titype = df_itype.transpose().stack().reset_index()
        df_titype.columns = ['Id','Residue','freq']
        df_titype.set_index(['Id', 'Residue'], inplace=True)
        int_dict = df_titype.to_dict()['freq']

        # Find int-freq values for this itype, and append them to main dataframe
        df_ts[itype] = df_ts.apply(lambda x : find_freq(x,int_dict), axis=1)
        
    return(df_ts)

def create_hovertool(itype, itypes_order, hb_itypes, typelist, width=400):
    """
    Creates a list in hovertool format from the two dictionaries above
    """   

    #Creating hovertool listzzzz
    hoverlist = [('GPCR', '@Name'),
                 ('Gprot', '@gprot_name'),   
                 ('PDB id', '@pdb_id'),
                 ('Residue', '@resname_gennum'),
                 (typelist[itype], '@{freq}{0.00}%')
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

    # Mapper colors
    # I left here the ones just in case
    colors_auld = ['#800000', '#860000', '#8c0000', '#930000', '#990000', '#9f0000', '#a60000', '#ac0000', '#b20000', '#b90000', '#bf0000', '#c50000', '#cc0000', '#d20000', '#d80000', '#df0000', '#e50000', '#eb0000', '#f20000', '#f80000', '#ff0000', '#ff0700', '#ff0e00', '#ff1500', '#ff1c00', '#ff2300', '#ff2a00', '#ff3100', '#ff3800', '#ff3f00', '#ff4600', '#ff4d00', '#ff5400', '#ff5b00', '#ff6200', '#ff6900', '#ff7000', '#ff7700', '#ff7e00', '#ff8500', '#ff8c00', '#ff9100', '#ff9700', '#ff9d00', '#ffa300', '#ffa800', '#ffae00', '#ffb400', '#ffba00', '#ffbf00', '#ffc500', '#ffcb00', '#ffd100', '#ffd600', '#ffdc00', '#ffe200', '#ffe800', '#ffed00', '#fff300', '#fff900', '#ffff00', '#f2ff00', '#e5ff00', '#d8ff00', '#ccff00', '#bfff00', '#b2ff00', '#a5ff00', '#99ff00', '#8cff00', '#7fff00', '#72ff00', '#66ff00', '#59ff00', '#4cff00', '#3fff00', '#33ff00', '#26ff00', '#19ff00', '#0cff00', '#00ff00', '#0afc0a', '#15fa15', '#1ff81f', '#2af62a', '#34f434', '#3ff13f', '#49ef49', '#54ed54', '#5eeb5e', '#69e969', '#74e674', '#7ee47e', '#89e289', '#93e093', '#9ede9e', '#a8dba8', '#b3d9b3', '#bdd7bd', '#c8d5c8', '#d3d3d3']
    colors_ylorrd = ['#800026', '#850026', '#8a0026', '#8f0026', '#940026', '#990026', '#9e0026', '#a30026', '#a80026', '#ad0026', '#b20026', '#b70026', '#bd0026', '#c00225', '#c30424', '#c60623', '#c90822', '#cc0a21', '#d00d21', '#d30f20', '#d6111f', '#d9131e', '#dc151d', '#df171c', '#e31a1c', '#e51e1d', '#e7221e', '#e9271f', '#eb2b20', '#ed2f21', '#ef3423', '#f13824', '#f33c25', '#f54126', '#f74527', '#f94928', '#fc4e2a', '#fc532b', '#fc582d', '#fc5d2e', '#fc6330', '#fc6831', '#fc6d33', '#fc7234', '#fc7836', '#fc7d37', '#fc8239', '#fc873a', '#fd8d3c', '#fd903d', '#fd933e', '#fd9640', '#fd9941', '#fd9c42', '#fd9f44', '#fda245', '#fda546', '#fda848', '#fdab49', '#fdae4a', '#feb24c', '#feb54f', '#feb853', '#febb56', '#febf5a', '#fec25d', '#fec561', '#fec864', '#fecc68', '#fecf6b', '#fed26f', '#fed572', '#fed976', '#feda79', '#fedc7d', '#fede80', '#fedf84', '#fee187', '#fee38b', '#fee48e', '#fee692', '#fee895', '#fee999', '#feeb9c', '#ffeda0', '#ffeea3', '#fff0a7', '#fff1ab', '#fff3ae', '#fff4b2', '#fff6b6', '#fff7b9', '#fff9bd', '#fffac1', '#fffcc4', '#fffdc8', '#ffffcc']
    colors_grorrd = ['#800026', '#850026', '#8a0026', '#8f0026', '#940026', '#990026', '#9e0026', '#a30026', '#a80026', '#ad0026', '#b20026', '#b70026', '#bd0026', '#c00225', '#c30424', '#c60623', '#c90822', '#cc0a21', '#d00d21', '#d30f20', '#d6111f', '#d9131e', '#dc151d', '#df171c', '#e31a1c', '#e51e1d', '#e7221e', '#e9271f', '#eb2b20', '#ed2f21', '#ef3423', '#f13824', '#f33c25', '#f54126', '#f74527', '#f94928', '#fc4e2a', '#fc532b', '#fc582d', '#fc5d2e', '#fc6330', '#fc6831', '#fc6d33', '#fc7234', '#fc7836', '#fc7d37', '#fc8239', '#fc873a', '#fd8d3c', '#fd903d', '#fd933e', '#fd9640', '#fd9941', '#fd9c42', '#fd9f44', '#fda245', '#fda546', '#fda848', '#fdab49', '#fdae4a', '#feb24c', '#feb54f', '#feb853', '#febb56', '#febf5a', '#fec25d', '#fec561', '#fec864', '#fecc68', '#fecf6b', '#fed26f', '#fed572', '#fed976', '#feda79', '#fedc7d', '#fede80', '#fedf84', '#fee187', '#fee38b', '#fee48e', '#fee692', '#fee895', '#fee999', '#feeb9c', '#ffeda0', '#fbeaa4', '#f7e8a8', '#f4e6ac', '#f0e4b1', '#ece2b5', '#e9e0b9', '#e5ddbd', '#e1dbc2', '#ded9c6', '#dad7ca', '#d6d5ce', '#d3d3d3']
    colors_inferno = ['#000003', '#000004', '#000006', '#010007', '#010109', '#01010B', '#02010E', '#020210', '#030212', '#040314', '#040316', '#050418', '#06041B', '#07051D', '#08061F', '#090621', '#0A0723', '#0B0726', '#0D0828', '#0E082A', '#0F092D', '#10092F', '#120A32', '#130A34', '#140B36', '#160B39', '#170B3B', '#190B3E', '#1A0B40', '#1C0C43', '#1D0C45', '#1F0C47', '#200C4A', '#220B4C', '#240B4E', '#260B50', '#270B52', '#290B54', '#2B0A56', '#2D0A58', '#2E0A5A', '#300A5C', '#32095D', '#34095F', '#350960', '#370961', '#390962', '#3B0964', '#3C0965', '#3E0966', '#400966', '#410967', '#430A68', '#450A69', '#460A69', '#480B6A', '#4A0B6A', '#4B0C6B', '#4D0C6B', '#4F0D6C', '#500D6C', '#520E6C', '#530E6D', '#550F6D', '#570F6D', '#58106D', '#5A116D', '#5B116E', '#5D126E', '#5F126E', '#60136E', '#62146E', '#63146E', '#65156E', '#66156E', '#68166E', '#6A176E', '#6B176E', '#6D186E', '#6E186E', '#70196E', '#72196D', '#731A6D', '#751B6D', '#761B6D', '#781C6D', '#7A1C6D', '#7B1D6C', '#7D1D6C', '#7E1E6C', '#801F6B', '#811F6B', '#83206B', '#85206A', '#86216A', '#88216A', '#892269', '#8B2269', '#8D2369', '#8E2468', '#902468', '#912567', '#932567', '#952666', '#962666', '#982765', '#992864', '#9B2864', '#9C2963', '#9E2963', '#A02A62', '#A12B61', '#A32B61', '#A42C60', '#A62C5F', '#A72D5F', '#A92E5E', '#AB2E5D', '#AC2F5C', '#AE305B', '#AF315B', '#B1315A', '#B23259', '#B43358', '#B53357', '#B73456', '#B83556', '#BA3655', '#BB3754', '#BD3753', '#BE3852', '#BF3951', '#C13A50', '#C23B4F', '#C43C4E', '#C53D4D', '#C73E4C', '#C83E4B', '#C93F4A', '#CB4049', '#CC4148', '#CD4247', '#CF4446', '#D04544', '#D14643', '#D24742', '#D44841', '#D54940', '#D64A3F', '#D74B3E', '#D94D3D', '#DA4E3B', '#DB4F3A', '#DC5039', '#DD5238', '#DE5337', '#DF5436', '#E05634', '#E25733', '#E35832', '#E45A31', '#E55B30', '#E65C2E', '#E65E2D', '#E75F2C', '#E8612B', '#E9622A', '#EA6428', '#EB6527', '#EC6726', '#ED6825', '#ED6A23', '#EE6C22', '#EF6D21', '#F06F1F', '#F0701E', '#F1721D', '#F2741C', '#F2751A', '#F37719', '#F37918', '#F47A16', '#F57C15', '#F57E14', '#F68012', '#F68111', '#F78310', '#F7850E', '#F8870D', '#F8880C', '#F88A0B', '#F98C09', '#F98E08', '#F99008', '#FA9107', '#FA9306', '#FA9506', '#FA9706', '#FB9906', '#FB9B06', '#FB9D06', '#FB9E07', '#FBA007', '#FBA208', '#FBA40A', '#FBA60B', '#FBA80D', '#FBAA0E', '#FBAC10', '#FBAE12', '#FBB014', '#FBB116', '#FBB318', '#FBB51A', '#FBB71C', '#FBB91E', '#FABB21', '#FABD23', '#FABF25', '#FAC128', '#F9C32A', '#F9C52C', '#F9C72F', '#F8C931', '#F8CB34', '#F8CD37', '#F7CF3A', '#F7D13C', '#F6D33F', '#F6D542', '#F5D745', '#F5D948', '#F4DB4B', '#F4DC4F', '#F3DE52', '#F3E056', '#F3E259', '#F2E45D', '#F2E660', '#F1E864', '#F1E968', '#F1EB6C', '#F1ED70', '#F1EE74', '#F1F079', '#F1F27D', '#F2F381', '#F2F485', '#F3F689', '#F4F78D', '#F5F891', '#F6FA95', '#F7FB99', '#F9FC9D', '#FAFDA0', '#FCFEA4']
    colors_magma = ['#000003', '#000004', '#000006', '#010007', '#010109', '#01010B', '#02020D', '#02020F', '#030311', '#040313', '#040415', '#050417', '#060519', '#07051B', '#08061D', '#09071F', '#0A0722', '#0B0824', '#0C0926', '#0D0A28', '#0E0A2A', '#0F0B2C', '#100C2F', '#110C31', '#120D33', '#140D35', '#150E38', '#160E3A', '#170F3C', '#180F3F', '#1A1041', '#1B1044', '#1C1046', '#1E1049', '#1F114B', '#20114D', '#221150', '#231152', '#251155', '#261157', '#281159', '#2A115C', '#2B115E', '#2D1060', '#2F1062', '#301065', '#321067', '#341068', '#350F6A', '#370F6C', '#390F6E', '#3B0F6F', '#3C0F71', '#3E0F72', '#400F73', '#420F74', '#430F75', '#450F76', '#470F77', '#481078', '#4A1079', '#4B1079', '#4D117A', '#4F117B', '#50127B', '#52127C', '#53137C', '#55137D', '#57147D', '#58157E', '#5A157E', '#5B167E', '#5D177E', '#5E177F', '#60187F', '#61187F', '#63197F', '#651A80', '#661A80', '#681B80', '#691C80', '#6B1C80', '#6C1D80', '#6E1E81', '#6F1E81', '#711F81', '#731F81', '#742081', '#762181', '#772181', '#792281', '#7A2281', '#7C2381', '#7E2481', '#7F2481', '#812581', '#822581', '#842681', '#852681', '#872781', '#892881', '#8A2881', '#8C2980', '#8D2980', '#8F2A80', '#912A80', '#922B80', '#942B80', '#952C80', '#972C7F', '#992D7F', '#9A2D7F', '#9C2E7F', '#9E2E7E', '#9F2F7E', '#A12F7E', '#A3307E', '#A4307D', '#A6317D', '#A7317D', '#A9327C', '#AB337C', '#AC337B', '#AE347B', '#B0347B', '#B1357A', '#B3357A', '#B53679', '#B63679', '#B83778', '#B93778', '#BB3877', '#BD3977', '#BE3976', '#C03A75', '#C23A75', '#C33B74', '#C53C74', '#C63C73', '#C83D72', '#CA3E72', '#CB3E71', '#CD3F70', '#CE4070', '#D0416F', '#D1426E', '#D3426D', '#D4436D', '#D6446C', '#D7456B', '#D9466A', '#DA4769', '#DC4869', '#DD4968', '#DE4A67', '#E04B66', '#E14C66', '#E24D65', '#E44E64', '#E55063', '#E65162', '#E75262', '#E85461', '#EA5560', '#EB5660', '#EC585F', '#ED595F', '#EE5B5E', '#EE5D5D', '#EF5E5D', '#F0605D', '#F1615C', '#F2635C', '#F3655C', '#F3675B', '#F4685B', '#F56A5B', '#F56C5B', '#F66E5B', '#F6705B', '#F7715B', '#F7735C', '#F8755C', '#F8775C', '#F9795C', '#F97B5D', '#F97D5D', '#FA7F5E', '#FA805E', '#FA825F', '#FB8460', '#FB8660', '#FB8861', '#FB8A62', '#FC8C63', '#FC8E63', '#FC9064', '#FC9265', '#FC9366', '#FD9567', '#FD9768', '#FD9969', '#FD9B6A', '#FD9D6B', '#FD9F6C', '#FDA16E', '#FDA26F', '#FDA470', '#FEA671', '#FEA873', '#FEAA74', '#FEAC75', '#FEAE76', '#FEAF78', '#FEB179', '#FEB37B', '#FEB57C', '#FEB77D', '#FEB97F', '#FEBB80', '#FEBC82', '#FEBE83', '#FEC085', '#FEC286', '#FEC488', '#FEC689', '#FEC78B', '#FEC98D', '#FECB8E', '#FDCD90', '#FDCF92', '#FDD193', '#FDD295', '#FDD497', '#FDD698', '#FDD89A', '#FDDA9C', '#FDDC9D', '#FDDD9F', '#FDDFA1', '#FDE1A3', '#FCE3A5', '#FCE5A6', '#FCE6A8', '#FCE8AA', '#FCEAAC', '#FCECAE', '#FCEEB0', '#FCF0B1', '#FCF1B3', '#FCF3B5', '#FCF5B7', '#FBF7B9', '#FBF9BB', '#FBFABD', '#FBFCBF']
    colors_ylgnbl = ['#081d58', '#0a1e5d', '#0c2062', '#0f2267', '#11246c', '#142671', '#162876', '#182a7b', '#1b2c80', '#1d2e85', '#20308a', '#22328f', '#253494', '#243795', '#243b97', '#243e99', '#24429a', '#23459c', '#23499e', '#234c9f', '#2350a1', '#2253a3', '#2257a4', '#225aa6', '#225ea8', '#2162aa', '#2166ac', '#206aae', '#206fb0', '#1f73b2', '#1f77b4', '#1f7bb6', '#1e80b8', '#1e84ba', '#1d88bc', '#1d8cbe', '#1d91c0', '#2094c0', '#2397c0', '#269ac1', '#299dc1', '#2ca0c1', '#2fa3c2', '#32a6c2', '#35a9c2', '#38acc3', '#3bafc3', '#3eb2c3', '#41b6c4', '#46b7c3', '#4bb9c2', '#50bbc1', '#55bdc1', '#5abfc0', '#60c1bf', '#65c3be', '#6ac5be', '#6fc7bd', '#74c9bc', '#79cbbb', '#7fcdbb', '#85cfba', '#8bd1b9', '#91d4b9', '#97d6b8', '#9dd8b8', '#a3dbb7', '#a9ddb6', '#afdfb6', '#b5e2b5', '#bbe4b5', '#c1e6b4', '#c7e9b4', '#caeab3', '#cdebb3', '#d0ecb3', '#d3eeb3', '#d6efb2', '#daf0b2', '#ddf1b2', '#e0f3b2', '#e3f4b1', '#e6f5b1', '#e9f6b1', '#edf8b1', '#eef8b4', '#f0f9b7', '#f1f9bb', '#f3fabe', '#f4fac1', '#f6fbc5', '#f7fcc8', '#f9fccb', '#fafdcf', '#fcfdd2', '#fdfed5', '#ffffd9']
    colors_rdylbl = ['#a50026', '#a60529', '#a80a2c', '#aa0f2f', '#ac1432', '#ae1a35', '#b01f38', '#b1243b', '#b3293e', '#b52e42', '#b73445', '#b93948', '#bb3e4b', '#bc434e', '#be4851', '#c04e54', '#c25357', '#c4585b', '#c65d5e', '#c76261', '#c96864', '#cb6d67', '#cd726a', '#cf776d', '#d17c70', '#d28274', '#d48777', '#d68c7a', '#d8917d', '#da9680', '#dc9c83', '#dda186', '#dfa689', '#e1ab8d', '#e3b090', '#e5b693', '#e7bb96', '#e8c099', '#eac59c', '#ecca9f', '#eed0a2', '#f0d5a6', '#f2daa9', '#f3dfac', '#f5e4af', '#f7eab2', '#f9efb5', '#fbf4b8', '#fdf9bb', '#ffffbf', '#fafabe', '#f6f6bd', '#f2f2bc', '#eeeebb', '#e9eaba', '#e5e6b9', '#e1e2b9', '#dddeb8', '#d9dab7', '#d4d5b6', '#d0d1b5', '#cccdb4', '#c8c9b3', '#c4c5b3', '#bfc1b2', '#bbbdb1', '#b7b9b0', '#b3b5af', '#afb1ae', '#aaacad', '#a6a8ad', '#a2a4ac', '#9ea0ab', '#9a9caa', '#9598a9', '#9194a8', '#8d90a7', '#898ca7', '#8588a6', '#8083a5', '#7c7fa4', '#787ba3', '#7477a2', '#7073a1', '#6b6fa1', '#676ba0', '#63679f', '#5f639e', '#5b5f9d', '#565a9c', '#52569b', '#4e529b', '#4a4e9a', '#464a99', '#414698', '#3d4297', '#393e96', '#353a95', '#313695']
    colors_grlgrdgr = ['#0d2b17', '#0e2d17', '#0f2f17', '#103118', '#123318', '#133618', '#143819', '#153a19', '#173c1a', '#183e1a', '#19411a', '#1a431b', '#1c451b', '#1d471b', '#1e4a1c', '#1f4c1c', '#214e1d', '#22501d', '#23521d', '#24551e', '#26571e', '#27591e', '#285b1f', '#295e1f', '#2b6020', '#2c6220', '#2d6420', '#2f6621', '#306921', '#316b22', '#326d22', '#346f22', '#357223', '#367423', '#377623', '#397824', '#3a7a24', '#3b7d25', '#3c7f25', '#3e8125', '#3f8326', '#408626', '#418826', '#438a27', '#448c27', '#458e28', '#469128', '#489328', '#499529', '#4a9729', '#4c9a2a', '#4e9b2d', '#519c30', '#549d34', '#569e37', '#599f3a', '#5ca03e', '#5ea141', '#61a345', '#64a448', '#67a54b', '#69a64f', '#6ca752', '#6fa855', '#71a959', '#74ab5c', '#77ac60', '#79ad63', '#7cae66', '#7faf6a', '#82b06d', '#84b170', '#87b374', '#8ab477', '#8cb57b', '#8fb67e', '#92b781', '#94b885', '#97b988', '#9abb8c', '#9dbc8f', '#9fbd92', '#a2be96', '#a5bf99', '#a7c09c', '#aac1a0', '#adc3a3', '#afc4a7', '#b2c5aa', '#b5c6ad', '#b8c7b1', '#bac8b4', '#bdc9b7', '#c0cbbb', '#c2ccbe', '#c5cdc2', '#c8cec5', '#cacfc8', '#cdd0cc', '#d0d1cf', '#d3d3d3']
    colors = colors_grlgrdgr
    colors.reverse()
    mapper = LinearColorMapper(palette=colors, low=0, high=100)

    #Bokeh figure
    legend_margin = 0#leave some space for x-axis artificial labels
    p = figure(
        plot_width=width,
        plot_height=height+legend_margin,
        #title="Example freq",
        y_range=list(dataframe.Id.drop_duplicates()),
        x_range=list(dataframe.Residue.drop_duplicates()),
        tools=["hover","tap","save","reset","wheel_zoom"], 
        x_axis_location="above",
        active_drag=None,
        toolbar_location="right",
        toolbar_sticky = False,
        min_border_top = legend_margin,#leave some space for x-axis artificial labels
        min_border_bottom = 0,
    )

    # Create rectangle for heatmap
    mysource = ColumnDataSource(dataframe)
    p.rect(
        y="Id", 
        x="Residue",
        width=1, 
        height=1, 
        source=mysource,
        line_color="white", 
        fill_color=transform("freq", mapper),

        # set visual properties for selected glyphs
        selection_line_color="black",
        selection_fill_color=transform("freq", mapper),
        # set visual properties for non-selected glyphs
        nonselection_fill_color=transform("freq", mapper),
        nonselection_fill_alpha=1,
        nonselection_line_alpha=1,
        nonselection_line_color="white"
        )

    #Very poor way of creating X-axis labels. Necessary for having linejumps inside the axis labels
    x_cord = 0
    y_cord = len(list(dataframe.Id.drop_duplicates()))#Residue: 11 spaces above the plot's top border
    foolabel = Label(x=-3,
                     y=y_cord,
                     text='\n\n           A: \n           B: \n           C: \n           F: \n\nG protein: \n\n\n',
                     render_mode='css', 
                     border_line_alpha=1.0,
                     text_font_size = "10pt",
                     background_fill_color = "#FFFFFF")
    p.add_layout(foolabel)

    #Fore every unique Residue in the set, add a label in axis
    for Residue in list(dataframe.Residue.drop_duplicates()):
        Residue = Residue.replace("Ligand","Lig\n\n\n\n\n")
        foolabel = Label(x=x_cord,
                         y=y_cord,
                         text=Residue,
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

def select_tool_callback(partial_db_dict, gennum, itype, typelist, mysource):
    """
    Prepares the javascript script necessary for the side-window
    """
    

    # Datasource for generic numberings
    df_gnum=pd.DataFrame(gennum)
    gnum_source=ColumnDataSource(df_gnum)

    #Select tool and callback: (SIMPLIFIED)
    CB = CustomJS(
        args={"mysource" : mysource, "db_info":partial_db_dict, "gnum_info":gnum_source, "itype":itype, "typelist" : typelist},
        code="""
            var sel_ind = mysource.selected.indices[0];
            var plot_bclass=$("#retracting_parts").attr("class");
            if (sel_ind.length != 0){
                var data = mysource.data;
                var gnum_data=gnum_info.data;
                var recept_name=data["Name"][sel_ind];
                var dyn_id=data["Id"][sel_ind];
                var db_dyn = db_info[dyn_id]
                var resnamegnum = data["resname_gennum"][sel_ind];
                var gnums_array = resnamegnum.split(" ").map(val => { return val.slice(1) })
                var pos = data["resID"][sel_ind];
                var freq_type=data["freq"][sel_ind];
                var pos_array = pos.split(" ");
                var pos_string = pos_array.join("_")

                //We'll remove the last 4 characters of each label, corresponding to the residue name
                var pos_ind_array = gnums_array.map(value => { return gnum_data['index'].indexOf(value); });
                var nglsel_pos_array = pos_ind_array.map(value => { return gnum_data[dyn_id][value].slice(0,-4); });

                //Put db_data of this sym into variables
                var lig=db_dyn['lig_sname'];
                var lig_lname=db_dyn['lig_lname'];
                var recept=db_dyn['up_name'];
                var dId=dyn_id.match(/\d*$/)[0];
                var prot_id=db_dyn['prot_id'];
                var prot_lname=db_dyn['prot_lname'];
                var comp_id=db_dyn['comp_id'];
                var peplig=db_dyn['peplig']
                var struc_fname=db_dyn['struc_fname'];
                var struc_file=db_dyn['struc_f'];
                var traj_fnames=db_dyn['traj_fnames'];
                var traj_f=db_dyn['traj_f'];
                var pdb_id=db_dyn['pdb_id'];
                var pdb_id_nochain = pdb_id.split(".")[0];
                var gpcr_chain=db_dyn['gpcr_chain'];
                var gprot_chain_a=db_dyn['gprot_chain_a'];
                var gprot_chain_b=db_dyn['gprot_chain_b'];
                var gprot_chain_g=db_dyn['gprot_chain_g'];
                var delta=db_dyn['delta'];
             
                if (plot_bclass != "col-xs-9"){
                    $("#retracting_parts").attr("class","col-xs-9");
                    $("#first_col").attr("class","col-xs-7");
                    $("#second_col").attr("class","col-xs-5");
                    $("#info").css({"visibility":"visible","position":"relative","z-index":"auto"});
                }
                
                //Show NA comment if there is a NA in the Residue
                if(/N\/A/.test(resnamegnum)){
                    $('#na_comment').show();
                }

                //Setting type specific frequencies
                $( "#freq_" + itype).html(freq_type.toFixed(2) + "%");
                if (itype == "all") {
                    var my_type;
                    for (my_type in typelist) {
                        freq_type = data[my_type][sel_ind];
                        $( "#freq_" + my_type).html(parseFloat(freq_type).toFixed(2) + "%");
                    }
                }

                $("#recept_val").html(prot_lname + " ("+recept+")");
                $("#pos_val").html(resnamegnum);
                $("#pdb_id").html(pdb_id);
                $("#pdb_link").attr("href","https://www.rcsb.org/structure/" + pdb_id_nochain)
                if (Boolean(lig)) {
                    $("#lig_link").show();
                    if (peplig){
                        $("#lig_val").html(lig_lname);
                        $("#lig_link").attr("href","../../../dynadb/protein/id/"+comp_id);
                    } else {
                        $("#lig_val").html(lig_lname + " ("+lig+")");
                        $("#lig_link").attr("href","../../../dynadb/compound/id/"+comp_id);
                    }
                }
                else {
                    $("#lig_val").html("None");
                    $("#lig_link").hide();
                }
                $("#viewer_link").attr("href","../../../view/"+dId+"/"+pos_string);
                $("#recept_link").attr("href","../../../dynadb/protein/id/"+prot_id);
                
                $('#ngl_iframe')[0].contentWindow.$('body').trigger('createNewRef', 
                [struc_file, traj_fnames, traj_f ,lig, delta, pos, nglsel_pos_array,
                 gpcr_chain, gprot_chain_a, gprot_chain_b, gprot_chain_g]);

            } else {
                if (plot_bclass != "col-xs-12"){
                    $("#retracting_parts").attr("class","col-xs-12");
                    $("#info").css({"visibility":"hidden","position":"absolute","z-index":"-1"});
                } 
            }           
        """)

    p.js_on_event(Tap,CB)
    return(p)

# Three to one dictionary for residues
three_to_one = {
    'ALA': 'A',  # Alanine
    'ARG': 'R',  # Arginine
    'ASN': 'N',  # Asparagine
    'ASP': 'D',  # Aspartic Acid
    'CYS': 'C',  # Cysteine
    'GLU': 'E',  # Glutamic Acid
    'GLN': 'Q',  # Glutamine
    'GLY': 'G',  # Glycine
    'HIS': 'H',  # Histidine (neutral form)
    'HSD': 'H',  # Histidine (delta-protonated)
    'HSE': 'H',  # Histidine (epsilon-protonated)
    'HSP': 'H',  # Histidine (protonated on both delta and epsilon)
    'HID': 'H',  # Histidine (delta-protonated)
    'HIE': 'H',  # Histidine (epsilon-protonated)
    'HIP': 'H',  # Histidine (protonated on both delta and epsilon)    
    'ILE': 'I',  # Isoleucine
    'LEU': 'L',  # Leucine
    'LYS': 'K',  # Lysine (neutral form)
    'LYN': 'K',  # Lysine (protonated)
    'MET': 'M',  # Methionine
    'PHE': 'F',  # Phenylalanine
    'PRO': 'P',  # Proline
    'SER': 'S',  # Serine
    'THR': 'T',  # Threonine
    'TRP': 'W',  # Tryptophan
    'TYR': 'Y',  # Tyrosine
    'VAL': 'V'   # Valine
}

####################
## Initial variables
####################

# Set paths
server_filespath = "/GPCRmd/media/files/Precomputed/gpcr_gprot/web_inputs/"
# filespath = settings.MEDIA_ROOT
mediaroot = "/home/daranda/files_kasparov/"
precompath = mediaroot+"Precomputed/"
gpcrgprot_path = precompath + "gpcr_gprot/"
interta_path = gpcrgprot_path+"inter_tables/"
os.makedirs(interta_path, exist_ok=True)

# Load Database information from compl_info.json file
db_dict = json_dict(precompath + "compl_info.json")

# Load flareplot template
df_path = "%sall.tsv"%interta_path
df_raw = pd.read_csv(df_path, sep="\s+")
df_lowfreq = filter_lowfreq(df_raw)
template_path = gpcrgprot_path + "template.json" 
flareplot_template_gpcrgprot(df_lowfreq, template_path)
flare_template = json_dict(template_path)

# Interaction types and corresponding names
typelist =  {
    'all' : 'all types',
    'sb' : 'salt bridge',
    "pc" : 'pi-cation',
    "ps" : 'pi-stacking',
    'ts' : 't-stacking',
    "vdw" : 'van der waals',
    'hp' : 'hydrophobic',
    "hbbb" : 'backbone to backbone HB',
    "hbsb" : 'sidechain to backbone HB',
    "hbss" : 'sidechain to sidechain HB',
    "wb" : 'water bridge',
    "wb2" : 'extended water bridge',
    "hb" : 'hydrogen bonds',
}
hb_itypes = {
    "hbbb" : 'backbone to backbone',
    "hbsb" : 'sidechain to backbone',
    "hbss" : 'sidechain to sidechain',
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
cores = 5

#######
## Main
#######

# typelist =  {"all" : 'all types'}
typelist =  {"hb" : 'water bridge'}
for itype in typelist.keys():

    #####################
    # Adjusting dataframe
    #####################
    
    # Load data
    df_path = "%s%s.tsv"%(interta_path, itype)
    if not os.path.exists(df_path):
        print("no data for interaction type %s. Skipping..."%itype)
        continue
    df_raw = pd.read_csv(df_path, sep="\s+")
    print("Computing contmaps inputs for %s" % (itype))

    # Prepare table: filter low-freq inters, pass freqs to percentage, ....
    (df_all,df_standard) = prepare_table(df_raw,db_dict)

    # Make simulation-individual flareplots
    sim_jsons_path = '%sweb_inputs/%s/flareplots_sims/'%(gpcrgprot_path,itype) 
    dyn_flareplots(df_all, sim_jsons_path, flare_template)
    
    #Repeat everything for standartd and non-standard dataframes (our simulations and the simulations from everone in GPCRmd)
    for (stnd,df) in (("cmpl", df_all), ("stnd", df_standard)):
        
        # If there are no interactions with this ligandonly-itype combination
        if df.empty:
            print("No interactions avalible for this molecular partners and interaction type:%s-%s"%(itype,stnd)) 
            continue

        # Folders for heatmaps and dendrograms
        outputs_serverpath = "%s/%s/%s/" %(server_filespath, itype, stnd)
        outputs_path = "%sweb_inputs/%s/%s/" %(gpcrgprot_path, itype, stnd)
        os.makedirs(outputs_path, exist_ok=True)
        
        # Stack matrix (one row for each interaction pair and dynamic).
#       # Colnames are dynid,Residue and interaction frequency)
        df_ts = df.transpose().stack().reset_index()
        df_ts.columns = ['Id','Residue','freq']

        #Obtain information of each receptor such as their names and stuff
        (partial_db_dict,df_ts,gennum)=improve_receptor_names(df_ts,db_dict)
        
        # Create new column with both residue names and generic numbering of both residues interacting
        df_ts = df_ts.apply(lambda x: find_resnames_resids(x, db_dict, three_to_one),axis=1)
        
        #Storing dataframe with results in a CSV file, downloadable from web
        create_csvfile(outputs_path, partial_db_dict, df)

        ######################
        ## Create and save precomputed files for dendrograms shown left-side of heatmap
        ######################
        (dyn_dend_order,dend_height) = dendrogramming(df,outputs_path,partial_db_dict)
    
        ###########
        ## Heatmaps
        ###########

        # Sort according to dendrogram results
        df_ts = sort_simulations(df_ts, dyn_dend_order)

        #Taking some variables for dataframe slicing
        max_columns = 45
        pairs_number = df.shape[0]
        inter_number = df_ts.shape[0]
        inter_per_pair =  inter_number/pairs_number 
        number_heatmaps = ceil((inter_number/inter_per_pair)/max_columns)

        #Create heatmap folder if not yet exists
        heatmap_serverpath = "%sheatmaps/" % (outputs_serverpath)
        heatmap_path = "%sheatmaps/" % (outputs_path)
        os.makedirs(heatmap_path, exist_ok=True)

        # Append frequencies for all interaction types, if we are parsing itype 'all'
        if itype=='all':
            df_ts = find_itype_freqs(df_ts,typelist)
        
        #Saving dataframe for future uses in customized heatmaps
        df_ts.to_pickle(heatmap_path+"dataframe_for_customized.pkl")

        #Make heatmaps each 50 interacting pairs
        div_list = []
        heatmap_filename_list = []
        number_heatmap_list = []
        prev_slicepoint = 0
        pool = mp.Pool(cores)
        for i in range(1,number_heatmaps+1):
            number_heatmap_list.append(str(i))

            #Slice dataframe. Also definig heigth and width of the heatmap
            slicepoint = int(i*inter_per_pair*max_columns)
            if i == number_heatmaps:
                df_slided = df_ts[prev_slicepoint:]
            else:
                df_slided = df_ts[prev_slicepoint:slicepoint]
            num_respairs = len(df_slided['Residue'].unique())
            w = int(num_respairs*20+40)
            prev_slicepoint = slicepoint
            h=dend_height
            
            # Define bokeh figure and hovertool
            hover = create_hovertool(itype, itypes_order, hb_itypes, typelist)
            mysource,p = define_figure(w, h, df_slided, hover, itype)

            # Creating javascript for side-window
            p = select_tool_callback(partial_db_dict, gennum, itype, typelist, mysource)

            # Extract bokeh plot components and store them in lists
            script, div = components(p)

            # Write heatmap on file
            heatmap_filename = "%s%iheatmap.html" % (heatmap_path,i)
            with open(heatmap_filename, 'w') as heatmap:
                heatmap.write(script)
            
            # Save names of files and divs in lists, to be used by web app
            div_list.append(div.lstrip())
            heatmap_serverfilename = "%s%iheatmap.html" % (heatmap_serverpath,i)
            heatmap_filename_list.append(heatmap_serverfilename)
                
        pool.close()
        pool.join()             
        
        # Write server filenames of heatmaps and variables in a file
        variables_file = outputs_path+"variables.py" 
        with open(variables_file, 'w') as varfile:
            varfile.write("div_list = [\'%s\']\n" % "\',\'".join(div_list))
            varfile.write("heatmap_filename_list = [\'%s\']\n" % "\',\'".join(heatmap_filename_list))
            varfile.write("number_heatmaps_list = [\'%s\']\n" % "\',\'".join(number_heatmap_list))
        