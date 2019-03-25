$(document).ready(function(){
	
	////////////
	// Functions
	////////////

    function createFlareplotCustom(fpsize, jsonData, fpdiv, showContacts, plot){
        var fpjson=jsonData;
        if (fpjson.edges[0].helixpos != undefined) {
            //$("#fpShowResSetBtns").css("display","inline-block");
            if(showContacts!= "all"){
                var edges=fpjson.edges;
                var newedges=[];
                for (eN=0; eN < edges.length ; eN++ ){
                    var edge = edges[eN];
                    if (edge.helixpos == showContacts){
                        newedges.push(edge);
                    }
                }
                fpjson.edges=newedges;
            }
        }/* else {
            $("#fpShowResSetBtns").css("display","none");
        }*/
        plot=createFlareplot(fpsize, fpjson, fpdiv);
        return(plot);
    }

    function setFpNglSize(applyMinSize, flare_container){
	    var screen_h=screen.height;
	    var min_size=550;
	    var fpcont_w_str=$(flare_container).css("width");
	    var fpcont_w=Number(fpcont_w_str.match(/^\d*/g)[0]);
	    var final_size = fpcont_w;
	    if (screen_h){
	        var max_h=screen_h*0.5;
	        var maxR_h=Math.round(max_h);
	        if (fpcont_w > maxR_h){
	            final_size = maxR_h;
	        }
	    } 
	    
	    if (applyMinSize){
	        if (final_size < min_size){
	            final_size = min_size;
	        }
	    }
	    return (final_size)
	}

    function emptyFPsels(flare_container, plot){
        $(flare_container).find("g.node.toggledNode").each(function(){
            if (plot){
                var nodename = $(this).attr("id");
                var nodenum=nodename.split("-")[1];
                plot.toggleNode(nodenum)
                fpSelInt={};
            }
        });
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
        showContacts=$(fpdiv).find(".fp_display_element.is_active").data("tag");

        //Update display button
        $("#clusterbutton" + id).html("Cluster " + showContacts + ' <span class="caret"></span>');

        //pg_framenum=new_fnum //?
        var pre_resSelected=[];
        $(flare_container).find("g.node.toggledNode").each(function(){
            var nodename=$(this).attr("id");
            var nodenum=nodename.split("-")[1];
            pre_resSelected.push(nodenum);
        })
        var fpfile_now="cluster" + showContacts + ".json";
        d3.json(fpdir+fpfile_now, function(jsonData){
            $(flare_container).html("");
            var fpsize=setFpNglSize(true, flare_container); // Or just use the size used before?
            plots[id] = createFlareplotCustom(fpsize, jsonData, flare_container, showContacts, plots[id]);
            allEdges= plots[id].getEdges();
            numfr = plots[id].getNumFrames();
            
            if ($("#fp_display_summary").hasClass("is_active")){
                plots[id].framesSum(0, numfr);
            }
            
            for (nN=0;nN<pre_resSelected.length;nN++){//Select at plot the residues selected before
                plots[id].toggleNode(pre_resSelected[nN]);
            }

            //updateFPInt(plot, flare_container)//I'm going to skip this for the moment. fpgpcrdb_dict is hard to obtain. //Update fpSelInt depending on what is in the fplot.
            $("#selectionDiv").trigger("click");

        });

    }

	////////////////////
	//Flare plots time!!
	////////////////////

    var fpdir = $("#flare_col").data("fpdir");

	//Create initial nitial flareplots
	if (fpdir) {
		var allEdges0, numfr0, allEdges1, numfr1;
		var plots = [];
        var fpsize=setFpNglSize(true, "#flare-container0");

        d3.json(fpdir+"cluster1.json", function(jsonData){
	        plots[0] = createFlareplot(fpsize, jsonData, "#flare-container0", "Inter");
           	$('#loading_flare0').css('display', 'none');
            allEdges0 = plots[0].getEdges();
            numfr0 = plots[0].getNumFrames();
        });
        d3.json(fpdir+"cluster2.json", function(jsonData){
	        plots[1] = createFlareplot(fpsize, jsonData, "#flare-container1", "Inter");
	        $('#loading_flare1').css('display', 'none');
            allEdges1 = plots[1].getEdges();
            numfr1 = plots[1].getNumFrames();
        });
	}

	//clear button
	$("#fpdiv0").on("click","#FPclearSel0", function(){
		emptyFPsels("#flare-container0", plots[0]);
	});
	$("#fpdiv1").on("click","#FPclearSel1", function(){
		emptyFPsels("#flare-container1", plots[1]);
	});

	//Hover in "cluster" dropup
    colorsHoverActiveInactive(".fp_display_element","is_active","#f2f2f2","#bfbfbf","#FFFFFF");	

    //On click of cluster dropup
    $("#fpdiv0 .clusters_dropup-ul li").click(function(){
    	var to_activate =$(this).attr('id');
    	var to_inactivate = $("#fpdiv0 .clusters_dropup-ul .is_active").attr('id');
    	if (to_activate != to_inactivate){
	    	change_display_sim_option("#" + to_activate, "#" + to_inactivate);
    		changeContactsInFplot("0", fpdir, plots);
    	}
    });
    $("#fpdiv1 .clusters_dropup-ul li").click(function(){
    	var to_activate =$(this).attr('id');
    	var to_inactivate = $("#fpdiv1 .clusters_dropup-ul .is_active").attr('id');
    	if (to_activate != to_inactivate){
	    	change_display_sim_option("#" + to_activate, "#" + to_inactivate);
	    	changeContactsInFplot("1", fpdir, plots);
	    }
    });

});