import matplotlib# MANDATORY TO BE IN FIRST PLACE!!
matplotlib.use('Agg')# MANDATORY TO BE IN SECOND PLACE!!
from django.shortcuts import render
from django.http import HttpResponse
from math import pi
from bokeh.palettes import cividis 
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool, TapTool, CustomJS,DataRange1d, Range1d, FuncTickFormatter, FixedTicker, ColorBar, ColumnDataSource, LinearColorMapper, PrintfTickFormatter
from bokeh.transform import transform
import pandas as pd
import numpy as np
from bokeh.io import output_notebook, show
from view.views import obtain_domain_url
from json import loads
from re import sub,compile
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, leaves_list, dendrogram
import mpld3

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

def removing_entries_and_freqsdict(df,itypes):
    """
    This function removes same-helix interactions from the dataframe, and merges toghether frequencies from same pair of 
    residues.
    It also returns a dictionary with the frequency data separated by type, for future uses
    """
    
    positions = dict()
    todelete = set()
    counter = 0
    dict_freqs = {}
    #This dictionary will be used to filter by a minimum total frequency threshold. Same as dict_freqs, but not separated by type
    dict_freqs_total = { pos: { dyn: 0.0 for dyn in df if (dyn != "Position") and (dyn != "itype") } for pos in df['Position'] }
    uplim = 0.0
    
    #Filtering same-helix contacts
    helixpattern = compile(r"""^(..)\w+\s+(\1)""")#For detecting same-helix contacts, the ones like 1.22x22 1.54x54
    helixfilter = df['Position'].str.contains(helixpattern)
    df = df[~helixfilter]
    
    for row in df.iterrows():
        seen = True
        position = row[1]["Position"]
        itype = row[1]["itype"]
        
        # Checking if that position is already seen
        if row[1]["Position"] not in positions.keys(): #If column doesn't has been seen yet
            positions[position] = row[0]
            dict_freqs[position] = {}
            seen = False
        
        #Iterating over Position,dyns and itype
        for entry,freq in row[1].iteritems():
            if type(freq) == str: #Avoid adding itypes and position codes
                continue
            
            #Adding to dict_freqs_by_pos, and checking if its higher than current maximum
            dict_freqs_total[position][entry] = dict_freqs_total[position][entry] + freq
            if dict_freqs_total[position][entry] > uplim: 
                uplim = dict_freqs_total[position][entry]
            
            if entry not in dict_freqs[position].keys():
                dict_freqs[position][entry] = {}
            dict_freqs[position][entry][itype] = freq
            if seen:
                freqtosum = df.at[positions[position], entry]
                df.at[positions[position], entry] = freqtosum + freq
        
        if seen:
            todelete.add(row[0])
            
    #Delete marked positions (Repeated-different-type interactions)
    df = df.loc[~df.index.isin(todelete)]
    
    # Delete positions in which all dyn are below threshold
    thres = uplim / 10
    pos_todelete = set(df['Position'])
    
    for pos in dict_freqs_total:
        for dyn in dict_freqs_total[pos]:
            frq = dict_freqs_total[pos][dyn]
            if frq >= thres:
                pos_todelete.discard(pos)
    
    df = df[~df['Position'].isin(pos_todelete)]
    
    
    return(df,dict_freqs)

def adapt_to_marionas(df):
    """
    This function comprises a series of operations to adapt the new tsv format to Mariona's original scripts.
    Also returns a dictionary
    """
    
    #Merging toghether both contacting aminoacid Ids
    df['Position'] = df[['Position1', 'Position2']].apply(lambda x: ' '.join(x), axis=1)
    df = df.drop(df.columns[[0, 1]], axis=1)

    #Changing ballesteros format from X-XXxXX to XxXX
    pattern = compile("-\d+")
    df['Position'] =df['Position'].apply(lambda x: sub(pattern,"",x))

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
    type_freqs = {}

    for itype in set_itypes:
        type_freqs[itype] = []

    # Filling dictionary for frequencies by interaction type
    for row in df_ts.iterrows():
        dyn = row[1]['Id']
        position = row[1]['Position']
        for itype in set_itypes:
            itype
            if itype in dict_freqs[position][dyn]:
                type_freqs[itype].append(dict_freqs[position][dyn][itype])
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


