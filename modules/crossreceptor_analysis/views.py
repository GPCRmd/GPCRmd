from django.shortcuts import render
from django.conf import settings
import random
from bokeh.plotting import figure 
from bokeh.embed import components
#from bokeh.models.tools import HoverTool
from bokeh.models import HoverTool, TapTool, CustomJS #,PanTool
from bokeh.models import BasicTicker, ColorBar, ColumnDataSource, LinearColorMapper, PrintfTickFormatter
from bokeh.transform import transform
from os import path
import pandas as pd
import re
from bokeh.io import output_file, save
import json
from scipy.cluster.hierarchy import  linkage
from scipy.spatial.distance import pdist, squareform
from modules.view.views import obtain_domain_url
from modules.dynadb.models import DyndbFiles, DyndbFilesDynamics
#import numpy as np
#import mdtraj as md
#import molpx
#import pyemma

#import matplotlib
#from matplotlib import pylab as plt
##%matplotlib ipympl

def seriation(Z,N,cur_index):
    '''
        input:
            - Z is a hierarchical tree (dendrogram)
            - N is the number of points given to the clustering process
            - cur_index is the position in the tree for the recursive traversal
        output:
            - order implied by the hierarchical tree Z
            
        seriation computes the order implied by a hierarchical tree (dendrogram)
    '''
    if cur_index < N:
        return [cur_index]
    else:
        left = int(Z[cur_index-N,0])
        right = int(Z[cur_index-N,1])
        return (seriation(Z,N,left) + seriation(Z,N,right))

def compute_serial_matrix(dist_mat,method="ward"):#[New]
    '''
        input:
            - dist_mat is a distance matrix
            - method = ["ward","single","average","complete"]
        output:
            - [Removed] seriated_dist is the input dist_mat,
              but with re-ordered rows and columns
              according to the seriation, i.e. the
              order implied by the hierarchical tree
            - res_order is the order implied by
              the hierarhical tree
            - res_linkage is the hierarhical tree (dendrogram)
        
        compute_serial_matrix transforms a distance matrix into 
        a sorted distance matrix according to the order implied 
        by the hierarchical tree (dendrogram)
    '''
    N = len(dist_mat)
    flat_dist_mat = squareform(dist_mat)
    res_linkage = linkage(flat_dist_mat, method=method)
    res_order = seriation(res_linkage, N, N + N-2)
    #seriated_dist = np.zeros((N,N))
    #a,b = np.triu_indices(N,k=1)
    #seriated_dist[a,b] = dist_mat[ [res_order[i] for i in a], [res_order[j] for j in b]]
    #seriated_dist[b,a] = seriated_dist[a,b]
    return  res_order, res_linkage

#Modify data to the necessary format
def convert_indep_to_tablelike(dep,indep):
    rep_dep=len(indep)
    dep_post=dep*rep_dep
    rep_indep=len(dep)
    indep_post=[]
    for n in indep:
        indep_post +=[n]*rep_indep
    return (dep_post,indep_post)

def json_dict(path):
    """Converts json file to pyhton dict."""
    json_file=open(path)
    json_str = json_file.read()
    json_data = json.loads(json_str)
    return json_data

def improve_receptor_names(df_t,compl_data):
    """Parses the dataframe to create the data source of the plot. When defining a name for each dynamics entry: if there is any other dynamics in the datadrame that is created fromt he same pdb id and ligand, all these dynamics will indicate the dynamics id"""

    recept_info={}
    recept_info_order={"upname":0, "resname":1,"dyn_id":2,"prot_id":3,"comp_id":4,"prot_lname":5,"pdb_id":6,"lig_lname":7,"struc_fname":8,"traj_fnames":9,"delta":10}
    taken_protlig={}
    index_dict={}
    dyn_gpcr_pdb={}
    for recept_id in df_t.index: 
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
    df_t=df_t.rename(index=index_dict)
    return(recept_info,recept_info_order,df_t,dyn_gpcr_pdb)
    



