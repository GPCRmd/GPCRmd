from sys import argv,exit
import pandas as pd
from  numpy import array
from json import loads, dump
import numpy as np
import os
import re
from math import ceil,pi
from bokeh.plotting import figure, show, reset_output
from bokeh.embed import components
from bokeh.models import HTMLLabel,Label, HoverTool, TapTool, CustomJS, BasicTicker, ColorBar, ColumnDataSource, LinearColorMapper, PrintfTickFormatter
from bokeh.transform import transform
from bokeh.events import Tap


# Be careful with this!!! Put here only because some false-positive warnings from pandas
import warnings
warnings.filterwarnings('ignore')

#onary for residues
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


############
## Functions
############

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
        'gprot_chain_a','gprot_chain_b','gprot_chain_g','arr_name','arr_chain','gpcr_chain']:
            dyn_data[k] = compl_data[dyn_id][k]

        # Dictionary for generic numberings       
        gennums[dyn_id]=compl_data[dyn_id]["gpcr_pdb"]
        gennums[dyn_id].update(compl_data[dyn_id]["gprot_pdb"])
        gennums[dyn_id].update(compl_data[dyn_id]["arr_pdb"])

        partial_data[dyn_id] = dyn_data

    df_ts['pdb_id'] = df_ts['Id'].apply(lambda x: partial_data[x]['pdb_id'])
    df_ts['Name'] = df_ts['Id'].apply(lambda x: partial_data[x]['recept_name'])
    df_ts['gprot_name'] = df_ts['Id'].apply(lambda x: partial_data[x]['gprot_name'])
    df_ts['arr_name'] = df_ts['Id'].apply(lambda x: partial_data[x]['arr_name'])

    return(partial_data,df_ts,gennums)

def create_hovertool(itype, typelist, gprot = False, arr = False):
    """
    Creates a list in hovertool format from the two dictionaries above
    """

    #Creating hovertool listzzzz
    hoverlist = [
                 ('PDB id', '@pdb_id'),
                 ('Residue', '@resname_gennum'),
                 (typelist[itype], '@{freq}{0.00}%')
                ]
    if arr:
        hoverlist.insert(0,('Arrestin', '@arr_name'))
    if gprot:
        hoverlist.insert(0,('Gprot', '@gprot_name'))
    hoverlist.insert(0,('GPCR', '@Name'))

    #Hover tool:
    hover = HoverTool(
        tooltips=hoverlist
    )

    return hover
  
def define_figure(width, height, dataframe, hover, colors, app='gpcr_gprot'):
    """
    Prepare bokeh figure heatmap as intended
    """

    # Mapper colors
    # I left here the ones just in case
    mapper = LinearColorMapper(palette=colors, low=0, high=100)

    #Bokeh figure
    legend_margin = 0#leave some space for x-axis artificial labels
    p = figure(
        width= width,
        height=height+legend_margin,
        #title="Example freq",
        y_range=list(dataframe.Name.drop_duplicates()),
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
        y="Name", 
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

    # Initial X-label
    if app=='gpcr_gprot':
        title = '\n\n           A: \n           B: \n           C: \n           F: \n\nG protein: \n\n\n'
        my_x=-3
    elif app=='gpcr_arr':
        title = '\n\n           A: \n           B: \n           C: \n           F: \n\nArrestin: \n\n\n'
        my_x=-2
    else:
        title = '\nA: \nB: \nC: \nF: \n\n\nA: \nB: \nC: \nF: \n'
        my_x=-1
    #Very poor way of creating X-axis labels. Necessary for having linejumps inside the axis labels
    x_cord = 0
    y_cord = len(list(dataframe.Id.drop_duplicates()))#Residue: 11 spaces above the plot's top border
    foolabel = HTMLLabel(x=my_x,
                     y=y_cord,
                     text=title,
                    #  render_mode='css', 
                     border_line_alpha=1.0,
                     text_font_size = "10pt",
                     background_fill_color = "#FFFFFF")
    p.add_layout(foolabel)

    #Fore every unique Residue in the set, add a label in axis
    for Residue in list(dataframe.Residue.drop_duplicates()):
        Residue = Residue.replace("Ligand","Lig\n\n\n\n\n")
        foolabel = HTMLLabel(x=x_cord,
                         y=y_cord,
                         text=Residue,
                        #  render_mode='css', 
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
    p.xaxis.visible = False
    p.axis.major_label_standoff = 0
    p.xaxis.major_label_orientation = 1

    # Adding hover
    p.add_tools(hover)

    # Needed later
    return(mysource,p)

def select_tool_callback(p, partial_db_dict, gennum, itype, typelist, mysource):
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
                var pos_ind_array = gnums_array
                    .map(value => gnum_data['index'].indexOf(value))
                    .filter(value => value !== -1); // Filter out values equal to -1
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
                var arr_chain=db_dyn['arr_chain'];
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
                gpcr_chain, gprot_chain_a, gprot_chain_b, gprot_chain_g, peplig, arr_chain]);

            } else {
                if (plot_bclass != "col-xs-12"){
                    $("#retracting_parts").attr("class","col-xs-12");
                    $("#info").css({"visibility":"hidden","position":"absolute","z-index":"-1"});
                } 
            }           
        """)

    p.js_on_event(Tap,CB)
    return(p)


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
            
        # If from Gprot/Arrestin
        else:
            prot = 'gprot' if pos.startswith('G') else 'arr'
            gennum = pos.replace('_','.')
            gennum = pos.replace('\n','.')

        # Find resids and resnames for generic numberings
        if pos == 'Ligand':
            resname = ''
            resid = 'Ligand'
        else:                
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

def customized_csv(df_filt,itype):

    """
    Prepare the downloadable customized csv file
    """
    
    df_filt['Name'] = df_filt['Name']+' ('+df_filt['Id']+')'
    df_csv = df_filt.pivot(index='Residue', columns='Name')
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

    csv_data = df_csv.to_csv(float_format='%.1f')
    return csv_data

########
## Main
########

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
    "wb" : 'water bridge',
    "wb2" : 'extended water bridge',
    "hb" : 'hydrogen bonds',
    'all' : 'all types',
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