def dendrogram_clustering(dend_matrix, labels, height, width): 
    """
    dendrogram time, my dudes
    """
    arbitrary_dpi = 50 # Arbitrary. Don't pay attention to it
    inch_height = height / arbitrary_dpi
    inch_width = width / arbitrary_dpi

    #Setting matplotlib figure
    plt.figure(dpi = arbitrary_dpi,figsize = [inch_width, inch_height],facecolor = "white")
    
    # Creating dendrogram
    dn = dendrogram(
        dend_matrix,
        orientation = 'left',
        labels = labels,
        show_contracted = True
    )
    
    # Setting labels font size and color
    ax = plt.gca()
    ax.tick_params(axis='both', which='both', labelsize=15, colors="red", right= False, bottom=False)

    #Hiding dendrogram borders
    #ax.spines['left'].set_visible(False)
    #ax.spines['top'].set_visible(False)
    #ax.spines['right'].set_visible(False)

    # Rendering html figure with mpld3 module from our matplotlib figure
    html_dendrogram = mpld3.fig_to_html(plt.gcf())
    
    return mpld3.fig_to_html(plt.gcf())

def remove_lowfreq(df):
    """
    Delete position-pairs which frequency values don't reach a certain threshold in all simulations
    """
    lowthres = df['value'].max() /10
    positions_mantain = set(df[df['value'] >= lowthres]['Position'])    
    df = df[df['Position'].isin(positions_mantain)]
    return df