def ligand_receptor_interaction(request,sel_thresh):
    mdsrv_url=obtain_domain_url(request)
    
        
    sel_thresh=float(sel_thresh)
    cra_path=settings.MEDIA_ROOT + "Precomputed/crossreceptor_analysis_files"
    resli_file_path=path.join(cra_path,"ligres_int.csv")
    #resli_file_pathobj = Path(resli_file_path)
    #try:
    #resli_abs_path = resli_file_pathobj.resolve()
    df = pd.read_csv(resli_file_path,index_col=[0,1])
    #except FileNotFoundError:
    #    df=pd.DataFrame({})
    all_thresh=set(df.index.get_level_values(0))
    other_thresh_set=all_thresh - {sel_thresh}
    other_thresh=sorted(list(other_thresh_set))

    
    compl_file_path=path.join(cra_path,"compl_info.json")
    compl_data = json_dict(compl_file_path)
    #Prepare data        
    df_t=df.loc[sel_thresh]
    df_t.columns.names=["Position"]
    df_t=df_t.fillna(value=0)
    
    # [!] Only in prod

    """
    indexes = df_t.index.values
    index_f = sorted([idx for idx in indexes if int(idx[3:]) > 29],key=lambda x: int(x[3:]))
    df_t = df_t.loc[index_f]
    """

    #Compute cluster and order accordingly
    dist_mat_md = squareform(pdist(df_t))
    method="ward"
    res_order, res_linkage = compute_serial_matrix(dist_mat_md,method)
    df_order=[]
    for e in res_order:
        df_order.append(df_t.iloc[e].name)
    df_t=df_t.loc[df_order]
    
    #Rename dyn identifiers
    (recept_info,recept_info_order,df_t,dyn_gpcr_pdb)=improve_receptor_names(df_t,compl_data)
    #df_t.sort_index(inplace=True,ascending=False)
    df_ts = df_t.stack().rename("value").reset_index()
    #DataSource with extra information
    df_ri=pd.DataFrame(recept_info)
    ri_source=ColumnDataSource(df_ri)
    df_rio=pd.DataFrame(recept_info_order, index=[0])
    rio_source=ColumnDataSource(df_rio)
    df_gnum=pd.DataFrame(dyn_gpcr_pdb)
    gnum_source=ColumnDataSource(df_gnum)

    extra_source = ColumnDataSource({"thresh":[sel_thresh], "mdsrv_url":[mdsrv_url]})
    
    #Map colors
    colors = colors=["#FFFFFF",'#f7fcfc', '#f6fbfc', '#f5fafc', '#f4fafb', '#f2f9fb', '#f1f8fa', '#f0f8fa', '#eff7fa', '#edf6f9', '#ecf6f9', '#ebf5f8', '#e9f4f8', '#e8f4f7', '#e7f3f7', '#e6f2f7', '#e4f1f6', '#e3f0f6', '#e2f0f5', '#e1eff5', '#dfeef4', '#deedf4', '#ddecf4', '#dbebf3', '#daeaf3', '#d9eaf2', '#d8e9f2', '#d6e8f1', '#d5e7f1', '#d4e6f1', '#d3e5f0', '#d1e4f0', '#d0e3ef', '#cfe2ef', '#cde1ee', '#cce0ee', '#cbdfee', '#cadeed', '#c8dded', '#c7dcec', '#c6daec', '#c5d9ec', '#c3d8eb', '#c2d7eb', '#c1d6ea', '#bfd5ea', '#bed4e9', '#bdd2e9', '#bcd1e9', '#bad0e8', '#b9cfe8', '#b8cee7', '#b7cce7', '#b5cbe6', '#b4cae6', '#b3c9e6', '#b1c7e5', '#b0c6e5', '#afc5e4', '#aec3e4', '#acc2e3', '#abc1e3', '#aabfe3', '#a9bee2', '#a7bce2', '#a6bbe1', '#a5bae1', '#a3b8e0', '#a2b7e0', '#a1b5e0', '#a0b4df', '#9eb2df', '#9db1de', '#9cafde', '#9aaedd', '#99acdd', '#98abdd', '#97a9dc', '#95a8dc', '#94a6db', '#93a4db', '#92a3db', '#90a1da', '#8fa0da', '#8e9ed9', '#8c9cd9', '#8b9bd8', '#8a99d8', '#8997d8', '#8795d7', '#8694d7', '#8592d6', '#8490d6', '#828ed5', '#818dd5', '#808bd5', '#7e89d4', '#7d87d4', '#7c85d3', '#7b84d3', '#7982d2', '#7880d2', '#777ed2', '#767cd1', '#747ad1', '#7378d0', '#7276d0', '#7074cf', '#6f72cf', '#6e70cf', '#6d6fce', '#6b6dce', '#6a6bcd', '#6969cd', '#6968cd', '#6866cc', '#6865cc', '#6764cb', '#6762cb', '#6661ca', '#6660ca', '#655fca', '#655dc9', '#645cc9', '#645bc8', '#645ac8', '#6358c7', '#6357c7', '#6356c7', '#6254c6', '#6253c6', '#6252c5', '#6151c5', '#614fc4', '#614ec4', '#614dc4', '#604bc3', '#604ac3', '#6049c2', '#6048c2', '#6046c1', '#5f45c1', '#5f44c1', '#5f43c0', '#5f41c0', '#5f40bf', '#5f3fbe', '#5f3fbd', '#603fbc', '#603eba', '#603eb9', '#603db8', '#613db7', '#613cb5', '#613cb4', '#613cb3', '#623bb2', '#623bb0', '#623aaf', '#623aae', '#6239ac', '#6239ab', '#6239aa', '#6238a9', '#6338a7', '#6337a6', '#6337a5', '#6336a3', '#6336a2', '#6336a1', '#6335a0', '#63359e', '#63349d', '#63349c', '#63349b', '#633399', '#633398', '#633297', '#623295', '#623194', '#623193', '#623192', '#623090', '#62308f', '#622f8e', '#622f8d', '#612e8b', '#612e8a', '#612e89', '#612d87', '#602d86', '#602c85', '#602c84', '#602b82', '#5f2b81', '#5f2b80', '#5f2a7f', '#5e2a7d', '#5e297c', '#5e297b', '#5d2879', '#5d2878', '#5d2877', '#5c2776', '#5c2774', '#5b2673', '#5b2672', '#5a2671', '#5a256f', '#59256e', '#59246d', '#58246b', '#58236a', '#572369', '#572368', '#562266', '#562265', '#552164', '#552163', '#542061', '#532060', '#53205f', '#521f5d', '#511f5c', '#511e5b', '#501e5a', '#4f1d58', '#4f1d57', '#4e1d56', '#4d1c55', '#4c1c53', '#4c1b52', '#4b1b51', '#4a1a4f', '#491a4e', '#481a4d', '#48194c', '#47194a', '#461849', '#451848', '#441746', '#431745', '#421744', '#411643', '#411641', '#401540', '#3f153f', '#3e153d', '#3c143c', '#3b143a', '#3a1339']
    mapper = LinearColorMapper(palette=colors, low=0, high=100)

    # Define a figure

    #pan=PanTool(dimensions="width")
    #mytools = ["hover","tap","save","reset","wheel_zoom",pan]

    mytools = ["hover","tap","save","reset","wheel_zoom","pan"]
    #w=int(len(df_t.columns)*40,)
    cw=275
    ch=30
    #h=int(((w-cw)*len(df_t.index)/len(df_t.columns))+ch)
    w= 760
    h= 132

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
        toolbar_sticky = False
        )

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

    color_bar = ColorBar(color_mapper=mapper, location=(0, 0),
                         ticker=BasicTicker(desired_num_ticks=2),
                         formatter=PrintfTickFormatter(format="%d%%"))
    p.add_layout(color_bar, 'right')


    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.xaxis.major_label_text_font_size = "9pt"
    p.yaxis.major_label_text_font_size = "8pt"
    p.axis.major_label_standoff = 0
    p.xaxis.major_label_orientation = 1#"vertical"
    
    #Hover tool:
    p.select_one(HoverTool).tooltips = [
         ('Receptor', '@Id'),
         ('Position', '@Position'),
         ('Frequency', '@value{(0.0)}%'),
    ]
    
    #Select tool and callback:
    mysource.callback = CustomJS(args={"r_info":ri_source,"ro_info":rio_source,"extra_info":extra_source,"gnum_info":gnum_source},
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
                var freq=data["value"][sel_ind];
                var pos_ind=gnum_data['index'].indexOf(pos)
                var pdb_pos=gnum_data[recept_id][pos_ind]
                var lig=ri_data[recept_id][rio_data['resname']];
                var lig_lname=ri_data[recept_id][rio_data['lig_lname']];
                var recept=ri_data[recept_id][rio_data['upname']];
                var dyn_id_pre=ri_data[recept_id][rio_data['dyn_id']];
                var dyn_id=dyn_id_pre.match(/\d*$/)[0];
                var prot_id=ri_data[recept_id][rio_data['prot_id']];
                var prot_lname=ri_data[recept_id][rio_data['prot_lname']];
                var comp_id=ri_data[recept_id][rio_data['comp_id']];
                var sel_thresh=extra_info.data["thresh"][0];
                var struc_fname=ri_data[recept_id][rio_data['struc_fname']];
                var traj_fnames=ri_data[recept_id][rio_data['traj_fnames']];
                var delta=ri_data[recept_id][rio_data['delta']];

                $('#ngl_iframe')[0].contentWindow.$('body').trigger('createNewRef', [struc_fname , traj_fnames ,lig, delta ,pos, pdb_pos]);
                
                if (plot_bclass != "col-xs-9"){
                    $("#plot_col").attr("class","col-xs-9");
                    $("#info").css({"visibility":"visible","position":"relative","z-index":"auto"});
                }
                
                $("#freq_val").html(freq);
                $("#recept_val").html(prot_lname + " ("+recept+")");
                $("#pos_val").html(pos);
                $("#lig_val").html(lig_lname + " ("+lig+")");
                $("#viewer_link").attr("href","../../../view/"+dyn_id+"/"+sel_thresh+"/"+pos);
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
            'script' : script , 
            'div' : div,
            'other_thresh':other_thresh,
            'sel_thresh':sel_thresh,
            'plotdiv_w':plotdiv_w,
            'mdsrv_url':mdsrv_url
            }
    return render(request, 'crossreceptor_analysis/index_h.html', context)


