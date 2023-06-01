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
from bokeh.models import Label, HoverTool, TapTool, CustomJS, BasicTicker, ColorBar, ColumnDataSource, LinearColorMapper, PrintfTickFormatter
from bokeh.transform import transform


# Be careful with this!!! Put here only because some false-positive warnings from pandas
import warnings
warnings.filterwarnings('ignore')

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


def new_columns(df):
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

    df.reset_index(drop = True, inplace = True)
    df_newcols1 =  split_by_class(df["Position1"])
    df_newcols2 =  split_by_class(df["Position2"])
    df = pd.concat([df, df_newcols1, df_newcols2], axis = 1)

    return df

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
    colors_auld = ['#800000', '#860000', '#8c0000', '#930000', '#990000', '#9f0000', '#a60000', '#ac0000', '#b20000', '#b90000', '#bf0000', '#c50000', '#cc0000', '#d20000', '#d80000', '#df0000', '#e50000', '#eb0000', '#f20000', '#f80000', '#ff0000', '#ff0700', '#ff0e00', '#ff1500', '#ff1c00', '#ff2300', '#ff2a00', '#ff3100', '#ff3800', '#ff3f00', '#ff4600', '#ff4d00', '#ff5400', '#ff5b00', '#ff6200', '#ff6900', '#ff7000', '#ff7700', '#ff7e00', '#ff8500', '#ff8c00', '#ff9100', '#ff9700', '#ff9d00', '#ffa300', '#ffa800', '#ffae00', '#ffb400', '#ffba00', '#ffbf00', '#ffc500', '#ffcb00', '#ffd100', '#ffd600', '#ffdc00', '#ffe200', '#ffe800', '#ffed00', '#fff300', '#fff900', '#ffff00', '#f2ff00', '#e5ff00', '#d8ff00', '#ccff00', '#bfff00', '#b2ff00', '#a5ff00', '#99ff00', '#8cff00', '#7fff00', '#72ff00', '#66ff00', '#59ff00', '#4cff00', '#3fff00', '#33ff00', '#26ff00', '#19ff00', '#0cff00', '#00ff00', '#0afc0a', '#15fa15', '#1ff81f', '#2af62a', '#34f434', '#3ff13f', '#49ef49', '#54ed54', '#5eeb5e', '#69e969', '#74e674', '#7ee47e', '#89e289', '#93e093', '#9ede9e', '#a8dba8', '#b3d9b3', '#bdd7bd', '#c8d5c8', '#d3d3d3']
    colors_ylgnbl = ['#081d58', '#0a1e5d', '#0c2062', '#0f2267', '#11246c', '#142671', '#162876', '#182a7b', '#1b2c80', '#1d2e85', '#20308a', '#22328f', '#253494', '#243795', '#243b97', '#243e99', '#24429a', '#23459c', '#23499e', '#234c9f', '#2350a1', '#2253a3', '#2257a4', '#225aa6', '#225ea8', '#2162aa', '#2166ac', '#206aae', '#206fb0', '#1f73b2', '#1f77b4', '#1f7bb6', '#1e80b8', '#1e84ba', '#1d88bc', '#1d8cbe', '#1d91c0', '#2094c0', '#2397c0', '#269ac1', '#299dc1', '#2ca0c1', '#2fa3c2', '#32a6c2', '#35a9c2', '#38acc3', '#3bafc3', '#3eb2c3', '#41b6c4', '#46b7c3', '#4bb9c2', '#50bbc1', '#55bdc1', '#5abfc0', '#60c1bf', '#65c3be', '#6ac5be', '#6fc7bd', '#74c9bc', '#79cbbb', '#7fcdbb', '#85cfba', '#8bd1b9', '#91d4b9', '#97d6b8', '#9dd8b8', '#a3dbb7', '#a9ddb6', '#afdfb6', '#b5e2b5', '#bbe4b5', '#c1e6b4', '#c7e9b4', '#caeab3', '#cdebb3', '#d0ecb3', '#d3eeb3', '#d6efb2', '#daf0b2', '#ddf1b2', '#e0f3b2', '#e3f4b1', '#e6f5b1', '#e9f6b1', '#edf8b1', '#eef8b4', '#f0f9b7', '#f1f9bb', '#f3fabe', '#f4fac1', '#f6fbc5', '#f7fcc8', '#f9fccb', '#fafdcf', '#fcfdd2', '#fdfed5', '#ffffd9']
    colors_ylorrd = ['#800026', '#850026', '#8a0026', '#8f0026', '#940026', '#990026', '#9e0026', '#a30026', '#a80026', '#ad0026', '#b20026', '#b70026', '#bd0026', '#c00225', '#c30424', '#c60623', '#c90822', '#cc0a21', '#d00d21', '#d30f20', '#d6111f', '#d9131e', '#dc151d', '#df171c', '#e31a1c', '#e51e1d', '#e7221e', '#e9271f', '#eb2b20', '#ed2f21', '#ef3423', '#f13824', '#f33c25', '#f54126', '#f74527', '#f94928', '#fc4e2a', '#fc532b', '#fc582d', '#fc5d2e', '#fc6330', '#fc6831', '#fc6d33', '#fc7234', '#fc7836', '#fc7d37', '#fc8239', '#fc873a', '#fd8d3c', '#fd903d', '#fd933e', '#fd9640', '#fd9941', '#fd9c42', '#fd9f44', '#fda245', '#fda546', '#fda848', '#fdab49', '#fdae4a', '#feb24c', '#feb54f', '#feb853', '#febb56', '#febf5a', '#fec25d', '#fec561', '#fec864', '#fecc68', '#fecf6b', '#fed26f', '#fed572', '#fed976', '#feda79', '#fedc7d', '#fede80', '#fedf84', '#fee187', '#fee38b', '#fee48e', '#fee692', '#fee895', '#fee999', '#feeb9c', '#ffeda0', '#ffeea3', '#fff0a7', '#fff1ab', '#fff3ae', '#fff4b2', '#fff6b6', '#fff7b9', '#fff9bd', '#fffac1', '#fffcc4', '#fffdc8', '#ffffcc']
    colors_grorrd = ['#800026', '#850026', '#8a0026', '#8f0026', '#940026', '#990026', '#9e0026', '#a30026', '#a80026', '#ad0026', '#b20026', '#b70026', '#bd0026', '#c00225', '#c30424', '#c60623', '#c90822', '#cc0a21', '#d00d21', '#d30f20', '#d6111f', '#d9131e', '#dc151d', '#df171c', '#e31a1c', '#e51e1d', '#e7221e', '#e9271f', '#eb2b20', '#ed2f21', '#ef3423', '#f13824', '#f33c25', '#f54126', '#f74527', '#f94928', '#fc4e2a', '#fc532b', '#fc582d', '#fc5d2e', '#fc6330', '#fc6831', '#fc6d33', '#fc7234', '#fc7836', '#fc7d37', '#fc8239', '#fc873a', '#fd8d3c', '#fd903d', '#fd933e', '#fd9640', '#fd9941', '#fd9c42', '#fd9f44', '#fda245', '#fda546', '#fda848', '#fdab49', '#fdae4a', '#feb24c', '#feb54f', '#feb853', '#febb56', '#febf5a', '#fec25d', '#fec561', '#fec864', '#fecc68', '#fecf6b', '#fed26f', '#fed572', '#fed976', '#feda79', '#fedc7d', '#fede80', '#fedf84', '#fee187', '#fee38b', '#fee48e', '#fee692', '#fee895', '#fee999', '#feeb9c', '#ffeda0', '#fbeaa4', '#f7e8a8', '#f4e6ac', '#f0e4b1', '#ece2b5', '#e9e0b9', '#e5ddbd', '#e1dbc2', '#ded9c6', '#dad7ca', '#d6d5ce', '#d3d3d3']
    colors = colors_grorrd
    colors.reverse()
    mapper = LinearColorMapper(palette=colors, low=0, high=100)

    #Bokeh figure
    p = figure(
        plot_width= width,
        plot_height=height,
        #title="Example freq",
        y_range=list(dataframe.shortName.drop_duplicates()),
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
        y="shortName", 
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

def customized_csv(df_filt,itype):

    """
    Prepare the downloadable customized csv file
    """
    
    df_csv = df_filt.pivot(index='Position', columns='shortName')[itype]

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