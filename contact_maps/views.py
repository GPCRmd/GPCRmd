import matplotlib# MANDATORY TO BE IN FIRST PLACE!!
matplotlib.use('Agg')# MANDATORY TO BE IN SECOND PLACE!!
from os.path import exists 
from django.shortcuts import render
from importlib.machinery import SourceFileLoader
from django.http import HttpResponse
from math import pi
from bokeh.palettes import cividis
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool, TapTool, CustomJS, DataRange1d, Range1d, BasicTicker, ColorBar, ColumnDataSource, LinearColorMapper, PrintfTickFormatter
from bokeh.transform import transform
import pandas as pd
import numpy as np
from bokeh.io import output_notebook, show
from view.views import obtain_domain_url
from json import loads
from re import sub,compile

def json_dict(path):
    """Converts json file to pyhton dict."""
    json_file=open(path)
    json_str = json_file.read()
    json_data = loads(json_str)
    return json_data

def get_contacts_plots(request, itype = "all", ligandonly = "prt_lg", rev = "norev"):
	"""
	Main view of contact plots
	"""
	mdsrv_url=obtain_domain_url(request)

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
	    "hb" : 'hydrogen bond',
	    'all' : 'all types',
	}
	hb_itypes = [
		("hbbb", 'backbone to backbone HB'),
	    ("hbsb" , 'sidechain to backbone HB'),
	    ("hbss" , 'sidechain to sidechain HB'),
	    ("hbls" , 'ligand to sidechain HB'),
	    ("hblb" , 'ligand to backbone HB'),
	]

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

	# Creating set_itypes, with all in case it is not still in it
	if not itype == "all":
	    set_itypes = set(itype.split("_"))
	else: 
	    set_itypes =  (("sb", "pc", "ps", "ts", "vdw", "hp", "hb", "hbbb", "hbsb", "hbss", "wb", "wb2", "hbls", "hblb"))

	#Creating itypes dictionary for selected types
	selected_itypes = { x:typelist[x] for x in set_itypes }

	# Loading json dict
	compl_data = json_dict("/protwis/sites/files/Precomputed/crossreceptor_analysis_files/compl_info.json")

	basedir = "/protwis/sites/files/Precomputed/get_contacts_files/view_input_dataframe/"

	# Loading csv if it exists. If not, load "no interactions" template instead
	csv_name = basedir + itype + "_" + ligandonly + "_" + rev + "_dataframe.csv"
 
	if exists(csv_name):
		df_ts = pd.read_csv(csv_name, sep=",", index_col = 0)
	else:
		context = {
			'itype_code' : itype,
			'itype_name' : typelist[itype],
			'hb_itypes' : hb_itypes,
			'itypes_order' : itypes_order,
			'selected_itypes' : selected_itypes,
		}
		return render(request, 'contact_maps/index_nodata.html', context)

	# Loading variables
	variablesmod = SourceFileLoader("module.name", basedir + itype + "_" + ligandonly + "_variables.py").load_module()
	recept_info = variablesmod.recept_info
	recept_info_order = variablesmod.recept_info_order
	dyn_gpcr_pdb = variablesmod.dyn_gpcr_pdb
	figure_shape = variablesmod.figure_shape

	# Loading dendrogram
	dendr_figure = open(basedir + itype + "_" + ligandonly + "_dendrogram_figure.html", 'r').read()

	#Storing main data frame in session (to download as csv file in another view)
	request.session[0] = df_ts

	#Create data source
	df_ri=pd.DataFrame(recept_info)
	ri_source=ColumnDataSource(df_ri)
	df_rio=pd.DataFrame(recept_info_order, index=[0])
	rio_source=ColumnDataSource(df_rio)
	df_gnum=pd.DataFrame(dyn_gpcr_pdb)
	gnum_source=ColumnDataSource(df_gnum)
	extra_source = ColumnDataSource({"mdsrv_url":[mdsrv_url]})

	# Mapper
	colors = ['#FF0000','#FF0800','#FF1000','#FF1800','#FF2000','#FF2800','#FF3000','#FF3800','#FF4000','#FF4800','#FF5000','#FF5900','#FF6100','#FF6900','#FF7100','#FF7900','#FF8100','#FF8900','#FF9100','#FF9900','#FFA100','#FFAA00','#FFB200','#FFBA00','#FFC200','#FFCA00','#FFD200','#FFDA00','#FFE200','#FFEA00','#FFF200','#FFFA00','#FAFF00','#F2FF00','#EAFF00','#E2FF00','#DAFF00','#D2FF00','#CAFF00','#C2FF00','#BAFF00','#B2FF00','#AAFF00','#A1FF00','#99FF00','#91FF00','#89FF00','#81FF00','#79FF00','#71FF00','#69FF00','#61FF00','#59FF00','#50FF00','#48FF00','#40FF00','#38FF00','#30FF00','#28FF00','#20FF00','#18FF00','#10FF00','#08FF00','#00FF00']
	colors.reverse()
	mapper = LinearColorMapper(palette=colors, low=0, high=100)

	# Define a figure
	mytools = ["hover","tap","save","reset","wheel_zoom"]

	cw=275
	p = figure(
		plot_width= figure_shape['width'], 
		plot_height=figure_shape['height'],
		#title="Example freq",
		y_range=list(df_ts.Id.drop_duplicates()),
		x_range=list(df_ts.Position.drop_duplicates()),
		tools=mytools, 
		x_axis_location="above",
		active_drag=None,
		toolbar_location="right",
		toolbar_sticky = False,
		min_border_top = round(figure_shape['height'] * 0.045) # The proportion of margin to be left on top of matrix to align with dendrogram
		)

	# Rotate angle of x-axis labels
	p.xaxis.major_label_orientation = pi/3

	# Create rectangle for heatmap
	mysource = ColumnDataSource(df_ts)
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

	#Creating hovertool list
	hoverlist = [('Id', '@Id'), ('Position', '@Position')]
	if itype == "all":
	    for group,type_tuple in itypes_order:
	        for itype_code,itype_name in type_tuple:
	            hoverlist.append((itype_name, "@{" + itype_code + '}{0.00}%'))
	            if itype_code == "hb":
	                for hb_code,hb_name in hb_itypes:
	                    hoverlist.append((hb_name, "@{" + hb_code + '}{0.00}%'))
	else:
	    hoverlist.append((typelist[itype], "@{" + itype + '}{0.00}%'))
	hoverlist.append(('Total interaction frequency', '@{all}{0.00}%'))

	#Hover tool:
	hover = HoverTool(
	    tooltips=hoverlist
	)
	p.add_tools(hover)


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

	# Find path to files 

	plotdiv_w= figure_shape['width'] + cw
	script, div = components(p)
	context={
		'itypes_order' : itypes_order,
		'itypes_dict' : typelist,
		'itype_code' : itype,
		'ligandonly' : ligandonly,
		'itype_name' : typelist[itype],
		'dendrogram' : dendr_figure,
		'hb_itypes' : hb_itypes,
		'script' : script , 
		'div' : div,
		'plotdiv_w':plotdiv_w,
		'mdsrv_url':mdsrv_url
	}
	return render(request, 'contact_maps/index_h.html', context)

def get_csv_file(request,foo):
	"""
	Processing informatino from get_contact plots to create and download a csv file
	"""

	#Retrieving info for session
	df = request.session[0]

	#Creating and downloading CSV file from df
	csvfile = df.to_csv(index=False)#Rownames are undesired
	response = HttpResponse(csvfile, content_type='text/plain')
	response['Content-Disposition'] = 'attachment; filename={0}'.format("ContactPlots")
	return response

def get_itype_help(request, foo):
	return render(request, 'contact_maps/itype_help.html')