def obtain_dyn_files(dyn_id):
    """Given a dyn id, provides the stricture file name and a list with the trajectory filenames and ids."""
    dynfiles=DyndbFilesDynamics.objects.prefetch_related("id_files").filter(id_dynamics=dyn_id)
    traj_list=[]
    traj_name_list=[]
    p=re.compile(f"({settings.MEDIA_ROOT})(.*)")
    p2=re.compile("[\.\w]*$")
    for fileobj in dynfiles:
        path=fileobj.id_files.filepath
        myfile=p.search(path).group(2)
        myfile_name=p2.search(myfile).group()
        if myfile.endswith(".pdb"): 
            structure_file=myfile
            structure_file_name=myfile_name
        elif myfile.endswith((".xtc", ".trr", ".netcdf", ".dcd")):
            traj_list.append([myfile,fileobj.id_files.id])
            traj_name_list.append(myfile_name)
    return (structure_file,structure_file_name,traj_list,traj_name_list)

#def molpx_plots(request,dyn_id):
 #    test_datapath=settings.MEDIA_ROOT + "tests/molpx/"
 #    top = test_datapath+'bpti-c-alpha_centered.pdb'
 #    MD_trajfiles = [test_datapath+'c-alpha_centered.stride.1000.xtc',
 #                   test_datapath+'c-alpha_centered.stride.1000.reversed.xtc',
 #                    test_datapath+'c-alpha_centered.stride.1000.halved.xtc'
 #                   ]
