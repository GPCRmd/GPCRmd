$(document).ready( function () {

//-------- Obtain important data from template --------


    var struc = $(".str_file").data("struc_file");
    var dyn_id=$(".str_file").data("dyn_id");
    var delta=$("#view_screen").data("delta");
    var included_prots=$("#view_screen").data("included_prots");
    var pg_framenum=0;
    var ngliframe= $('#embed_mdsrv')[0].contentWindow;
    var trajidtoframenum= $("#selectedTraj").data("trajidtoframenum");

//----- General
    function isEmptyDict(mydict){
        empty=true;
        for (key in mydict){
            if (mydict[key].length >= 1){
                empty=false;
                break;
            }
        }
      return empty;
    }

    function getDictKeys(mydict){
        mykeys=[]
        for (key in mydict){
            mykeys[mykeys.length]=key
        }
      return mykeys;
    }


//-------- Style

    function colorsHoverActiveInactive(myselector,activeclass,colorhov,colorNohobAct, colorNohobInact){
        var sel_el=$(myselector);
        var is_disabled=sel_el.hasClass("disabled");
        sel_el.hover(function(){
            if (! $(this).hasClass("disabled")){
                $(this).css("background-color",colorhov);
            }
        },
        function(){
            var selected=$(this).hasClass(activeclass);
            if ((selected) && (! $(this).hasClass("disabled"))){
                $(this).css("background-color",colorNohobAct);
            } else {
                $(this).css("background-color",colorNohobInact);
            }
        });
    };
    
    colorsHoverActiveInactive(".traj_element","tsel","#f2f2f2","#FFF7F7","#FFFFFF");
    colorsHoverActiveInactive(".fp_options","is_active","#f2f2f2","#bfbfbf","#FFFFFF");
    colorsHoverActiveInactive(".onclickshow","is_active","#f2f2f2","#FFF7F7","#FFFFFF");




// -------- Manage flare plots ------------
    plot=false;
    fpSelInt={};


    function update_FP_rep(){
        if ($("#FPdisplay").hasClass("active")){
            var fpSelInt_send=fpSelInt;
        } else {
            var fpSelInt_send={};
        }
        ngliframe.manageNGLReps_dynamic("FP int","sele_fp",fpSelInt_send);
    }

    function updateFPTypesForTraj(traj_el){
        /*When trajectory is changed:
            - Checks if int types that were not available before, are now; and viceversa
        */
        $(".fp_int_type").each(function(){
            var int_tag=$(this).data("tag");
            var int_this_jsonpath=traj_el.data(int_tag);
            if (int_this_jsonpath){
                $(this).removeClass("disabled");
            } else {
                $(this).addClass("disabled");
            }
        })
    }
    
    function FPTypeAvailUnavail(is_avail){
        /*Modificaitons done when user goes from FP int type available to unavailable or viceversa*/
        if (is_avail){
            $(".disableIfNoIntFP").removeClass("disabled");
        } else{
            $(".disableIfNoIntFP").addClass("disabled");
        }

    }


    changeTrajFlarePlot = function(traj_el_sel,new_fnum){
        traj_el=$(traj_el_sel);
        updateFPTypesForTraj(traj_el);
        var traj_p=traj_el.data("tpath");
        var traj_id=traj_el.attr("id").replace("traj_id_","");
        var fpfile_new=traj_el.data("fplot_file");
        var old_fp=$("#selectedTraj").data("fplot_file");
        $("#selectedTraj").data("tpath",traj_p).data("fplot_file",fpfile_new);
        $("#selectedTraj_id").text(traj_id);
        var traj_note=traj_el.data("trajcomment");
        if (traj_note){
            $("#selectedTraj_note").text(traj_note);
        }
        traj_el.css("background-color","#FFF7F7").addClass("tsel");
        traj_el.siblings().css("background-color","#FFFFFF").removeClass("tsel");

        /* [!] Link to big FP with slide
        var oldhref = $("#gotofplot").attr("href");
        newhref=oldhref.replace(/\w+.json/i,fpfile_new);
        $("#gotofplot").attr("href",newhref);
        */
        pg_framenum=new_fnum
        var trajchange=false;
        if (fpfile_new != old_fp){
            $("#downl_json_hb").attr("href",fpfile_new);
            trajchange=true;
            if ($("#fp_display_summary").hasClass("is_active")){
                change_display_sim_option("#fp_display_frame","#fp_display_summary");
                setFPFrame(pg_framenum)
            }
            if (fpfile_new){
                d3.json(fpfile_new, function(jsonData){
                    $("#flare-container").html("");
                    var fpsize=setFpNglSize(true);
                    plot = createFlareplotCustom(fpsize, jsonData, "#flare-container" , "filtered");
                    plot.setFrame(pg_framenum);
                    //setFPFrame(pg_framenum)
                    allEdges= plot.getEdges();
                    numfr = plot.getNumFrames();
                    //$(".showIfTrajFP").css("display","inline");
                    FPTypeAvailUnavail(true);
                    inter_btn=$("#fp_display_filtered")
                    inter_btn.addClass("is_active").css("background-color","#bfbfbf"); 
                    $(".fp_display_element_type").not(inter_btn).each(function(){
                       $(this).removeClass("is_active").css("background-color","#FFFFFF"); 
                    });
                    
                    
                });
            } else {
                FPTypeAvailUnavail(false);
                alert_msg='<div class="alert alert-info" style="margin:95px 0;">\
                            There is no flare plot available for this trajectory and interaction type yet.\
                          </div>';
                $("#flare-container").html(alert_msg);
                //$(".showIfTrajFP").css("display","none");
            }
            fpSelInt={};
        }
        return trajchange;
    }
    window.changeTrajFlarePlot=changeTrajFlarePlot;

    function emptyFPsels(){
        $("#flare-container").find("g.node.toggledNode").each(function(){
            if (plot){
                var nodename = $(this).attr("id");
                var nodenum=nodename.split("-")[1];
                plot.toggleNode(nodenum)
                fpSelInt={};
            }
        });
    }
    window.emptyFPsels=emptyFPsels;
// FP mouse control
    function hoverlabelsFP(){
        var pos, source_pos, target_pos;
        var source_pos_pat = /source-(\w+)/;
        var target_pos_pat = /target-(\w+)/;
        //Put hoverlabels (tooltips) in flareplots position rectangles
        $('#flare-container .trackElement path').each(function(){
            $(this).tooltip({
              html: true,
              placement: 'auto',
              container: 'body'
            });
        });

        //Put hoverlabels (tooltips) in flareplot position texts
        $('#flare-container .node text').each(function(){
            pos = $(this).html();
            $(this).tooltip({
              title: pos,
              html: true,
              placement: 'auto',
              container: 'body'
            });
        });

        //Put hoverlabels on interaction lines
        $('#flare-container .link').each(function(){
            source_pos = $(this).attr('class').match(source_pos_pat)[1];
            target_pos = $(this).attr('class').match(target_pos_pat)[1];
            $(this).tooltip({
              title: source_pos+"-"+target_pos,
              html: true,
              placement: 'auto',
              container: 'body',
              delay: {show: 0, hide: 500}
            });
        });
    };

    var mouseX;
    var mouseY;
    $(document).mousemove( function(e) {
       // mouse coordinates
       mouseX = e.pageX; 
       mouseY = e.pageY;

    });  
    $(document).on("mouseenter","path",function(e){
        $(".tooltip").css({'top':mouseY - 30,'left':mouseX - 30});
    })
    
    $(".fp_display_element_type").on("click",function(){
        if (! $(this).hasClass("is_active")){
             $(this).addClass("is_active").css("background-color","#bfbfbf"); 
             $(".fp_display_element_type").not($(this)).each(function(){
                $(this).removeClass("is_active").css("background-color","#FFFFFF"); 
             });
        }
        changeContactsInFplot()
    });

    $(".fp_int_type").on("click",function(){
        if ((! $(this).hasClass("is_active")) && (! $(this).hasClass("disabled"))){
            FPTypeAvailUnavail(true);
            $(this).addClass("is_active").css("background-color","#bfbfbf"); 
            $(".fp_int_type").not($(this)).each(function(){
                $(this).removeClass("is_active").css("background-color","#FFFFFF"); 
            });
            if ($(this).hasClass("submenu_el")){
                $(this).closest(".dropdown-submenu").children(".submenu_btn").css("background-color","#f2f2f2");
                $("#fp_int_type_info").html('<p class="fp_int_type_info_p">Hydrogen bonds:</p><p class="fp_int_type_info_p">'+$(this).text()+'</p>');
            } else {
                $(".submenu_btn").css("background-color","#FFFFFF");
                $("#fp_int_type_info").html('<p class="fp_int_type_info_p">'+$(this).text()+'</p>');
            }
            //var int_jsonpath=$(this).data("path");
            var jsonpath=$(this).data("path");
            $("#downl_json_hb").attr("href",jsonpath);
            var int_tag=$(this).data("tag");
            $(".traj_element").each(function(){
                var int_this_jsonpath=$(this).data(int_tag);
                if (!int_this_jsonpath){
                    int_this_jsonpath="";
                }
                $(this).data("fplot_file",int_this_jsonpath);
                if ($(this).hasClass("tsel")){
                    $("#selectedTraj").data("fplot_file",int_this_jsonpath);
                }
            });
            //fplot_intli
            changeContactsInFplot()
        }
    });

// ----- Hovering and clicking on FP 
    changeContactsInFplot = function(){
        //create new FP but saving the selected contacts
        showContacts=$(".fp_display_element_type.is_active").data("tag");
        
        //pg_framenum=new_fnum //?
        var pre_resSelected=[];
        $("#flare-container").find("g.node.toggledNode").each(function(){
            var nodename=$(this).attr("id");
            var nodenum=nodename.split("-")[1];
            pre_resSelected.push(nodenum);
        })
        var fpfile_now=$("#selectedTraj").data("fplot_file");
        //add loading img
        var cont_h_s=$("#flare-container").css("height")
        cont_h=(Number(cont_h_s.replace(/\D/g, "")) / 2) + 70;
        $("#loading_fp").css({"display":"block","top":cont_h})
        d3.json(fpfile_now, function(jsonData){
            $("#flare-container").html("");
            var fpsize=setFpNglSize(true); // Or just use the size used before?
            plot = createFlareplotCustom(fpsize, jsonData, "#flare-container",showContacts);
            $("#loading_fp").css({"display":"none"})
            plot.setFrame(pg_framenum);
            allEdges= plot.getEdges();
            numfr = plot.getNumFrames();
            
            if ($("#fp_display_summary").hasClass("is_active")){
                plot.framesSum(0, numfr);
            }
            
            for (nN=0;nN<pre_resSelected.length;nN++){//Select at plot the residues selected before
                plot.toggleNode(pre_resSelected[nN]);
            }

            updateFPInt()// //Update fpSelInt depending on what is in the fplot. 
            update_FP_rep();
            $(".tooltip").tooltip("hide");
        });
        

    }


    var clickEdgeSelectNodes = function(d){
        var name_s=d.source.name;
        var name_t=d.target.name;
        var nodeclass_s=$("#node-"+name_s).attr("class");
        var nodeclass_t=$("#node-"+name_t).attr("class");
        var is_sel_s =nodeclass_s.indexOf("toggledNode") != -1 ;
        var is_sel_t =nodeclass_t.indexOf("toggledNode") != -1 ;
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
        var nodeclass_s=$("#node-"+name_s).attr("class");
        var nodeclass_t=$("#node-"+name_t).attr("class");
        captureClickedFPInt(name_s,nodeclass_s)
        captureClickedFPInt(name_t,nodeclass_t)
        //plot.setFrame(pg_framenum);
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



// Create plot and control frames


    function createFlareplotCustom(fpsize, jsonData, fpdiv, showContacts){
        var fpjson=jsonData;
        if (fpjson.edges[0].is_neighbour != undefined) {
            //$("#fpShowResSetBtns").css("display","inline-block");
            if(showContacts!= "all"){
                var edges=fpjson.edges;
                var newedges=[];
                for (eN=0; eN < edges.length ; eN++ ){
                    var edge = edges[eN];
                    if (edge.is_neighbour == false){
                        newedges.push(edge);
                    }
                }
                fpjson.edges=newedges;
            }
        }
        /* else {
            $("#fpShowResSetBtns").css("display","none");
        }*/
        plot=createFlareplot(fpsize, fpjson, fpdiv,false);
        hoverlabelsFP()
        hoverLinksFP()
        plot.addEdgeToggleListener( function(d){
            clickEdgeSelectNodes(d);
        });
        return(plot);
    }

    var show_fp=$("#fpdiv").data("show_fp");
    var fpfile = $("#selectedTraj").data("fplot_file");

    var plot, allEdges, numfr;
    var fpSelInt={};
    if (show_fp && fpfile){
        var fpsize=setFpNglSize(true);        
        d3.json(fpfile, function(jsonData){
            plot = createFlareplotCustom(fpsize, jsonData, "#flare-container" , "filtered");
            $("#loading_fp").css({"display":"none","position":"absolute"})
            allEdges= plot.getEdges()
            numfr = plot.getNumFrames();
        });
    };    
    hoverlabelsFP()
      
    function setFPFrame(framenum){
        //Changes the frame displayed at the FP and updates fpSelInt (dict of FP residues selected) according tot he new frame, by calling updateFPInt().
        if (!$("#fp_display_summary").hasClass("is_active")){
            plot.setFrame(Number(framenum));
            if ($("#FPdisplay").hasClass("active")){
                updateFPInt();
                return(fpSelInt)
            } else {
                return({});
            }
        } else {
            return(fpSelInt)
        }
    }


    var updateFlarePlotFrame = function(framenum){
        //Calls setFPFrame(), which changes the frame displayed at the FP and updates fpSelInt (dict of FP residues selected) according tot he new frame. This function iscalled from NGL -> the flare plot frame will match the NGL frame. 
        pg_framenum=framenum;
        var fpSelInt_send=fpSelInt;
        if (plot){
            if ($("#analysis_fplot").hasClass("in")){
                fpSelInt_send=setFPFrame(framenum)
            } else if ($("#flare-container").find("g.node.toggledNode").length > 0) {
                fpSelInt_send=setFPFrame(framenum)
            }

            //fpSelInt_send=setFPFrame(framenum)
        }
        return(fpSelInt_send)
    }
    window.updateFlarePlotFrame=updateFlarePlotFrame; 
          
    function fpLabelToSel(nodenum){
        var nodenumsp= nodenum.split("_");
        var res=nodenumsp[0];
        var resid=res.slice(1)
        var chain=nodenumsp[1]
        var mysel=resid+":"+chain
        return (mysel)

    }
    
    function captureClickedFPInt(nodenum,nodeclass){
        //If the node was not clicked before: Takes a given node and search for all the residues with which it interacts. If the num of interacting res > 0, adds the info of the node + int. nodes to fpSelInt. If the node was clicked before: removes it from fpSelInt.
        var nodepos=fpLabelToSel(nodenum);
        if (nodeclass.indexOf("toggledNode") == -1){
            delete fpSelInt[nodepos];
        } else {
            var edges=[];
            allEdges.forEach(function(e){
                if (e.edge.name1==nodenum){
                    var othernum=e.edge.name2;
                    edges.push(fpLabelToSel(othernum));
                } else if (e.edge.name2==nodenum){
                    var othernum=e.edge.name1;
                    edges.push(fpLabelToSel(othernum));
                }
            });
            if (edges.length > 0){
                fpSelInt[nodepos]=edges;
            }
        }
        update_FP_rep();
    }
    
    $("#flare-container").on("click" , "g.trackElement" , function(){
        if (allEdges){
            var trackname=$(this).attr("id");
            if (trackname.indexOf("trackElement-") !== -1){
                var tracknum=trackname.split("-")[1];
                var nodeclass=$("g#node-"+tracknum).attr("class");
                captureClickedFPInt(tracknum,nodeclass);
            }
        }
    });
    
    $("#flare-container").on("click" , "g.node" , function(){
        if (allEdges){
            var nodename=$(this).attr("id");
            if (nodename.indexOf("node-") !== -1){
                var nodenum=nodename.split("-")[1];                
                var nodeclass=$(this).attr("class");
                captureClickedFPInt(nodenum,nodeclass)
            }
        }
    });

    function updateFPInt(){
        //Updates the fpSelInt dict depending on the nodes that are clicked
        allEdges= plot.getEdges()
        var updFpSelInt={}
        $("#flare-container").find("g.node.toggledNode").each(function(){
            var nodename=$(this).attr("id");
            if (nodename.indexOf("node-") !== -1){
                var nodenum=nodename.split("-")[1];
                var nodepos=fpLabelToSel(nodenum);
                
                var edges=[];
                allEdges.forEach(function(e){
                    if (e.edge.name1==nodenum){
                        var othernum=e.edge.name2;
                        edges.push(fpLabelToSel(othernum));
                    } else if (e.edge.name2==nodenum){
                        var othernum=e.edge.name1;
                        edges.push(fpLabelToSel(othernum));
                    }
                });
                if (edges.length > 0){
                    updFpSelInt[nodepos]=edges;
                }
            }
        })
        fpSelInt = updFpSelInt;
    }


    function change_display_sim_option(to_activate,to_inactivate){
        $(to_activate).addClass("is_active");
        $(to_activate).css("background-color","#bfbfbf");
        
        $(to_inactivate).removeClass("is_active");
        $(to_inactivate).css("background-color","#FFFFFF");
    }
    
    $("#fpdiv").on("click","#fp_display_summary",function(){
        if (! $(this).hasClass("is_active")){
            change_display_sim_option("#fp_display_summary","#fp_display_frame");
            
            plot.framesSum(0, numfr);
            updateFPInt();
        }
        update_FP_rep();
    });

    $("#fpdiv").on("click","#fp_display_frame",function(){
        if (! $(this).hasClass("is_active")){
            change_display_sim_option("#fp_display_frame","#fp_display_summary");
            
            setFPFrame(pg_framenum);
        }
        $("#selectionDiv").trigger("click");
    });


    $("#fpdiv").on("click","#FPdisplay",function(){
        if ($(this).hasClass("active")){
            $(this).removeClass("active");
            //$(this).text("Display interactions");
        } else {
            $(this).addClass("active");
            //$(this).text("Hide interactions");
            updateFPInt();
        }
        update_FP_rep();
    });
    

    function clearFP(){
        emptyFPsels();
        fpSelInt={};
        update_FP_rep();
    }

    $("#fpdiv").on("click","#FPclearSel",function(){
        clearFP()
    });

    $("#analysisDiv").click(function(){
        $("#flare-container").find("g.trackElement").each(function(){
            var nodeid=$(this).attr("id");
            var nodenum=nodeid.split("-")[1];
            $(this).attr("title",nodenum);
        });
    })


    function setFpNglSize(applyMinSize){
        var screen_h=screen.height;
        var min_size=550;
        var fpcont_w_str=$("#flare-container").css("width");
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

//--------- When frame changes ------------
    var passinfoToPlayTraj= function(){ //defined in the parent 
        // Selections that change when frame changes 

        //var bs_info=obtainBS();
        //window.bs_info=bs_info;
        //var dist_sel_res=obtainDistSel();  
        //var dist_of=dist_sel_res[0];  
        //window.dist_of=dist_of;
        //var water_dist=obtainWaterDist()[1];     //
        //window.water_dist=water_dist;
        //var water_check = obtainWaterDist()[0];
        //window.water_check = water_check; 

        window.bs_info=[];
        window.dist_of=[];
        window.water_dist=[];
        window.water_check = []; 


    }
    window.passinfoToPlayTraj=passinfoToPlayTraj;



//-------- AJAX --------

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

//-------- Manage buttons --------

    displayDropBtn("#moreSettings",".dropbtn");
    displayDropBtn("#moreSettings_div",".dropbtn_opt");

    function displayDropBtn(input_select, btn_select){
        $(input_select).on("click", btn_select,function(){
            if ($(this).hasClass("opened")){
                $(this).siblings(".dropdown-content").css("display","none");
                $(this).removeClass("opened");
            }else {
                $(this).siblings(".dropdown-content").css("display","block");
                $(this).addClass("opened");
            }
        });
    }

    $(".showHSet").click(function(){
        if (! $(this).hasClass("active")){
            $(this).addClass("active");
            $(this).siblings(".showHSet").removeClass("active");
        }
        var showH = false;
        if ($("#showHOn.active").length >0){
            showH=true;
        } 
        ngliframe.changeCompSelection(showH)
    });

    function return_default_input(rowsel){
        var reptype=rowsel.find(".high_type");
        reptype.val("licorice");
        var repscheme=rowsel.find(".high_scheme");
        repscheme.val("element");
        changeLastInputColor("#00d215",rowsel);
        var nglname=rowsel.attr("id");
        ngliframe.nglrepsToDefault(nglname);
    }

    $("#clearAll").click(function(){
        // new2
        /*var num_active_domains=$(".whiterep_if_act.active").length;
        if (num_active_domains > 0){
        } */
        ngliframe.manageNGLReps_dynamic("protein","colorScheme","residueindex");
        // end new2
        $(".clickUnclick").each(function(){
            unclickBtn($(this));
        })
        //Input selection
        $("#text_input_all").find(".text_input").each(function(){
            $(this).find(".ti_rm_btn").trigger("click")
        });
        $("#text_input_all").find(".input_dd_color").val("");
        var text_inp_row_alert=$("#text_input_all").find(".ti_alert");
        text_inp_row_alert.find(".ti_alert_gnum").html("");
        text_inp_row_alert.find(".ti_alert_ngl").html("");

        return_default_input($(".text_input"));

        clearFP()

        $("#rmsf_clear_rep").trigger("click");

        $(".displayinview").each(function(){
            if ($(this).is(":checked")){
                $(this).trigger("click");
            }

        })

        $(".sel_within").find(".dist_sel:not(:first-child)").each(function(){
            $(this).remove();
            $(".sel_within").find(".add_btn:last").css("visibility","visible");            
        });
    }); 

    $('body').tooltip({
        selector: '.hovertexttooltip',
        trigger:"hover",
        html:true,
        //container: "#view_screen"
    }); 


    $('#domainsel').tooltip({
        selector: '.showdomtooltip',
        trigger:"click",
        html:true,
        //container: "#view_screen"
    }); 

    $('#mutations_sel').tooltip({
        selector: '.showtooltip',
        trigger:"hover",
        html:true,
        //container: "#view_screen"
    }); 

    $('#var_impact_score').tooltip({
        selector: '.showtooltip_me',
        trigger:"manual",
        html:true,
        //container: "#view_screen"
    }); 

    $(".showtooltip_me").focus(function(){
        $(this).addClass("is_focused")
        $(this).tooltip("show");
    })
    $(".showtooltip_me").blur(function(){
        $(this).removeClass("is_focused")
        $(this).tooltip("hide");
    })
    $(".showtooltip_me").hover(function(){
        if (! $(this).hasClass("is_focused")){
            $(this).tooltip("show")
        }
    },
    function(){
        if (! $(this).hasClass("is_focused")){
            $(this).tooltip("hide")
        }
    }
    )

    $('#var_impact_score').tooltip({
        selector: '.showtooltip_extra',
        trigger:"hover",
        html:true,
        //container: "#view_screen"
    }); 

    $('#varinfo_par').tooltip({
        selector: '.showtooltip',
        trigger:"hover",
        html:true,
        container: "#view_screen"

    });  

    $('#all_analysis').tooltip({
        selector: '.varscoretooltip',
        trigger:"hover",
    }); 

    $("#varinfo_par").on("click", ".close_var_mut" , function(){
        $("#varinfo_par").html("");
        //$('.popover').popover("hide");                    
    });

    $('#seq_w_variants').tooltip({
        selector: '.seq_sel',
        trigger:"hover",
        //html:true,
        //container: "#view_screen"
    }); 

    function change_collapse_glyphicon(trigger_sel,icon_sel,gi_open,gi_closed){
        $(trigger_sel).click(function(){
            var target=$(this).attr("data-target");
            var upOrDown=$(target).attr("class");
            if(upOrDown.indexOf("in") > -1){
                var arrow=$(this).children(icon_sel);
                arrow.removeClass(gi_open);
                arrow.addClass(gi_closed);
            } else {
                var arrow=$(this).children(icon_sel);
                arrow.removeClass(gi_closed);
                arrow.addClass(gi_open);
                if (target=="#analysis_fplot"){
                    if (plot){
                        setFPFrame(pg_framenum)
                    }
                }
            }
        });
    }

    change_collapse_glyphicon(".section_pan",".arrow","glyphicon-chevron-up","glyphicon-chevron-down");
    change_collapse_glyphicon(".td_collapsed_btn",".glyphicon","glyphicon-minus-sign","glyphicon-plus-sign");
    change_collapse_glyphicon("#var_impact_score_w_tdp_collapse",".glyphicon","glyphicon-minus-sign","glyphicon-plus-sign");


    function click_unclick(class_name){
        $("body").on("click",class_name,function(){
            var clickedobj=$(this);
            var nglname=clickedobj.data("nglname")
            pos_class=clickedobj.attr("class");
            var datatype= clickedobj.data("datatype");
            if(pos_class.indexOf("active") > -1){
                clickedobj.removeClass("active");
                ngliframe.manageNGLReps(nglname,false);
                if (datatype=="mutation"){
                    ngliframe.manageNGLReps(nglname+"_label",false);
                }
            } else {
                clickedobj.addClass("active");
                ngliframe.manageNGLReps(nglname,true);
                if ((datatype=="domain") || datatype=="mutation" ){
                    ngliframe.zoomtorep(nglname);
                }
                if (datatype=="mutation"){
                    ngliframe.manageNGLReps(nglname+"_label",true);
                    ngliframe.zoomtorep(nglname);
                }

            }
        });
    }
    click_unclick(".clickUnclick")

    function clickBtn(myobj){
        var nglname=myobj.data("nglname")
        if (! myobj.hasClass("active")){
            myobj.addClass("active");
            ngliframe.manageNGLReps(nglname,true);
            var datatype=myobj.data("datatype");
            if (datatype=="mutation"){
                ngliframe.manageNGLReps(nglname+"_label",true);
            }
        }            
    }

    $("#btn_all").click(function(){
        $(".rep_element:not(.active)").each(function(){
            clickBtn($(this))
        })
    });

    $("#btn_clear").click(function(){
        $(".rep_element.active").each(function(){
            unclickBtn($(this))
        })
    });

    $(".btn_clear_section").click(function(){
        var mysel=$(this).data("selector")
        $(mysel).each(function(){
            unclickBtn($(this))
            // new2
            //ngliframe.manageNGLReps_dynamic("protein","colorScheme","residueindex");
            change_colorscheme_if_noscorecolor("residueindex");
            // end new2

        })
    });

    function unclickBtn(myobj){
        var nglname=myobj.data("nglname")
        if (myobj.hasClass("active")){
            myobj.removeClass("active");
            ngliframe.manageNGLReps(nglname,false);
            var datatype=myobj.data("datatype");
            if (datatype=="mutation"){
                ngliframe.manageNGLReps(nglname+"_label",false);
            }
        }            
    }

    // new2
    function change_colorscheme_if_noscorecolor(colorscheme_name){
        //Do not trigger change if the impact score colormapping is being used
        var allow_colorchange=true;
        if (posColorMap){
            if ($("#displayinview_var_impact").is(":checked")){
                allow_colorchange=false;
            }
        }
        if (allow_colorchange){
            ngliframe.manageNGLReps_dynamic("protein","colorScheme",colorscheme_name);
        }

    }
    // end new2

    $(".whiterep_if_act").on("click", function(){
        var is_inactivated=$(this).hasClass("active");
        var num_active_domains=$(".whiterep_if_act.active").length;


        if (is_inactivated){
            if (num_active_domains == 1){
                // new2
                //ngliframe.manageNGLReps_dynamic("protein","colorScheme","residueindex");
                change_colorscheme_if_noscorecolor("residueindex");
                // end new2
            }
        } else {
            if (num_active_domains == 0){
                // new2
                change_colorscheme_if_noscorecolor("uniform");
                //ngliframe.manageNGLReps_dynamic("protein","colorScheme","uniform");
                // end new2
            }
        }
    })


//-------- Control text inputs --------

    function maxInputLength(select, select2, maxlength){
        $(select).on('keyup blur',select2, function() {
            var val = $(this).val();
            if (val.length > maxlength) {
                $(this).val(val.slice(0, maxlength));
            }
        });
    }

    maxInputLength('#rmsd_my_sel_sel',"",50);
    maxInputLength(".inp_stride", "",4);
    maxInputLength(".maxinp8","",8);
    maxInputLength("#trajStep","",3);
    maxInputLength("#trajTimeOut","",6);
    maxInputLength('input.sel_input',"",100);



    function removeSpacesInInput(my_selector){
        $(my_selector).blur(function(){
            my_input=$(this).val().replace(/\s+/g, '');
            $(this).val(my_input);
         });
    }

    removeSpacesInInput("#rmsd_frame_1");
    removeSpacesInInput("#rmsd_frame_2");
    removeSpacesInInput("#rmsd_ref_frame");
    removeSpacesInInput(".inp_stride");
    removeSpacesInInput(".rvSpaces");

// Custom selection

    function set_dyn_reps(myobject){
        var nglname=myobject.parents(".text_input").attr("id");
        var myval=myobject.val()
        if (myobject.hasClass("high_scheme")){
            // Color scheme
            var myparam="colorScheme";
        } else if (myobject.hasClass("input_dd_color")){
            // Color Value from input
            var myparam="colorValue";
        } else if (myobject.hasClass("dropcolor")){
            // Color Value from dropdown
            var myval=myobject.data("color");
            var myparam="colorValue";
        } else if (myobject.hasClass("high_type")){
            // Rep type
            var myparam="repType";
        }
        ngliframe.manageNGLReps_dynamic(nglname,myparam,myval);
    }

    $("#text_input_all").on("click" , ".nglCallClickTI", function(){
        set_dyn_reps($(this));
    });

    $("#text_input_all").on("change" , ".nglCallChangeTI", function(){
        set_dyn_reps($(this));
    
    });

    $("#text_input_all").on("change" , ".sel_input", function(){
        var nglname=$(this).parents(".text_input").attr("id");
        $("#"+nglname).find(".ti_alert_ngl").html("");
        $("#"+nglname).find("input").css("border-color","");
        var pre_sel = $(this).val();
        if (pre_sel.length >0){
            ngliframe.manageNGLReps_dynamic(nglname,"sele",pre_sel);
        } else {
            ngliframe.manageNGLReps(nglname,false);
        }
    });

    function createNewTextInput(){
        if ($("#text_input_all").children().length < 20){
        
            $("#text_input_all").find(".ti_add_btn").css("visibility","hidden");
            var row='<div  class="text_input" id="ti_row'+ti_i+'" style="margin-bottom:5px">\
                           <div  class="row">\
                              <div class="ti_left" style="width:80%;display:inline-block;"> \
                                <input type="text" value="" class="form-control sel_input nglCallChange" placeholder="Specify your selection" style="width:100%;background-color:#F8F8F8">\
                                <div class="pull-right" style="padding:0;margin:0;font-size:12px">\
                                     <div style="float:left;" >\
                                        <select class="high_type nglCallChangeTI" name="high_type'+ti_i+'" style="padding:0;font-size:12px;height:24px;margin: 3px 0 0 0">\
                                           <option value="licorice">Licorice</option>\
                                           <option value="ball+stick">Ball+stick</option>\
                                           <option value="hyperball">Hyperball</option>\
                                           <option value="line">Line</option>\
                                           <option value="spacefill">Spacefill</option>\
                                           <option value="cartoon">Cartoon</option>\
                                           <option value="ribbon">Ribbon</option>\
                                           <option value="rope">Rope</option>\
                                           <option value="tube">Tube</option>\
                                        </select>\
                                        <select class="high_scheme nglCallChangeTI" name="high_scheme'+ti_i+'" style="padding:0;font-size:12px;width:90px;height:24px;margin: 3px 0 0 0">\
                                           <option value="element">Element</option>\
                                           <option value="uniform">Uniform</option>\
                                           <option value="chainid">Chain</option>\
                                           <option value="moleculetype">Molecule type</option>\
                                           <option value="sstruc">Structure</option>\
                                           <option value="resname">Residue name</option>\
                                           <option value="residueindex">Residue index</option>\
                                           <option value="hydrophobicity">Hydrophobicity</option></select>\
                                      </div>\
                                      <div class="dropdown displaydrop" style="float:left;height:27px;margin:3px 0 0 0;padding:0">\
                                        <button class="dropbtn" style="margin-top: 7px; margin-left: 3px;" data-color="#00d215" ></button> \
                                        <div class="dropdown-content" style="margin-left:3px">\
                                              <div class="dropcolor nglCallClickTI" style="background-color:#3193ff;width:16px; height: 16px;" data-color="#3193ff"></div>\
                                              <div class="dropcolor nglCallClickTI" style="background-color:#B3072F;width:16px; height: 16px;" data-color="#B3072F"></div>\
                                              <div class="dropcolor nglCallClickTI" style="background-color:#ff4c00;width:16px; height: 16px;" data-color="#ff4c00"></div>\
                                              <div class="dropcolor nglCallClickTI" style="background-color:#c5c5c5;width:16px; height: 16px;" data-color="#c5c5c5"></div>\
                                              <div style="background-color:white;width:16px; height: 16px;border:1px solid #808080;" class="dropcolor morecolors nglCallClickTI" data-color="#FFFFFF"><span class="glyphicon glyphicon-plus-sign" style="color:#696969;padding-left:1px"></span></div>\
                                        </div>\
                                      </div>\
                                      <span class="span_morecolors displaydrop" style="float:left" ></span>\
                               </div>\
                              </div>\
                              <div class="radio" style="width:15%;display:inline-block;">\
                                    <button class="btn btn-link ti_rm_btn rm_row_btn" style="color:#bb1133;font-size:15px;margin:0;padding:0;"><span class="glyphicon glyphicon-remove-sign"></span></button>\
                                    <button class="btn btn-link ti_add_btn add_row_btn" style="color:#329a32;font-size:15px;margin:0;padding:0"><span class="glyphicon glyphicon-plus-sign"></span></button>\
                              </div>\
                          </div>\
                          <div class="ti_alert"><div class="ti_alert_gnum"></div><div class="ti_alert_ngl"></div></div>      \
                      </div>';

            $("#text_input_all").append(row);
            ti_i+=1;
        }
    }

    var ti_i=1;
    $("#text_input_all").on("click",".ti_add_btn",function(){ 
        createNewTextInput();
    });


    function createNewSelWithinInput(){
        if ($(".sel_within").children().length < 15){
            $(".sel_within").find(".add_btn").css("visibility","hidden");
            var examplerow=$(".dist_sel:first");
            var res_wth_opt=examplerow.find(".resWthComp").html();
            var res_of_opt=examplerow.find(".wthComp").html();
            var first_resof_opt=examplerow.find(".wthComp option:first").val();
            var res_of_opt_selection='';
            if (first_resof_opt=="user_sel"){
                res_of_opt_selection='<input class="form-control input-sm user_sel_input nglCallChangeWth" type="text" style="width:95px;padding-left:7px">';
            }
            var row='<div class="dist_sel" id=row'+wth_i.toString()+' style="margin-bottom:5px;">\
                      <span class="tick" ></span>\
                      <span class="always" style="margin-left:14px">\
                        Show \
                        <select class="resWthComp nglCallChangeWth" name="rescomp">\
                            ' + res_wth_opt + '</select>\
                         within \
                        <input class="form-control input-sm inputdist nglCallChangeWth" type="text" style="width:40px;padding-left:7px">\
                          &#8491; of\
                            <select class="wthComp" name="comp">' + res_of_opt + '</select>\
                            <span class="user_sel_input_p">'+res_of_opt_selection+'</span>\
                            <button class="btn btn-link rm_btn rm_row_btn" ><span class="glyphicon glyphicon-remove-sign"></span></button>\
                            <button class="btn btn-link add_btn add_row_btn"  ><span class="glyphicon glyphicon-plus-sign"></span></button>\
                        </span>\
                        <div class="alert_sel_wth"><div class="alert_sel_wth_gnum"></div><div class="alert_sel_wth_ngl"></div></div>\
                      </div>';
            $(".sel_within").append(row);
            wth_i+=1;
        }
    }

    var wth_i=1;    
    $(".sel_within").on("click",".add_btn",function(){ 
        createNewSelWithinInput()
    });

    function inactivate_row(row){
        var active_before= row.hasClass("sw_ok");
        if (active_before){
            row.find(".tick").html("");
            row.find(".always").attr("style","margin-left:14px");
            row.removeClass("sw_ok");
        }
    }


    $(".sel_within").on("click", ".rm_btn" , function(){
        var row = $(this).closest(".dist_sel");
        var numWthRows = $(".sel_within").children().length;
        if(numWthRows==1){
            $(".sel_within").find(".inputdist").val("");
            $(".sel_within").find(".user_sel_input").val("");
            $(".sel_within").find(".alert_sel_wth_gnum").html("");
            $(".sel_within").find(".alert_sel_wth_ngl").html("");
            $(".sel_within").find("input").css("border-color","");
            inactivate_row(row);
        }else{
            var wBlock =$(this).closest(".dist_sel");
            if (wBlock.is(':last-child')){
                wBlock.remove();
                $(".sel_within").find(".add_btn:last").css("visibility","visible");
            } else {
                wBlock.remove();
            }
        }
    });

    function input_dd_color_setBackground(inputColorObj){
        var lcolor=inputColorObj.val();
        inputColorObj.parent(".span_morecolors").removeClass("has-error");
        if (lcolor == ""){
            inputColorObj.css("background-color","");
        } else if (! /^#(?:[0-9a-fA-F]{3}){2}$/.test(lcolor)) {
            inputColorObj.parent(".span_morecolors").addClass("has-error");
            inputColorObj.css("background-color","");
        } else {
            inputColorObj.css("background-color",lcolor);
        }
    }

    var available_colors=[]
    function changeLastInputColor(colorcode,def_row){
        if (available_colors.length == 0){
            var first_textinput=$("#text_input_all").find(".text_input:first");
            first_textinput.find(".dropcolor:not(.morecolors)").each(function(){
                var thiscolor=$(this).data("color");
                available_colors[available_colors.length]=thiscolor;
            });
            available_colors[available_colors.length]=first_textinput.find(".dropbtn").data("color");

        }


        if (available_colors.indexOf(colorcode)>-1){//if colorcode in available_colors     
            if (def_row){
                selrow=def_row;
            } else {
                var selrow=$("#text_input_all").find(".text_input:last");
            }
            dCont=selrow.find(".dropdown-content");
            var dDwn=selrow.find(".displaydrop");
            var selColorCont=false;
            selrow.find(".dropcolor").each(function(){
                if ($(this).data("color")==colorcode){
                    selColorCont=$(this);
                }
            })
            if (selColorCont){
                var clicked_color= selColorCont.data("color");
                var dBtn=selrow.find(".dropbtn");
                var old_color=dBtn.data("color");

                if (dBtn.hasClass("morecolors")){
                    dBtn.css({"background-color":clicked_color , "border":"none"}).html("").removeClass("morecolors").data("color",clicked_color);
                    selColorCont.css({"background-color":old_color , "border":"1px solid #808080"}).html('<span style="color:#696969;padding-left:1px" class="glyphicon glyphicon-plus-sign"></span>').addClass("morecolors").data("color",old_color).appendTo(dCont);
                    dDwn.siblings(".span_morecolors").html('');
                    if (dDwn.hasClass("ed_ddwn")){
                        var ed_colSect=dDwn.parent();
                        var lw=ed_colSect.data("short");
                        ed_colSect.css("width",lw);
                    }
                } else {
                    selColorCont.css("background-color",old_color).data("color",old_color);
                    dBtn.css("background-color",clicked_color).data("color",clicked_color);
                }

            }
        } else {
            if (def_row){
                selrow=def_row;
            } else {
                var selrow=$("#text_input_all").find(".text_input:last");
            }

            var dDwn=selrow.find(".displaydrop");
            var selColorCont=dDwn.find(".dropcolor.morecolors");
            var dBtn=dDwn.find(".dropbtn");

            //Select "other colors"
            var clicked_color= selColorCont.data("color"); //This has to be wwite
            var old_color=dBtn.data("color"); //This starts being green
            selColorCont.css({"background-color":old_color , "border":"none"}).html("").removeClass("morecolors").data("color",old_color);
            dBtn.css({"background-color":clicked_color , "border":"1px solid #808080" /*, "vertical-align":"-3px"*/}).html('<span style="color:#696969;padding-bottom:2px" class="glyphicon glyphicon-plus-sign"></span>').addClass("morecolors").data("color",clicked_color);
            var diffcolor_span=dDwn.siblings(".span_morecolors");
            diffcolor_span.html('<input type="text" style="font-size:12px;height:24px;margin: 3px 0 0 3px;  width:60px;padding-left:3px;padding-right:3px;" placeholder="#FFFFFF" class="form-control input-sm input_dd_color nglCallChangeTI">');

            //Indicate at input the desired color
            diffcolor_input=diffcolor_span.children(".input_dd_color");
            diffcolor_input.val(colorcode);
            input_dd_color_setBackground(diffcolor_input);
           // diffcolor_input.change();
        }
    }

    function rmTextInputRow(textrowToRv){
        var numTiRows = $("#text_input_all").children().length;
        if(numTiRows==1){
            $("#text_input_all").find(".sel_input").val("");
            $("#text_input_all").find(".ti_alert_gnum").html("");
            $("#text_input_all").find(".ti_alert_ngl").html("");
            $("#text_input_all").find(".sel_input").css("border-color","");
            $("#text_input_all").find(".input_dd_color").css("background-color","").val("");
            $("#text_input_all").find(".span_morecolors").removeClass("has-error");
            last_input_row=$("#text_input_all").find(".text_input");

            return_default_input(last_input_row);
            //changeLastInputColor("#00d215",last_input_row);

        }else{
            var wBlock =textrowToRv.closest(".text_input");
            if (wBlock.is(':last-child')){
                wBlock.remove();
                $("#text_input_all").find(".ti_add_btn:last").css("visibility","visible");
            } else {
                wBlock.remove();
            }
        }
    }

    $("#text_input_all").on("click", ".ti_rm_btn" , function(){
        var inpval= $(this).closest(".text_input").find(".sel_input").val();
        rmTextInputRow($(this));
        if (inpval != ""){
            var numTiRows = $("#text_input_all").children().length;
            var nglname=$(this).parents(".text_input").attr("id");
            if(numTiRows>=1){
                ngliframe.delete_rep(nglname);
            } else {
                ngliframe.manageNGLReps(nglname,false);
            }
        }
    });

//-------- Color dropdown --------

    function displayDropBtn(input_select, btn_select){
        $(input_select).on("click", btn_select,function(){
            if ($(this).hasClass("opened")){
                $(this).siblings(".dropdown-content").css("display","none");
                $(this).removeClass("opened");
            }else {
                $(this).siblings(".dropdown-content").css("display","block");
                $(this).addClass("opened");
            }
        });
    }
    displayDropBtn("#text_input_all",".dropbtn");


    function colorSel(input_select){
        $(input_select).on("click",".dropcolor",function(){
            var dCont=$(this).parent();
            var dBtn=dCont.siblings(".dropbtn");
            var dDwn=dBtn.parent();
            dCont.css("display","none");
            dBtn.removeClass("opened");
            //dBtn.trigger("change");
            if ($(this).hasClass("morecolors")){
            
                var clicked_color= $(this).data("color");
                var old_color=dBtn.data("color");
                $(this).css({"background-color":old_color , "border":"none"}).html("").removeClass("morecolors").data("color",old_color);
                dBtn.css({"background-color":clicked_color , "border":"1px solid #808080" /*, "vertical-align":"-3px"*/}).html('<span style="color:#696969;padding-bottom:2px" class="glyphicon glyphicon-plus-sign"></span>').addClass("morecolors").data("color",clicked_color);

                if (dDwn.hasClass("ed_ddwn")){
                    var ed_colSect=dDwn.parent();
                    var lw=ed_colSect.data("long");
                    ed_colSect.css("width",lw);
                    var html_span='<input type="text" style="font-size:12px;height:24px;margin: 0 0 0 3px;  width:60px;padding-left:3px;padding-right:3px;" placeholder="#FFFFFF" class="form-control input-sm input_dd_color EDcolorFree">';
                } else {
                    var html_span='<input type="text" style="font-size:12px;height:24px;margin: 3px 0 0 3px;  width:60px;padding-left:3px;padding-right:3px;" placeholder="#FFFFFF" class="form-control input-sm input_dd_color nglCallChangeTI">';
                }

                dDwn.siblings(".span_morecolors").html(html_span);

                
            } else {     
                if (dBtn.hasClass("morecolors")){
                    var clicked_color= $(this).data("color");
                    var old_color=dBtn.data("color");
                    dBtn.css({"background-color":clicked_color , "border":"none" /*, "vertical-align":"2px"*/}).html("").removeClass("morecolors").data("color",clicked_color);
                    $(this).css({"background-color":old_color , "border":"1px solid #808080"}).html('<span style="color:#696969;padding-left:1px" class="glyphicon glyphicon-plus-sign"></span>').addClass("morecolors").data("color",old_color).appendTo(dCont);
                    dDwn.siblings(".span_morecolors").html('');
                    if (dDwn.hasClass("ed_ddwn")){
                        var ed_colSect=dDwn.parent();
                        var lw=ed_colSect.data("short");
                        ed_colSect.css("width",lw);
                    }

                } else {
                    var clicked_color= $(this).data("color");
                    var old_color=dBtn.data("color");
                    $(this).css("background-color",old_color).data("color",old_color);
                    dBtn.css("background-color",clicked_color).data("color",clicked_color);
                }
            }
            var selcolel=dDwn.siblings(".EDselcolvar");
            selcolel.attr("data-color",clicked_color);
            selcolel.trigger("click")
        });
    }
    colorSel("#text_input_all");

    

    function input_dd_color_setBackground(inputColorObj){
        var lcolor=inputColorObj.val();
        inputColorObj.parent(".span_morecolors").removeClass("has-error");
        if (lcolor == ""){
            inputColorObj.css("background-color","");
        } else if (! /^#(?:[0-9a-fA-F]{3}){2}$/.test(lcolor)) {
            inputColorObj.parent(".span_morecolors").addClass("has-error");
            inputColorObj.css("background-color","");
        } else {
            inputColorObj.css("background-color",lcolor);
        }
    }

    $("#allSelTools").on("change",".input_dd_color",function(){
        input_dd_color_setBackground($(this));
    })
//-------- ANALYSIS --------

    function showErrorInblock(selector, error_msg){
         var sel_fr_error="<div style='color:#DC143C'>" + error_msg + "</div>";
         $(selector).html(sel_fr_error);
    }
    
    function showBigError(msg,selector){
        add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>'+ msg;
        $(selector).html(add_error);  
    }

    function strideVal(inp_div){
        var stride = $(inp_div).val();
        if (stride){
            stride = Number(stride);
            var pos = Math.abs(stride)
            var rounded= Math.round(pos);
            if (rounded <= 0){
                var rounded = 1;
            } 
            if (stride != rounded){
                stride = rounded;
                $(inp_div).val(stride);
                $(inp_div).parent().addClass("has-warning");
            }
        } else {
            stride=$(inp_div).data("default");
        }
        return (stride)
    }

    $(".changeVal").on("change", function(){
        var val_changed=$(this).val();
        if (val_changed=="" || /^[\d]+$/.test(val_changed)){
            $(this).parent().removeClass("has-error");            
        }else {
            $(this).parent().addClass("has-error");
        }
    });
    
    $(".inp_stride").on("change" , function(){
        var stride = $(this).val();
        if (stride==""){
            $(this).val("");
        } else {
            stride = Number(stride);
            var pos = Math.abs(stride)
            var rounded= Math.round(pos);
            if (rounded <= 0){
                var rounded = 1;
            } 
            if (stride != rounded){
                stride = rounded;
                $(this).val(stride);
            }
        }
    });
    
    $("#int_thr").on("change" , function(){
        var stride = $(this).val();
        stride = Number(stride);
        var pos = Math.abs(stride);
        if (stride != pos){
            stride = pos;
            $(this).val(stride);
        }
    });

    $(".changeThresh").on("change" , function(){
        var stride = $(this).val();
        stride = Number(stride);
        var pos = Math.abs(stride)
        var rounded= Math.round(pos);
        if (stride != rounded){
            stride = rounded;
            $(this).val(stride);
        }
    });

    function displayResidueFromPlot(mychart,myarray){
        var mysel = mychart.getSelection()[0];
        if (mysel){        
            var mypos=myarray[mysel.row+1][0];
            var resname=mypos.slice(0,3);
            if (! isNaN(parseInt(resname))){
                resname="["+resname+"]";
            }                
            var resnum=mypos.slice(3);
            var rmsf_sele=resname + " and "+ resnum;
            ngliframe.manageNGLReps_dynamic("rmsf_rep","sele",rmsf_sele);
            $("#rmsf_clear_rep").css("display","inline")

        }
    }

    $("#rmsf_clear_rep").on("click",function(){
        ngliframe.manageNGLReps("rmsf_rep",false);
        $("#rmsf_clear_rep").css("display","none")
    })

    function updateframeFromPlot(mychart,array_f,transform_from_time){
        var mysel = mychart.getSelection()[0];
        if (mysel){        
            var frame_num=array_f[mysel.row+1][0];
            if (transform_from_time){
                frame_num=(frame_num/Number(delta))-1;
            }
            //var frameinput_sel=$('#embed_mdsrv')[0].contentWindow.$("#trajRange");
            //frameinput_sel.val(frame_num);
            //frameinput_sel.slider("refresh");
            $('#embed_mdsrv')[0].contentWindow.$('body').trigger('changeframeNGL', [ frame_num ]);
        }
    }

    function calculate_stride(delta,framenum){
        //Obtains the stride that has been used for the variant analysis. This has to be in accordance with the metric_calculator script, used for precomputation!
        var stride=delta*10 //the desired delta is 100ps (0.1 ns)
        var final_num_frames=Math.floor(framenum/stride)
        if (final_num_frames> 5000){
            stride=delta*100 //the desired delta is 10ps (0.01 ns)
        }
        return stride   
    }

    function updateframeFromStridedPlot(mychart,array_f,transform_from_time){
        var mysel = mychart.getSelection()[0];
        if (mysel){        
            var frame_num=array_f[mysel.row+1][0];
            if (transform_from_time){
                var mydelta=Number(delta);
                var traj_id=Number($("#selectedTraj_id").text());
                var total_frames=trajidtoframenum[traj_id];
                var stride_val=calculate_stride(delta,total_frames)
                frame_num=(((frame_num-mydelta)/mydelta)*stride_val);
            }
            //var frameinput_sel=$('#embed_mdsrv')[0].contentWindow.$("#trajRange");
            //frameinput_sel.val(frame_num);
            //frameinput_sel.slider("refresh");
            $('#embed_mdsrv')[0].contentWindow.$('body').trigger('changeframeNGL', [ frame_num ]);
        }
    }

//-------- RMSD computation --------
    var r_id=1;
    function SelectionName(traj_sel){
        var set_sel;
        if (traj_sel == "bck"){
            set_sel="protein CA";
        } else if (traj_sel == "noh"){
            set_sel="non-hydrogen protein atoms";
        } else if (traj_sel == "min"){
            set_sel="protein CA, CB, C, N, O";
        /*} else if (traj_sel == "all_atoms"){
            set_sel="all atoms";*/
        } else if (traj_sel == "all_prot" ){
            set_sel="all protein atoms";
        } else {
            set_sel=traj_sel;
        }
        return (set_sel);
    }

    $("#gotoRMSDPg").click(function(){
        $("#rmsd_sel_frames_error").html("");
        $("#rmsd_ref_frames_error").html("");
        $("#rmsd_stride_parent").removeClass("has-warning");
        numComputedR = $("#rmsd_chart").children().length;
        if (numComputedR < 15){
            rmsdTraj=$("#rmsd_traj_sel").val();
            rmsdFrames=$("#rmsd_sel_frames_id input[name=rmsd_sel_frames]:checked").val();
            if (rmsdFrames=="rmsd_frames_mine"){
                frameFrom=$("#rmsd_frame_1").val();
                frameTo=$("#rmsd_frame_2").val();
                var framesOk=true;
                if (!frameFrom){
                    $("#rmsd_frame_1").parent().addClass("has-error");
                    framesOk=false;
                }
                if (!frameTo){
                    $("#rmsd_frame_2").parent().addClass("has-error");
                    framesOk=false;
                }
                if (framesOk) {
                    if (/^[\d]+$/.test(frameFrom + frameTo)){
                        if (Number(frameFrom) < Number(frameTo)){
                            rmsdFrames=frameFrom + "-" + frameTo;
                        } else {
                            showErrorInblock("#rmsd_sel_frames_error", "Initial frame must be lower than final frame.");
                            rmsdFrames=false;
                        }

                    } else {
                        showErrorInblock("#rmsd_sel_frames_error", "Input must be a positive integer.");
                        rmsdFrames=false;
                    }
                } else {
                    rmsdFrames=false;
                }
            }
            rmsdRefFr=$("#rmsd_ref_frame").val();
            if (rmsdRefFr == ""){
                rmsdRefFr="0";
            } else if (! /^[\d]+$/.test(rmsdRefFr)){
                showErrorInblock("#rmsd_ref_frames_error", "Input must be a positive integer.");
                rmsdRefFr=false;
            }/* else if (Number(rmsdRefFr)<1){
                showErrorInblock("#rmsd_ref_frames_error", "Frame must be at least 1.");
                rmsdRefFr=false;
            }*/
            rmsdRefTraj=$("#rmsd_ref_traj_id").val();
            rmsdSel=$("#rmsd_sel_id input[name=rmsd_sel]:checked").val();
            if (rmsdSel == "rmds_my_sel"){
                rmsdSel=$("#rmsd_my_sel_sel").val(); //Curate this so that mdtraj understands it            
            }
            if (! rmsdTraj || ! rmsdFrames || ! rmsdRefFr || ! rmsdRefTraj || ! rmsdSel){
                add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>Some fields are empty or contain errors.';
                $("#rmsd_alert").html(add_error);
            } else {
                $("#rmsd_chart").after("<p style='margin-top:5px;padding:5px;background-color:#e6e6ff;border-radius:3px;clear:left' id='wait_rmsd'><span class='glyphicon glyphicon-time'></span> Computing RMSD...</p>");        
                $("#rmsd_alert").html("");
                $("#gotoRMSDPg").addClass("disabled");
                $(".href_save_data_dist_plot,.href_save_data_rmsd_plot,.href_save_data_rmsf_plot, .href_save_data_int, #downl_json_hb").addClass("disabled"); 
                act_rmsd_plots=[];
                $("#rmsd_chart").children(".rmsd_plot").each(function(){
                    act_rmsd_plots.push($(this).data("rmsd_id"));
                });
                var stride = strideVal("#rmsd_stride");
                var t0=performance.now();
                $.ajax({
                    type: "POST",
                    url: "/covid19/ajax_rmsd/", 
                    dataType: "json",
                    data: { 
                      "rmsdStr": struc,
                      "rmsdTraj": rmsdTraj,
                      "rmsdFrames": rmsdFrames,
                      "rmsdRefFr": rmsdRefFr,
                      "rmsdRefTraj": rmsdRefTraj,
                      "rmsdSel": rmsdSel,
                      "no_rv" :act_rmsd_plots.join(),
                      "stride" :stride,
                      "dyn_id" : dyn_id,
                      "delta":Number(delta),
                    },
                    success: function(data_rmsd) {
                        $("#wait_rmsd").remove();
                        $("#gotoRMSDPg").removeClass("disabled");
                        var success=data_rmsd.success;
                        if (success){
                            var rmsd_array_t=data_rmsd.result_t;
                            var rmsd_array_f=data_rmsd.result_f;
                            var rmsd_id=data_rmsd.rmsd_id;          
                            var strided=data_rmsd.strided;
                            var strideText="";
                            if (Number(strided)> 1){
                                strideText = ", str: "+strided;
                            }
                            function drawChart2(){
                                var patt = /[^/]*$/g;
                                var trajFile = patt.exec(rmsdTraj);
                                var patt = /[^/]*$/g;
                                var refTrajFile = patt.exec(rmsdRefTraj);
                                var rmsdSelOk=SelectionName(rmsdSel);
                                var data_t = google.visualization.arrayToDataTable(rmsd_array_t,false);
                                var data_f = google.visualization.arrayToDataTable(rmsd_array_f,false);
                                var options_t = {'title':'RMSD (traj:'+trajFile+', ref: fr '+rmsdRefFr+' of traj '+refTrajFile + strideText+', sel: '+rmsdSelOk+')',
                                    "height":350, "width":640, "legend":{"position":"none"}, 
                                    "chartArea":{"right":"10","left":"60","top":"50","bottom":"60"},hAxis: {title: 'Time (ns)'},vAxis: {title: 'RMSD (nm)'},
                                    "tooltip": { "trigger": 'selection' }
                                };
                                var options_f = {'title':'RMSD (traj:'+trajFile+', ref: fr '+rmsdRefFr+' of traj '+refTrajFile + strideText+', sel: '+rmsdSelOk+')',
                                    "height":350, "width":640, "legend":{"position":"none"}, 
                                    "chartArea":{"right":"10","left":"60","top":"50","bottom":"60"},hAxis: {title: 'Frame number'},vAxis: {title: 'RMSD (nm)'},
                                    "tooltip": { "trigger": 'selection' }
                                };
                                newRMSDgraph_sel="rmsd_chart_"+r_id.toString();
                                var RMSDplot_html;
                                var dyn_id=$(".str_file").data("dyn_id");
                                var disable_class=""
                                if ($.active>1){
                                    disable_class="disabled"
                                }
                                rmsd_id_int=rmsd_id.split("_")[1]
                                RMSDplot_html="<div class='rmsd_plot' id='all_"+newRMSDgraph_sel+"' data-rmsd_id='"+rmsd_id+"' style='border:1px solid #F3F3F3;overflow:auto;overflow-y:hidden;-ms-overflow-y: hidden;'>\
                                                <div class='rmsd_time' id='"+newRMSDgraph_sel+"t'></div>\
                                                <div class='rmsd_frame' id='"+newRMSDgraph_sel+"f'></div>\
                                                <div class='rmsd_settings' id='opt_"+newRMSDgraph_sel+"' style='margin:5px'>\
                                                    <div class='plot_rmsd_by_sel_cont' style='font-size:12px;margin-left:5px'>\
                                                      Plot RMSD by\
                                                        <span >\
                                                            <select class='plot_rmsd_by_sel' name='frame_time'>\
                                                                <option class='plot_rmsd_by' selected value='time'>time</option>\
                                                                <option class='plot_rmsd_by' value='frame'>frame</option>\
                                                            </select>\
                                                        </span>\
                                                    </div>\
                                                    <div style='display:inline-block;margin:5px;cursor:pointer;'>\
                                                        <a role='button' class='btn btn-link save_img_rmsd_plot settingsB' href='#' target='_blank' style='color:#585858;margin-right:0;margin-left;padding-right:0;padding-left:0;margin-bottom:3px'>\
                                                            <span  title='Save plot as image' class='glyphicon glyphicon-stats'></span>\
                                                        </a>\
                                                    </div>\
                                                    <div style='display:inline-block;margin:5px;'>\
                                                        <a role='button' class='btn btn-link href_save_data_rmsd_plot settingsB "+disable_class+"' href='/covid19/dwl/"+dyn_id+"/rmsd/"+rmsd_id_int+"' style='color:#585858;margin-right:0;margin-left;padding-right:0;padding-left:0;margin-bottom:3px'>\
                                                            <span  title='Save data' class='glyphicon glyphicon-download-alt save_data_rmsd_plot'></span>\
                                                        </a>\
                                                    </div>\
                                                    <div style='display:inline-block;margin:5px;color:#DC143C;cursor:pointer;'>\
                                                        <span title='Delete' class='glyphicon glyphicon-trash delete_rmsd_plot' data-rmsd_id='"+rmsd_id+"'></span>\
                                                    </div>\
                                                </div>\
                                            </div>";//color:#239023

                                $("#rmsd_chart").append(RMSDplot_html);
                                var chart_cont_li =[[newRMSDgraph_sel+"t",data_t,options_t],[newRMSDgraph_sel+"f",data_f,options_f]];

                                var chart_cont=chart_cont_li[0][0];
                                var data=chart_cont_li[0][1];
                                var options=chart_cont_li[0][2];
                                var rmsd_chart_div = document.getElementById(chart_cont);
                                var chart0r = new google.visualization.LineChart(rmsd_chart_div);    
                                google.visualization.events.addListener(chart0r, 'ready', function () {
                                    var rmsd_img_source =  chart0r.getImageURI(); 
                                    $("#"+chart_cont).attr("data-url",rmsd_img_source);
                                });
                                chart0r.setAction({
                                  id: "c0r",
                                  text: 'Display frame on viewer',
                                  action: function() {
                                    updateframeFromPlot(chart0r,rmsd_array_f,false);
                                  }
                                });
                                chart0r.draw(data, options);   
//                                google.visualization.events.addListener(chart0r, 'select', function(){  
//                                    updateframeFromPlot(chart0r,rmsd_array_f);
//                                });

                                var chart_cont=chart_cont_li[1][0];
                                var data=chart_cont_li[1][1];
                                var options=chart_cont_li[1][2];
                                var rmsd_chart_div = document.getElementById(chart_cont);
                                var chart1r = new google.visualization.LineChart(rmsd_chart_div);    
                                google.visualization.events.addListener(chart1r, 'ready', function () {
                                    var rmsd_img_source =  chart1r.getImageURI(); 
                                    $("#"+chart_cont).attr("data-url",rmsd_img_source);
                                });
                                chart1r.setAction({
                                  id: "c0r",
                                  text: 'Display frame on viewer',
                                  action: function() {
                                    updateframeFromPlot(chart1r,rmsd_array_f,false);
                                  }
                                });
                                chart1r.draw(data, options);   

                                $("#"+newRMSDgraph_sel+"f").css("display","none");  
                                var rmsd_img_source_t=$("#"+newRMSDgraph_sel+"t").data("url");
                                $("#"+newRMSDgraph_sel+"t").siblings(".rmsd_settings").find(".save_img_rmsd_plot").attr("href",rmsd_img_source_t);
                                r_id+=1;
                                
                                
                                if (small_errors.length >= 1){
                                    errors_html="";
                                    for (error_msg =0 ; error_msg < small_errors.length ; error_msg++){
                                        errors_html+="<p>"+small_errors[error_msg]+"</p>";
                                    }
                                    errors_html_div='<div style="margin-bottom:5px;clear:left" class="alert alert-warning"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>'+errors_html;
                                    //$("#all_"+newRMSDgraph_sel).after(errors_html_div);
                                    errors_html_div='<div style="margin:3px;clear:left" class="alert alert-warning"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>'+errors_html;
                                    $("#opt_"+newRMSDgraph_sel).after(errors_html_div);
                                                                
                                }
                                
                            }
                            google.load("visualization", "1", {packages:["corechart"],'callback': drawChart2});
                            small_errors=data_rmsd.msg;
    ////////////////////
                        } else {
                            var e_msg=data_rmsd.msg;
                            add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>'+ e_msg;
                            $("#rmsd_alert").html(add_error);                              
                        }
                        if ($.active<=1){
                            $(".href_save_data_dist_plot,.href_save_data_rmsd_plot,.href_save_data_rmsf_plot, .href_save_data_int, #downl_json_hb").removeClass("disabled");
                        }
                    var t1= performance.now();
                    },
                    error: function() {
                        $("#gotoRMSDPg").removeClass("disabled");
                        $("#wait_rmsd").remove();
                        add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>An unexpected error occurred.';
                        $("#rmsd_alert").html(add_error);  
                        if ($.active<=1){
                            $(".href_save_data_dist_plot,.href_save_data_rmsd_plot,.href_save_data_rmsf_plot, .href_save_data_int, #downl_json_hb").removeClass("disabled");
                        }
                    },
                    timeout: 600000
                });

            }
        } else {
            add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>Please, remove some RMSD results to obtain new ones.';
            $("#rmsd_alert").html(add_error);  
        }
    });

    $('body').on('click','.delete_rmsd_plot', function(){
        var plotToRv=$(this).parents(".rmsd_plot").attr("id");
        $('#'+plotToRv).remove();
    });
    

    $("#rmsd_chart").on("change",".plot_rmsd_by_sel", function(){
        xAxis=$(this).val();
        var rmsd_frame_cont=$(this).closest(".rmsd_settings").siblings(".rmsd_frame");
        var rmsd_time_cont=$(this).closest(".rmsd_settings").siblings(".rmsd_time");
        if (xAxis == "time"){
            rmsd_frame_cont.css("display","none");
            rmsd_time_cont.css("display","inline");            
            var img_source=rmsd_time_cont.data("url");
            $(this).closest(".rmsd_settings").find(".save_img_rmsd_plot").attr("href",img_source);

        } else {            
            rmsd_time_cont.css("display","none");
            rmsd_frame_cont.css("display","inline");
            var img_source=rmsd_frame_cont.data("url");
            $(this).closest(".rmsd_settings").find(".save_img_rmsd_plot").attr("href",img_source);
        }
    });


//-------- RMSF computation --------
    var rf_id=1;
    $("#gotoRMSFPg").click(function(){
        $("#rmsf_sel_frames_error").html("");
        $("#rmsf_ref_frames_error").html("");
        $("#rmsf_stride_parent").removeClass("has-warning");
        numComputedR = $("#rmsf_chart").children().length;
        if (numComputedR < 15){
            rmsfTraj=$("#rmsf_traj_sel").val();
            rmsfFrames=$("#rmsf_sel_frames_id input[name=rmsf_sel_frames]:checked").val();
            if (rmsfFrames=="rmsf_frames_mine"){
                frameFrom=$("#rmsf_frame_1").val();
                frameTo=$("#rmsf_frame_2").val();
                var framesOk=true;
                if (!frameFrom){
                    $("#rmsf_frame_1").parent().addClass("has-error");
                    framesOk=false;
                }
                if (!frameTo){
                    $("#rmsf_frame_2").parent().addClass("has-error");
                    framesOk=false;
                }
                if (framesOk) {
                    if (/^[\d]+$/.test(frameFrom + frameTo)){
                        if (Number(frameFrom) < Number(frameTo)){
                            rmsfFrames=frameFrom + "-" + frameTo;
                        } else {
                            showErrorInblock("#rmsf_sel_frames_error", "Initial frame must be lower than final frame.");
                            rmsfFrames=false;
                        }

                    } else {
                        showErrorInblock("#rmsf_sel_frames_error", "Input must be a positive integer.");
                        rmsfFrames=false;
                    }
                } else {
                    rmsfFrames=false;
                }
            }

            rmsfSel=$("#rmsf_sel_id input[name=rmsf_sel]:checked").val();
            if (! rmsfTraj || ! rmsfFrames || ! rmsfSel){
                add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>Some fields are empty or contain errors.';
                $("#rmsf_alert").html(add_error);
            } else {
                $("#rmsf_chart").after("<p style='margin-top:5px;padding:5px;background-color:#e6e6ff;border-radius:3px;clear:left' id='wait_rmsf'><span class='glyphicon glyphicon-time'></span> Computing RMSF...</p>");        
                $("#rmsf_alert").html("");
                $("#gotoRMSFPg").addClass("disabled");
                $(".href_save_data_dist_plot,.href_save_data_rmsd_plot,.href_save_data_rmsf_plot, .href_save_data_int, #downl_json_hb").addClass("disabled"); 
                act_rmsf_plots=[];
                $("#rmsf_chart").children(".rmsf_plot").each(function(){
                    act_rmsf_plots.push($(this).data("rmsf_id"));
                });
                var stride = strideVal("#rmsf_stride");
                var t0=performance.now();
                $.ajax({
                    type: "POST",
                    url: "/covid19/ajax_rmsf/", 
                    dataType: "json",
                    data: { 
                      "rmsfStr": struc,
                      "rmsfTraj": rmsfTraj,
                      "rmsfFrames": rmsfFrames,
                      "rmsfSel": rmsfSel,
                      "no_rv" :act_rmsf_plots.join(),
                      "stride" :stride,
                      "dyn_id" : dyn_id,
                      "delta":Number(delta),
                    },
                    success: function(data_rmsf) {
                        $("#wait_rmsf").remove();
                        $("#gotoRMSFPg").removeClass("disabled");
                        var success=data_rmsf.success;
                        if (success){
                            var rmsf_array=data_rmsf.result;
                            var rmsf_id=data_rmsf.rmsf_id;          
                            var strided=data_rmsf.strided;
                            var strideText="";
                            if (Number(strided)> 1){
                                strideText = ", str: "+strided;
                            }
                            function drawChartRMSF(){
                                var patt = /[^/]*$/g;
                                var trajFile = patt.exec(rmsfTraj);
                                var patt = /[^/]*$/g;
                                var rmsfSelOk=SelectionName(rmsfSel);
                                var datatoplot = google.visualization.arrayToDataTable(rmsf_array,false);
                                var options = {'title':'RMSF (traj:'+trajFile + strideText+', sel: '+rmsfSelOk+')',
                                    "height":350, "width":640, "legend":{"position":"none"}, 
                                    "chartArea":{"right":"10","left":"60","top":"50","bottom":"60"},hAxis: {title: 'Residue'},vAxis: {title: 'RMSF (nm)'},
                                    "tooltip": { "trigger": 'selection' }
                                };
                                newRMSFgraph_sel="rmsf_chart_"+rf_id.toString();
                                var RMSFplot_html;
                                var dyn_id=$(".str_file").data("dyn_id");
                                var disable_class=""
                                if ($.active>1){
                                    disable_class="disabled"
                                }
                                rmsf_id_int=rmsf_id.split("_")[1]
                                RMSFplot_html="<div class='rmsf_plot' id='all_"+newRMSFgraph_sel+"' data-rmsf_id='"+rmsf_id+"' style='border:1px solid #F3F3F3;overflow:auto;overflow-y:hidden;-ms-overflow-y: hidden;'>\
                                                <div class='rmsf_byres' id='"+newRMSFgraph_sel+"'></div>\
                                                <div class='rmsf_settings' id='opt_"+newRMSFgraph_sel+"' style='margin:5px'>\
                                                    <div style='display:inline-block;margin:5px;cursor:pointer;'>\
                                                        <a role='button' class='btn btn-link save_img_rmsf_plot settingsB' href='#' target='_blank' style='color:#585858;margin-right:0;margin-left;padding-right:0;padding-left:0;margin-bottom:3px'>\
                                                            <span  title='Save plot as image' class='glyphicon glyphicon-stats'></span>\
                                                        </a>\
                                                    </div>\
                                                    <div style='display:inline-block;margin:5px;'>\
                                                        <a role='button' class='btn btn-link href_save_data_rmsf_plot settingsB "+disable_class+"' href='/covid19/dwl/"+dyn_id+"/rmsf/"+rmsf_id_int+"'  style='color:#585858;margin-right:0;margin-left;padding-right:0;padding-left:0;margin-bottom:3px'>\
                                                            <span  title='Save data' class='glyphicon glyphicon-download-alt save_data_rmsf_plot'></span>\
                                                        </a>\
                                                    </div>\
                                                    <div style='display:inline-block;margin:5px;color:#DC143C;cursor:pointer;'>\
                                                        <span title='Delete' class='glyphicon glyphicon-trash delete_rmsf_plot' data-rmsf_id='"+rmsf_id+"'></span>\
                                                    </div>\
                                                </div>\
                                            </div>";//color:#239023

                                $("#rmsf_chart").append(RMSFplot_html);
                                var chart_cont=newRMSFgraph_sel;
                                var data=datatoplot;
                                var options=options;
                                var rmsf_chart_div = document.getElementById(chart_cont);
                                var chart0r = new google.visualization.LineChart(rmsf_chart_div);    
                                google.visualization.events.addListener(chart0r, 'ready', function () {
                                    var rmsf_img_source =  chart0r.getImageURI(); 
                                    $("#"+chart_cont).attr("data-url",rmsf_img_source);
                                });

                                chart0r.setAction({
                                  id: "c0r",
                                  text: 'Display residue on viewer',
                                  action: function() {
                                    //updateframeFromPlot(chart0r,rmsd_array_f);
                                    displayResidueFromPlot(chart0r,rmsf_array)
                                  }
                                });

                                chart0r.draw(data, options);   

                                var rmsf_img_source=$("#"+newRMSFgraph_sel).data("url");
                                $("#"+newRMSFgraph_sel).siblings(".rmsf_settings").find(".save_img_rmsf_plot").attr("href",rmsf_img_source);
                                rf_id+=1;
                                
                                if (small_errors.length >= 1){
                                    errors_html="";
                                    for (error_msg =0 ; error_msg < small_errors.length ; error_msg++){
                                        errors_html+="<p>"+small_errors[error_msg]+"</p>";
                                    }
                                    errors_html_div='<div style="margin-bottom:5px;clear:left" class="alert alert-warning"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>'+errors_html;
                                    errors_html_div='<div style="margin:3px;clear:left" class="alert alert-warning"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>'+errors_html;
                                    $("#opt_"+newRMSFgraph_sel).after(errors_html_div);
                                                                
                                }
                                
                            }
                            google.load("visualization", "1", {packages:["corechart"],'callback': drawChartRMSF});
                            small_errors=data_rmsf.msg;
    ////////////////////
                        } else {
                            var e_msg=data_rmsf.msg;
                            add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>'+ e_msg;
                            $("#rmsf_alert").html(add_error);                              
                        }
                        if ($.active<=1){
                            $(".href_save_data_dist_plot,.href_save_data_rmsf_plot,.href_save_data_rmsf_plot, .href_save_data_int, #downl_json_hb").removeClass("disabled");
                        }
                    var t1= performance.now();
                    },
                    error: function() {
                        $("#gotoRMSFPg").removeClass("disabled");
                        $("#wait_rmsf").remove();
                        add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>An unexpected error occurred.';
                        $("#rmsf_alert").html(add_error);  
                        if ($.active<=1){
                            $(".href_save_data_dist_plot,.href_save_data_rmsf_plot,.href_save_data_rmsd_plot, .href_save_data_int, #downl_json_hb").removeClass("disabled");
                        }
                    },
                    timeout: 600000
                });

            }
        } else {
            add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>Please, remove some RMSF results to obtain new ones.';
            $("#rmsf_alert").html(add_error);  
        }
    });

    $('body').on('click','.delete_rmsf_plot', function(){
        var plotToRv=$(this).parents(".rmsf_plot").attr("id");
        $('#'+plotToRv).remove();
        if ($(".rmsf_plot").length==0){
            $("#rmsf_clear_rep").trigger("click")
        }
    });
    

    $(".displayinview").on("change", function(){
        var nglname_li_s=$(this).data("nglname");
        var nglname_li= nglname_li_s.split(";");
        if ($(this).is(":checked")){
            var display=true;
        } else {
            var display=false;
        }
        for (i=0;i<nglname_li.length;i++){
            var nglname=nglname_li[i];
            ngliframe.manageNGLReps(nglname,display);

        }
        if ($(this).attr("id")=="displayinview_var_impact"){  
            var protein_name=get_active_protein_name();
            color_ngl_seq(posColorMap,protein_name);
        }
    })

// -------- Variant analysis------------    
                        
    function drawChartVarImpactTime(var_impact_time_res,myselector,data_type,varpos,dyn_id){
        var datatoplot = google.visualization.arrayToDataTable(var_impact_time_res,false);
        var options = {
            "height":350, "width":620, "legend":{"position":"none"}, 
            "chartArea":{"right":"10","left":"70","top":"50","bottom":"100"},hAxis: {title: var_impact_time_res[0][0], slantedText:true, slantedTextAngle:45},vAxis: {title: var_impact_time_res[0][1]},
            "tooltip": { "trigger": 'selection' }
        };
        var traj_id=Number($("#selectedTraj_id").text());
        link_to_dwn="/covid19/dwl/variantimpact/"+dyn_id+"/"+traj_id+"/"+varpos+"/"+data_type+"/";
        var plot_html="<div class='VarImpactTime_plot_cont'>\
                        <div class='VarImpactTime_plot' ></div>\
                        <div class='VarImpactTime_plot_settings'>\
                            <div class='plot_settings_btn_cont'>\
                                <a role='button' class='btn btn-link VarImpactTime_plot_saveImg ' href='#' target='_blank'>\
                                    <span  title='Save plot as image' class='glyphicon glyphicon-stats'></span>\
                                </a>\
                            </div>\
                            <div class='plot_settings_btn_cont'>\
                                <a role='button' class='btn btn-link VarImpactTime_plot_saveData disablewhenajax' href='"+link_to_dwn+"' >\
                                    <span  title='Save data' class='glyphicon glyphicon-download-alt '></span>\
                                </a>\
                            </div>\
                        </div>\
                    </div>";

        myselector.append(plot_html);
        var plot_element_obj=myselector.find(".VarImpactTime_plot");
        var plot_element=plot_element_obj[0];
        if (data_type=="rmsf"){
            //options["chartArea"]["haxis"]["slantedText"]=true;
            var chart0r = new google.visualization.ColumnChart(plot_element);        
        } else {
            var chart0r = new google.visualization.LineChart(plot_element);    
        }
        var plot_img_source="#";
        google.visualization.events.addListener(chart0r, 'ready', function () {
            plot_img_source =  chart0r.getImageURI(); 
        });

        if (var_impact_time_res[0][0]=="Time (ns)"){
            chart0r.setAction({
              id: "myid",
              text: 'Display frame on viewer',
              action: function() {
                updateframeFromStridedPlot(chart0r,var_impact_time_res,true);
              }
            });
        }

        chart0r.draw(datatoplot, options);   
        myselector.find(".VarImpactTime_plot_saveImg").attr("href",plot_img_source);
            

    }

    function capitalizeFirstLetter(string) {
      return string.charAt(0).toUpperCase() + string.slice(1);
    }


    function update_average_sd_data(traj_id,protname,varpos,data_type){
        var vardata_found=false;
        if (impact_per_var_all){
            if (traj_id in impact_per_var_all){
                var impact_per_var_traj=impact_per_var_all[traj_id];
                if (protname in impact_per_var_traj){
                    var impact_per_var_prot= impact_per_var_traj[protname];
                    if (varpos in impact_per_var_prot){
                        var impact_per_var_var=impact_per_var_prot[varpos]["time_dep"];
                        vardata_found=true;
                       /*if (data_type.startsWith("contact_")){
                            var selected_data_type=$("#var_impact_score_tdp").val();
                            if (selected_data_type != data_type){
                                return false; //We onlu need to indicate the contact type that is selected
                            }
                            var average_sel="#val_average_analysis_contnum";
                            var sd_sel="#val_sd_analysis_contnum";
                        } else {
                        }*/
                        var average_sel="#val_average_analysis_mut_"+data_type;
                        var sd_sel="#val_sd_analysis_mut_"+data_type;
                        if (data_type in impact_per_var_var){
                            var impact_param= impact_per_var_var[data_type];
                            var average_val=fix_float_to_n_nonzero(impact_param["average"],3,3,10);
                            var sd_val=fix_float_to_n_nonzero(impact_param["sd"],3,3,10);
                        } else {
                            var average_val="-";
                            var sd_val="-";
                        }
                        $(average_sel).html(average_val);
                        $(sd_sel).html(sd_val);
                    }
                }

            }
            
        }
        if (! vardata_found){
            $(".td_summary_res_table").html("-");
        }

    }

    var var_measurements_abbr={"rmsd": "RMSD (nm)",
        "rmsf": "RMSF (nm)",
        "sasa": "SASA (nm^2)",
        "chi1": "Chi1 (degrees)",
        "contact_hb": "Hydrogen bond contacts",
        "contact_sb": "Salt brudge contacts",
        "contact_hp": "Hydrophobic contacts",
        "contact_pc": "Pi-cation contacts",
        "contact_ps": "Pi-stacking contacts",
        "contact_ts": "T-stacking contacts",
        "contact_vdw": "VdW contacts",
        "contact_wb": "Water bridge  contacts",
        "contact_wb2": "Ext. water bridge contacts"};

    var var_input_res={};
    function obtain_timedependent_data(protname,varpos){
      $("#variant_impact_errors").html("");
      $(".timeDep_chart").html("");
      $("#selected_var").find(".active_pos").css("display","none");
      $(".loading_var").css("display","inline");
      var traj_id=Number($("#selectedTraj_id").text());
      $.ajax({
            type: "POST",
            url: "/covid19/ajax_variant_impact/", 
            dataType: "json",
            data: { 
              "dyn_id": dyn_id,
              "traj_id": traj_id,
              "position": varpos,
              "delta":delta,
            },
          success: function(out_data) {
            var_input_res=out_data.result;
            $(".var_impact_score_slider_time_dependent").removeAttr("disabled");
            //var some_contact_found=false;

            $(".timeDep_chart").each(function(){
                var myselector=$(this);
                var data_type=myselector.data("type").toLowerCase();
                if (data_type in var_input_res){
                    var var_impact_time_all= var_input_res[data_type];
                    var var_impact_time_res=var_impact_time_all["result"]

                    //var res_average=var_impact_time_all["average"]
                    //var res_sd=var_impact_time_all["sd"]

                    var var_name=var_impact_time_res[0][1];
                    if (var_name in var_measurements_abbr){
                        var_name=var_measurements_abbr[var_name];
                    } else {
                        var_name=var_name.replace("_"," ");
                        var_name=capitalizeFirstLetter(var_name);                        
                    }
                    var_impact_time_res[0][1]=var_name;
                    google.load("visualization", "1", {packages:["corechart"],'callback': function(){ drawChartVarImpactTime(var_impact_time_res,myselector,data_type,varpos,dyn_id) }});
                    myselector.data("result_values",var_impact_time_res)

                    /*if (data_type.startsWith("contact_")){
                        some_contact_found=true;
                    } */
                } else {
                    var error_html='<div class="alert alert-warning alert-dismissible">\
                                <a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>\
                                Results for this position are not available.\
                              </div>';
                    myselector.append(error_html)
                    //if (! data_type.startsWith("contact_")){
                    var slider_el=$(".td_slider_analysis_mut_"+data_type);
                    disable_slider(slider_el);
                }
                update_average_sd_data(traj_id,protname,varpos,data_type)

            })
            //update impsct score table
            /*if (! some_contact_found){
                var slider_el=$("#td_slider_analysis_contnum");
                disable_slider(slider_el);
            }*/
            //Apply selected param. weights
            var active_defaut_weights=$(".imp_score_fitted_weights.active");
            if (active_defaut_weights.length>0){
                param_weights=active_defaut_weights.data("param_weights");
                apply_default_weights_all(param_weights);
            }
            obtain_impact_score();
          },
          error: function() {
              var error_html='<div class="alert alert-warning alert-dismissible">\
                                <a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>\
                                An error ocurred and the variant impact results could not be updated according to the selected position.\
                              </div>';
              $("#variant_impact_errors").html(error_html)
          }, complete: function(){
            $(".loading_var").css("display","none");
            $("#selected_var").find(".active_pos").css("display","inline");
          },
          timeout: 600000
      });
    }

    triggerUpdateTimedependentData = function(){
        var thisvarname= $(".selected_var_name").html();
        //var protname=$(".seq_sel.hasvariants.selected").data("protein_name");//
        var protname=get_active_protein_name();
        var residsel=$(".var_impact_selected_resid").html()
        if (protname && residsel){
            obtain_timedependent_data(protname,residsel);
        }
    }
    window.triggerUpdateTimedependentData=triggerUpdateTimedependentData;

    function new_variant_update_html(varname,seq_id,resid,chain,protname){
        $(".var_impact_selected_resseq").text(seq_id);
        $(".var_impact_selected_resid").text(resid);
        $(".var_impact_selected_chain").text(chain);
        $(".var_impact_selected_varname").text(varname);
        $(".var_impact_selected_protname").text(protname);
        $(".var_impact_selected_none").css("display","none");
        $(".var_impact_selected").css("display","inline");
        $("#var_impact_score_common_section").css("display","block");

    }

//    function createDivAtStrClick(d, divid, myhtml) {
//        var mouse_pos=d.canvasPosition;
//        var x_pos= mouse_pos["x"];
//        var y_pos=mouse_pos["y"]
//        var max_h_s=$("#viewport").css("height");
//        var max_h=Number(max_h_s.replace("px",""))
//        var y_pos_mod=max_h - y_pos 
//
//        myhtml=myhtml.replace(/\*\*x_pos\*\*/,x_pos);
//        myhtml=myhtml.replace(/\*\*y_pos\*\*/,y_pos_mod);                
//        $(divid).html(myhtml);          
//
//    }

    // new2
    $("#seq_w_variants").on("click",".seq_sel.hasvariants.activeseqpos", function(){
    // end new2
        var var_info=$(this).data("varinfo");
        var topd=$(this)[0].offsetTop - $("#seq_w_variants").scrollTop();
        var leftd=$(this)[0].offsetLeft + 25;
        var thispos_id=$(this).attr("id");
        $(this).siblings().removeClass("clicked");
        $(this).addClass("clicked");


        var myhtml_opt="";
        for (varname in var_info){
            var model_sel=var_info[varname]["model_sel"];
            myhtml_opt+= "<p><button class='btn btn-default btn-xs seq_sel_var_btn' data-select='"+model_sel+"' >"+varname+"</button></p>";
        }
        control_var_impact_reps(model_sel,"var_impact_seq",true)

        var myhtml="<div id='seq_sel_var_opt' class='seq_sel_var_set' data-parentpos_id='"+thispos_id+"' style='left:"+leftd+"px;top:"+topd+"px'>\
        <span class='glyphicon glyphicon-remove close_var_mut close_cross' ></span>\
        <div >\
        "+myhtml_opt+"\
        </div>";
        $("#seq_sel_var_add").html(myhtml)


        $(document).on("mouseup",function(e) {
            var container = $("#seq_sel_var_opt");
            // if the target of the click isn't the container nor a descendant of the container
            var close_btn= $("#seq_sel_var_add").find(".close_var_mut");
            if (close_btn.length > 0){
                if ((!container.is(e.target) && container.has(e.target).length === 0) || close_btn.is(e.target)) {

                    var other_seq_pos=$(".seq_sel.hasvariants");
                    if (!other_seq_pos.is(e.target) && other_seq_pos.has(e.target).length === 0)  {
                        var parentpos_id=close_btn.parent(".seq_sel_var_set").data("parentpos_id");
                        $("#"+parentpos_id).removeClass("clicked");
                        ngliframe.manageNGLReps("var_impact_seq",false);
                    }
                    $("#seq_sel_var_opt").remove();

                }
            }
        });

    })

    function update_seq_varinfo(sel_var_data,is_allmuts){
        $("#seq_w_variants").find(".seq_sel.hasvariants").each(function(){
            var var_prot=$(this).data("protein_name");
            var newvarinfo="";
            if (var_prot in sel_var_data){
                var var_pos=Number($(this).children(".seq_sel_pos_seqpos").text());
                var prot_data=sel_var_data[var_prot];
                if (var_pos in prot_data){
                    if (is_allmuts){
                        newvarinfo=prot_data[var_pos]["pos_variants"];
                    } else {
                        $(this).addClass("activeseqpos");
                        newvarinfo=prot_data[var_pos]
                    }
                }

            }
            $(this).data("varinfo",newvarinfo)
            //JSON.stringify
        })

    }

    // new!



    function update_isolate(thisval){
        if (thisval=="ALL"){ // show all
            update_seq_varinfo(finpseq_to_model,true);
            $(".seq_sel.hasvariants").addClass("activeseqpos");
            //var protein_name=$(".seq_sel.selected").data("protein_name");
            var protein_name=get_active_protein_name();
            color_html_seq(posColorMap,protein_name);
        } else {
            $("#loading_isolates").css("display","inline");
            var muts_in_iso={}
            $.ajax({
                  type: "POST",
                  url: "/covid19/ajax_muts_in_isolate/", 
                  dataType: "json",
                  data: { 
                    "dyn_id": dyn_id,
                    "isolate": thisval,
                  },
                success: function(out_data) {
                    muts_in_iso=out_data.result;
                    var some_mut_in_struc=out_data.some_mut_in_struc;
                    if (! some_mut_in_struc){
                        $("#no_muts_in_struc").css("display","block");
                    }
                },
                error: function() {
                    muts_in_iso={}
                }, complete: function(){
                    $(".seq_sel.hasvariants").removeClass("activeseqpos");
                    update_seq_varinfo(muts_in_iso,false);
                    //var protein_name=$(".seq_sel.selected").data("protein_name");
                    var protein_name=get_active_protein_name();
                    color_html_seq(posColorMap,protein_name);
                    $("#loading_isolates").css("display","none");
                },
                timeout: 600000
            });

        } 
    }



    $( "#select_isolate" ).autocomplete({  
        //source: "/covid19/"+dyn_id+"/",
        source: function(request,response){
                $("#loading_isolates").css("display","inline");
                $.ajax({
                    url: "/covid19/ajax_autocomp_isolates/",
                    type:"GET",
                    dataType:"json",
                    data:{
                        search: request.term,
                        prots: included_prots.join(),
                       // dyn_id: dyn_id

                    },  
                    success:function(data){
                        response(data);
                    },
                    complete: function(){
                        $("#loading_isolates").css("display","none");
                    }
                })
        },
        open: function(){
            setTimeout(function () {
                $('.ui-autocomplete').css('z-index', 99);
            }, 0);
        }
    });  

/*
    $( "#select_isolate" ).autocomplete({  
        source: "/covid19/"+dyn_id+"/",
        open: function(){
            setTimeout(function () {
                $('.ui-autocomplete').css('z-index', 99);
            }, 0);
        }
    });  */



    $( "#select_isolate" ).on( "autocompletesearch", function( event, ui ) {
        $(this).parent().removeClass("has-error");
        $(this).parent().removeClass("has-success");
    } );

    $( "#select_isolate" ).on( "autocompletechange", function( event, ui ) {
        var result=ui["item"];
        $("#no_muts_in_struc").css("display","none");
        if (result){
            var result_val=result["value"]
            $(this).parent().addClass("has-success");
            $("#select_isolate_res").text(result_val)
            update_isolate(result_val)

        } else {
            $(this).parent().addClass("has-error");
        }
    } );



    function control_var_impact_reps(selection,nglname, zoomtorep){
        var selection_cont="protein and ("+selection+")";
        ngliframe.manageNGLReps_changesele(nglname,selection_cont);
        if ($("#displayinview_var_impact").is(":checked")){
            ngliframe.manageNGLReps(nglname,true);
            if (zoomtorep){
                ngliframe.zoomtorep(nglname);
            }
        }
    }

    function get_aa_charge(myaa){
        var positive_aa=["D","E"];
        var negative_aa=["K","R","H"];
        charge=0;
        if (positive_aa.indexOf(myaa)>=0){
            charge=1;
        } else if (negative_aa.indexOf(myaa)>=0){
            charge=-1;
        }
        return charge;
    }

    function format_annotation(str){
      var start_link=str.indexOf("[");
      var info_text=str.slice(0,start_link);
      var link_data=str.slice(start_link);
      
      var end_ref=link_data.indexOf("]");
      var ref_data=link_data.slice(1,end_ref);
      var link_url=link_data.slice(end_ref+2,link_data.length-1);

      return info_text+" <a href='"+link_url+"' target='_blank'>"+ref_data+"</a>";

    }

    function compare_param_threshold(param_val,threshold,threshold_type){
        var is_relevant=false;
        if (threshold_type==">" && param_val>threshold){
            is_relevant=true;
        } else if ((threshold_type==">=" || threshold_type=="<=" || threshold_type=="=") && param_val==threshold){
            is_relevant=true;
        } else if (threshold_type=="<" && param_val<threshold){
            is_relevant=true;
        }
        return is_relevant
    }

    function update_impact_param_val(myselector,param_res,isnull){
        var param_cont=$("body").find(myselector)
        if (isnull){
            param_cont.html("-");
            param_cont.data("res_value",false);
        } else {
            param_cont.html(fix_float_to_n_nonzero(param_res,3,3,10));
            param_cont.data("res_value",param_res);
        }

    }

    function disable_slider(this_slider){
        this_slider.val(0);
        this_slider.removeClass("active_impact_param");
        this_slider.attr("disabled",true);
        $(this_slider.data("value_target")).html(0)

    }

    function set_slider_val(this_slider,new_val){
        new_val=fix_float_to_n_nonzero(new_val,1,1,3);
        this_slider.val(new_val);
        $(this_slider.data("value_target")).html(new_val); //Show value in html
        if (Math.abs(new_val)>0){
            this_slider.addClass("active_impact_param");
        } else {
            this_slider.removeClass("active_impact_param");
        }
    }

    function update_mutation_effect(impact_per_var_all,thisvarinfo,protname){
        var thisvarname=thisvarinfo["mut_name"];
        var resid_finprot=thisvarinfo["resid_finprot"];
        $("#analysis_variant_impact").find(".var_impact_score_slider_mutimpact").removeAttr("disabled");
        var missing_var_data=false;
        if (impact_per_var_all){
            var traj_id=Number($("#selectedTraj_id").text());
            var var_protdata=impact_per_var_all[traj_id][protname];
            var resid_finprot_n= Number(resid_finprot);
            if (resid_finprot_n in var_protdata){
                var var_posdata=var_protdata[resid_finprot_n]["variants"];  
                if (thisvarname in var_posdata){
                    var var_imp_data=var_posdata[thisvarname];
                    for (var_type_id in var_imp_data){
                        if (var_type_id=="mutfunc"){ //Data from mutfunc
                            for (mtf_param in var_imp_data["mutfunc"]){
                                var param_val = var_imp_data["mutfunc"][mtf_param]

                                //Ontain selector for this data
                                var selector_formatted="#variant_mutfunc_"+mtf_param;

                                if (mtf_param=="template"){
                                    //Modify tooltip details to indicate template
                                    if (! param_val){
                                        param_val="-";
                                    }
                                    $(".imp_score_me_table .mod_tooltip").each(function(){
                                        tooltip_text=$(this).data("title");
                                        var span_i=tooltip_text.lastIndexOf(">");
                                        mod_tooltip_text=tooltip_text.slice(0,span_i+1)+param_val+tooltip_text.slice(span_i+1);
                                        $(this).data("title",mod_tooltip_text)
                                    })
                                } else if (mtf_param=="ptm"){
                                    if (param_val){
                                        var param_impact=1;
                                    } else {
                                        param_val="-";
                                        var param_impact=0;
                                    }
                                    var param_cont=$(selector_formatted);
                                    param_cont.html(param_val);
                                    param_cont.data("res_value",param_impact);
                                } else {
                                    //Display data
                                    if (param_val || param_val==0){
                                        if (mtf_param=="annotation"){
                                            var ann_li=param_val.split(";");
                                            if (ann_li.length > 1){
                                                var annotation_html="<ul>";
                                                for (var i=0;i<ann_li.length;i++){
                                                    var ann_str_pre=ann_li[i];
                                                    var ann_str=format_annotation(ann_str_pre)
                                                    annotation_html+="<li>"+ann_str+"</li>";
                                                }
                                                annotation_html+="</ul>";
                                            } else {
                                                var ann_str_pre=ann_li[0];
                                                var ann_str=format_annotation(ann_str_pre)
                                                var annotation_html=ann_str;
                                            }
                                            param_val=annotation_html;
                                        }

                                        var relevant_vals_li=$(selector_formatted).data("relevant_vals");
                                        var relevance_mark="";
                                        if (relevant_vals_li){
                                            for (var i=0;i<relevant_vals_li.length;i++){
                                                var relevant_vals_i=relevant_vals_li[i]
                                                is_relevant=compare_param_threshold(param_val,relevant_vals_i["threshold"],relevant_vals_i["threshold_type"])
                                                if (is_relevant){
                                                    var rel_text=relevant_vals_i["text"];
                                                    relevance_mark='<span class="glyphicon glyphicon-exclamation-sign showtooltip_extra" style="color:#ff7b25;padding-left:5px;top:2px" data-toggle="tooltip" data-title="'+rel_text+'"></span>';
                                                }
                                            }
                                        }
                                        update_impact_param_val(selector_formatted,param_val,false);

                                        $(selector_formatted+"_warn").html(relevance_mark);
                                    } else {
                                        var slider_el=$("#me_slider_variant_mutfunc_"+mtf_param);
                                        disable_slider(slider_el);
                                        update_impact_param_val(selector_formatted,false,true);

                                    }

                                }
                            } 
                        } else if (var_type_id=="hydrophobicity") {
                            var hp_param=$("#variant_dhydro_options").val();
                            var this_mutimp_res = var_imp_data["hydrophobicity"][hp_param];
                            var meparam_cont_sel="#variant_dhydro";
                            if (this_mutimp_res || this_mutimp_res==0){
                                update_impact_param_val(meparam_cont_sel,this_mutimp_res,false);

                            } else {
                                var slider_el=$("#me_slider_variant_dhydro");
                                disable_slider(slider_el);
                                update_impact_param_val(meparam_cont_sel,false,true);
                            }
                        } else {
                            var this_mutimp_res=var_imp_data[var_type_id];
                            var meparam_cont_sel="#"+var_type_id;
                            if (this_mutimp_res || this_mutimp_res==0){
                                update_impact_param_val(meparam_cont_sel,this_mutimp_res,false);

                            } else {
                                var slider_el=$("#me_slider_"+var_type_id);
                                disable_slider(slider_el);
                                update_impact_param_val(meparam_cont_sel,false,true);
                            }
                        }
                    }
                } else {
                    missing_var_data=true;
                }
            } else {
                missing_var_data=true;
            }
        } else {
            missing_var_data=true;
        }
        if (missing_var_data){
            update_impact_param_val(".mut_effect_res_data",false,true);
            $("#analysis_variant_impact").find(".var_impact_score_slider_mutimpact").each(function(){
                var slider_el=$(this);
                disable_slider(slider_el);
            })
        }

    }
                       
    function drawScoresPerVariantHisto(selector_id,score_values,selected_var_score,quartiles_traj_data,is_time_dependent,protein_name){

        var datatoplot = google.visualization.arrayToDataTable(score_values,false);
        var options = {
            "title":"Histogram of impact score over all variants",
            "height":350, "width":620, "legend":{"position":"none"}, 
            "chartArea":{"right":"130","left":"70","top":"50","bottom":"60"},
            hAxis: {title: "Score",slantedText:true, slantedTextAngle:45},vAxis: {title: "Occurrences"},
            colors:["#3366CC"],
            histogram: { lastBucketPercentile: 5 },
          tooltip: {isHtml: true}
        };
        
        var chart = new google.visualization.Histogram(document.getElementById(selector_id));

        
        chart.draw(datatoplot, options);   

        var selector_tag="#"+selector_id;
        var score_line_style="stroke:rgb(0,0,0); stroke-width:3;";
        d3.select(selector_tag + " svg")
            .append('line') 
            .attr('id', 'lineId')
            .attr("class","protscoretooltip")
            .attr('style', score_line_style)
            .attr('x1', chart.getChartLayoutInterface().getXLocation(selected_var_score))
            .attr('y1', chart.getChartLayoutInterface().getChartAreaBoundingBox().top)
            .attr('x2', chart.getChartLayoutInterface().getXLocation(selected_var_score))
            .attr('y2', chart.getChartLayoutInterface().getChartAreaBoundingBox().height + chart.getChartLayoutInterface().getChartAreaBoundingBox().top)
            .append("title")
              .append("text")
                      .text("Obtained score");
        var leg_container="#quartile_chart_common_extra_legend";
        d3.select(leg_container).selectAll("*").remove();
        if (typeof (quartiles_traj_data) == "object"){
            var sel_score_min=quartiles_traj_data[0];
            var sel_score_25=quartiles_traj_data[1];
            var sel_score_50=quartiles_traj_data[2];
            var sel_score_75=quartiles_traj_data[3];
            var sel_score_max=quartiles_traj_data[4];

            var stroke_color="#166956";
            var stroke_width=2;
            var fill_color="#8FBCB2";
            var box_location=d3.select(selector_tag + " svg g g g");
            //Q1 to med
            add_svg_box(chart,box_location,sel_score_25,sel_score_50,stroke_color,stroke_width,fill_color)
            //Med to Q3
            add_svg_box(chart,box_location,sel_score_50,sel_score_75,stroke_color,stroke_width,fill_color)
            //Min and max line
            linestyle="stroke:"+stroke_color+"; stroke-width:"+stroke_width+";";
            add_svg_vertical_line(chart,box_location,sel_score_min,linestyle,"Minimum score of the selected variant in this trajectoriy")
            add_svg_vertical_line(chart,box_location,sel_score_max,linestyle,"Maximum score of the selected variant in this trajectoriy")
            //Horizontal lines from min to Q1 and Q3 to max
            add_svg_horizontal_line(chart,box_location,sel_score_min,sel_score_25,stroke_color,stroke_width)
            add_svg_horizontal_line(chart,box_location,sel_score_75,sel_score_max,stroke_color,stroke_width)

            add_svg_legend(leg_container,score_line_style,true,linestyle,stroke_color,stroke_width,fill_color);
        } else {
            add_svg_legend(leg_container,score_line_style,false,false,false,false,false);
        }



    }

    function drawQuartileChart(selector_id,score_values,selected_var_score){
      array=[score_values];

      array=[score_values];
      //var array = [         [ 100, 90, 110, 85, 96, 104, 120],       ];


      var data = new google.visualization.DataTable();
      
      for (var j=0;j<array[0].length;j++){

        data.addColumn('number', 'x'+j);
      }

      data.addColumn({id:'max', type:'number', role:'interval'});
      data.addColumn({id:'min', type:'number', role:'interval'});
      data.addColumn({id:'firstQuartile', type:'number', role:'interval'});
      data.addColumn({id:'median', type:'number', role:'interval'});
      data.addColumn({id:'thirdQuartile', type:'number', role:'interval'});
      data.addColumn({id:'this_score', type:'number', role:'interval'});

      data.addRows(getBoxPlotValues(array,selected_var_score));

      /**
       * Takes an array of input data and returns an
       * array of the input data with the box plot
       * interval data appended to each row.
       */
      function getBoxPlotValues(array,selected_var_score) {

        var c = array[0].length;
        for (var i = 0; i < array.length; i++) {
          var arr = array[i].slice(1).sort(function (a, b) {
            return a - b;
          });

          var max = arr[arr.length - 1];
          var min = arr[0];

          array[i][c] = max;
          array[i][c+1] = min
          array[i][c+2] = Quartile(arr, 0.25);//firstQuartile;
          array[i][c+3] = Quartile(arr, 0.5);//median;
          array[i][c+4] = Quartile(arr, 0.75);//thirdQuartile;
          array[i][c+5] = selected_var_score
        }
        return array;
      }

          function Quartile(data, q) {
  data=Array_Sort_Numbers(data);
  var pos = ((data.length) - 1) * q;
  var base = Math.floor(pos);
  var rest = pos - base;
  if( (data[base+1]!==undefined) ) {
    return data[base] + rest * (data[base+1] - data[base]);
  } else {
    return data[base];
  }
}

function Array_Sort_Numbers(inputarray){
  return inputarray.sort(function(a, b) {
    return a - b;
  });
}



      var options = {
          title:'Impact score over all protein residues',
          height: 500,
          legend: {position: 'none'},
          hAxis: {
            gridlines: {color: '#fff'}
          },
          lineWidth: 0,
          series: [{'color': '#D3362D'}],
          intervals: {
            barWidth: 1,
            boxWidth: 1,
            lineWidth: 2,
            style: 'boxes'
          },
          interval: {
            max: {
              style: 'bars',
              fillOpacity: 1,
              color: '#777'
            },
            min: {
              style: 'bars',
              fillOpacity: 1,
              color: '#777'
            },
            this_score: { 'style':'points', 'color':'#8B0000', 'pointSize': 10,
            'lineWidth': 0, 'fillOpacity': 1 }
          }
      };

      var chart = new google.visualization.LineChart(document.getElementById(selector_id));

      chart.draw(data, options);
    }


    var impact_per_var_all=$("#var_impact_data_effect").data("impact_per_var");
    var finpseq_to_model=$(".finpseq_to_model").data("finpseq_to_model");


    function trigger_new_variant_sel(thisvarname,my_selector,parentpos_id){
        var selected_var_info_box= $("#selected_var");
        selected_var_info_box.find(".default").css("display","none");
        selected_var_info_box.find(".selected_var_name").text(thisvarname);

        control_var_impact_reps(my_selector,"var_impact",false)

        var parentcont=$("#"+parentpos_id);

        parentcont.siblings().removeClass("selected");
        parentcont.addClass("selected");

        var thisvarinfo=parentcont.data("varinfo")[thisvarname];
        var protname=parentcont.data("protein_name")
        selected_var_info_box.find(".selected_prot_name").text(protname);
        var my_selector_sp=my_selector.split(":");
        var resid_finprot= thisvarinfo["resid_finprot"]
        var old_resid_finprot=selected_var_info_box.find(".selected_var_name").data("position");
        update_mutation_effect(impact_per_var_all,thisvarinfo,protname)

        new_variant_update_html(thisvarname,resid_finprot,my_selector_sp[0],my_selector_sp[1],protname)
        if (resid_finprot != old_resid_finprot){
            selected_var_info_box.find(".selected_var_name").data("position",resid_finprot);
            obtain_timedependent_data(protname,resid_finprot);
        } else {
            selected_var_info_box.find(".active_pos").css("display","inline");
            var active_defaut_weights=$(".imp_score_fitted_weights.active");
            if (active_defaut_weights.length>0){
                param_weights=active_defaut_weights.data("param_weights");
                apply_default_weights_all(param_weights);
            }
            obtain_impact_score();
        }

    }

    $("#seq_w_variants").on("click",".seq_sel_var_btn", function(){
        var thisvarname=$(this).text();
        var my_selector=$(this).data("select");
        var parentpos_id=$(this).parents(".seq_sel_var_set").data("parentpos_id");
        trigger_new_variant_sel(thisvarname,my_selector,parentpos_id);
    })    

    function obtain_dowbload_link(selected_params){
        var download_link="";
        var traj_id=Number($("#selectedTraj_id").text());;
        var protname=$(".seq_sel.hasvariants.selected").data("protein_name");
        var varname=$(".selected_var_name").html()
        var varpos=varname.slice(1,varname.length-1)
        //var download_link="/covid19/dwl/variantscores_traj/"+dyn_id+"/"+traj_id+"/"+protname+"/"+varpos+"/"+varname+"/"+parameters_me+"/"+"/"+parameters_td+"/";
        //-----------
        return download_link

    }

    function drawScoresPerFrameHisto(sum_dep_li,myselector){
        var datatoplot = google.visualization.arrayToDataTable(sum_dep_li,false);
        var options = {
            "title":"Histogram of impact score of the selected variant over trajectory frames",
            "height":350, "width":620, "legend":{"position":"none"}, 
            "chartArea":{"right":"10","left":"70","top":"50","bottom":"60"},
            hAxis: {title: "Score", slantedText:true, slantedTextAngle:45},vAxis: {title: "Occurrences"},
            colors:["#166956"]
        };

        //download_link=obtain_dowbload_link(selected_params)


        var plot_html="<div class='VarImpactScore_plot_cont' style='overflow:auto;overflow-y:hidden;'>\
                        <div class='VarImpactScore_plot' ></div>\
                        <div class='VarImpactScore_plot_settings' style='display:none'>\
                            <div class='plot_settings_btn_cont'>\
                                <a role='button' class='btn btn-link VarImpactScore_plot_saveImg ' href='#' target='_blank'>\
                                    <span  title='Save plot as image' class='glyphicon glyphicon-stats'></span>\
                                </a>\
                            </div>\
                        </div>\
                    </div>";

        myselector.append(plot_html);
        var plot_element_obj=myselector.find(".VarImpactScore_plot");
        var plot_element=plot_element_obj[0];
        
        //var chart0r = new google.visualization.LineChart(plot_element);    
        var chart = new google.visualization.Histogram(plot_element);

        
        var plot_img_source="#";
        google.visualization.events.addListener(chart, 'ready', function () {
            plot_img_source =  chart.getImageURI(); 
        });

        chart.draw(datatoplot, options);   
        myselector.find(".VarImpactScore_plot_saveImg").attr("href",plot_img_source);
            

    }

    function sortNumber(a,b) {
        return a - b;
    }

    function quantile(array, percentile) {
        array.sort(sortNumber);
        index = percentile/100. * (array.length-1);
        if (Math.floor(index) == index) {
          result = array[index];
        } else {
            i = Math.floor(index)
            fraction = index - i;
            result = array[i] + (array[i+1] - array[i]) * fraction;
        }
        return result;
    }



    $(".chart_with_hoversvg").on("mouseenter",".all_scores_dist_hover",function(){
      var thisbox=$(this);
      var displaysentence=thisbox.data("text");
      displaypopup(true,displaysentence,thisbox)
    })
    $(".chart_with_hoversvg").on("mouseleave",".all_scores_dist_hover",function(){
      displaypopup(false,false,false)
    })

    function add_svg_box(chart,box_location,box_min,box_max,stroke_color,stroke_width,fill_color){
        box_location
            .append('rect') 
            .attr('class','all_scores_dist_hover')
            .attr('data-text','Impact score values of the selected variant over trajectory frames')
            .attr('x',  chart.getChartLayoutInterface().getXLocation(box_min))
            .attr('y',  chart.getChartLayoutInterface().getChartAreaBoundingBox().top)
            .attr("width",chart.getChartLayoutInterface().getXLocation(box_max) - chart.getChartLayoutInterface().getXLocation(box_min))
            .attr("height",chart.getChartLayoutInterface().getChartAreaBoundingBox().height )
            .attr("fill",fill_color) 
            .attr("stroke",stroke_color) 
            .attr("stroke-width",stroke_width)
            .attr("opacity","0.5")
           

    }

    function add_svg_horizontal_line(chart,line_location,line_min,line_max,stroke_color,stroke_width){
        y_line_pos=chart.getChartLayoutInterface().getChartAreaBoundingBox().top+((chart.getChartLayoutInterface().getChartAreaBoundingBox().height)/2);
        line_location
            .append('rect') 
            .attr('x',  chart.getChartLayoutInterface().getXLocation(line_min))
            .attr('y',  y_line_pos)
            .attr("width",chart.getChartLayoutInterface().getXLocation(line_max) - chart.getChartLayoutInterface().getXLocation(line_min))
            .attr("height",1)
            .attr("fill","none") 
            .attr("stroke",stroke_color) 
            .attr("stroke-width",stroke_width)
            .attr("opacity","0.5")
            
    }

    function add_svg_vertical_line(chart,line_location,line_value,linestyle,displaysentence){
      line_location
          .append('line') 
          .attr('data-text',displaysentence)
          .attr("class","all_scores_dist_hover")
          .attr('style', linestyle)
          .attr('x1', chart.getChartLayoutInterface().getXLocation(line_value))
          .attr('y1', chart.getChartLayoutInterface().getChartAreaBoundingBox().top)
          .attr('x2', chart.getChartLayoutInterface().getXLocation(line_value))
          .attr('y2', chart.getChartLayoutInterface().getChartAreaBoundingBox().height + chart.getChartLayoutInterface().getChartAreaBoundingBox().top)

    }


    function  add_svg_legend(leg_container,score_line_style,add_boxp,linestyle,stroke_color,stroke_width,fill_color){
      var svg_leg = d3.select(leg_container)
        .append("svg")
          .attr("height", "100px")
          .attr("width", "120px")
          .attr("id", "svg_extra_legend")
        .append("g")
        //  .attr("transform", "translate(100,0)");  // bit of margin on the left = 40

      var leg_square_h=20;
      var x_dist=2;
      var y_dist=0;

      svg_leg
        .append('line') 
        .attr('style', score_line_style)
        .attr('x1', x_dist)
        .attr('y1', y_dist)
        .attr('x2', x_dist)
        .attr('y2', y_dist+leg_square_h);
      
      svg_leg
        .append("text")
        .attr("x", 7)
        .attr("y", y_dist+15)
        .attr("font-size",  "12px")
      //  .attr("dy", ".35em")
        .attr("text-anchor", "left")
        .style("alignment-baseline", "middle")
        .text("Obtained score");

      if (add_boxp){
          y_dist=30

          svg_leg
            .append('line') 
            .attr('style', linestyle)
            .attr('x1', x_dist)
            .attr('y1', y_dist)
            .attr('x2', x_dist)
            .attr('y2', y_dist+leg_square_h);
          
          svg_leg
            .append('rect') 
            .attr('x',  x_dist)
            .attr('y',  y_dist+leg_square_h/2)
            .attr("width",10)
            .attr("height",1)
            .attr("fill","none") 
            .attr("stroke",stroke_color) 
            .attr("stroke-width",stroke_width)
            .attr("opacity","0.5");
          x_dist+=10;

          svg_leg
            .append('rect') 
              .attr('x',  x_dist)
              .attr('y', y_dist)
              .attr("width",15)
              .attr("height",leg_square_h)
              .attr("fill",fill_color) 
              .attr("stroke",stroke_color) 
              .attr("stroke-width",stroke_width)
              .attr("opacity","0.5");
          x_dist+=15;
          svg_leg
            .append('rect') 
              .attr('y', y_dist)
              .attr('x',  x_dist)
              .attr("width",15)
              .attr("height",leg_square_h)
              .attr("fill",fill_color) 
              .attr("stroke",stroke_color) 
              .attr("stroke-width",stroke_width)
              .attr("opacity","0.5");       
          x_dist+=15;

          svg_leg
            .append('rect') 
            .attr('x',  x_dist)
            .attr('y', y_dist+ leg_square_h/2)
            .attr("width",10)
            .attr("height",1)
            .attr("fill","none") 
            .attr("stroke",stroke_color) 
            .attr("stroke-width",stroke_width)
            .attr("opacity","0.5");
          x_dist+=10;

          svg_leg
            .append('line') 
            .attr('style', linestyle)
            .attr('x1', x_dist)
            .attr('y1', y_dist)
            .attr('x2', x_dist)
            .attr('y2', y_dist+leg_square_h);

          svg_leg
            .append("text")
            .attr("x", 0)
            .attr("y",  y_dist+leg_square_h+15)
            .attr("font-size",  "12px")
          //  .attr("dy", ".35em")
            .attr("text-anchor", "left")
            .style("alignment-baseline", "middle")
            .append("tspan")
              .attr("x", 0)
              .text("Impact score values")
            .append("tspan")
              .attr("x", 0)
              .attr("dy", "1em")
              .text("of the selected variant")
            .append("tspan")
              .attr("x", 0)
              .attr("dy", "1em")
              .text("over trajectory frames");

      }
    }

    function displaypopup(appear,displaysentence,thisbox){
      if (appear){
        plotparent=thisbox.parents(".chart_popup_box_parent");
        $("#chart_popup_box").html("<p>"+displaysentence+"</p>")
        var leftpos=mouseX -  $(".chart_popup_box_parent").offset()["left"] + 60;
        var toppos=plotparent[0].offsetTop + (mouseY - plotparent.offset()["top"]) ;
        $("#chart_popup_box").css({"display":"inline",'left':leftpos,"top":toppos});

      } else {
        $("#chart_popup_box").css("display","none");
      }
    }

    function hslToHex(h, s, l) {
      l /= 100;
      const a = s * Math.min(l, 1 - l) / 100;
      const f = n => {
        const k = (n + h / 30) % 12;
        const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
        return Math.round(255 * color).toString(16).padStart(2, '0');  
      };
      return `#${f(0)}${f(8)}${f(4)}`;
    }



    function extract_min_max_dict(mydict){
        var minval=false;
        var maxval=false;
        for (k in mydict){
            var myval=mydict[k];
            if (minval===false && maxval===false){
                minval=myval;
                maxval=myval;
            } else {
                if (myval>maxval){
                    maxval=myval;
                }
                if (myval < minval){
                    minval=myval
                }
            }
        }
        return [minval,maxval]

    }

    function valueToColorHue(scale,myval){
       myval = Math.min(scale.max.value, Math.max(scale.min.value, myval));
       const range = scale.max.value - scale.min.value;
       const hueRange = scale.max.hue - scale.min.hue;
       const value =  (myval - scale.min.value) / range;
       const hue = scale.max.hue - hueRange * value;
       
       //return hslToHex(hue, 100, 60)
       return hue
    }

    function valueToColorLightness(scale,myval){
       var hue=207;
       myval = Math.min(scale.max.value, Math.max(scale.min.value, myval));
       const range = scale.max.value - scale.min.value;
       const ligRange = scale.max.lig - scale.min.lig;
       const value =  (myval - scale.min.value) / range;
       const lig = scale.max.lig - ligRange * value;
       
       return hslToHex(hue, 100, lig)
    }

    function generate_score_colormap(color_map_data){
        var minmax=extract_min_max_dict(color_map_data);
        var minval=minmax[0];
        var maxval=minmax[1];
        var scale = {
              min: {value: minval, hue: 120, lig: 20},
              max: {value: maxval, hue: 1, lig: 100}
            } 
        var posColorMap={}
        posColorMap["no_data"]={"background":"#e6e6e6","border":"#d9d9d9"};
        posColorMap["data"]={}
        for (protpos in color_map_data){
            var posval=color_map_data[protpos];
            if (isNaN(posval)){
                var back_color=posColorMap["no_data"]["background"];
                var border_color=posColorMap["no_data"]["border"];
            } else {
                var mycolor_hue=valueToColorHue(scale,posval);
                var back_color=hslToHex(mycolor_hue, 100, 60)
                var border_color=hslToHex(mycolor_hue, 100, 50)
                //var mycolor=
                //var mycolor=valueToColorLightness(scale,posval);
            }
            posColorMap["data"][protpos]={"background":back_color,"border":border_color};

        }
        return posColorMap;
    }

    function apply_background_border_seqpos(parentpos,background,border){
            parentpos.css("background-color",background);
            parentpos.children(".seq_sel_pos").css("border-color",border);
    }

    function color_html_seq(posColorMap,protein_name){
        var all_inactive=$(".seq_sel:not(.activeseqpos)");
        var all_active=$(".seq_sel.activeseqpos");
        if (posColorMap){
            apply_background_border_seqpos(all_inactive,"#ffffff","#EDEDED"); //All inactive are white
            apply_background_border_seqpos(all_active,posColorMap["no_data"]["background"],posColorMap["no_data"]["border"]); //All active are 1st set to color representing 'no data'
            for (protpos in posColorMap["data"]){ //All active with data are colored
                var poscolor=posColorMap["data"][protpos];
                var thispos_seq_sel=$(".seq_sel.activeseqpos.seq_prot_"+protein_name+".seq_pos_"+protpos);
                apply_background_border_seqpos(thispos_seq_sel,poscolor["background"],poscolor["border"]);

            }  
            $("#colormap_legend").css("display","block");
        } else {
            apply_background_border_seqpos(all_inactive,"#ffffff","#EDEDED");  //All inactive are white
            apply_background_border_seqpos(all_active,"#D9EDF7","#BCE8F1");  //All active are default (blue)
            $("#colormap_legend").css("display","none");
        }
    }

    function color_ngl_seq(posColorMap,protein_name){
        if (posColorMap && $("#displayinview_var_impact").is(":checked")){
            color_scheme=[];
            for (seqpos in finpseq_to_model[protein_name]){
                var posdata = finpseq_to_model[protein_name][seqpos];
                var modelpos=posdata["seqpos"];
                var chain = posdata["chain"];

                if (seqpos in posColorMap["data"]){
                    var poscolor=posColorMap["data"][seqpos]["background"];
                } else {
                    var poscolor='#ffffff';
                }
                color_scheme[color_scheme.length]= [poscolor, modelpos+":"+chain]
            }
            ngliframe.applyCustomColorScheme(color_scheme)
        } else {
            ngliframe.applyCustomColorScheme(false)
        }
    }

    var posColorMap=false;
    function color_prot_by_score(color_map_data,protein_name){
        posColorMap=generate_score_colormap(color_map_data);
        //Color sequence in html
        color_html_seq(posColorMap,protein_name)
        color_ngl_seq(posColorMap,protein_name)
    }

    function formatPervarData(score_values_d){
        var score_values=[["Position","Score"]];
        for (varname in score_values_d){
            var vardata=score_values_d[varname];
            if (vardata["has_data"]){ //we ignore variants without data - we won't wat no data to be counted as score=0
                varscore=vardata["dep_sum"] + vardata["indep_sum"];
                score_values[score_values.length]=[varname,varscore];
            }
        }
        return score_values
    }


    function get_active_protein_name(){
        var selected_pos=$(".seq_sel.selected");
        if (selected_pos.length<=0){ //If there is no selected pos in the sequence, use the 1st protein (protien of the 1st seq pos)
            selected_pos=$("#prot1_pos1");
        }
        var protein_name=selected_pos.data("protein_name");
        return protein_name
    }

    function create_plot_by_residue(selected_params,sum_nodep,sum_dep,sum_dep_li){
        var traj_id=Number($("#selectedTraj_id").text());
        var protein_name=get_active_protein_name()
        if (impact_per_var_all){
            var impact_per_pos= impact_per_var_all[traj_id][protein_name];
            var value_perpos_indep={};
            var value_perpos_dep={};

            var value_pervar={};

            var any_time_dep_general=false;
            for (finprot_pos in impact_per_pos){ //Loop over positions
                impact_pos_values=impact_per_pos[Number(finprot_pos)]

                var pos_sum_indep=0;
                var pos_sum_dep=0;

                var any_data_in_pos=false;
                var any_time_dep_inpos=false;

                for (var i=0;i<selected_params.length;i++){ // Loop over parameters
                    var param_info=selected_params[i];
                    var param_name=param_info["analysis_type"];
                    var param_weight=param_info["correction"];

                    var var_sum_indep=0;
                    var var_sum_dep=0;
                    var variant_withval_num=0;
                    for (varname in impact_pos_values["variants"]){ // Loop over variants
                        if (!( varname in value_pervar)){
                            value_pervar[varname]={
                                "dep_sum":0,
                                "indep_sum":0,
                                "has_data":false
                            };
                        }
                        if (param_info["is_time_dependent"]){
                            any_time_dep_inpos=true;
                            any_time_dep_general=true;
                            if (param_name in impact_pos_values["time_dep"]){
                                variant_withval_num+=1;
                                var param_data_type=param_info["data_type"];
                                var param_value=(impact_pos_values["time_dep"][param_name][param_data_type])*param_weight;
                                var_sum_dep+=param_value;//for the measure per position (color map)
                                value_pervar[varname]["dep_sum"]+=param_value; //for the measure per variant (histogram)
                                value_pervar[varname]["has_data"]=true;//for the measure per variant (histogram)
                            }
                        } else {
                            var impact_var_values=impact_pos_values["variants"][varname];
                            if (param_info["is_mutfunc"]){
                                var param_name_sh=param_name.replace("variant_mutfunc_","");
                                var param_value_pre=impact_var_values["mutfunc"][param_name_sh]
                                if (param_name_sh=="ptm"){
                                    if (param_value_pre){
                                        var param_value_pre=1;
                                    } else {
                                        var param_value_pre=0;
                                    }
                                }
                            } else if (param_info["is_hydrophobicity"]){
                                var param_value_pre=impact_var_values["hydrophobicity"][param_name];
                            } else {
                                var param_value_pre=impact_var_values[param_name];
                            }
                            if ((typeof param_value_pre =="number") &&  (!isNaN(param_value_pre))){
                                variant_withval_num+=1;
                                var param_value=(param_value_pre)*param_weight;
                                var_sum_indep+=param_value;//for the measure per position (color map)
                                value_pervar[varname]["indep_sum"]+=param_value; //for the measure per variant (histogram)
                                value_pervar[varname]["has_data"]=true;//for the measure per variant (histogram)
                            }
                        }
                    }//End loop per varant

                    if (variant_withval_num>0){ //if for this parameter there is any variant with data
                        any_data_in_pos=true;

                        var_sum_indep=var_sum_indep/variant_withval_num;
                        var_sum_dep=var_sum_dep/variant_withval_num;
                        pos_sum_indep+=var_sum_indep;
                        pos_sum_dep+=var_sum_dep;

                    }

                }// End loop per parameter

                if (any_data_in_pos){
                    if (any_time_dep_inpos){ //If some if the data is time-dependent
                        pos_sum_dep+=pos_sum_indep;
                    } 
                    value_perpos_indep[finprot_pos]=pos_sum_indep;
                    value_perpos_dep[finprot_pos]=pos_sum_dep;
                   
                }
            }
            var quartiles_traj_data=false;

            if (sum_dep_li){
                var alltrajvalues=[];
                for (var i=0;i<sum_dep_li.length; i++){
                    if (i >0){//Skip title
                        thisval=sum_dep_li[i][1];
                        alltrajvalues[alltrajvalues.length]=thisval;
                    }
                }
                var quartilles_dev=[0,25,50,75,100];
                quartiles_traj_data=[];
                for (var i=0;i<quartilles_dev.length;i++){
                    var quantile_val=quantile(alltrajvalues, quartilles_dev[i]);
                    quartiles_traj_data[quartiles_traj_data.length]=quantile_val;
                }

            }

    /*            if (any_time_dep_general){
                    google.load("visualization", "1", {packages:["corechart"],'callback': function(){ drawQuartileChart("quartile_chart_dep_sd", value_perpos_dep_sd,sum_dep_sd) }});
                    google.load("visualization", "1", {packages:["corechart"],'callback': function(){ drawQuartileChart("quartile_chart_dep_average", value_perpos_dep_average, sum_dep_average) }});
                    var color_map_data=value_perpos_dep_average;
                } else {
                    google.load("visualization", "1", {packages:["corechart"],'callback': function(){ drawQuartileChart("quartile_chart_indep", value_perpos_indep,sum_nodep) }});
                    var color_map_data=value_perpos_indep;
                }
    */
            if (any_time_dep_general){
                var color_map_data=value_perpos_dep;
                var selected_var_score=sum_dep;
                var is_time_dependent=true;

            } else {
                var color_map_data=value_perpos_indep;
                var selected_var_score=sum_nodep;
                var is_time_dependent=false;

            }
            var value_pervar_li=formatPervarData(value_pervar);
            
            var p_score_pos=get_position_score_allvariants(value_pervar_li,selected_var_score);

            google.load("visualization", "1", {packages:["corechart"],'callback': function(){ drawScoresPerVariantHisto("quartile_chart_common", value_pervar_li,selected_var_score,quartiles_traj_data,is_time_dependent,protein_name) }});

            color_prot_by_score(color_map_data,protein_name)

        }

    }

    function apply_default_weights_particular(param_weights,this_slider){
        var is_disabled=this_slider.attr("disabled");
        if (typeof is_disabled == "undefined" || is_disabled == false ){
            var slider_id=this_slider.attr("id");
            if (slider_id.startsWith("me_")){
                var param_shortname=slider_id.replace("me_slider_variant_","");
                if (param_shortname=="dhydro"){
                    var dhydro_type=$("#variant_dhydro_options").val()
                    param_shortname=dhydro_type.replace("variant_","");;

                }   
            } else {
                var splitted_id=slider_id.split("_");
                var data_type=splitted_id[2];//sd or average
                var contactref_ind=slider_id.indexOf("contact_");
                if (contactref_ind>=0){
                    var param=slider_id.slice(contactref_ind);
                } else {
                    var param=splitted_id.slice(-1)[0];
                }
               /*if (param=="contnum"){
                    var param_shortname=$("#var_impact_score_tdp").val()+"_"+data_type;
                } else {
                }*/
                var param_shortname=param+"_"+data_type;
            }
            if (param_shortname in param_weights){
                var param_w=param_weights[param_shortname];
            } else {
                var param_w=0;
            }
            set_slider_val(this_slider,param_w);
        }
    }

    function apply_default_weights_all(param_weights){
        $("#analysis_variant_impact").find(".var_impact_score_slider").each(function(){
            var this_slider=$(this);
            apply_default_weights_particular(param_weights,this_slider);
        })
    }

    
    function load_predef_weights(param_weights){
        if (!param_weights){
            var active_defaut_weights=$(".imp_score_fitted_weights.active");
            if (active_defaut_weights.length>0){
                param_weights=active_defaut_weights.data("param_weights");
                //apply_default_weights_all(param_weights);
            }
        }
        if (param_weights){
            apply_default_weights_all(param_weights);
        }
        obtain_impact_score();   
    }

    $(".imp_score_fitted_weights").click(function(){
        var is_active=$(this).hasClass("active");
        if (!is_active){
            $(".imp_score_fitted_weights.active").removeClass("active");
            $(this).addClass("active");
            var param_weights=$(this).data("param_weights");
            load_predef_weights(param_weights)
            //apply_default_weights_all(param_weights);
            //obtain_impact_score();            
        }

    })


    added_custom_descr= function(new_impact_per_var_all,added_metrics){
        $("#custom_metrics_tbl").html("");
        var table_head='<table class="table imp_score_me_table">\
                  <thead>\
                    <tr style="background-color:#f3f3f3">\
                      <th class="table_title" colspan="3">User-provided descriptors</th>\
                    </tr>\
                  </thead>\
                  <tbody>';

        var table_bottom='</tbody>\
                        </table>\
            <button class="btn btn-link var_impact_score_clear" style="color:#DC143C;" data-target_ref=".var_impact_score_slider_mutimpact_custom">Clear selection</button>';
        var middle_html="";
        for (cn=0;cn<added_metrics.length;cn++){
            var new_cmetric=added_metrics[cn];
            add_html='<tr>\
                    <td class="col-md-3" >\
                        <div class="slider_div">\
                          <input  id="me_slider_'+new_cmetric+'" class="slider var_impact_score_slider var_impact_score_slider_mutimpact var_impact_score_slider_mutimpact_custom"  value="0" min="-10" max="10" step="1" type="range" data-value_target="#me_slider_val_'+new_cmetric+'" data-param_ref="'+new_cmetric+'" data-is_mutfunc="false">\
                        </div>\
                        <div  id="me_slider_val_'+new_cmetric+'" class="slider_val me_slider_val">0</div>\
                    </td>\
                    <td class="col-md-5 table_param_name" >\
                        '+new_cmetric+'\
                    </td>\
                    <td class="col-md-4">\
                      <span id="'+new_cmetric+'" class="mut_effect_res mut_effect_res_data" data-relevant_vals="" data-res_value="" ></span><span id="'+new_cmetric+'_warn" class="mut_effect_res mut_effect_res_warn"></span>\
                    </td>\
                  </tr>'
            middle_html+=add_html;
        }
        var num_added=added_metrics.length;
        $("#num_params_cust_total").text(num_added)
        var final_html=table_head+middle_html+table_bottom;
        $("#custom_metrics_tbl").html(final_html);
        impact_per_var_all=new_impact_per_var_all;

        if ($(".seq_sel.selected").length >=1){
            trigger_update_mutation_effect()
        }
        obtain_impact_score()
    }
    window.added_custom_descr=added_custom_descr;

    function fix_float_to_n_nonzero(myfloat,lt1,bg1,bt1max){
        //Fixes floats so that we can see at least 3 difits. The max is at 10^(-9) where we cut anyway.
        var myresult=myfloat;
        if (Number(myfloat)){
            var strfl=myfloat.toString();
            if (! strfl.indexOf("e-")>=0){
                if (strfl.indexOf(".")>=0){//Is decimal number
                    var lc=strfl.split(".")[0];
                    var rc=strfl.split(".")[1];
                    if (Number(lc) > 0){
                        myresult= myfloat.toFixed(lt1);            
                    } else {
                        num_zeros=rc.match(/(^0*)/)[0].length ;
                        var fin_val=myfloat;
                        if (num_zeros<9){
                            var fix_to=num_zeros+bg1;
                        } else {
                            var fix_to=bt1max;

                        }
                        myresult= myfloat.toFixed(fix_to);            

                    }
                }
            }
        }
        return myresult;
    }

/*
    function obtain_impact_score(){ //Per position 
        var sum_dep=0;
        var sum_dep_li=false;
        var sum_dep_extra=0; //for time-dependent params. that are not obtained per frame i.e. RMSF
        var sum_nodep=0;
        var some_selected=false;
        var includes_time_dep=false;
        var selected_params=[];
        $(".var_impact_score_slider").each(function(){
            var correction= Number($(this).val());
            var is_mutfunc= $(this).data("is_mutfunc");
            var is_hydrophobicity=false;
            var analysis_ref=$(this).data("param_ref");
            var data_type=false;
            if (Math.abs(correction)>0){ //If it's 0 the param is not considered
                some_selected=true;
                var is_time_dependent=$(this).hasClass("time_dependent")
                if (is_time_dependent){
                    includes_time_dep=true;
                    if (analysis_ref=="analysis_contnum"){
                        var analysis_type=$("#var_impact_score_tdp").val();
                    } else {
                        var analysis_type=analysis_ref.replace("analysis_mut_","");
                    }

                    data_type=$(this).data("data_type");
                    var analysis_data=var_input_res[analysis_type];
                    var analysis_data_val=analysis_data[data_type]; //average or SD
                    sum_dep+=analysis_data_val*correction;

                    //create score as funciton of time for histogram. In the case of RMSF, since it's not per frame but per atom, we just sum the value to the per-frame values
                    if (analysis_type == "rmsf"){
                        sum_dep_extra+=analysis_data_val*correction ;
                    } else {
                        var analysis_res=analysis_data["result"];
                        if (sum_dep_li){
                            for (var i=0;i<sum_dep_li.length;i++){
                                var pointval_score=sum_dep_li[i][1];
                                if (typeof(pointval_score)=="number"){
                                    sum_dep_li[i][1]=pointval_score+(analysis_res[i][1]*correction);
                                }
                            }
                        } else {
                            sum_dep_li=[["Time (ns)","Score"]];
                            for (var i=0;i<analysis_res.length;i++){
                                var pointval=analysis_res[i];
                                if (typeof(pointval[1])=="number"){
                                    var toadd=[pointval[0],(pointval[1]*correction)];
                                    sum_dep_li[sum_dep_li.length]=toadd;
                                }
                            }
                        }
                    }

                } else {
                    if (analysis_ref == "variant_dhydro" ){
                        is_hydrophobicity=true;
                        var analysis_type=$("#"+analysis_ref+"_options").val();
                    } else {
                        var analysis_type=analysis_ref;
                    }
                    var analysis_val=Number($("#"+analysis_ref).data("res_value"));
                    sum_nodep+=analysis_val*correction;

                }
                var param_data={"analysis_type":analysis_type,"correction":correction,"is_time_dependent":is_time_dependent,"is_mutfunc":is_mutfunc, "is_hydrophobicity":is_hydrophobicity, "data_type":data_type}
                selected_params[selected_params.length]=param_data;

            }

        })
        chart_selector=$("#var_impact_score_chart_perframe");
        chart_selector.html("");
        if (some_selected){
            sum_dep+=sum_nodep; 
            $("#var_impact_score_common").text(fix_float_to_n_nonzero(sum_dep));
            if (includes_time_dep){
                $("#var_impact_score_w_tdp").css("display", "inline");
                //create histogram
                if (sum_dep_li){
                    for (var i=0;i<sum_dep_li.length;i++){//We need to incorporate rmsf (if clicked) and mutaiton effect params (if clicked)
                        var pointval_time=sum_dep_li[i][0];
                        var pointval_score=sum_dep_li[i][1];
                        if (typeof(pointval_score)=="number"){
                            fin_val=pointval_score + sum_dep_extra + sum_nodep;
                            sum_dep_li[i]=[pointval_time.toFixed(3),fin_val]
                        }
                    }    

                    google.load("visualization", "1", {packages:["corechart"],'callback': function(){ drawScoresPerFrameHisto(sum_dep_li,chart_selector) }});
                }
                
            } else {
                $("#var_impact_score_w_tdp").css("display", "none");
            }
            $("#var_impact_score_result").css("display", "inline");

            create_plot_by_residue(selected_params,sum_nodep,sum_dep,sum_dep_li)


        } else {
            $("#var_impact_score_result").css("display", "none");
            posColorMap=false;
            color_html_seq(false,false);
            color_ngl_seq(false,false)
        }
    }*/




    function get_val_position(array,myval){
        array.sort(sortNumber);

        if (myval < array[0]){
            return 0
        } else if (myval > array[array.length-1]){
            return 1
        } else {
            var tempt_index=array.indexOf(myval);
            if (tempt_index>=0){
                var index=tempt_index;
            } else {
                //find closest value in the list
                var previous=array[0];
                var closest_floor=false;
                for (var i=1;i<array.length;i++){
                    var array_el=array[i];
                    if (myval > previous && myval < array_el){
                        closest_floor=previous;
                        break
                    }
                    previous=array_el;
                }
                var closest_ceil=array_el;
                // obtain diff
                var diff_val_floor=myval-closest_floor;
                if (diff_val_floor==0){
                    var fraction=0;
                } else {
                    var fraction=(diff_val_floor)/(closest_ceil - closest_floor);
                }
                index = array.indexOf(closest_floor) +(array.indexOf(closest_ceil)-array.indexOf(closest_floor))*fraction

            }
            p=index/(array.length-1);
            return p

        }

    }

    function get_position_score_allvariants(value_pervar_li,selected_var_score){
        var value_pervar_li_f=[];
        for (var i=1;i<value_pervar_li.length;i++){
            value_pervar_li_f[value_pervar_li_f.length]=value_pervar_li[i][1];
        }
        var p_score_pos=get_val_position(value_pervar_li_f,selected_var_score);
        $("#var_impact_score_pval").html(fix_float_to_n_nonzero(p_score_pos,2,2,4));
        return p_score_pos;
    }


    function obtain_impact_score(){
        var sum_dep=0;
        var sum_dep_li=false;
        var sum_dep_extra=0; //for time-dependent params. that are not obtained per frame i.e. RMSF
        var sum_nodep=0;
        var some_selected=false;
        var includes_time_dep=false;
        var selected_params=[];
        var active_params_me=0;
        var active_params_td=0;
        var active_params_cust=0;
        $("#analysis_variant_impact").find(".var_impact_score_slider").each(function(){
            var correction= $($(this).data("value_target")).html();
            //var correction= Number($(this).val());
            var is_mutfunc= $(this).data("is_mutfunc");
            var is_hydrophobicity=false;
            var analysis_ref=$(this).data("param_ref");
            var data_type=false;
            if (Math.abs(correction)>0){ //If it's 0 the param is not considered
                some_selected=true;
                var is_time_dependent=$(this).hasClass("time_dependent")
                if (is_time_dependent){
                    includes_time_dep=true;
                    active_params_td+=1;
                    /*if (analysis_ref=="analysis_contnum"){
                        var analysis_type=$("#var_impact_score_tdp").val();
                    } else {
                    }*/
                    var analysis_type=analysis_ref.replace("analysis_mut_","");
                    data_type=$(this).data("data_type");
                    if (analysis_type in var_input_res){
                        var analysis_data=var_input_res[analysis_type];
                        var analysis_data_val=analysis_data[data_type]; //average or SD
                        sum_dep+=analysis_data_val*correction;

                        //create score as funciton of time for histogram. In the case of RMSF, since it's not per frame but per atom, we just sum the value to the per-frame values
                        if (analysis_type == "rmsf"){
                            sum_dep_extra+=analysis_data_val*correction ;
                        } else {
                            var analysis_res=analysis_data["result"];
                            if (sum_dep_li){
                                for (var i=0;i<sum_dep_li.length;i++){
                                    var pointval_score=sum_dep_li[i][1];
                                    if (typeof(pointval_score)=="number"){
                                        sum_dep_li[i][1]=pointval_score+(analysis_res[i][1]*correction);
                                    }
                                }
                            } else {
                                sum_dep_li=[["Time (ns)","Score"]];
                                for (var i=0;i<analysis_res.length;i++){
                                    var pointval=analysis_res[i];
                                    if (typeof(pointval[1])=="number"){
                                        var toadd=[pointval[0],(pointval[1]*correction)];
                                        sum_dep_li[sum_dep_li.length]=toadd;
                                    }
                                }
                            }
                        }

                    } /*else {
                        console.log(analysis_type)
                    }*/

                } else {
                    if( $(this).hasClass("var_impact_score_slider_mutimpact_custom")){
                        active_params_cust+=1;
                    } else {
                        active_params_me+=1;

                    }
                    if (analysis_ref == "variant_dhydro" ){
                        is_hydrophobicity=true;
                        var analysis_type=$("#"+analysis_ref+"_options").val();
                    } else {
                        var analysis_type=analysis_ref;
                    }
                    var analysis_val=Number($("#"+analysis_ref).data("res_value"));
                    sum_nodep+=analysis_val*correction;

                }
                var param_data={"analysis_type":analysis_type,"correction":correction,"is_time_dependent":is_time_dependent,"is_mutfunc":is_mutfunc, "is_hydrophobicity":is_hydrophobicity, "data_type":data_type}
                selected_params[selected_params.length]=param_data;

            }

        })
        //set badges with number of actve sliders
        $("#num_params_td").html(active_params_td);
        $("#num_params_me").html(active_params_me);
        $("#num_params_cust").html(active_params_cust);
        //prepare cart
        chart_selector=$("#var_impact_score_chart_perframe");
        chart_selector.html("");
        if (some_selected){
            sum_dep+=sum_nodep; 
            $("#var_impact_score_common").text(fix_float_to_n_nonzero(sum_dep,3,3,10));
            var has_perframe_data=false;
            if (includes_time_dep){
                //$("#var_impact_score_w_tdp").css("display", "inline");
                //create histogram
                if (sum_dep_li){
                    for (var i=0;i<sum_dep_li.length;i++){//We need to incorporate rmsf (if clicked) and mutaiton effect params (if clicked)
                        var pointval_time=sum_dep_li[i][0];
                        var pointval_score=sum_dep_li[i][1];
                        if (typeof(pointval_score)=="number"){
                            fin_val=pointval_score + sum_dep_extra + sum_nodep;
                            sum_dep_li[i]=[pointval_time.toFixed(3),fin_val]
                        }
                    }    
                    per_frame_data=sum_dep_li;
                    has_perframe_data=true;

                }
                
            }
            if (! has_perframe_data){
                var per_frame_data=[["Frame", "Score" ]];//,["x" ,sum_dep]
                var traj_id=Number($("#selectedTraj_id").text());
                var total_frames=trajidtoframenum[traj_id];
                for (var i = 0; i < total_frames; i++) {
                    per_frame_data.push([i.toString() ,sum_dep]);
                }

            }


            //$("#var_impact_score_w_tdp").css("display", "none");
            google.load("visualization", "1", {packages:["corechart"],'callback': function(){ drawScoresPerFrameHisto(per_frame_data,chart_selector) }});


            $(".show_if_impactscore_result").css("display", "block");
            $(".show_if_NO_impactscore_result").css("display", "none");
            

            create_plot_by_residue(selected_params,sum_nodep,sum_dep,sum_dep_li)


        } else {
            $(".show_if_impactscore_result").css("display", "none");
            $(".show_if_NO_impactscore_result").css("display", "inline");
            posColorMap=false;
            color_html_seq(false,false);
            color_ngl_seq(false,false)
        }
        var predef_score_selected=$(".imp_score_fitted_weights.active").length;
        if (predef_score_selected>0){
            $("#is_default_score").css("display","inline");
        } else {
            $("#is_default_score").css("display","none");
        }
    }

    $("#analysis_variant_impact").on('input','.var_impact_score_slider',function(){
        console.log("1",$(this).data("param_ref"))
        var new_val=Number($(this).val());
        $($(this).data("value_target")).html(new_val); //Show value in html
        if (Math.abs(new_val)>0){
            $(this).addClass("active_impact_param");
        } else {
            $(this).removeClass("active_impact_param");
        }
    });

    //$("#analysis_variant_impact").find(".var_impact_score_slider").change(function(){ 
    $("#analysis_variant_impact").on('change','.var_impact_score_slider',function(){
        console.log("----2",$(this).data("param_ref"))
        $(".imp_score_fitted_weights.active").removeClass("active");
        obtain_impact_score();
    })

    $("#analysis_variant_impact").on("click",".var_impact_score_clear", function(){

        var target_clear=$(this).data("target_ref");
        $(target_clear).each(function(){
            var this_slider=$(this);
            this_slider.val(0);
            $(this_slider.data("value_target")).html(0);
            this_slider.removeClass("active_impact_param");
        })
        $(".imp_score_fitted_weights.active").removeClass("active");
        obtain_impact_score();
    })

/*
    $("#var_impact_score_tdp").change(function(){ 
        var recompute_impact_score=false;
        $(this).parents("tr").find(".var_impact_score_slider").each(function(){
            var slider_val=$($(this).data("value_target")).html();
            if (Math.abs(slider_val)>0){  
                recompute_impact_score=true;
            }
        })
        if (recompute_impact_score){  
            obtain_impact_score();                        
        }
        //Update time-dep. parameter plot
        var thisval=$(this).val();
        var selector="#analysis_contnum_"+thisval;
        $(selector).siblings().css("display","none")
        $(selector).css("display","inline")
        //Update average and SD values from table
        var traj_id=Number($("#selectedTraj_id").text());
        var protname=$(".seq_sel.hasvariants.selected").data("protein_name");
        var varpos=Number($(".seq_sel.hasvariants.selected .seq_sel_pos_seqpos").html());
        update_average_sd_data(traj_id,protname,varpos,thisval);
    })
*/
    function trigger_update_mutation_effect(){
        var activevar=$(".seq_sel.hasvariants.selected");
        if (activevar.length >0){
            var thisvarname= $(".selected_var_name").html();
            var protname=activevar.data("protein_name");
            var thisvarinfo=activevar.data("varinfo")[thisvarname];
            update_mutation_effect(impact_per_var_all,thisvarinfo,protname);            
        }
    }

    $("#variant_dhydro_options").change(function(){ 
        //Update average and SD values from table
        trigger_update_mutation_effect()
        
        
        //If a predefined score is selected, update the slider val to that one
        var active_defaut_weights=$(".imp_score_fitted_weights.active");
        var update_impacr_scre=false;
        if (active_defaut_weights.length>0){
            param_weights=active_defaut_weights.data("param_weights");
            var hydroph_slider=$("#me_slider_variant_dhydro");
            apply_default_weights_particular(param_weights,hydroph_slider);
            update_impacr_scre=true;
        }
        var slider_val=Number($(this).parents("tr").find(".slider_val").html());
        if (Math.abs(slider_val)>0){  
            update_impacr_scre=true;
        }
    
        //Recompute impact score if necessary
        if (update_impacr_scre){
            obtain_impact_score();                        
        }
    })


// -------- Others------------


    saveNotShowWarningInCache = function(warning_type){
        $.ajax({
            type: "POST",
            url: "/covid19/ajax_notshow_warn/", 
            dataType: "json",
            data: { 
              "warning_type":warning_type
            },

            timeout: 600000
            
        });
    }
    window.saveNotShowWarningInCache=saveNotShowWarningInCache;




//-------- Trigger NGL comp creation --------
    trigger_def_page_funcitons=function(){
        var is_variantimpact_def=$("#analysis_variant_impact_opt").data("variantimpact_def");
        var var_score_loaded=false;
        if (is_variantimpact_def){
            var firstvarpos=$(".activeseqpos:first");
            if (firstvarpos){
                var pos_vars_d=firstvarpos.data("varinfo");
                if (pos_vars_d){
                    var_score_loaded=true;
                    var thisvarname=getDictKeys(pos_vars_d).sort()[0];
                    var my_selector= pos_vars_d[thisvarname]["model_sel"];
                    var parentpos_id=firstvarpos.attr("id");
                    trigger_new_variant_sel(thisvarname,my_selector,parentpos_id)
                }
            }
        }
        if (!var_score_loaded){ //when it's not example page, or example var didn't load correctly
            //control_var_impact_reps(my_selector,"var_impact",false)
            load_predef_weights(false);
        }

    }
    window.trigger_def_page_funcitons=trigger_def_page_funcitons;
    


    var isTriggered=true;
    window.isTriggered=isTriggered;
    
    $('body').on('iframeSet',function(){
        $('#embed_mdsrv')[0].contentWindow.$('body').trigger('iframeSetOk');
        //var screen_w = screen.width;    
        var cont_w_max=$("#alloptionsdiv").css("width");
        var cont_w_max_num=Number(cont_w_max.match(/^\d*/g)[0]);
        var cont_w_num=cont_w_max_num - 2;
        var cont_w = cont_w_num.toString() + "px";
        var cont_w_in= (cont_w_num - 2).toString() + "px";
        
        if ($("#flare-container").length && $("#analysis_fplot").hasClass("in")){
            var cont_h_num_pre=setFpNglSize(false);
//            var cont_h_num = cont_h_num_pre - 44;
            var cont_h_num = cont_h_num_pre - 8;
        } else {
            var screen_h=screen.height;
            var cont_h_num=Math.round(screen_h*0.40);
        }
        var cont_h=(cont_h_num).toString() +"px";
        var cont_h_iframe_num=cont_h_num+30;
        var cont_h_iframe=(cont_h_iframe_num).toString() +"px";
        var cont_h_loading_num=cont_h_num/2
        var cont_h_loading=(cont_h_loading_num).toString() +"px";
        $("#loading").find("img").css("margin-top",cont_h_loading)
        //var cont_h_viewport=(cont_h_num-25).toString() +"px";
        //....
        $("#dropdownAndIframe").css({"border" : "1px solid #F5F5F5" , "max-width": cont_w_max , "height":cont_h});
        $("#embed_mdsrv").css("width",cont_w).attr("width",cont_w).attr("height",cont_h_iframe);
        $("#legend_row").css("max-width",cont_w_max);
        $(".showWhenNGLLoad").css("visibility","visible");
       // $("#loading").html("");
        $('#embed_mdsrv')[0].contentWindow.$('body').trigger('createNGL', [ cont_w , cont_w_in , cont_h_num ]);

    });

} );


