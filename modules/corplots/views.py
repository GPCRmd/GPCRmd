from django.shortcuts import render, redirect
from os.path import exists 
from importlib.machinery import SourceFileLoader
from django.http import HttpResponse
from modules.view.views import obtain_domain_url
from json import loads, dumps
from wsgiref.util import FileWrapper
from modules.contact_maps.scripts.customized_heatmap import *
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.conf import settings

import pandas as pd
import json
from io import BytesIO
import numpy as np
from scipy.stats.stats import pearsonr

from bokeh.embed import components,json_item
from bokeh import palettes
from bokeh.models import ColumnDataSource,Label,HoverTool, Span, Slope, LabelSet
from bokeh.layouts import row, column
from bokeh.plotting import figure, output_file, show

def robust_pearson(a, b):
    a = np.array(a)
    b = np.array(b)
    coef_list = []
    coef, p_val = pearsonr(a, b)
    coef_list.append(coef)
    for i in range(len(a)):
        coef, p_val = pearsonr(np.delete(a,i), np.delete(b,i))
        coef_list.append(coef)
    coef_purged = np.nan_to_num(coef_list)
    return min(coef_purged, key=lambda x: abs(x))

def json_dict(path):
    """Converts json file to pyhton dict."""
    json_file=open(path)
    json_str = json_file.read()
    json_data = json.loads(json_str)
    return json_data

def login_in(request): 
	"""
	Login page to access into corplots tool.
	"""
	next = ""
	if request.GET: # Get url to point in case of success
		next = request.GET['next']
	if request.POST: # When login button is clicked
		try:
			password = request.POST["password"] # Password introduced by the user on the login form
		except:
			password = "none"
		user = authenticate(username="corplots", password=password) # Ask to the djangodb to auth this user with the password
		if user is not None: # In case the password is correct:
			request.session.set_expiry(600)
			login(request, user)
			if next == "": # In case that url not found
				return HttpResponseRedirect("corplots/cor_login")
			else: # In case that url is good
				return HttpResponseRedirect(next)
		else: # In case that password is NOT correct
			return render(request, 'corplots/login.html', context={"next":next, "messages":["Error in the password!"]}) 

	else: # Main login form
		return render(request, 'corplots/login.html', context={"next":next, "messages":[""]}) 

@login_required(login_url="cor_login", redirect_field_name="next") # Login required. Comment or remove in case to not need to login.
def main(request):
	"""
	Load mainpage
	"""

	# Lists for dropdowns
	recs = ['5ht1a','5ht1b','5ht1d','5ht2a','5ht2b','5ht2c','5ht4','5ht6','5ht7a','5ht7b','d1','d2','d3','d4','d5','h1','m1','m2','m3','m4','m5','α1a','α2a','α2b','α2c']
	signprots = ['G14','Barrestin1','Barrestin2','G11','G12','G13','G15','Gi1','Gi2','Gi3','GoA','GoB','Gq','Gs','Gz']
	assts = ['antagonist','agonist'] 
	metrs = ['emax','ec50']
	out = ["overall_change","positive","negative_","depressive","social_functioning","discontinuation","weight_gain","parkinson","Akathisia","prolactin","qtc_prolongation","sedation","anticholinergic"]
	context = {
		'metrs' : metrs,
		'assts' : assts,
		'signprots' : signprots,
		'recs' : recs,
		'out' : out
	}
	# Load rec-signprot dictionary
	context['recsigns'] = json_dict(settings.MEDIA_ROOT + 'Precomputed/corplots/protdict.json')
	# Load correlations from CSV
	cor_df = pd.read_csv(settings.MEDIA_ROOT + 'Precomputed/corplots/cors.csv')

	# Filter out pairs with less than n:6 to start with
	# cor_df = cor_df[cor_df['n'] >= 6]
	
	round_cors = [ '%.4f' % elem for elem in cor_df['cors_r'].tolist() ]
	context['paircors'] = zip(
		cor_df['path'].tolist(),
		cor_df['out'].tolist(),
		round_cors,
		cor_df['n'].tolist()
		)

	return render(request,'corplots/index.html',context)	

