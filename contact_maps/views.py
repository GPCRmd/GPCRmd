import matplotlib# MANDATORY TO BE IN FIRST PLACE!!
matplotlib.use('Agg')# MANDATORY TO BE IN SECOND PLACE!!
from os.path import exists 
from django.shortcuts import render
from importlib.machinery import SourceFileLoader
from django.http import HttpResponse
import pandas as pd
from view.views import obtain_domain_url
from json import loads
from wsgiref.util import FileWrapper
from contact_maps.scripts.customized_heatmap import *
from django.views.decorators.csrf import csrf_protect

def json_dict(path):
	"""Converts json file to pyhton dict."""
	json_file=open(path)
	json_str = json_file.read()
	json_data = loads(json_str)
	return json_data

def get_contacts_plots(request):
	"""
	Main view of contact plots
	"""

	#Take query arguments, if any
	if request.GET.get('itype'): #If there are parameters
		itype = request.GET.get('itype')
		ligandonly = request.GET.get('prtn')
		rev = request.GET.get('rev')
		cluster = request.GET.get('cluster')
		stnd = request.GET.get('stnd')
	else:
		itype = 'all'
		ligandonly = 'prt_lg'
		rev = 'norev'
		cluster = '3'
		stnd = 'stnd'

	mdsrv_url=obtain_domain_url(request)
	basepath = "/protwis/sites/files/Precomputed/get_contacts_files/"
	basedir = "%scontmaps_inputs/%s/%s/%s/" % (basepath,itype,stnd,ligandonly)

	#Path to json
	fpdir = "/dynadb/files/Precomputed/get_contacts_files/contmaps_inputs/%s/%s/%s/flarejsons/%sclusters/" %  (itype, stnd, ligandonly, cluster)


	#First batch of context variables
	context = {
		'fpdir' : fpdir,
		'itype_code' : itype,
		'itype_name' : typelist[itype],
		'hb_itypes' : hb_itypes,
		'itypes_order' : itypes_order,
		'clusrange_all': list(range(2,21)),
		'ligandonly' : ligandonly,
		'rev' : rev,
		'stnd': stnd,
		'cluster' : int(cluster),
	}

	# Loading variables if file exists. If not, it means there are no interactions avalible for the selected options
	variablesfile = "%sheatmaps/%s/variables.py" % (basedir,rev)
	if exists(variablesfile):
		variablesmod = SourceFileLoader("module.name", variablesfile).load_module()
		number_heatmaps_list = variablesmod.number_heatmaps_list
		divwidth_list = variablesmod.divwidth_list
		div_list = variablesmod.div_list
		filenames_list = variablesmod.heatmap_filename_list
	else :
		return render(request,'contact_maps/index_nodata.html',context)

	#Loading json dynID-to-receptor_name dictionary
	dyn_to_names = json_dict(basedir+"name_to_dyn_dict.json")

	# Loading heatmap script 
	script_list = []
	for filename in filenames_list:
		with open(filename, 'r') as scriptfile:
			script = scriptfile.read()
		script_list.append(script)

	#Loading dynamics-cluster dictionary
	clustdict = json_dict("%sflarejsons/%sclusters/clustdict.json" % (basedir, cluster))

	# Loading dendrogram
	dendfile = ("%sdendrograms/%sclusters_dendrogram.html" % (basedir, cluster))
	dendr_figure = open(dendfile, 'r').read()

	first_sim = clustdict['cluster1'][0]

	# Send request 
	context.update({
		'clustdict' : clustdict,
		'itypes_dict' : typelist,
		'dendrogram' : dendr_figure,
		'script_list' : script_list, 
		'number_heatmaps_list' : number_heatmaps_list,
		'numbered_divs' : zip(number_heatmaps_list, div_list),
		'numbered_divwidths':zip(number_heatmaps_list, divwidth_list), 
		'clusrange_all': list(range(2,21)),
		'clusrange': list(range(1,int(cluster)+1)),
		'mdsrv_url':mdsrv_url,
		'dyn_to_names' : dyn_to_names,		
	})
	return render(request, 'contact_maps/index_h.html', context)

def get_csv_file(request):
	"""
	Processing informatino from get_contact plots to create and download a csv file
	"""

	#Taking arguments
	itype = request.GET.get('itype')
	ligandonly = request.GET.get('prtn')
	rev = request.GET.get('rev')
	stnd = request.GET.get('stnd')

	csv_name = "/protwis/sites/files/Precomputed/get_contacts_files/contmaps_inputs/%s/%s/%s/dataframe.csv" % (itype, stnd, ligandonly)

	#Creating and downloading CSV file from df
	csvfile = FileWrapper(open(csv_name, "r"))
	response = HttpResponse(csvfile, content_type='text/plain')
	response['Content-Disposition'] = 'attachment; filename={0}'.format("ContactMaps-%s-%s.csv" % (itype, ligandonly))
	return response

def get_itype_help(request, foo):
	return render(request=request, template_name='contact_maps/itype_help.html')