# 
 #    stride=1
 #    # This way the user does not have to care where the data are:
 #    top = molpx._molpxdir(top)
 #    MD_trajfiles = [molpx._molpxdir(ff) for ff in MD_trajfiles]
# 
 #    # Create a memory representation of the trajectories
 #    MD_list = [molpx.generate._md.load(itraj, top=top, stride=stride) for itraj in MD_trajfiles]
# 
# 
 #    feat = pyemma.coordinates.featurizer(top)
 #    pairs = feat.pairs(range(feat.topology.n_atoms)[::2])
 #    feat.add_distances(pairs)
 #    src  = pyemma.coordinates.source(MD_trajfiles, features=feat)
 #    Y = src.get_output()        
# 
 #    if stride > 1:
 #        i=0
 #        for i in  range(0,len(Y)):
 #            Y[i]=Y[i][0::stride]
# 
 #    proj_idxs = [108,112]
# 
##     mpx_wdg_box = molpx.visualize.FES(MD_list,
##                                       top,      
##                                       Y, 
##                                       nbins=50, 
##                                       proj_idxs=proj_idxs,
##                                       #proj_labels=feat,
##                                       proj_labels='feat',
##                                       #n_overlays=5,
##                                       #sticky=True,
##                                      )
 #    #mpx_wdg_box
# 
# 
## ############
 #    (structure_file,structure_file_name,traj_list,traj_name_list)=obtain_dyn_files(dyn_id)
 #    context={
 #            'structure_file' : structure_file ,
 #            'traj_list' : traj_list 
 #            }
 #    return render(request, 'crossreceptor_analysis/molpx.html', context)
 #    
## /home/mariona/gpcrmd_vagrant/shared/sites/files/Dynamics/10140_trj_4.dcd
## /home/mariona/gpcrmd_vagrant/shared/sites/files/Dynamics/10142_dyn_4.pdb
    
    
