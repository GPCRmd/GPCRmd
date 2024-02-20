import matplotlib# MANDATORY TO BE IN FIRST PLACE!!
matplotlib.use('Agg')# MANDATORY TO BE IN SECOND PLACE!!
from os.path import exists 
from django.shortcuts import render
from importlib.machinery import SourceFileLoader
from django.http import HttpResponse
from modules.view.views import obtain_domain_url
import json
from wsgiref.util import FileWrapper
from modules.gpcr_gprot.scripts.customized_heatmap import *
from django.views.decorators.csrf import csrf_protect
import csv

from django.conf import settings

def json_dict(path):
	"""Converts json file to pyhton dict."""
	json_file=open(path)
	json_str = json_file.read()
	json_data = json.loads(json_str)
	return json_data

def main(request):
	"""
	Main view of GPCR-Gprot interaction maps
	"""
    
	request.session.set_expiry(0) 

	#Take query arguments, if any
	if request.GET.get('itype'): #If there are parameters
		itype = request.GET.get('itype')
		cluster = request.GET.get('cluster')
		stnd = request.GET.get('stnd')
	else:
		itype = 'hb'
		cluster = '3'
		stnd = 'stnd'

	mdsrv_url=obtain_domain_url(request)
	
		
	basepath = settings.MEDIA_ROOT + "Precomputed/gpcr_gprot/"
	basedir =settings.MEDIA_ROOT + "Precomputed/gpcr_gprot/web_inputs/%s/%s/" % (itype, stnd)
 
	#Path to json
	fpdir = "/dynadb/files/Precomputed/gpcr_gprot/web_inputs/%s/%s/flareplots_clusters/%sclusters/" %  (itype, stnd, cluster)

	#First batch of context variables
	context = {
		'fpdir' : fpdir,
		'itype_code' : itype,
		'itype_name' : typelist[itype],
		'hb_itypes' : hb_itypes,
		'itypes_order' : itypes_order,
		'clusrange_all': list(range(2,21)),
		'stnd': stnd,
		'cluster' : int(cluster),
	}

	#Creating and downloading CSV file from df
	csv_name = basedir+"dataframe.csv" 
	csv_data_list = open(csv_name, 'r').readlines()
	csv_data = ''.join(csv_data_list)

	# Loading variables if file exists. If not, it means there are no interactions avalible for the selected options
	variablesfile = basedir+"variables.py"
	if exists(variablesfile):
		variablesmod = SourceFileLoader("module.name", variablesfile).load_module()
		number_heatmaps_list = variablesmod.number_heatmaps_list
		div_list = variablesmod.div_list
		filenames_list = variablesmod.heatmap_filename_list
	else :
		return render(request,'gpcr_gprot/index_nodata.html',context)

	#Loading json dynID-to-receptor_name dictionary
	dyn_to_names = json_dict(basedir+"name_to_dyn_dict.json")

	# Loading heatmap script 
	script_list = []
	for filename in filenames_list:
		with open(filename, 'r') as scriptfile:
			script = scriptfile.read()
		script_list.append(script)

	#Loading dynamics-cluster dictionary
	clustdict = json_dict("%sflareplots_clusters/%sclusters/clustdict.json" % (basedir, cluster))

	# Loading dendrogram
	dendfile = ("%sdendrograms/%sclusters_dendrogram.html" % (basedir, cluster))
	dendr_figure = open(dendfile, 'r',encoding='utf-8').read()

	first_sim = clustdict['cluster1'][0]

	# Send request 
	context.update({
		'clustdict' : clustdict,
		'itypes_dict' : typelist,
		'dendrogram' : dendr_figure,
		'script_list' : script_list, 
		'number_heatmaps_list' : number_heatmaps_list,
		'numbered_divs' : zip(number_heatmaps_list, div_list),
		'clusrange_all': list(range(2,21)),
		'clusrange': list(range(1,int(cluster)+1)),
		'mdsrv_url':mdsrv_url,
		'dyn_to_names' : dyn_to_names,
		'csvfile' : json.dumps(csv_data),
		'flarerange' : list(range(1,21))
	})
	return render(request, 'gpcr_gprot/index_h.html', context)

def get_csv_file(request):
	"""
	Processing informatino from get_contact plots to create and download a csv file
	"""

	#Taking arguments
	itype = request.GET.get('itype')
	stnd = request.GET.get('stnd')
	csvstring = request.POST['csvfile']

	#Creating and downloading CSV file from df
	response = HttpResponse(eval(csvstring), content_type='text/plain')
	response['Content-Disposition'] = 'attachment; filename={0}'.format("GPCR_Gprot_interactions-%s.csv" % (itype))
	
	return response

