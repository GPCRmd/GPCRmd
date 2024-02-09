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
        "traj_fnames","traj_f","delta",'class','peplig','gprot_name','gprot_chain','gpcr_chain']:
            dyn_data[k] = compl_data[dyn_id][k]

        # Dictionary for generic numberings       
        gennums[dyn_id]=compl_data[dyn_id]["gpcr_pdb"]
        gennums[dyn_id].update(compl_data[dyn_id]["gprot_pdb"])

        partial_data[dyn_id] = dyn_data

    df_ts['pdb_id'] = df_ts['Id'].apply(lambda x: partial_data[x]['pdb_id'])
    df_ts['Name'] = df_ts['Id'].apply(lambda x: partial_data[x]['recept_name'])
    df_ts['gprot_name'] = df_ts['Id'].apply(lambda x: partial_data[x]['gprot_name'])

    return(partial_data,df_ts,gennums)

def create_hovertool(itype, itypes_order, hb_itypes, typelist):
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
    p = figure(
        width= width,
        height=height,
        #title="Example freq",
        y_range=list(dataframe.Name.drop_duplicates()),
        x_range=list(dataframe.Residue.drop_duplicates()),
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

    #Very poor way of creating X-axis labels. Necessary for having linejumps inside the axis labels
    x_cord = 0
    y_cord = len(list(dataframe.Id.drop_duplicates()))#Residue: 11 spaces above the plot's top border
    foolabel = Label(x=-3,
                     y=y_cord,
                     text='\n\n           A: \n           B: \n           C: \n           F: \n\nG protein: \n\n\n',
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
                var gprot_chain=db_dyn['gprot_chain'];
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
                
                console.log(gpcr_chain,gprot_chain)
                $('#ngl_iframe')[0].contentWindow.$('body').trigger('createNewRef', 
                [struc_file, traj_fnames, traj_f ,lig, delta, pos, nglsel_pos_array, gpcr_chain, gprot_chain]);

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

def customized_csv(df_filt,itype):

    """
    Prepare the downloadable customized csv file
    """
    
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