def get_contacts_plots(request, itypes, ligandonly):
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
		"vdw" : 'Van der Waals',
		"hbbb" : 'backbone to backbone HB',
		"hbsb" : 'sidechain to backbone HB',
		"hbss" : 'sidechain to sidechain HB',
		"hbls" : 'ligand to sidechain HB',
		"hblb" : 'ligand to backbone HB',
		"wb" : 'water bridge',
		"wb2" : 'extended water bridge',
		"lwb" : 'ligand water bridge',
		"lwb2" : 'ligand extendedwater bridge'
	}
	hb_itypes = {
		"hbbb" : 'backbone to backbone',
		"hbsb" : 'sidechain to backbone',
		"hbss" : 'sidechain to sidechain',
		"hbls" : 'ligand to sidechain',
		"hblb" : 'ligand to backbone',
	}
	wb_itypes = {
		"wb" : 'protein to protein',
		"wb2" : 'extended protein to protein',
		"lwb" : 'ligand to protein',
		"lwb2" : 'extended ligand to protein'    	
	}
	other_itypes = {
		'sb' : 'salt bridge',
		"pc" : 'pi-cation',
		"ps" : 'pi-stacking',
		'ts' : 't-stacking',
		"vdw" : 'Van der Waals',    
	}

	#Converting recieved interaction types into a set (except if option "all interactiosn" has been checked)
	if not itypes == "all":
		set_itypes = set(itypes.split("_"))
	else: 
		set_itypes =  (("sb", "pc", "ps", "ts", "vdw", "hbbb", "hbsb", "hbss", "wb", "wb2", "hbls", "hblb", "lwb", "lwb2"))

	#Creating itypes dictionary for selected types
	selected_itypes = { x:typelist[x] for x in set_itypes }

	#Loading files
	df_raw = pd.read_csv("/protwis/sites/files/get_contacts_files/contact_tables/compare_all.tsv",sep="\s+")
	compl_data = json_dict("/protwis/sites/files/Precomputed/crossreceptor_analysis_files/compl_info.json")

	# Filtering out non-desired interaction types
	if itypes != "all":
	    df = df_raw[df_raw['itype'].isin(set_itypes)]
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

	#Removing helix-to-helix and merging same residue-pair interaction frequencies
	df,dict_freqs = removing_entries_and_freqsdict(df,set_itypes)

	#Transposing dataframe
	df = df.set_index('Position')
	df_t = df.transpose()

	#Dropping away interaction type column
	df_t = df_t.drop('itype')

	#changing lowbars by withespaces in receptor's name (useless now)
	df_t.index = list( map(lambda x: x.replace("_"," ") ,df_t.index) )

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
	clust_order_names = [ index_dict[dyn] for dyn in clust_order ]
	# Adding column based in new order recieved from clustering
	clust_order_num = [  ]
	for row in df_ts.iterrows():
	    name = row[1][0]
	    clust_index = clust_order_names.index(name)
	    clust_order_num.append(clust_index)
	df_ts['clust_order'] = clust_order_num

	#Changing denlabels to full name format
	dendlabels_names = [ index_dict[dyn] for dyn in dendlabels ]

	#Sorting by ballesteros Id's (helixloop column) and clustering order
	df_ts['helixloop'] = df_ts['Position'].apply(lambda x: sub(r'^(\d)x',r'\g<1>0x',x)) 
	df_ts = df_ts.sort_values(["helixloop",'clust_order'])


	#Storing main data frame in session (to download as csv file in another view)
	request.session[0] = df_ts
	################
	##Mariona's part
	################

	#Create data source
	df_ri=pd.DataFrame(recept_info)
	ri_source=ColumnDataSource(df_ri)
	df_rio=pd.DataFrame(recept_info_order, index=[0])
	rio_source=ColumnDataSource(df_rio)
	df_gnum=pd.DataFrame(dyn_gpcr_pdb)
	gnum_source=ColumnDataSource(df_gnum)
	extra_source = ColumnDataSource({"mdsrv_url":[mdsrv_url]})

	# Mapper
	uplim = df_ts['value'].max()
	colors = ['#FF0000','#FF0800','#FF1000','#FF1800','#FF2000','#FF2800','#FF3000','#FF3800','#FF4000','#FF4800','#FF5000','#FF5900','#FF6100','#FF6900','#FF7100','#FF7900','#FF8100','#FF8900','#FF9100','#FF9900','#FFA100','#FFAA00','#FFB200','#FFBA00','#FFC200','#FFCA00','#FFD200','#FFDA00','#FFE200','#FFEA00','#FFF200','#FFFA00','#FAFF00','#F2FF00','#EAFF00','#E2FF00','#DAFF00','#D2FF00','#CAFF00','#C2FF00','#BAFF00','#B2FF00','#AAFF00','#A1FF00','#99FF00','#91FF00','#89FF00','#81FF00','#79FF00','#71FF00','#69FF00','#61FF00','#59FF00','#50FF00','#48FF00','#40FF00','#38FF00','#30FF00','#28FF00','#20FF00','#18FF00','#10FF00','#08FF00','#00FF00']
	colors.reverse()
	mapper = LinearColorMapper(palette=colors, low=0, high=uplim)

	# Define a figure
	mytools = ["hover","tap","save","reset","wheel_zoom","pan"]
	h=int(df.shape[1]*80 + 20)# I use the df dataframe instead of df_ts because the last one has acopled itypes columns
	w=16300 if int(df.shape[0]*80 + 80) > 16300 else int(df.shape[0]*80 + 80)  	
	cw=275
	p = figure(
		plot_width= w,#len(df_t.columns)*40, 
		plot_height=h,#int(len(df_t.index)*40*0.8),
		#title="Example freq",
		y_range=list(df_ts.Id.drop_duplicates()),
		x_range=list(df_ts.Position.drop_duplicates()),
		tools=mytools, 
		x_axis_location="above",
		active_drag=None,
		toolbar_location="right",
		toolbar_sticky = False,
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
		line_color=None, 
		fill_color=transform('value', mapper),

		# set visual properties for selected glyphs
		selection_line_color="crimson",
		selection_fill_color=transform('value', mapper),
		# set visual properties for non-selected glyphs
		nonselection_fill_alpha=1,
		nonselection_fill_color=transform('value', mapper),
		nonselection_line_color=None
		)

	#Creating dendrogram
	dend_width = 160 #Same width as two square column
	dendr_figure = dendrogram_clustering(dend_matrix, dendlabels_names, h-20, dend_width) 

	# Add legend
	ticker = FixedTicker(ticks=[0,uplim])
	formatter = FuncTickFormatter(
		args={'uplim':uplim},
		code="""
		    var data = {};
		    data[0] = 'Lower';
		    data[uplim] = 'Higher';
		    return data[tick];
			"""
		)
	color_bar = ColorBar(
		color_mapper=mapper, 
        location=(0, 0),
        label_standoff = 12,
        ticker=ticker,
        formatter=formatter,
        major_label_text_font_size="11pt"
    	)
	p.add_layout(color_bar, 'left')

	# Setting axis
	p.axis.axis_line_color = None
	p.axis.major_tick_line_color = None
	p.xaxis.major_label_text_font_size = "11pt"
	p.yaxis.major_label_text_font_size = "10pt"
	p.yaxis.visible = False
	p.axis.major_label_standoff = 0
	p.xaxis.major_label_orientation = 1#"vertical"

	#Creating hovertool list
	hoverlist = []
	for col in df_ts:
	    if col in set_itypes: #If is a type frequency column
	        itype = typelist[col]
	        hoverlist.append((itype, "@{" + col + '}{0.00}%'))

	    elif col == "value":#Total frequencies are only needed for color intensity, must not appear in the hovertool
	        continue
	        
	    else:
	        hoverlist.append((col, "@" + col))

	#Hover tool:
	hover = HoverTool(
	    tooltips=hoverlist
	)
	p.add_tools(hover)

	#Select tool and callback: (SIMPLIFIED)
	mysource.callback = CustomJS(
		args={"r_info":ri_source,"ro_info":rio_source,"gnum_info":gnum_source,"dict_freqs":dict_freqs,"selected_itypes":selected_itypes},
		code="""
			var sel_ind = cb_obj.selected["1d"].indices;
			var plot_bclass=$("#plot_col").attr("class");
			if (sel_ind.length != 0){
				var data = cb_obj.data;
				var ri_data=r_info.data;
				var rio_data=ro_info.data;
				var gnum_data=gnum_info.data;
				var recept_id=data["Id"][sel_ind];
				var pos=data["Position"][sel_ind];
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
				var sel_thresh=2.8;
                var struc_fname=ri_data[recept_id][rio_data['struc_fname']];
                var traj_fnames=ri_data[recept_id][rio_data['traj_fnames']];
                var delta=ri_data[recept_id][rio_data['delta']];

                $('#ngl_iframe')[0].contentWindow.$('body').trigger('createNewRef', [struc_fname, traj_fnames ,lig, delta, pos, pdb_pos_array]);
                
                if (plot_bclass != "col-xs-9"){
                    $("#plot_col").attr("class","col-xs-9");
                    $("#info").css({"visibility":"visible","position":"relative","z-index":"auto"});
                }

                //Printing my type-specific frequencies
                var freq = "";
                var typeid = "";
                for (type in selected_itypes){
                	freq = dict_freqs[pos]['dyn' + dyn_id][type];
                	typeid = "#freq_" + type;
					if(Boolean(freq)){
						$(typeid).html(freq);
					}
					else {
						freq= 0.0;
						$(typeid).html(freq);
					}
                }
                $("#freq_val").html(freq);
                $("#recept_val").html(prot_lname + " ("+recept+")");
                $("#pos_val").html(pos);
                $("#lig_val").html(lig_lname + " ("+lig+")");
                $("#viewer_link").attr("href","../../../view/"+dyn_id+"/"+pos_string);
                $("#recept_link").attr("href","../../../dynadb/protein/id/"+prot_id);
                $("#lig_link").attr("href","../../../dynadb/compound/id/"+comp_id);
            } else {
                if (plot_bclass != "col-xs-12"){
                    $("#info").css({"visibility":"hidden","position":"absolute","z-index":"-1"});
                    $("#plot_col").attr("class","col-xs-12");
                } 
            }            
            
        """)

	plotdiv_w=w+cw
	script, div = components(p)
	context={
		'dendrogram' : dendr_figure,
		'hb_itypes' : hb_itypes,
		'wb_itypes' : wb_itypes,
		'other_itypes' : other_itypes,
		'selected_itypes' : selected_itypes,
		'dict_freqs' : dict_freqs,
		'script' : script , 
		'div' : div,
		'plotdiv_w':plotdiv_w,
		'mdsrv_url':mdsrv_url
	}
	return render(request, 'contact_plots/index_h.html', context)

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