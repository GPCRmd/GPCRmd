from django.shortcuts import render
from django.http import HttpResponse
from math import pi
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool, TapTool, CustomJS,DataRange1d, Range1d, FuncTickFormatter, FixedTicker, ColorBar, ColumnDataSource, LinearColorMapper, PrintfTickFormatter
from bokeh.transform import transform
import pandas as pd
from bokeh.io import output_notebook, show
from view.views import obtain_domain_url
from json import loads
from re import sub,compile
from view.views import obtain_domain_url

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
    return(recept_info,recept_info_order,df_ts,dyn_gpcr_pdb)


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
    #Filtering same-helix contacts
    print(df)
    helixpattern = compile(r"""^(\d+)x.*\s+(\1)""")#For detecting same-helix contacts, the ones like 1.22x22 1.54x54
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
            if entry not in dict_freqs[position].keys():
                dict_freqs[position][entry] = {}
            dict_freqs[position][entry][itype] = freq
            if seen:
                freqtosum = df.at[positions[position], entry]
                df.at[positions[position], entry] = freqtosum + freq
        
        if seen:
            todelete.add(row[0])
    
    #Delete marked positions (Repeated-different-type interactions or same-helix)
    for rowname in todelete:
        df = df.drop(labels = [rowname], axis = 0)
    
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

	# Converting to df_ts table, 
	df_ts = df_t.stack().rename("value").reset_index()
	df_ts.rename(columns={"level_0": "Id"}, inplace=True)

	# Appending to the data-frame type-specific frequencies (will be needed for the hovertool)
	df_ts = add_itype_freqs(df_ts, set_itypes, dict_freqs) 

	#Changing ID names by simulation names
	(recept_info,recept_info_order,df_t,dyn_gpcr_pdb)=improve_receptor_names(df_ts,compl_data)

	#Sorting by ballesteros Id's
	df_ts = df_ts.sort_values("Position")

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
	colors = colors=["#FFFFFF",'#f7fcfc', '#f6fbfc', '#f5fafc', '#f4fafb', '#f2f9fb', '#f1f8fa', '#f0f8fa', '#eff7fa', '#edf6f9', '#ecf6f9', '#ebf5f8', '#e9f4f8', '#e8f4f7', '#e7f3f7', '#e6f2f7', '#e4f1f6', '#e3f0f6', '#e2f0f5', '#e1eff5', '#dfeef4', '#deedf4', '#ddecf4', '#dbebf3', '#daeaf3', '#d9eaf2', '#d8e9f2', '#d6e8f1', '#d5e7f1', '#d4e6f1', '#d3e5f0', '#d1e4f0', '#d0e3ef', '#cfe2ef', '#cde1ee', '#cce0ee', '#cbdfee', '#cadeed', '#c8dded', '#c7dcec', '#c6daec', '#c5d9ec', '#c3d8eb', '#c2d7eb', '#c1d6ea', '#bfd5ea', '#bed4e9', '#bdd2e9', '#bcd1e9', '#bad0e8', '#b9cfe8', '#b8cee7', '#b7cce7', '#b5cbe6', '#b4cae6', '#b3c9e6', '#b1c7e5', '#b0c6e5', '#afc5e4', '#aec3e4', '#acc2e3', '#abc1e3', '#aabfe3', '#a9bee2', '#a7bce2', '#a6bbe1', '#a5bae1', '#a3b8e0', '#a2b7e0', '#a1b5e0', '#a0b4df', '#9eb2df', '#9db1de', '#9cafde', '#9aaedd', '#99acdd', '#98abdd', '#97a9dc', '#95a8dc', '#94a6db', '#93a4db', '#92a3db', '#90a1da', '#8fa0da', '#8e9ed9', '#8c9cd9', '#8b9bd8', '#8a99d8', '#8997d8', '#8795d7', '#8694d7', '#8592d6', '#8490d6', '#828ed5', '#818dd5', '#808bd5', '#7e89d4', '#7d87d4', '#7c85d3', '#7b84d3', '#7982d2', '#7880d2', '#777ed2', '#767cd1', '#747ad1', '#7378d0', '#7276d0', '#7074cf', '#6f72cf', '#6e70cf', '#6d6fce', '#6b6dce', '#6a6bcd', '#6969cd', '#6968cd', '#6866cc', '#6865cc', '#6764cb', '#6762cb', '#6661ca', '#6660ca', '#655fca', '#655dc9', '#645cc9', '#645bc8', '#645ac8', '#6358c7', '#6357c7', '#6356c7', '#6254c6', '#6253c6', '#6252c5', '#6151c5', '#614fc4', '#614ec4', '#614dc4', '#604bc3', '#604ac3', '#6049c2', '#6048c2', '#6046c1', '#5f45c1', '#5f44c1', '#5f43c0', '#5f41c0', '#5f40bf', '#5f3fbe', '#5f3fbd', '#603fbc', '#603eba', '#603eb9', '#603db8', '#613db7', '#613cb5', '#613cb4', '#613cb3', '#623bb2', '#623bb0', '#623aaf', '#623aae', '#6239ac', '#6239ab', '#6239aa', '#6238a9', '#6338a7', '#6337a6', '#6337a5', '#6336a3', '#6336a2', '#6336a1', '#6335a0', '#63359e', '#63349d', '#63349c', '#63349b', '#633399', '#633398', '#633297', '#623295', '#623194', '#623193', '#623192', '#623090', '#62308f', '#622f8e', '#622f8d', '#612e8b', '#612e8a', '#612e89', '#612d87', '#602d86', '#602c85', '#602c84', '#602b82', '#5f2b81', '#5f2b80', '#5f2a7f', '#5e2a7d', '#5e297c', '#5e297b', '#5d2879', '#5d2878', '#5d2877', '#5c2776', '#5c2774', '#5b2673', '#5b2672', '#5a2671', '#5a256f', '#59256e', '#59246d', '#58246b', '#58236a', '#572369', '#572368', '#562266', '#562265', '#552164', '#552163', '#542061', '#532060', '#53205f', '#521f5d', '#511f5c', '#511e5b', '#501e5a', '#4f1d58', '#4f1d57', '#4e1d56', '#4d1c55', '#4c1c53', '#4c1b52', '#4b1b51', '#4a1a4f', '#491a4e', '#481a4d', '#48194c', '#47194a', '#461849', '#451848', '#441746', '#431745', '#421744', '#411643', '#411641', '#401540', '#3f153f', '#3e153d', '#3c143c', '#3b143a', '#3a1339']
	mapper = LinearColorMapper(palette=colors, low=0, high=uplim)

	# Define a figure
	mytools = ["hover","tap","save","reset","wheel_zoom","pan"]
	h=int(df.shape[1]*80)
	w=int(df.shape[0]*80 + 500) # I use the df dataframe instead of df_ts becauese the last one has acopled itypes columns
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

	# Rotate angle of legends
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

	# Add legend
	ticker = FixedTicker(ticks=[0,uplim])
	formatter = FuncTickFormatter(args={'uplim':uplim},code="""
	    var data = {};
	    data[0] = 'Lower';
	    data[uplim] = 'Higher';
	    return data[tick];
	""")
	color_bar = ColorBar(color_mapper=mapper, 
	                     location=(0, 0),
	                     label_standoff = 12,
	                     ticker=ticker,
	                    formatter=formatter,
	                     major_label_text_font_size="11pt"
	                    )
	p.add_layout(color_bar, 'right')
	p.axis.axis_line_color = None
	p.axis.major_tick_line_color = None
	p.xaxis.major_label_text_font_size = "11pt"
	p.yaxis.major_label_text_font_size = "10pt"
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