@csrf_protect
def customized_heatmap(request, foo):

	"""
	This whole script is designed with the single purpouse of creating a customized bokeh interaction heatmap for a desired set of simulations
		- dyn_list: set with the identifiers of the selected simulations
		- itype, ligandonly, rev, stnd: parameters of the selected contactMap
		- code: unique identifier of this request.
	"""

	#Parameters
	dyn_list  = request.POST['SimList'].split('&')
	itype = request.GET.get('itype')
	ligandonly = request.GET.get('prtn')
	rev = request.GET.get('rev')
	cluster = request.GET.get('cluster')
	stnd = request.GET.get('stnd')
	code = request.GET.get('code')

	#Paths
	basepath = "/protwis/sites/files/Precomputed/get_contacts_files/"
	options_path = "%scontmaps_inputs/%s/%s/%s/" %(basepath, itype, stnd, ligandonly)
	heatmap_path_jupyter = "/protwis/sites/files/Precomputed/get_contacts_files/contmaps_inputs/%s/%s/%s/heatmaps/%s/" % (itype,stnd,ligandonly,rev)
	heatmap_path = "%sheatmaps/%s/" % (options_path,rev)
	custom_path = "%scustom_heatmaps_temp/" % (basepath)

	print(str("Processing heatmap and dendrograms for %s-%s") % (itype, ligandonly))

	#Loading files
	compl_data = json_dict(str(basepath + "compl_info.json"))
	df_ts = pd.read_pickle("%sheatmaps/%s/dataframe_for_customized.pkl" % (options_path, rev))

	#Getting GPCR long-names (improved names)
	(recept_info,recept_info_order,df_ts,dyn_gpcr_pdb,index_dict)=improve_receptor_names(df_ts,compl_data)

	#Remove non-listed simulations from the dataframe
	df_filt = df_ts[df_ts['Id'].isin(dyn_list)]

	#Calculate heatmap height from the number of simulations present
	h = int( len(df_filt.Id.unique()) * 16 + 200)

	#Taking some variables for dataframe slicing
	max_columns = 50
	pairs_number = len(df_filt.Position.unique())
	inter_number = df_filt.shape[0]
	inter_per_pair = (inter_number/pairs_number)/2 if rev == "rev" else inter_number/pairs_number 
	number_heatmaps = ceil((inter_number/inter_per_pair)/max_columns)

	#Create custom heatmaps folder if not yet exists
	os.makedirs(custom_path, exist_ok=True)

	#Add PDB id column
	pdb_id = recept_info_order['pdb_id']
	df_filt['pdb_id'] = df_filt['Id'].apply(lambda x: recept_info[x][pdb_id])

	#Add complete name (RECEPTOR_NAME (PDB_ID) (DYNID if repeqted))
	df_filt['complete_name'] = df_filt['Id'].apply(lambda x: recept_info[x][14])
	
	#Make a CSV donwlodable file for this customized heatmap
	csvpath = "%sdataframe_%s.csv"%(custom_path,code)
	customized_csv(df_filt,itype,recept_info, csvpath)

	#Make heatmaps each 50 interacting pairs
	div_list = []
	divwidth_list = []
	heatmap_filename_list = []
	number_heatmaps_list = []
	prev_slicepoint = 0
	for i in range(1,number_heatmaps+1):
		number_heatmaps_list.append(str(i))

		#Slice dataframe. Also definig width of the heatmaps
		slicepoint = int(i*inter_per_pair*max_columns)
		if i == number_heatmaps:
			df_slided = df_filt[prev_slicepoint:]
		else:
			df_slided = df_filt[prev_slicepoint:slicepoint]
		w = int(df_slided.shape[0]/inter_per_pair*21+300)
		dend_width = 450
		prev_slicepoint = slicepoint
		
		# Define bokeh figure and hovertool
		hover = create_hovertool(itype, itypes_order, hb_itypes, typelist)
		mysource,p = define_figure(w, h, df_slided, hover, itype)
		# Creating javascript for side-window
		mysource = select_tool_callback(recept_info, recept_info_order, dyn_gpcr_pdb, itype, typelist, mysource)
		
		# Extract bokeh plot components and store them in lists
		script, div = components(p)
		divwidth_list.append(str(dend_width+w))
		div_list.append(div.lstrip())
		heatmap_filename = "%s%iheatmap_%s.html" % (custom_path,i, code)
		heatmap_filename_list.append(heatmap_filename)

		# Write heatmap on file
		heatmap_filename = "%s%iheatmap_%s.html" % (custom_path,i,code)
		with open(heatmap_filename, 'w') as heatmap:
			heatmap.write(script)
		print("heatmap",i)

	#==================================

	mdsrv_url=obtain_domain_url(request)
	basepath = "/protwis/sites/files/Precomputed/get_contacts_files/"
	basedir = "%scontmaps_inputs/%s/%s/%s/" % (basepath,itype,stnd,ligandonly)

	#Path to json
	fpdir = "/dynadb/files/Precomputed/get_contacts_files/contmaps_inputs/%s/%s/%s/flarejsons/%sclusters/" %  (itype, stnd, ligandonly, cluster)

	#First batch of context variables
	context = {
		'fpdir' : fpdir,
		'itype_code' : itype,
		'itype_name' : typelist[itype],
		'hb_itypes' : hb_itypes,
		'itypes_order' : itypes_order,
		'clusrange_all': list(range(2,21)),
		'ligandonly' : ligandonly,
		'rev' : rev,
		'stnd': stnd,
		'cluster' : int(cluster),
	}

	# Loading heatmap script 
	script_list = []
	for filename in heatmap_filename_list:
		with open(filename, 'r') as scriptfile:
			script = scriptfile.read()
		script_list.append(script)

	#Loading json dynID-to-receptor_name dictionary
	dyn_to_names = json_dict(basedir+"name_to_dyn_dict.json")

	# Send request 
	context.update({
		'itypes_dict' : typelist,
		'script_list' : script_list, 
		'number_heatmaps_list' : number_heatmaps_list,
		'numbered_divs' : zip(number_heatmaps_list, div_list),
		'numbered_divwidths':zip(number_heatmaps_list, divwidth_list), 
		'clusrange_all': list(range(2,21)),
		'clusrange': list(range(1,int(cluster)+1)),
		'mdsrv_url':mdsrv_url,
		'dyn_to_names' : dyn_to_names,	
	})
	print('returning')

	return render(request, 'contact_maps/customized.html', context)