@csrf_protect
def customized_heatmap(request, foo):

	"""
	This whole script is designed with the single purpouse of creating a customized bokeh interaction heatmap for a desired set of simulations
		- dyn_list: set with the identifiers of the selected simulations
		- itype, stnd: parameters of the selected contactMap
		- code: unique identifier of this request.
	"""

	#Parameters
	dyn_list  = request.POST['SimList'].split('&')
	itype = request.GET.get('itype')
	cluster = request.GET.get('cluster')
	stnd = request.GET.get('stnd')
	code = request.GET.get('code')

	#Paths
	precompath = settings.MEDIA_ROOT + "Precomputed/"
	app_path = precompath+"gpcr_gprot/"
	mydata_path = app_path + "web_inputs/%s/%s/" % (itype, stnd)
	heatmap_path = mydata_path+"heatmaps/"
	custom_path = "%scustom_heatmaps_temp/" % (precompath)

	print("Processing heatmap and dendrograms for %s" % (itype))

	#Loading files
	db_dict = json_dict(precompath + "compl_info.json")
	df_ts = pd.read_pickle(heatmap_path+"dataframe_for_customized.pkl")
	flare_template = json_dict(app_path + "template.json")

	#Getting GPCR long-names (improved names)
	(partial_db_dict,df_ts,gennum)=improve_receptor_names(df_ts,db_dict)
    
	# Create new column with both residue names and generic numbering of both residues interacting
	df_ts = df_ts.apply(lambda x: find_resnames_resids(x, db_dict, three_to_one),axis=1)
        
	#Get long names of simulations
	name_list = [ partial_db_dict[dyn]['recept_name_dynid']  for dyn in dyn_list ]

	#Remove non-listed simulations from the dataframe
	df_filt = df_ts[df_ts['Id'].isin(dyn_list)]

	#Calculate heatmap height from the number of simulations present
	h = int( len(df_filt.Id.unique()) * 18 )

	#Taking some variables for dataframe slicing
	max_columns = 50
	pairs_number = len(df_filt.Residue.unique())
	inter_number = df_filt.shape[0]
	inter_per_pair = inter_number/pairs_number 
	number_heatmaps = ceil((inter_number/inter_per_pair)/max_columns)

	#Create custom heatmaps folder if not yet exists
	os.makedirs(custom_path, exist_ok=True)

	#Make a CSV donwlodable file for this customized heatmap
	csv_data = customized_csv(df_filt,itype)

	#Make heatmaps each 50 interacting pairs
	div_list = []
	heatmap_filename_list = []
	number_heatmaps_list = []
	script_list = []
	prev_slicepoint = 0
	for i in range(1,number_heatmaps+1):
		number_heatmaps_list.append(str(i))

		#Slice dataframe. Also definig width of the heatmaps
		slicepoint = int(i*inter_per_pair*max_columns)
		if i == number_heatmaps:
			df_slided = df_filt[prev_slicepoint:]
		else:
			df_slided = df_filt[prev_slicepoint:slicepoint]
		num_respairs = len(df_slided['Residue'].unique())
		w = int(num_respairs*20+40+248)
		prev_slicepoint = slicepoint
		
		# Define bokeh figure and hovertool
		hover = create_hovertool(itype, itypes_order, hb_itypes, typelist)
		mysource,p = define_figure(w, h, df_slided, hover, itype)
		# Creating javascript for side-window
		p = select_tool_callback(p, partial_db_dict, gennum, itype, typelist, mysource)
		
		# Extract bokeh plot components and store them in lists
		script, div = components(p)
		div_list.append(div.lstrip())
		script_list.append(script)

	#==================================

	mdsrv_url=obtain_domain_url(request)

	#Path to json
	fpdir = "/dynadb/files/Precomputed/gpcr_gprot/web_inputs/%s/flareplots_sims/" % itype
	
	#First batch of context variables
	context = {
		'fpdir' : fpdir,
		'itype_code' : itype,
		'itype_name' : typelist[itype],
		'hb_itypes' : hb_itypes,
		'itypes_order' : itypes_order,
		'clusrange_all': list(range(2,21)),
		'stnd': stnd,
		'cluster' : int(cluster),
		'dyn_list' : dyn_list,
		'itypes_dict' : typelist,
		'script_list' : script_list, 
		'number_heatmaps_list' : number_heatmaps_list,
		'numbered_divs' : zip(number_heatmaps_list, div_list),
		'sim_list' : list(zip(dyn_list, name_list)),
		'mdsrv_url':mdsrv_url,
		'csvfile' : json.dumps(csv_data),
		'flarerange' : list(range(1,21))
	}

	return render(request, 'gpcr_gprot/customized.html', context)