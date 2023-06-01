//Get path arguments (if any)
var param_string, search_params, itype, clusters, ligandonly, rev, stnd;
param_string = window.location.search; 
search_params = new URLSearchParams(param_string)
if (Boolean(param_string)) {
    itype = search_params.get('itype');
    clusters = search_params.get('cluster');
    ligandonly = search_params.get('prtn');
    rev = search_params.get('rev');
    stnd = search_params.get('stnd');
}
else {
    itype = "hb";
    clusters = "3";
    ligandonly = "prt_lg";
    rev = "norev";
    stnd = "cmpl";
}

$(document).ready(function(){
    
    //I don't know what this line does, but Mariona told me to add it and I trust her wisdom
    document.domain=document.domain;

	////////////
	// Functions
	////////////

    function fake_hasClass(selector,classnm){
        return $(selector).attr("class").indexOf(classnm) != -1 ;
    }

    var clickEdgeSelectNodes = function(d, plot){
        var name_s=d.source.name;
        var name_t=d.target.name;
        var is_sel_s = fake_hasClass("#node-"+name_s,"toggledNode");// $("#node-"+name_s).attr("class").indexOf("toggledNode") != -1 ;
        var is_sel_t = fake_hasClass("#node-"+name_t,"toggledNode");//$("#node-"+name_t).attr("class").indexOf("toggledNode") != -1;
        if (is_sel_s == is_sel_t ){
            plot.toggleNode(name_s);
            plot.toggleNode(name_t);
        } else {
            if (!is_sel_s){
                plot.toggleNode(name_s);
            } else if (!is_sel_t){
                plot.toggleNode(name_t);
            }
        }
        $("#selectionDiv").trigger("click");
    }

    function hoverLinksFP(){
        $("path.link").hover(function(){
           var newclass=$(this).attr("class") + " hoverlink";
           $(this).attr("class",newclass);
        }, function(){
           var newclass=$(this).attr("class").replace("hoverlink","");
           $(this).attr("class",newclass);            
        });
    }

    function createFlareplotCustom(fpsize, fpjson, fpdiv, class_numbering){
        
        //Setting edges section of corresponding nomenclature
        fpjson['edges'] = fpjson[class_numbering+'edges'] 

        //Take only the topX edges required
        var top_number = $('#flarerange option:selected').val();
        fpjson['edges'] = fpjson['edges'].slice(0, top_number);

        plot=createFlareplot(fpsize, fpjson, fpdiv);

        //Wider lines
        $("path.link").css('stroke-width', 6); 
        //Thicker lines
        $("path.link").css('stroke-opacity', 0.5);         

        //Make hoverlabels of edges appear on mouse
        var mouseX;
        var mouseY;
        $(fpdiv).mousemove( function(e) {
           // mouse coordinates
           mouseX = e.pageX - $(fpdiv).offset().left;
           mouseY = e.pageY - $(fpdiv).offset().top + $(fpdiv).scrollTop();
        });  
//      $(fpdiv).on("mouseenter","path",function(e){
//            $(".tooltip").css({'left':mouseX,'top':mouseY});
//      })

        hoverLinksFP();

        return(plot);
    }

    function setFpNglSize(applyMinSize, flare_container){
	    var min_size=300;
	    var fpcont_w_str=$(flare_container).css("width");
	    var fpcont_w=Number(fpcont_w_str.match(/^\d*/g)[0]);
	    var final_size = fpcont_w;	    
	    if (applyMinSize){
	        if (final_size < min_size){
	            final_size = min_size;
	        }
	    }
	    return (final_size)
	}

    function emptyFPsels(flare_container, plot){
        //Clear all selected positions from both NGL and flareplots
        $(flare_container).find("g.node.toggledNode").each(function(){
            if (plot){
                var nodename = $(this).attr("id");
                var nodenum=nodename.split("-")[1];
                plot.toggleNode(nodenum)
                fpSelInt={};
            }
        });
        //Trigger click on random position to activate embed_contmaps_bottom set_positions function
        $(flare_container+" #node-5x42 text").trigger("click");        
    }

    function show_in_structure(flare_container, fp_display){
        if($(fp_display).hasClass("active")){
            $(fp_display).removeClass("active");            
        }
        else{
            $(fp_display).addClass("active");            
        }
        //Trigger click on random position to activate embed_contmaps_bottom set_positions function
        $(flare_container+" #node-5x42 text").trigger("click");
    }

    function colorsHoverActiveInactive(myselector,activeclass,colorhov,colorNohobAct, colorNohobInact){
        $(myselector).hover(function(){
            $(this).css("background-color",colorhov);
        },
        function(){
            var selected=$(this).hasClass(activeclass);
            if (selected){
                $(this).css("background-color",colorNohobAct);
            } else {
                $(this).css("background-color",colorNohobInact);
            }
        });
    };

    function change_display_sim_option(to_activate,to_inactivate){
        $(to_activate).addClass("is_active");
        $(to_activate).css("background-color","#bfbfbf");
        
        $(to_inactivate).removeClass("is_active");
        $(to_inactivate).css("background-color","#FFFFFF");
    }

    function updateFPInt(plot, flare_container){
        //Updates the fpSelInt dict depending on the nodes that are clicked
        allEdges= plot.getEdges()
        var updFpSelInt={}
        $(flare_container).find("g.node.toggledNode").each(function(){
            var nodename=$(this).attr("id");
            if (nodename.indexOf("node-") !== -1){        
                var nodenum=nodename.split("-")[1];
                var nodepos=fpgpcrdb_dict[nodenum].join(":"); 
                
                var edges=[];
                allEdges.forEach(function(e){
                    if (e.edge.name1==nodenum){
                        var othernum=e.edge.name2;
                        edges.push(fpgpcrdb_dict[othernum].join(":"));
                    } else if (e.edge.name2==nodenum){
                        var othernum=e.edge.name1;
                        edges.push(fpgpcrdb_dict[othernum].join(":"));
                    }
                });
                if (edges.length > 0){
                    updFpSelInt[nodepos]=edges;
                }
            }
        })
        fpSelInt = updFpSelInt;
    }

	function changeContactsInFplot(id, fpdir, plots){
        //create new FP but saving the selected contacts
        
        flare_container = "#flare-container" + id;
        fpdiv = "#fpdiv" + id;

        //Update cluster button
        cluster_num=$(fpdiv+" .clusters_dropup-div .fp_display_element.is_active").data("tag");
        $("#clusterbutton" + id).html("Cluster " + cluster_num + ' <span class="caret"></span>');

        //Update numbering button
        class_numbering = $(fpdiv+" .numbering_dropup-div .fp_display_element.is_active").data("tag");
        $("#numberbutton" + id).html("Class " + class_numbering + ' numbering <span class="caret"></span>');        

        //pg_framenum=new_fnum //?
        var pre_resSelected=[];
        $(flare_container).find("g.node.toggledNode").each(function(){
            var nodename=$(this).attr("id");
            var nodenum=nodename.split("-")[1];
            pre_resSelected.push(nodenum);
        })
        var fpfile_now="cluster" + cluster_num + ".json";
        $.getJSON(fpdir+fpfile_now,id,function(jsonData){

            flare_container = "#flare-container" + id;
            fpdiv = "#fpdiv" + id;            
            $(flare_container).html("");
            var fpsize=setFpNglSize(true, flare_container); // Or just use the size used before?
            plots[id] = createFlareplotCustom(fpsize, jsonData, flare_container, class_numbering);
            numfr = plots[id].getNumFrames();
            
            if ($("#fp_display_summary").hasClass("is_active")){
                plots[id].framesSum(0, numfr);
            }
            
            for (nN=0;nN<pre_resSelected.length;nN++){//Select at plot the residues selected before
                plots[id].toggleNode(pre_resSelected[nN]);
            }

            //updateFPInt(plot, flare_container)//I'm going to skip this for the moment. fpgpcrdb_dict is hard to obtain. //Update fpSelInt depending on what is in the fplot.
            $("#selectionDiv").trigger("click");

            //Add hoverlabels
            hoverlabels(id)

            //Add click-on-edges
            plots[id].addEdgeToggleListener( function(d){
                clickEdgeSelectNodes(d, plots[id]);
            });

            //To reset the selection system from fareplot
            $('#ngl_iframe'+id)[0].contentWindow.$('body').trigger('flareplot_changed');

        });
    }

    function hoverlabels(id){
        var pos, source_pos, target_pos;
        var source_pos_pat = /source-(\w+)/;
        var target_pos_pat = /target-(\w+)/;
        //Put hoverlabels (tooltips) in flareplots position rectangles
        $('#flare-container'+id+' .trackElement path').each(function(){
            $(this).tooltip({
              html: true,
              placement: 'top',
              container: 'body'
            });
        });

        //Put hoverlabels (tooltips) in flareplot position texts
        $('#flare-container'+id+' .node text').each(function(){
            pos = $(this).html();
            $(this).tooltip({
              title: pos,
              html: true,
              placement: 'top',
              container: 'body'
            });
        });

        //Put hoverlabels on interaction lines
        $('#flare-container'+id+' .link').each(function(){
            source_pos = $(this).attr('class').match(source_pos_pat)[1];
            target_pos = $(this).attr('class').match(target_pos_pat)[1];
            $(this).tooltip({
              title: source_pos+"-"+target_pos,
              html: true,
              placement: 'auto',
              container: 'body',
              delay: {show: 0, hide: 200}              
            });
        });
    };

	////////////////////
	//Flare plots time!!
	////////////////////
    //Make sure NGL viewers are ok before starting flareplots
    $('body').on('iframeSet',function(){
        $('#ngl_iframe0')[0].contentWindow.$('body').trigger('iframeSetOk');
        $('#ngl_iframe1')[0].contentWindow.$('body').trigger('iframeSetOk');
        var fpdir = $("#flare_col").data("fpdir");

    	//Create initial flareplots
    	if (fpdir) {
    		var plots = [];
            var fpsize=setFpNglSize(true, "#flare-container0");

            d3.json(fpdir+"cluster1.json", function(jsonData){
    	        plots[0] = createFlareplotCustom(fpsize, jsonData, "#flare-container0", "A");
               	$('#loading_flare0').css('display', 'none');

                //Put hoverlabels to flareplot
                hoverlabels(0)

                //Add click-on-edges
                plots[0].addEdgeToggleListener( function(d){
                    clickEdgeSelectNodes(d,plots[0]);
                });

            });
            d3.json(fpdir+"cluster2.json", function(jsonData){
    	        plots[1] = createFlareplotCustom(fpsize, jsonData, "#flare-container1", "A");
    	        $('#loading_flare1').css('display', 'none');

                //Put hoverlabels to flareplot
                hoverlabels(1)

                //Add click-on-edges
                plots[1].addEdgeToggleListener( function(d){
                    clickEdgeSelectNodes(d, plots[1]);
                });
            });

    	}

    	//clear buttons
    	$("#FPclearSel0").click(function(){
    		emptyFPsels("#flare-container0", plots[0]);
    	});
    	$("#FPclearSel1").click(function(){
    		emptyFPsels("#flare-container1", plots[1]);
    	});

        //"Show in structure buttons"
        $("#FPdisplay0").click(function(){
            show_in_structure("#flare-container0", "#FPdisplay0");
        });
        $("#FPdisplay1").click(function(){
            show_in_structure("#flare-container1", "#FPdisplay1");
        });

    	//Hover in "cluster" dropups
        colorsHoverActiveInactive(".fp_display_element","is_active","#f2f2f2","#bfbfbf","#FFFFFF");	

        //On click of cluster or nomenclature dropups, reset Flareplots with new parameter (and shadow selected option)
        var to_activate, to_inactivate;
        $("#fpdiv0 .clusters_dropup-ul li, #fpdiv0 .numbering_dropup-ul li").click(function(){
        	to_activate =$(this).attr('id');
            to_inactivate=$(this).parent("ul").children(".is_active").attr('id');
            if (to_activate != to_inactivate){
    	    	change_display_sim_option("#" + to_activate, "#" + to_inactivate);
        		changeContactsInFplot("0", fpdir, plots);
        	}
        });
        $("#fpdiv1 .clusters_dropup-ul li, #fpdiv1 .numbering_dropup-ul li").click(function(){
        	to_activate =$(this).attr('id');
            to_inactivate=$(this).parent("ul").children(".is_active").attr('id');
        	if (to_activate != to_inactivate){
    	    	change_display_sim_option("#" + to_activate, "#" + to_inactivate);
    	    	changeContactsInFplot("1", fpdir, plots);
    	    }
        });

        //On change of number of interactions selected, reload the flareplots
        $("#flarerange").change(function(){
            changeContactsInFplot("0", fpdir, plots);
            changeContactsInFplot("1", fpdir, plots);
        });

        //Load needed Json files and execute NGL bottom viewers
        var clustdict_file, compl_data_file;
        clustdict_file = "/dynadb/files/Precomputed/get_contacts_files/contmaps_inputs/"+itype+"/"+stnd+"/"+ligandonly+"/flarejsons/"+clusters+"clusters/clustdict.json";
        compl_data_file = window.location.origin + "/dynadb/files/Precomputed/get_contacts_files/compl_info.json"; 
        $.getJSON(clustdict_file, function(clustdict){  
            $.getJSON(compl_data_file, function(compl_data){
                //Trigger the NGL viewers
                $('#ngl_iframe0')[0].contentWindow.$('body').trigger('createNGL0', [clustdict, compl_data]);
                $('#ngl_iframe1')[0].contentWindow.$('body').trigger('createNGL1', [clustdict, compl_data]);
            });
        });
    });
});