def corplots(out,path):
	"""
	Make correlation lineplot of specified outcome and pathway
	"""

	# Load correlation data
	df = pd.read_csv(settings.MEDIA_ROOT + "Precomputed/corplots/polypharma_clinical_outcomes.csv")

	# Check if selected outcome is actually avaliable. If it is not, return "not avaliable" html thingy
	if not path in df:
		div = '<div id="notav" class="error_message warning alert-warning" style="display:block">Pathway '+path+' not avaliable in the set.</div>'
		return("",div) 

	# Sort dataframe according to outcome (x-axis) values
	df.sort_values(by=[out],inplace=True)

	# Extract rows with value in our selected path
	df = df[df[path].notna()]
	df = df[df[out].notna()]

	# Extract path and outcome information
	out_values = df[out].tolist()
	path_values = df[path].tolist()
	drugs = list(df['Drug'])

	# Get correlation value once again
	cor = round(robust_pearson(df[out], df[path]), 4)
	cor = "0" if ((cor < 0.0001) and (cor > -0.0001)) else str(cor)

	# Compute regression line from values
	par = np.polyfit(out_values, path_values, 1, full=True)
	slope=par[0][0]
	intercept=par[0][1]
	regression_line = Slope(gradient=slope, y_intercept=intercept, line_color="red")

	# Caculate ranges for plots (leaving small margin for beautiness)
	max_out = max(out_values)
	min_out = min(out_values)
	margin_out = (max_out-min_out)/10 
	max_path = max(path_values) 
	min_path = min(path_values)
	margin_path = (max_path-min_path)/10 
	x_range = [ min_out-margin_out, max_out+margin_out ] if (max_out != min_out) else [min_out-0.1,min_out+1]
	y_range = [ min_path-margin_path, max_path+margin_path ] if (max_path != min_path) else [min_path-0.1,min_path+1]

	# Plottin time with bokeh
	p = figure(
		height=500,
		width=900,
		#title="Example freq",
		y_range=y_range,
		x_range=x_range,
		y_axis_label=path,
		x_axis_label=out,
	#	 tools=["hover","tap","save","reset","wheel_zoom"], 
	#	 x_axis_location="above",
	#	 active_drag=None,
	#	 toolbar_location="right",
	#	 toolbar_sticky = False,
		min_border_top = 10,
		min_border_bottom = 0,
	)
	p.sizing_mode = "scale_width"


	# Markers for lineplot
	mysource = ColumnDataSource(df)
	p.circle(
		x=out,
		y=path,
		legend_label="Correlation value: "+cor, 
		size=12,
		source=mysource,		
		)
	# Regression line
	p.add_layout(regression_line)

	# Labels with drug names
	labels = LabelSet(
            x=out,
            y=path,
            text='Drug',
            level='glyph',
            x_offset=5, 
            y_offset=5, 
            source=mysource, 
	    	text_font = {'value': 'canvas'}
            # render_mode='canvas'
			)
	p.add_layout(labels)

	# A legend just for correlation plot
	p.legend.location = "top_center"
	p.legend.border_line_width = 1
	p.legend.border_line_color = "#A8A8A8"
	p.legend.glyph_height = 0
	p.legend.glyph_width = 0

	# Change axis font size
	p.xaxis.axis_label_text_font_size = "16pt"
	p.yaxis.axis_label_text_font_size = "16pt"
	p.xaxis.major_label_text_font_size = "12pt"
	p.yaxis.major_label_text_font_size = "12pt"

	# Adding hover
	#Creating hovertool listzzzz
	hoverlist = [
				 (path, '@{'+path+'}{0.00}'),
				 (out, '@{'+out+'}{0.00}'),
				 ("Drug", "@Drug")
				]

	#Hover tool:
	hover = HoverTool(
		tooltips=hoverlist
	)
	p.add_tools(hover)
	
	# Return plot components
	script, div = components(p)
	return(script,div)

def custom_plot(request):
	"""
	Create custom plot with specified pathway and outcome selections
	"""

	# Get options stored in the POST data
	metr = request.POST.get("metrs")
	asst = request.POST.get("assts")
	recsign = request.POST.get("recsign")
	out= request.POST.get("out")
	(rec,signprot) = recsign.split('|')

	# Merge path options to make column header
	path = "%s_%s_%s_%s"%(signprot, asst,rec,metr)

	# Make plot
	(script,div) = corplots(out,path)
	context = {
		'path' : path,
		'out' : out,
		'div' : div,
		'script' : script
		}

	return HttpResponse(json.dumps(context), content_type='corplots/')   

def topcor_plot(request):
	"""
	Create custom plot with specified pathway and outcome selections
	"""

	# Get options stored in the POST data
	pair= request.POST.get("pairs")

	# Merge path options to make column header
	(path,out) = pair.split('||')

	# Make plot
	(script,div) = corplots(out,path)
	context = {
		'path' : path,
		'out' : out,
		'div' : div,
		'script' : script
		}
		
	return HttpResponse(json.dumps(context), content_type='corplots/')   

def infoplot(request, out, path):
	"""
	Save and download info refering this outcome and pathway in particular
	"""

	# Load correlation data
	df = pd.read_csv(settings.MEDIA_ROOT + "Precomputed/corplots/polypharma_clinical_outcomes.csv")

	# Select desired columns
	df_filt = pd.concat([df['Drug'],df[path],df[out]],axis=1)

	# Return a response in csv format
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename=plotded_data.csv'
	df_filt.to_csv(path_or_buf=response,sep=',',float_format='%.2f',index=False)
	return(response)