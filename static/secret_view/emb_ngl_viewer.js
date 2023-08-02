$(document).ready(function(){
    $(".sel_input, .inputdist, .dist_from, .dist_to").val("");
    //$("#show_within").empty();
    // $("#rad_high").attr("checked",false).checkboxradio("refresh");
    // $("#rad_sel").attr("checked",true).checkboxradio("refresh");// CHECK IF WORKS, AND IF BOTH SEL AND HIGH ARE CHECKED OR ONLY SEL
    
    $('[data-toggle="popover"]').popover(); 

    //---------Avoid dropdown menu to retract at click
    $('.notretract').on("click", function(e){
        e.stopPropagation();
    });
    
    function drawBasic(rows,xlabel,ylabel) {
        var data = new google.visualization.DataTable();
        data.addColumn('number', xlabel);
        data.addColumn('number', ylabel);

        data.addRows(rows);
        var options = {
        hAxis: {
          title: xlabel
        },
        vAxis: {
          title: ylabel
        }
        };

        return [data,options];

    }

    function click_unclick(class_name){
        $("body").on("click",class_name,function(){
            pos_class=$(this).attr("class");
            if(pos_class.indexOf("active") > -1){
                $(this).removeClass("active");
            } else {
                $(this).addClass("active");
            }
            if ($(this).hasClass("ed_map_el")){
                $("#EDselectionDiv").trigger("click");
            } else {
                $("#selectionDiv").trigger("click");
            }
        });
    }
  
    $(".check_trigger_ngl").on("change",function(){
        var triggerreps=false;
        $("#text_input_all").find(".sel_input").each(function(){
            if ($(this).val()){
                triggerreps=true;
            }
        })
        if (triggerreps){
            $("#selectionDiv").trigger("click");
        }
    })

    $(".PolarDisplay").on("click", function(){ 
        $("#selectionDiv").trigger("click");
    })

    $(".WaterDistDisplay").on("click", function(){ 
        $("#selectionDiv").trigger("click");
    })

    $(".waterswithin").on("change", function(){
        $("#selectionDiv").trigger("click");
    })





    function uniq(a) {
        var seen = {};
        return a.filter(function(item) {
            return seen.hasOwnProperty(item) ? false : (seen[item] = true);
        });
    }
    
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

    $("body").find(".settingsB").hover(function(){
        $(this).css("color","black");
    },
    function(){
        $(this).css("color","#585858");
    });
    

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
    
/*    $(".traj_element").hover(function(){
        $(this).css("background-color","#f2f2f2");
    },
    function(){
        var selected=$(this).hasClass("tsel");
        if (selected){
            $(this).css("background-color","#FFF7F7");
        } else {
            $(this).css("background-color","#FFFFFF");
        }
    });
    

    $(".fp_display_element").hover(function(){
        $(this).css("background-color","#f2f2f2");
    },
    function(){
        var selected=$(this).hasClass("is_active");
        if (selected){
            $(this).css("background-color","#bfbfbf");
        } else {
            $(this).css("background-color","#FFFFFF");
        }
    });   */ 
    
    
    
    function arrayMin(arr) {
      return arr.reduce(function (p, v) {
        return ( p < v ? p : v );
      });
    }    


//-------- Obtain important data from template --------


    var struc = $(".str_file").data("struc_file");
    var dyn_id=$(".str_file").data("dyn_id");
    var delta=$(".str_file").data("delta");
    var mdsrv_url=$("#embed_mdsrv").data("mdsrv_url");
    var sel = "";
    var sel_enc = sel;
    var fpsegStr=$("#view_screen").data("seg_li");
    console.log(fpsegStr);
    var pg_framenum=0;
    var is_network_default=$("#view_screen").data("network_default")
    var is_ligprotint_default=$("#view_screen").data("ligprotint_default")
    var predef_int_data=$("#view_screen").data("predef_int_data");

    if (fpsegStr && (fpsegStr.indexOf(":") != -1) ){
        var fpsegli=fpsegStr.split(",");
        var fpsegStrTmpLi=[];
        for (segN=0; segN<fpsegli.length ;segN++ ){
            var segsel=fpsegli[segN];
            if (segsel){
                var segselPosChLi=segsel.split(/-|:/);
                var segFromPos= segselPosChLi[0];
                var segFromCh= segselPosChLi[1];
                var segToPos= segselPosChLi[2];
                var segToCh= segselPosChLi[3];
                if (segFromCh==segToCh){
                    var pos_range=segFromPos + "-" +segToPos+":"+segFromCh;
                    fpsegStrTmpLi.push(pos_range);
                } else {
                    var start=all_chains.indexOf(segFromCh);
                    var end=all_chains.indexOf(segToCh);
                    var middle_str="";
                    var considered_chains=all_chains.slice(start+1,end);
                    for (chain=0 ; chain < considered_chains.length ; chain++){
                        middle_str += "+:"+ considered_chains[chain];// "+" = " or "
                    }
                    var pos_range=segFromPos + "-:"+segFromCh + middle_str+ "+1-"+segToPos+":" +segToCh;
                    fpsegStrTmpLi.push(pos_range);
                }
                
            }
            else {
                fpsegStrTmpLi.push("");
            }
        }        
        fpsegStr=fpsegStrTmpLi.join(",");
    }
    window.fpsegStr=fpsegStr;

    var trajidtoframenum= $("#selectedTraj").data("trajidtoframenum");
      
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
            fpSelInt={};
            FpSelPos = {}
            if (fpfile_new){
                d3.json(fpfile_new, function(jsonData){
                    $("#flare-container").html("");
                    var fpsize=setFpNglSize(true);
                    if (is_network_default){
                        inter_btn=$("#fp_display_all");
                    } else {
                        inter_btn=$("#fp_display_inter");
                    }
                    var int_pairs=inter_btn.data("tag");
                    plot = createFlareplotCustom(fpsize, jsonData, "#flare-container" , int_pairs);
                    plot.setFrame(pg_framenum);
                    //setFPFrame(pg_framenum)
                    allEdges= plot.getEdges();
                    numfr = plot.getNumFrames();

                    if (is_network_default){ 
                        FPselectALLnodes();
                        $("#selectionDiv").trigger("click");
                    }

                    //$(".showIfTrajFP").css("display","inline");
                    FPTypeAvailUnavail(true);
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
                FpSelPos = {};
            }
        });
    }
    window.emptyFPsels=emptyFPsels;
   
    
    function obtainDicts(gpcr_pdb_dict){
        var all_gpcr_dicts={};
        var num_gpcrs=0;
        pdb_gpcrdb={}
        for (gpcr_id in gpcr_pdb_dict){
            var bw_dict={};
            var gpcrdb_dict={};
            for (gen_num in gpcr_pdb_dict[gpcr_id]) {
                split=gen_num.split(new RegExp('[\.x]','g'));
                bw = split[0]+"."+ split[1];
                db = split[0]+"x"+ split[2];
                var pdbppos=gpcr_pdb_dict[gpcr_id][gen_num];
                var pdbppos_s=pdbppos[0]+":"+pdbppos[1]
                bw_dict[bw]=pdbppos
                gpcrdb_dict[db]=pdbppos
                pdb_gpcrdb[pdbppos_s]=db
            }
            num_gpcrs++;
            all_gpcr_dicts[gpcr_id]={"combined_num":gpcr_pdb_dict[gpcr_id], "bw_num": bw_dict, "gpcrDB_num":gpcrdb_dict};
        }
        return [all_gpcr_dicts , num_gpcrs,pdb_gpcrdb];
    }
    
    $("#receptor").addClass("active");

    var chains_str =$("#receptor").attr("title");
    var all_chains_raw = $(".str_file").data("all_chains");
    var all_chains_raw_s=all_chains_raw.toString();
    var all_chains = all_chains_raw_s.split(",");

    var gpcr_pdb_dict = $(".gpcr_pdb").data("gpcr_pdb");
    var bw_dict,gpcrdb_dict,pdb_gpcrdb,gpcr_id_name,all_gpcr_dicts,num_gpcrs;
    if (gpcr_pdb_dict !="no"){
        gpcr_id_name=$("#cons_pos_box_all").data("gpcr_id_name");
        //gpcr_pdb_dict=JSON.parse(gpcr_pdb_dict);
        dicts_results=obtainDicts(gpcr_pdb_dict);
        all_gpcr_dicts=dicts_results[0];  
        num_gpcrs =dicts_results[1];
        pdb_gpcrdb=dicts_results[2];
    }
    window.pdb_gpcrdb=pdb_gpcrdb;
    


    function changeLastInputColor(colorcode,def_row){
        if (available_colors.indexOf(colorcode)>-1){//if colorcode in available_colors     
            if (def_row){
                selrow=def_row;
            } else {
                var selrow=$("#text_input_all").find(".text_input:last");
            }
            //var selColorCont=selrow.find(".dropcolor[data-color='"+colorcode+"']");
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


    function checkPosInGpcrNum(list_of_gnum){
        ///Given list of positions in GPCRdb num., checks if the GPCR(s) in the dynamics contains it. Returns a list containing the accepted positions.
        var sel_pos_li=[];
        for (i = 0; i < list_of_gnum.length; i++) {
            var gnum_pos = list_of_gnum[i];
            for (gpcr_id in all_gpcr_dicts){
                my_gpcr_dicts=all_gpcr_dicts[gpcr_id];
                gpcrdb_dict=my_gpcr_dicts["gpcrDB_num"];
                if (gpcrdb_dict[gnum_pos] != undefined){
                    sel_pos_li.push(gnum_pos);
                    continue;
                }
            }
        }
        return sel_pos_li
    }
    function createRepFromCrossGPCRpg(){
        var bind_domain=$("#VisualizationDiv").data("bind_domain");
        var presel_pos=$("#VisualizationDiv").data("presel_pos");
        var presel_pos_ary = undefined;
        var presel_pos_here=false;
        if (bind_domain  && presel_pos){
            var dom_pos_li=bind_domain.split(",");
            var sel_dom_pos_li=checkPosInGpcrNum(dom_pos_li)
            var sel_dom_pos_s="";
            for (dpi=0; dpi<sel_dom_pos_li.length;dpi++){
                sdom_pos=sel_dom_pos_li[dpi];
                if ((sel_dom_pos_s.length + sdom_pos.length)<100){
                    sel_dom_pos_s+=sdom_pos+",";
                } else {
                    sel_dom_pos_fin=sel_dom_pos_s.slice(0,-1);
                    $("#text_input_all").find(".sel_input:last").val(sel_dom_pos_fin);
                    changeLastInputColor("#3193ff",false);
                    $("#text_input_all").find(".ti_add_btn:last").trigger("click");
                    sel_dom_pos_s=sdom_pos+",";
                }
            }
            sel_dom_pos_fin=sel_dom_pos_s.slice(0,-1);
            $("#text_input_all").find(".sel_input:last").val(sel_dom_pos_fin);
            changeLastInputColor("#3193ff",false);

            //David here: some changes intrudeced to mark more than a residue at time
            presel_pos_ary = presel_pos.split("_");
            if (presel_pos_ary.length > 1){
                for (index in presel_pos_ary){
                    presel_pos = presel_pos_ary[index];
                    var presel_ok_li=checkPosInGpcrNum([presel_pos])
                    if (presel_ok_li.length > 0){
                        $("#text_input_all").find(".ti_add_btn:last").trigger("click");
                        $("#text_input_all").find(".sel_input:last").val(presel_pos);
                        $("#text_input_all").find(".text_input:last .high_type").val("ball+stick");
                        //$("#text_input_all").find(".text_input:last .high_scheme").val("uniform");
                        changeLastInputColor("#ff4c00",false);
                    }
                }
            }
            else {
                //Selected pos:
                var presel_ok_li=checkPosInGpcrNum([presel_pos])
                if (presel_ok_li.length > 0){
                    $("#text_input_all").find(".ti_add_btn:last").trigger("click");
                    $("#text_input_all").find(".sel_input:last").val(presel_pos);
                    $("#text_input_all").find(".text_input:last .high_type").val("ball+stick");
                    //$("#text_input_all").find(".text_input:last .high_scheme").val("uniform");
                    changeLastInputColor("#ff4c00",false);
                }
            }
            //$("#selectionDiv").trigger("click");
        }
    }
    
    var available_colors=[]
    var first_textinput=$("#text_input_all").find(".text_input:first");
    first_textinput.find(".dropcolor:not(.morecolors)").each(function(){
        var thiscolor=$(this).data("color");
        available_colors[available_colors.length]=thiscolor;
    });
    available_colors[available_colors.length]=first_textinput.find(".dropbtn").data("color");



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




//-------- Collapse Arrow
    $(".section_pan").click(function(){
        var target=$(this).attr("data-target");
        var upOrDown=$(target).attr("class");
        if(upOrDown.indexOf("in") > -1){
            var arrow=$(this).children(".arrow");
            arrow.removeClass("glyphicon-chevron-up");
            arrow.addClass("glyphicon-chevron-down");
        } else {
            var arrow=$(this).children(".arrow");
            arrow.removeClass("glyphicon-chevron-down");
            arrow.addClass("glyphicon-chevron-up");
            if (target=="#analysis_fplot"){
                if (plot){
                    setFPFrame(pg_framenum)
                }
            }
        }
    });
    
    $("#show_hide_info").click(function(){

        if ($("#more_info").attr("aria-expanded")=="true"){
            $("#show_hide_info_text").text("Help");
        } else {
            $("#show_hide_info_text").text("Hide");
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
    displayDropBtn("#seq_input_all",".dropbtn");
    displayDropBtn("#moreSettings",".dropbtn");
    displayDropBtn("#moreSettings_div",".dropbtn_opt");
    displayDropBtn("#ED2fofcColor",".dropbtn");
    displayDropBtn("#EDfofcColorPos",".dropbtn");
    displayDropBtn("#EDfofcColorNeg",".dropbtn");
    




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
    colorSel("#seq_input_all");
    colorSel("#ED2fofcColor");
    colorSel("#EDfofcColorPos");
    colorSel("#EDfofcColorNeg");

    

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
//-------- Text Input --------
    function retrieveRowCol(colSect){
        var dBtn = colSect.find(".dropbtn");
        if (dBtn.hasClass("morecolors")){
            lcolor=colSect.find(".input_dd_color").val();
            if (lcolor == ""){
                lcolor = "#FFFFFF";
            } else if (! /^#(?:[0-9a-fA-F]{3}){2}$/.test(lcolor)) {
                lcolor = "#FFFFFF";
                //$(this).find(".span_morecolors").addClass("has-error");
            }
        } else {
            var lcolor = dBtn.data("color");
        }
        return (lcolor);
    }
    
    function obtainTextInput(){
        var layer=[];
        var layer_row=[];
        customsel_hasOKval=false;
        $("#text_input_all").find(".text_input").each(function(){
            //$(this).find(".span_morecolors").removeClass("has-error");
            var rownum=$(this).attr("id");
            var pre_sel = $(this).find(".sel_input").val();
            sel_enc =inputText(gpcr_pdb_dict,pre_sel,rownum,"main",".ti_alert");
            if (sel_enc.length > 0){
                customsel_hasOKval=true;
                var ltype = $(this).find(".high_type").val();
                var lscheme = $(this).find(".high_scheme").val();
                var lcolor=retrieveRowCol($(this));
                layer[layer.length]=[sel_enc, ltype, lcolor,lscheme];
                layer_row[layer_row.length]=[sel_enc, ltype, lcolor,lscheme,rownum];
            }
        });
        
        $("#seq_input_all").find(".seq_input_row").each(function(){
            $(this).find(".span_morecolors").removeClass("has-error");
            var pre_sel = $(this).find(".seq_input").val();
            var rownum=$(this).attr("id");
            sel_enc =inputText(gpcr_pdb_dict,pre_sel,rownum,"main",".si_alert");
            if (sel_enc.length > 0){
                var ltype = $(this).find(".high_type").val();
                var lscheme = $(this).find(".high_scheme").val();
                var dBtn = $(this).find(".dropbtn");
                if (dBtn.hasClass("morecolors")){
                    lcolor=$(this).find(".input_dd_color").val();
                    if (lcolor == ""){
                        lcolor = "#FFFFFF";
                    } else if (! /^#(?:[0-9a-fA-F]{3}){2}$/.test(lcolor)) {
                        lcolor = "#FFFFFF";
                        $(this).find(".span_morecolors").addClass("has-error");
                    }
                } else {
                    var lcolor = dBtn.data("color");
                }
                layer[layer.length]=[sel_enc, ltype, lcolor,lscheme];
                layer_row[layer_row.length]=[sel_enc, ltype, lcolor,lscheme,rownum];
            }
        });
        return([layer,layer_row,customsel_hasOKval]);
    }
    


//-------- Control text inputs --------

    function maxInputLength(select, select2, maxlength){
        $(select).on('keyup blur',select2, function() {
            var val = $(this).val();
            if (val.length > maxlength) {
                $(this).val(val.slice(0, maxlength));
            }
        });
    }

    maxInputLength('.inputdist',"",6);
    maxInputLength('input.sel_input',"",100);
    maxInputLength('input.seq_input',"",100);
    maxInputLength('input.ed_input',"",100);
    maxInputLength('#rmsd_my_sel_sel',"",50);
    maxInputLength("#int_thr", "",4);
    maxInputLength(".inp_stride", "",4);
    maxInputLength(".sel_within", ".user_sel_input",40);
    maxInputLength(".maxinp8","",8);
    maxInputLength("#trajStep","",3);
    maxInputLength("#trajTimeOut","",6);


    function sorting_table(class_table){
        //Make an HTML table into sortable
        $('.'+class_table).DataTable({
           "columnDefs": [
                { "searchable": false, "targets": 4 } 
            ]
        });
    }


    function removeSpacesInInput(my_selector){
        $(my_selector).blur(function(){
            my_input=$(this).val().replace(/\s+/g, '');
            $(this).val(my_input);
         });
    }

    removeSpacesInInput("#rmsd_frame_1");
    removeSpacesInInput("#rmsd_frame_2");
    removeSpacesInInput("#rmsd_ref_frame");
    removeSpacesInInput("#int_thr");
    removeSpacesInInput(".inp_stride");
    removeSpacesInInput(".rvSpaces");

    function createNewTextInput(){
        if ($("#text_input_all").children().length < 20){
            var addFPschOpt="";
            if (fpsegStr){
                addFPschOpt='<option value="FPscheme">GPCR Helices</option>';
            }
        
            $("#text_input_all").find(".ti_add_btn").css("visibility","hidden");
            var row='<div  class="text_input" id="ti_row'+ti_i+'" style="margin-bottom:5px">\
                           <div  class="row">\
                              <div class="col-sm-10 ti_left" style="padding-right:3px;padding-left:3px"> \
                                <input type="text" value="" class="form-control sel_input nglCallChange" placeholder="Specify your selection" style="width:100%;background-color:#F8F8F8">\
                                <div class="pull-right" style="padding:0;margin:0;font-size:12px">\
                                     <div style="float:left;height:27px" >\
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
                                           <option value="hydrophobicity">Hydrophobicity</option>'+addFPschOpt+
                                        '</select>\
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
                              <div class="col-sm-2 radio" style="padding-right:0;padding-left:0;margin-top:7px;width:48px;text-align: center">\
                                    <button class="btn btn-link ti_rm_btn" style="color:#DC143C;font-size:20px;margin:0;padding:0;"><span class="glyphicon glyphicon-remove-sign"></span></button>\
                                    <button class="btn btn-link ti_add_btn" style="color:#57C857;font-size:20px;margin:0;padding:0"><span class="glyphicon glyphicon-plus-sign"></span></button>\
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
            last_input_row.removeClass("ed_input_rep ed_input_rep_GPCR ed_input_rep_otherprot ed_input_rep_sel");
            $(".ed_ligand").each(function(){
                var lig_nm=$(this).data("shortn");
                lig_nm=lig_sel_if_starts_num(lig_nm);
                var class_nm="ed_input_rep_lig_"+lig_nm;
                last_input_row.removeClass(class_nm)
            });
            changeLastInputColor("#00d215",last_input_row);

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
            $("#selectionDiv").trigger("click");
        }
    });


    $("#text_input_all").on("change",".high_scheme",function(){
        var repSch = $(this).val();
        if (repSch == "uniform" || repSch == "element"){
            $(this).closest(".text_input").find(".displaydrop").css("display","inline");
        } else {
            $(this).closest(".text_input").find(".displaydrop").css("display","none");
        }  
    });





    var si_i=1;
    $("#seq_input_all").on("click",".si_add_btn",function(){ 
        if ($("#seq_input_all").children().length < 20){
            var addFPschOpt="";
            if (fpsegStr){
                addFPschOpt='<option value="FPscheme">GPCR Helices</option>';
            }
        
            $("#seq_input_all").find(".si_add_btn").css("visibility","hidden");
            var row='<div  class="seq_input_row" id="si_row'+si_i+'" style="margin-bottom:5px">\
                           <div  class="row">\
                              <div class="col-sm-11 si_left" style="padding-right:3px;padding-left:3px"> \
	                            <input type="text" value="" class="form-control seq_input nglCallChange" placeholder="Specify your selection" style="width:100%;background-color:#F8F8F8">\
	                            <div class="pull-right" style="padding:0;margin:0;font-size:12px">\
	                                 <div style="float:left;height:27px" >\
                                        <select class="high_type nglCallChangeTI" name="high_type'+si_i+'" style="padding:0;font-size:12px;height:24px;margin: 3px 0 0 0">\
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
                                        <select class="high_scheme nglCallChangeTI" name="high_scheme'+si_i+'" style="padding:0;font-size:12px;width:90px;height:24px;margin: 3px 0 0 0">\
                                           <option value="element">Element</option>\
                                           <option value="uniform">Uniform</option>\
                                           <option value="chainid">Chain</option>\
                                           <option value="moleculetype">Molecule type</option>\
                                           <option value="sstruc">Structure</option>\
                                           <option value="resname">Residue name</option>\
                                           <option value="residueindex">Residue index</option>\
                                           <option value="hydrophobicity">Hydrophobicity</option>'+addFPschOpt+
                                        '</select>\
                                      </div>\
                                      <div class="dropdown displaydrop" style="float:left;height:27px;margin:3px 0 0 0;padding:0">\
                                        <button class="dropbtn" style="margin-top: 7px; margin-left: 3px;" data-color="#00d215"></button> \
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
                              <div class="col-sm-1 radio" style="padding-right:0;padding-left:0;margin-top:7px;width:48px;text-align: center">\
                                    <button class="btn btn-link si_rm_btn" style="color:#DC143C;font-size:20px;margin:0;padding:0;"><span class="glyphicon glyphicon-remove-sign"></span></button>\
                                    <button class="btn btn-link si_add_btn" style="color:#57C857;font-size:20px;margin:0;padding:0;visibility:hidden"><span class="glyphicon glyphicon-plus-sign"></span></button>\
                              </div>\
                          </div>\
                          <div class="si_alert"><div class="si_alert_gnum"></div><div class="si_alert_ngl"></div></div>\
                      </div>';

            $("#seq_input_all").append(row);
            si_i+=1;
        }
    });
    
    $("#seq_input_all").on("click", ".si_rm_btn" , function(){
        var inpval= $(this).closest(".seq_input_row").find(".seq_input").val();
        var numSiRows = $("#seq_input_all").children().length;
        if(numSiRows==1){
            var color_input=$("#seq_input_all").find(".input_dd_color");
            color_input.val("");
            color_input.css("background-color","");
            $("#seq_input_all").find(".span_morecolors").removeClass("has-error");
            $("#seq_input_all").css("display","none");
            $("#seq_input_all").find(".seq_input").val("");

            $("#seq_input_all").find(".si_alert_gnum").html("");
            $("#seq_input_all").find(".si_alert_ngl").html("");
            $("#seq_input_all").find(".seq_input").css("border-color","");
        }else{
            var wBlock =$(this).closest(".seq_input_row");
            if (wBlock.is(':last-child')){
                wBlock.remove();
                $("#seq_input_all").find(".si_add_btn:last").css("visibility","visible");
            } else {
                wBlock.remove();
            }
        }
        if (inpval != ""){
            $("#selectionDiv").trigger("click");
        }
    });


    $("#seq_input_all").on("change",".high_scheme",function(){
        var repSch = $(this).val();
        if (repSch == "uniform" || repSch == "element"){
            $(this).closest(".seq_input_row").find(".displaydrop").css("display","inline");
        } else {
            $(this).closest(".seq_input_row").find(".displaydrop").css("display","none");
        }  
    });





//-------- Parse input selection --------

  
    function encode (sth) {return encodeURIComponent(sth).replace(/%20/g,'+');}
    
    function obtainInputedGPCRnum(pre_sel){
        var gpcr = "((\\d{1,2}\\.\\d{1,2}(x\\d{2,3})?)|(\\d{1,2}x\\d{2,3}))";
        var re = new RegExp(gpcr,"g");
        var res = pre_sel.match(re); 
        return(res);
    }

    function obtainInputedGPCRrange(pre_sel) {
        var gpcr = "((\\d{1,2}\\.\\d{1,2}(x\\d{2,3})?)|(\\d{1,2}x\\d{2,3}))";
        var gpcr_range = gpcr + "\\s*\\-\\s*"+gpcr;
        var re = new RegExp(gpcr_range,"g");
        var res = pre_sel.match(re); 
        return(res);
    }

    function addErrorToInput(rowIndex,inpSource,alertComp,appOrSubst,text){
        if (inpSource == "main"){
            var to_add='<div class="alert alert-danger row" style = "margin-bottom:10px" ><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a><span class="error_text">'+text+'</span></div>';
            var textrow=$(rowIndex);
            textrow.find("input").css("border-color","#A94442");
        } else {
            to_add='<div class="alert alert-danger row" style = "padding:5px;font-size:12px;margin-top:3px;margin-bottom:10px;margin-left:14px;width:430px" ><a href="#" class="close" data-dismiss="alert" aria-label="close" style = "font-size:15px" >&times;</a><span class="error_text">'+text+'</span></div>';
            var textrow=$(".sel_within").find(rowIndex);
            inactivate_row(textrow,false);
            textrow.find(".user_sel_input").css("border-color","#A94442");
        }
        if (appOrSubst=="append"){
            textrow.find(alertComp).append(to_add);
        } else {
            textrow.find(alertComp).html(to_add);      
        }
    }
    
    var NGL_addErrorToInput=function(rowIndex){
        var to_add="Invalid selection.";
        addErrorToInput(rowIndex,"inp_wth",".alert_sel_wth_ngl","html",to_add);
    }
    window.NGL_addErrorToInput=NGL_addErrorToInput;

    function parseGPCRnum(sel,lonely_gpcrs,rownum,inpSource,alertSel){
        var add_or ="";
        if (num_gpcrs >1){
            add_or=" or ";
        }    
        for (i = 0; i < lonely_gpcrs.length; i++) {
            var my_gpcr = lonely_gpcrs[i];
            var subst_pos_all ="";
            for (gpcr_id in all_gpcr_dicts){
                var subst_pos ="";
                my_gpcr_dicts=all_gpcr_dicts[gpcr_id];
                gpcr_comb_dict=my_gpcr_dicts["combined_num"];
                bw_dict=my_gpcr_dicts["bw_num"];
                gpcrdb_dict=my_gpcr_dicts["gpcrDB_num"];
                
                if(gpcr_comb_dict[my_gpcr] != undefined) {
                    var res_chain=gpcr_comb_dict[my_gpcr];  
                } else if (bw_dict[my_gpcr] != undefined) {
                    var res_chain=bw_dict[my_gpcr];  
                } else if (gpcrdb_dict[my_gpcr] != undefined){
                    var res_chain=gpcrdb_dict[my_gpcr];                   
                } else {
                    res_chain=undefined;
                    if (inpSource=="main"){
                        var to_add_inside=my_gpcr+' not found at '+gpcr_id_name[gpcr_id]+'.';
                        addErrorToInput("#"+rownum,inpSource,alertSel+"_gnum","append",to_add_inside);
                    } else if (inpSource=="inp_wth") {
                        var to_add_inside=my_gpcr+' not found at '+gpcr_id_name[gpcr_id]+'.';
                        addErrorToInput("#"+rownum,inpSource,alertSel+"_gnum","append",to_add_inside);
                    }
                }
                if (res_chain){
                    subst_pos=" "+res_chain[0]+":"+res_chain[1];
                    subst_pos_all += subst_pos + add_or;
                }
            }
            if (subst_pos_all){
                if (num_gpcrs >1){
                    subst_pos_all=subst_pos_all.slice(0,-4);
                } 
                subst_pos_all="(protein and ("+subst_pos_all+"))";
                sel = sel.replace(my_gpcr ,subst_pos_all );
            } else {
                sel="";
            }
        }
        return (sel);
    }
    
    function parseGPCRrange(pre_sel,gpcr_ranges,rownum,inpSource,alertSel){
        var add_or ="";
        if (num_gpcrs >1){
            add_or=" or ";
        }    
        for (i=0 ; i < gpcr_ranges.length ; i++){
            var gpcr_pair_str = gpcr_ranges[i];
            var gpcr_pair=gpcr_pair_str.split(new RegExp('\\s*-\\s*','g'));
            var pos_range_all="";
            for (gpcr_id in all_gpcr_dicts){
                var pos_range="";
                my_gpcr_dicts=all_gpcr_dicts[gpcr_id];
                gpcr_comb_dict=my_gpcr_dicts["combined_num"];
                bw_dict=my_gpcr_dicts["bw_num"];
                gpcrdb_dict=my_gpcr_dicts["gpcrDB_num"];
                var chain_pair=[];
                var res_pair=[];
                for (n=0 ; n < gpcr_pair.length ; n++){
                    var gpcr_n=gpcr_pair[n];  
                    if(gpcr_comb_dict[gpcr_n] != undefined) {
                        var res_chain=gpcr_comb_dict[gpcr_n];  
                    } else if (bw_dict[gpcr_n] != undefined) {
                        var res_chain=bw_dict[gpcr_n];  
                    } else if (gpcrdb_dict[gpcr_n] != undefined){
                        var res_chain=gpcrdb_dict[gpcr_n];                   
                    } else {
                        res_chain=undefined;
                        chain_pair=false;
                        if (inpSource=="main"){
                            var to_add_inside=gpcr_pair_str+' not found at '+gpcr_id_name[gpcr_id]+'.';
                            addErrorToInput("#"+rownum,inpSource,alertSel+"_gnum","append",to_add_inside);

                        } else if (inpSource=="inp_wth") {
                            var to_add_inside=gpcr_pair_str+' not found at '+gpcr_id_name[gpcr_id]+'.';
                            addErrorToInput("#"+rownum,inpSource,alertSel+"_gnum","append",to_add_inside);
                        }
                        break;
                    }
                    res_pair[res_pair.length]=res_chain[0];
                    chain_pair[chain_pair.length]=res_chain[1];
                }
                if (chain_pair){
                    if (chain_pair[0]==chain_pair[1]){
                        pos_range=" ("+res_pair[0] + "-" +res_pair[1]+":"+chain_pair[0]+")";
                    } else {
                        start=all_chains.indexOf(chain_pair[0]);
                        end=all_chains.indexOf(chain_pair[1]);
                        var middle_str="";
                        considered_chains=all_chains.slice(start+1,end);
                        for (chain=0 ; chain < considered_chains.length ; chain++){
                            middle_str += " or :"+ considered_chains[chain];
                        }
                        pos_range=" ("+res_pair[0] + "-:"+chain_pair[0] + middle_str+ " or 1-"+res_pair[1]+":" +chain_pair[1]+")";
                    }
                    pos_range_all += pos_range + add_or; 
                }
            }//END FOR GPROT
        if (pos_range_all){
            if (num_gpcrs >1){
                pos_range_all=pos_range_all.slice(0,-4);
                pos_range_all="protein and ("+pos_range_all+")";
            }  else {
                pos_range_all="protein and "+pos_range_all;
            }
            pre_sel = pre_sel.replace(gpcr_pair_str, pos_range_all);
        } else {
            pre_sel="";
        }
        sel=pre_sel;
        }//END FOR GPCR RANGES
    return(sel);
    }    
    

    function inputText(gpcr_pdb_dict,pre_sel,rownum,inpSource,alertSel){
        if (inpSource=="main"){
            $("#"+rownum).find(alertSel+"_gnum").html("");
            $("#"+rownum).find(alertSel+"_ngl").html("");
            $("#"+rownum).find("input").css("border-color","");
        } 
        var gpcr_ranges=obtainInputedGPCRrange(pre_sel);
        if (gpcr_ranges == null){
            sel = pre_sel ;
        } else if (gpcr_pdb_dict=="no"){
            sel = "";
            if (inpSource=="main"){
                var to_add_inside="GPCR generic residue numbering is not supported for this stricture.";
                addErrorToInput("#"+rownum,inpSource,alertSel+"_gnum","append",to_add_inside);
            } else if (inpSource=="inp_wth"){
                var to_add_inside="GPCR generic residue numbering is not supported for this stricture.";
                addErrorToInput("#"+rownum,inpSource,alertSel+"_gnum","html",to_add_inside);
            }
        } else {
            sel=parseGPCRrange(pre_sel,gpcr_ranges,rownum,inpSource,alertSel);
        }
        var lonely_gpcrs=obtainInputedGPCRnum(sel);
        if (lonely_gpcrs != null){
            if (gpcr_pdb_dict=="no"){
                sel = "";
                if (inpSource=="main"){
                    var to_add_inside="GPCR generic residue numbering is not supported for this stricture.";
                    addErrorToInput("#"+rownum,inpSource,alertSel+"_gnum","append",to_add_inside);
                } else {
                    var to_add_inside="GPCR generic residue numbering is not supported for this stricture.";
                    addErrorToInput("#"+rownum,inpSource,alertSel+"_gnum","html",to_add_inside);                    
                }
            } else {
                sel=parseGPCRnum(sel,lonely_gpcrs,rownum,inpSource,alertSel);
            }
        }
        var sel_sp = sel.match(/(\s)+-(\s)+/g);
        if (sel_sp != null){ //Remove white spaces between "-" and nums
            for(i=0; i < sel_sp.length ; i++){
                var sp=sel_sp[i];
                sel=sel.replace(sp,"-");
            }
        }
        return sel;
    }



//-------- Text input modified signal --------

    $("#text_input_all").on("change" , ".sel_input", function(){
        /*var inp_row=$(this).parents(".text_input");
        var inp_row_alert=inp_row.find(".ti_alert")
        inp_row_alert.find(".ti_alert_gnum").html("");
        inp_row_alert.find(".ti_alert_ngl").html("");*/
        $("#selectionDiv").trigger("click");
    });

    $("#text_input_all").on("change" , ".nglCallChangeTI", function(){
        if ($(this).closest(".ti_left").children(".sel_input").val() !=""){
            $("#selectionDiv").trigger("click");
        }
    });
    
    $("#text_input_all").on("click" , ".nglCallClickTI", function(){
        if ($(this).closest(".ti_left").children(".sel_input").val() !=""){
            $("#selectionDiv").trigger("click");
        }
    });
    

    $("#seq_input_all").on("change" , ".seq_input", function(){
        $("#selectionDiv").trigger("click");
    });

    $("#seq_input_all").on("change" , ".nglCallChangeTI", function(){
        if ($(this).closest(".si_left").children(".seq_input").val() != ""){
            $("#selectionDiv").trigger("click");
        }
    });
    
    $("#seq_input_all").on("click" , ".nglCallClickTI", function(){
        if ($(this).closest(".si_left").children(".seq_input").val() !=""){
            $("#selectionDiv").trigger("click");
        }
    });


//-------- Selected molecules to display --------
    function clickRep (id, newRep, clicked) {
        if ( clicked == 1 ) {
            var index = $.inArray(newRep,rep);
            if (index == -1) {
                rep[rep.length]=newRep;
            }
            //url = url_orig + ("&sel=" + sel_enc + "&rep=" + encode(rep));
            $(id).addClass("active");
            return  2;
        } else {
            var index = $.inArray(newRep,rep);
            if (index > -1) {
                rep.splice(index, 1);
            }
            //url = url_orig + ("&sel=" + sel_enc + "&rep=" + encode(rep));
            $(id).removeClass("active");
            return  1;
        }
    }


    function obtainTMs(tmsel_section){
        var tm_show_li=[]
        if (tmsel_section=="em"){
            var tmcjqsel=".ed_tmsel.active";
        } else {
            var tmcjqsel=".tmsel.active";
        }
        $(tmcjqsel).each(function(){
            var sel_li=[];
            var tmsel=$(this).data("tmsel");
            for (id in tmsel){
                sel_li[sel_li.length]=tmsel[id];
            }
            var tm_show=sel_li.join(" or ");
            tm_show_li[tm_show_li.length]="("+tm_show+")";
        }); 
        if (tm_show_li){
            var tm_show_all=tm_show_li.join(" or ");
            tm_show_ok=inputText(gpcr_pdb_dict,tm_show_all,false,false,false);
        } else{
            tm_show_ok="";
        }    
        return tm_show_ok;
    }

    function obtainCompounds(){
        var shortTypeName={'Ligand':'lg','Lipid':'lp','Ions':'i','Water':'w','Other':'o'}
        var comp=[];
        var cp_req_load_heavy=false;
        $(".comp.active").each(function(){
            var ctype=$(this).data("comptype");
            comp[comp.length]=$(this).attr("id")+"_"+shortTypeName[ctype];
            if ($(this).hasClass("load_heavy")){
                cp_req_load_heavy=true;
            }
        });
        var tms_selstr=obtainTMs("qs");
        if (tms_selstr){
            comp[comp.length]=tms_selstr+"_"+"t" //T for TM
        }
        return [comp,cp_req_load_heavy];
    }
    
    function obtainBS(){
        var bs_info="";
        if ($("#bindingSite").hasClass("active")){
            var receptorsel=gpcr_selection();
            var ligli=$("#bindingSite").data("ligli");
            bs_info=receptorsel+"-"+ligli;
        }
        return (bs_info);
    }
//-------- Protein chains

    function obtainNonGPCRchains(selector){
        var nonGPCR_chains_all=[];
        $(selector).each(function(){
            var nonGPCR_chains=$(this).data("selector");
            //var patt = new RegExp("protein and \\((.*)\\)");
            //var nonGPCR_substr = patt.exec(nonGPCR_chains);
            //if (nonGPCR_substr){
            //nonGPCR_substr=nonGPCR_substr[1];
            nonGPCR_li = nonGPCR_chains.match(/[A-Z]/g);
            nonGPCR_str = nonGPCR_li.join();
            nonGPCR_chains_all.push(nonGPCR_str);
        });
        return (nonGPCR_chains_all);
    }


//-------- Predefined GPCR positions --------
    $(".gpcr_sel").change(function(){
        var section=$(this).parents(".cons_pos_section");
        var gpcr_id=$(this).children(":selected").val();
        var chosen_id = ".gpcr_id_"+gpcr_id;
        section.find(chosen_id).css("display","inline");
        section.find(".gpcr_prot_show_cons:not("+chosen_id+")").css("display","none");
    });

    $(".high_pd").each(function(){
        if ($(this).data("pdbpos").toString() == "None"){
            $(this).attr("disabled", true);
        }
    });

    function color_cons_pos(pos_name){
        var pos_filt_l = pos_name.match(/\d+\.\d+/g);
        color_d={
                "Rotamer toggle switch":"#519C6D",
                "PIF": "#2C6AA5",
                "Sodium binding site":"#991217",
                "NPxxY":"#ff7d7d",
                "Ionic lock":"#c35527",
                "DRY":"#a5ab4b",
                "3.32" : "#47CDAF",
                "6.30" : "#9284AF",
                "6.48":  "#a46060",
                "h.50" : {
                    "1": "#78C5D5",
                    "2": "#459BA8",
                    "3": "#79C268",
                    "4": "#C5D747",
                    "5": "#F5D63D",
                    "6": "#F18C32",
                    "7": "#E868A1",
                    "8": "#BF63A6"
                }
        }




        if (pos_filt_l){//It's indicated in GPCR res. num.
            var color=false;
            var pos_filt=pos_filt_l[0];
            if (pos_filt.split(".")[1]=="50"){
                color=color_d["h.50"][pos_filt.split(".")[0]];
            } else {
                if (pos_filt in color_d){
                    color=color_d[pos_filt];
                }
            }
        } else if (pos_name in color_d){
            color=color_d[pos_name];
        }

        if (! color){
            color = "#9B9393";
        }

        return(color);
    }

    function getSelectedPosLists(selector,pos_color_d){
        var selPosList=[];
        $(selector).each(function(){
            range = $(this).data("pdbpos").toString();
            var pos_name=$(this).text();
            var color =color_cons_pos(pos_name);
            if (range != "None"){
                if (range.indexOf(",") > -1){
                    range_li=range.split(",");
                    for (num=0; num < range_li.length ; num++){
                        selPosList[selPosList.length]=" " + range_li[num];
                        pos_color_d[range_li[num]]=color
                    }
                } else{
                    selPosList[selPosList.length]=" " + range;
                    pos_color_d[range]=color;
                }
            }
        });

        selPosList.sort(function(x,y){
            var patt = /\d+/;
            var xp = Number(patt.exec(x));
            var yp = Number(patt.exec(y));
            return xp - yp });
        selPosList=uniq(selPosList);
        return [selPosList,pos_color_d];
    }

    function obtainPredefPositions(){
        var high_pre={"A":[], "B":[], "C":[], "F":[],"colors":{}};
        var color_d={}
        var resA=getSelectedPosLists(".high_pdA.active",color_d);
        color_d=resA[1];
        var resB=getSelectedPosLists(".high_pdB.active",color_d);
        color_d=resB[1];
        var resC=getSelectedPosLists(".high_pdC.active",color_d);
        color_d=resC[1];
        var resF=getSelectedPosLists(".high_pdF.active",color_d);
        color_d=resF[1];
        high_pre["A"]=resA[0];
        high_pre["B"]=resB[0];
        high_pre["C"]=resC[0];
        high_pre["F"]=resF[0];
        high_pre["colors"]=color_d;
        high_pre["rep"]=$(".conspos_style_sel").val();
        return (high_pre);
    }

    $(".clear_conspos").click(function(){;
        if ($(this).hasClass("ed_section")){
            var sectionid="#ed_cons_pos_box";
        } else {
            var sectionid="#cons_pos_box";
        }

        $(sectionid+" .high_pd.active").each(function(){
            $(this).removeClass("active");
        });
        $("#selectionDiv").trigger("click");
    });    


    function disableMissingClasses(){
        $("li.cons_nav").each(function(){ 
            if ($(this).data("TF") == "False"){
                $(this).addClass("disabled");
            }
        });
        $("a.cons_nav").each(function(){ 
            if ($(this).data("TF") == "False"){
                $(this).removeAttr("data-toggle").removeAttr("href").attr("title","Class not avaliable");
            }
        });         
    }
    disableMissingClasses();

//    function obtainLegend(legend_el){
//        var color_dict={"A":"<span style='margin-right:5px;color:#01C0E2'>Class A </span>","B":"<span style='margin-right:5px;color:#EF7D02'>Class B </span>","C":"<span style='margin-right:5px;color:#C7F802'>Class C </span>","F":"<span style='margin-right:5px;color:#F904CE'>Class F </span>"};
//        var legend="";
//        if (legend_el.length > 1){
//            for (el=0; el < legend_el.length ; el++){
//                var add=color_dict[legend_el[el]];
//                legend+=add;
//            }
//            var legend_fin = "<span style='margin-top:5px'>" + legend + "</span>";
//            $("#legend").html(legend_fin);
//        } else {
//            $("#legend").html("");
//        }
//    }


    
    
//-------- Residues within xA of compound --------

    var comp_lg=[];
    var comp_sh=[];
    var comp_loadheavy_mask=[];
    var comp_loadheavy=[]
    $(".comp").each(function(){
        var comp_l=$(this).text();
        var comp_s=$(this).attr("id");
        comp_lg[comp_lg.length]=comp_l;
        comp_sh[comp_sh.length]=comp_s;
        var loadheavy_mask=false;
        if ($(this).hasClass("load_heavy")){
            var loadheavy_mask=true;
            comp_loadheavy[comp_loadheavy.length]=comp_s
        }
        comp_loadheavy_mask[comp_loadheavy_mask.length]=loadheavy_mask;
    });

    
    $(".nonGPCR").each(function(){
        var comp_l=$(this).text();
        var comp_s=$(this).attr("id");
        comp_lg[comp_lg.length]=comp_l;
        comp_sh[comp_sh.length]=comp_s;
        comp_loadheavy_mask[comp_loadheavy_mask.length]=false;
    });

    var select="";
    for (comp_n = 0; comp_n < comp_lg.length ; comp_n++){
        var load_heavy_class="";
        if (comp_loadheavy_mask[comp_n]){
            load_heavy_class="load_heavy";
        }
        var option='<option value="'+comp_sh[comp_n]+'" class="'+load_heavy_class+'">'+comp_lg[comp_n]+'</option>';
        select += option;
    }
    

    var wth_i=1;    
    $(".sel_within").on("click",".add_btn",function(){ 
        if ($(".sel_within").children().length < 15){
            $(".sel_within").find(".add_btn").css("visibility","hidden");
            var row='<div class="dist_sel" id=row'+wth_i.toString()+' style="margin-bottom:5px;">\
                      <span class="tick" ></span>\
                      <span class="always" style="margin-left:14px">\
                        Show \
                        <select class="resWthComp nglCallChangeWth" name="rescomp">\
                            <option  selected value="protein">residues</option>' + select + '</select>\
                         within \
                        <input class="form-control input-sm inputdist nglCallChangeWth" type="text" style="width:40px;padding-left:7px">\
                          &#8491; of\
                            <select class="wthComp" name="comp">' + select + '<option   value="user_sel">Selection</option></select>\
                            <span class="user_sel_input_p"></span>\
                            <button class="btn btn-link rm_btn" style="color:#DC143C;font-size:20px;margin:0;padding:0;" ><span class="glyphicon glyphicon-remove-sign"></span></button>\
                            <button class="btn btn-link add_btn" style="color:#57C857;font-size:20px;margin:0;padding:0" ><span class="glyphicon glyphicon-plus-sign"></span></button>\
                        </span>\
                        <div class="alert_sel_wth"><div class="alert_sel_wth_gnum"></div><div class="alert_sel_wth_ngl"></div></div>\
                      </div>';
            $(".sel_within").append(row);
            wth_i+=1;
        }
    });
    
    $(".sel_within").on("click", ".rm_btn" , function(){
        var row = $(this).closest(".dist_sel");
        var isactive= row.hasClass("sw_ok");
        var numWthRows = $(".sel_within").children().length;
        if(numWthRows==1){
            $(".sel_within").find(".inputdist").val("");
            $(".sel_within").find(".user_sel_input").val("");
            $(".sel_within").find(".alert_sel_wth_gnum").html("");
            $(".sel_within").find(".alert_sel_wth_ngl").html("");
            $(".sel_within").find("input").css("border-color","");
            inactivate_row(row,false);
        }else{
            var wBlock =$(this).closest(".dist_sel");
            if (wBlock.is(':last-child')){
                wBlock.remove();
                $(".sel_within").find(".add_btn:last").css("visibility","visible");
            } else {
                wBlock.remove();
            }
        }
        if (isactive){
            $("#selectionDiv").trigger("click");
        }
    });


    function obtainDistSel(){
        var dist_of=[];
        //var consider_comp=[];
        var ds_req_load_heavy=false;
        $(".sel_within").find(".dist_sel").each(function(){ 
            var inp=$(this).find(".inputdist").val();
            if (inp && /^[\d.]+$/.test(inp)) {
                var comp=$(this).find(".wthComp").val();
                var rownum = $(this).attr("id");
                if (comp=="user_sel"){
                    pre_sel=$(this).find(".user_sel_input").val();
                    var def_sel=inputText(gpcr_pdb_dict,pre_sel,rownum,"inp_wth",".alert_sel_wth");
                    if (def_sel ==""){
                        comp="none";
                        $(this).find(".user_sel_input").val("");
                    } else {
                        comp=def_sel;
                    }
                }
                if (comp != "none"){
                    var show_sel=$(this).find(".resWthComp");
                    var show = show_sel.val();
                    dist_of[dist_of.length]=show+"-"+inp+"-"+comp+"-"+rownum;
                    if (show_sel.find(":selected").hasClass("load_heavy")){
                        ds_req_load_heavy=true;
                    }
                }
            }

        });
        return [dist_of,ds_req_load_heavy];
    }

    function obtainWaterDist(){             
        //TO DO: ask if this is error proof! now we define, if there is something typed and if it is a digit. but what if user types a character ?    //we are in the parent so no need for window.parent.document                                     
        var checked=$(".WaterDistDisplay").is(":checked");  //with Jquery check if checkbox is checked, if it not consider radius as 0. 
        show_wat=false;
        if (checked){
            var inp=$("#waterswithin").val()
            if(inp && /^[\d.]+$/.test(inp)) {  
                var water_dist=Number(inp)
                $("#waterswithin_parent").removeClass("has-error")
                show_wat=true;
            }else{
                water_dist=Number(0)      //give an error?? or not? for example if user types a letter 
                $("#waterswithin_parent").addClass("has-error")
            }
            
        }

        return[show_wat, water_dist]
    }

    function obtainPolar(){
        var checked=$(".PolarDisplay").is(":checked");
        return (checked)
    }

    function obtainWaterBox(){
        var inp = $("#waterswithin").val()
        if(inp && /^[\d.]+$/.test(inp)) {  
            var water_box=Number(inp)
        }else{
            water_box = Number(0)
        }
        return(water_box)
    }


    function activate_row(row,triggerNGL){
        row.find(".tick").html('<span class="glyphicon glyphicon-ok" style="font-size:10px;color:#7acc00;padding:0;margin:0"></span>');
        row.find(".always").attr("style","");
        row.addClass("sw_ok");
        if (triggerNGL){
            $("#selectionDiv").trigger("click");
        }
    }
    function inactivate_row(row,triggerNGL){
        var active_before= row.hasClass("sw_ok");
        if (active_before){
            row.find(".tick").html("");
            row.find(".always").attr("style","margin-left:14px");
            row.removeClass("sw_ok");
            if (triggerNGL){
                $("#selectionDiv").trigger("click");
            }
        }
    }
    


    function activate_or_inactivate_row(selector){    
        var row = $(selector).closest(".dist_sel");
        var row_alert=row.find("alert_sel_wth");
        row_alert=row.find(".alert_sel_wth_gnum").html("");
        row_alert=row.find(".alert_sel_wth_ngl").html("");
        row.find("input").css("border-color","");
        var inp=row.find(".inputdist").val().replace(/\s+/g, '');
        row.find(".inputdist").val(inp);
        if (inp && /^[\d.]+$/.test(inp)) {
            if (row.find(".wthComp").val()=="user_sel"){
                if (row.find(".user_sel_input").val() == ""){
                    inactivate_row(row,true);
                }else {
                    activate_row(row,true);
                }            
            } else {
                activate_row(row,true);
            }
        } else {
            row.find(".inputdist").css("border-color","#A94442");//Red border to show error
            if (row.attr("class").indexOf("sw_ok") > -1){
                inactivate_row(row,true);
            }
        }
    }
  
    
    $(".sel_within").on("change", ".nglCallChangeWth" ,function(){
        activate_or_inactivate_row(this);
    });    


    $(".sel_within").on('change', ".wthComp" ,function(){
        if ($(this).val()=="user_sel"){
            var sw_input='<input class="form-control input-sm user_sel_input nglCallChangeWth" type="text" style="width:95px;padding-left:7px">';
            $(this).siblings(".user_sel_input_p").html(sw_input);
            var row = $(this).closest(".dist_sel");
            inactivate_row(row,true);
        } else {
            $(this).siblings(".user_sel_input_p").html("");
            activate_or_inactivate_row(this);
        }
    });
//!!!!!!!!!!!!!!!!!!!!
    $(".updateSelOrNot").change(function(){
        
        $("#selectionDiv").trigger("click");
    });
//!!!!!!!!!!!!!!!!!!!!

//-------- Freq of Interaction --------
    function gnumFromPosChain(pos, chain){
        result="-";
        for (gpcr in all_gpcr_dicts){ //[1]["combined_num"]
            var search_dict=all_gpcr_dicts[gpcr]["combined_num"];
            for (gnum in search_dict){
                if (search_dict[gnum][0] == pos && search_dict[gnum][1] ==chain){
                    result = gnum;
                }
            }
        }
        return result;
    }
    

    function build_ligresint_result(int_data,traj_path,thr_ok,dist_scheme_name,i_id){
        var int_id=int_data.int_id;
        var strided=int_data.strided;
        var int_data=int_data.result;
        var strideText="";
        if (Number(strided)> 1){
            strideText = " (str: "+strided+")";
        }
        if (! isEmptyDict(int_data)){
            var patt = /[^/]*$/g;
            var trajFile = patt.exec(traj_path);
            //Table
            var table_html='<div class="int_tbl" id=int_tbl'+i_id+' data-int_id='+int_id+' class="table-responsive" style="border:1px solid #F3F3F3;padding:10px;overflow:auto">\
            <div style="font-size:12px;margin-top:10px;margin-bottom:10px" ><b>Threshold:</b> '+thr_ok+' &#8491; ('+dist_scheme_name+'), <b>Trajectory:</b> '+trajFile+strideText+'</div>\
              <div style="overflow-y:auto;overflow-x:hidden;max-height:400px">\
              <table class="table table-condensed int_results_tbl" style="font-size:12px;">\
                <thead>\
                  <tr>\
                    <th>Ligand</th>\
                    <th>AA</th>\
                    <th>Chain</th>\
                    <th>Generic num</th>\
                    <th>Frequency</th>\
                  </tr>\
                </thead>\
              <tbody>';
            var mylist=[];
            for (lig in int_data){
                res_int=int_data[lig];
                var num_res_int=res_int.length;
                //1) Inside the table body, the 1st tr has the "rowspan" td. We create it:
                table_html+='<tr><td rowspan='+num_res_int+'>'+lig+'</td>';
                var res_int_1st=res_int[0];
                var res_int_1st_ok=[res_int_1st[2]+" "+res_int_1st[0].toString(),res_int_1st[1],gnumFromPosChain(res_int_1st[0].toString(), res_int_1st[1]),res_int_1st[3]+"%"];

                gnum_mylist=gnumFromPosChain(res_int_1st[0].toString(), res_int_1st[1])
                if (gnum_mylist == "-"){
                    gnum_mylist=res_int_1st[2]+res_int_1st[0].toString()+":"+res_int_1st[1];
                }
                mylist.push([res_int_1st[0],gnum_mylist ,res_int_1st[3] ]);

                //2) And then we create the rest of td inside this tr.
                table_html+='<td class="AA_td" style="cursor:pointer;">'+res_int_1st_ok[0]+'</td>\
                             <td class="chain_td">'+res_int_1st_ok[1]+'</td>\
                             <td class="gnum_td">'+res_int_1st_ok[2]+'</td>\
                             <td class="freq_td">'+res_int_1st_ok[3]+'</td>';
                /*for (info=1 ; info < res_int_1st_ok.length ; info++){
                    table_html+='<td>'+res_int_1st_ok[info]+'</td>';
                }*/
                table_html+='</tr>';
                var res_int_rest=res_int.slice(1,res_int.length);
                //3) The rest of td of the table body do ot have rowspan:
                for (res_infoN=0; res_infoN < res_int_rest.length ; res_infoN++){
                    var res_info=res_int_rest[res_infoN];
                    var res_info_ok=[res_info[2]+" "+res_info[0].toString(),res_info[1],gnumFromPosChain(res_info[0].toString(), res_info[1]),res_info[3]+"%"];
                    //
                    gnum_mylist=gnumFromPosChain(res_info[0].toString(), res_info[1])
                    if (gnum_mylist == "-"){
                        gnum_mylist=res_info[2]+res_info[0].toString()+":"+res_info[1];
                    }
                    mylist.push([res_info[0],gnum_mylist ,res_info[3] ]);
                    //
                    table_html+='<tr>';
                    table_html+='<td class="AA_td" style="cursor:pointer;">'+res_info_ok[0]+'</td>\
                                 <td class="chain_td">'+res_info_ok[1]+'</td>\
                                 <td class="gnum_td">'+res_info_ok[2]+'</td>\
                                 <td class="freq_td">'+res_info_ok[3]+'</td>';
                    /*for (infoN=1 ; infoN < res_info_ok.length ; infoN++){
                        var info=res_info_ok[infoN];
                        table_html+='<td>'+info+'</td>';
                    }*/
                    table_html+='</tr>';
                }                              
            }

            table_html+="</tbody></table></div>\
            <button class='btn btn-link pull-right clear_int_tbl' style='color:#DC143C;'>Clear table</button>";
            var dyn_id=$(".str_file").data("dyn_id");
            var chart_div="int_chart_"+i_id.toString();
            var infoAndOpts= "<div id='"+chart_div+"' style='margin-top:30px'></div>\
                <div class='checkbox' style='font-size:12px;margin-bottom:0;display:inline-block'>\
                    <label><input type='checkbox' name='view_int' checked class='display_int'>Display interacting residues</label>\
                </div>\
                <div class='int_settings'>\
                    <div style='display:inline-block;margin:5px 5px 5px 0;cursor:pointer;'>\
                        <a role='button' class='btn btn-link save_img_int_plot settingsB' href='#' target='_blank' style='color:#585858;margin-right:0;margin-left;padding-right:0;padding-left:0;margin-bottom:3px'>\
                            <span  title='Save plot as image' class='glyphicon glyphicon-stats'></span>\
                        </a>\
                    </div>\
                    <div style='display:inline-block;margin:5px'>\
                        <a role='button' class='btn btn-link href_save_data_int settingsB' href='/view/dwl/"+dyn_id+"/"+int_id+"' style='color:#585858;margin-right:0;margin-left;padding-right:0;padding-left:0;margin-bottom:3px'>\
                            <span  title='Save data' class='glyphicon glyphicon-download-alt save_data_int'></span>\
                        </a>\
                    </div>\
                    <div style='display:inline-block;margin:5px;color:#DC143C;cursor:pointer;vertical-align:-1px'>\
                        <span title='Delete' class='glyphicon glyphicon-trash delete_int_tbl' data-int_id='"+int_id+"' ></span>\
                    </div>\
                </div>\
            </div>";
            $("#int_info").append(table_html+infoAndOpts);
            if ($.active>1){
                $("#int_info").find(".href_save_data_int").addClass("disabled");
            }
            
            
            
            
            //Plot
            for (lig in int_data){
                res_int=int_data[lig];
                var res_int_ok=[["Position","Freq"]];
                for (posN=0 ; posN < res_int.length ; posN++){
                    var pos=res_int[posN];
                    var gnum=gnumFromPosChain(pos[0].toString(), pos[1]);
                    if (gnum == "-"){
                        var gnum = pos[2]+pos[0].toString()+":"+pos[1];
                    }
                    res_int_ok.push([gnum,Number(pos[3])]);
                }
                function drawChart3(){
                    var data = google.visualization.arrayToDataTable(res_int_ok,false);
                    var options = {"height":350,"legend":{"position":"none"}, 
            "chartArea":{"right":"5","left":"60","top":"50","bottom":"70"},vAxis: {title: 'Frequency (%)', viewWindow: {min: 0,  max: 100}} , hAxis: {slantedText: true, slantedTextAngle: 90  }};
                    var int_chart_div = document.getElementById(chart_div);

                    var chart = new google.visualization.ColumnChart(int_chart_div);    
                    google.visualization.events.addListener(chart, 'ready', function () {
                        var int_img_source =  chart.getImageURI(); 
                        $("#"+chart_div).attr("data-url",int_img_source);
                    });
                    chart.draw(data, options);   
                    var int_img_source=$("#int_info").find("#"+chart_div).attr("data-url");
                    $("#"+chart_div).siblings(".int_settings").find(".save_img_int_plot").attr("href",int_img_source);
                    
                    //google.visualization.events.addListener(chart, 'select', function(){  
                        //var mysel = chart.getSelection()[0];
                        //if (mysel){          
                            //var row_to_sel=mysel.row +1
                            //$("#"+chart_div).closest(".int_tbl").find("table tr:eq("+row_to_sel+")").children(".AA_td").trigger("click");
                        //}
                    //});
                    var before=false;
                    google.visualization.events.addListener(chart, 'click', function(target){  
                        var targetID=target["targetID"];
                        if (targetID.startsWith("bar")){
                            var row_data=Number(targetID.split("#")[2]);
                            var row_to_sel=row_data +1
                            var mycell=$("#"+chart_div).closest(".int_tbl").find("table tr:eq("+row_to_sel+")").children(".AA_td");
                            if (mycell.hasClass("showInP")){
                                if (targetID == before){
                                    mycell.trigger("click");        
                                }
                            } else {
                                mycell.trigger("click");
                            }
                            before=targetID;
                        }
                    });


                    /*var this_tbl_td=$('#int_tbl'+i_id.toString()).find("td");
                    $("#int_info").on("click", this_tbl_td , function(){
                        var this_row=$(this).parent().index();
                    })*/
                    
                    /*google.visualization.events.addListener(chart, 'select', selectHandler);

                    function selectHandler(e) {
                        var rc= chart.getSelection();
                        var row =rc[0]["row"];
                        var col =rc[0]["column"];
                        if (row != undefined && col != undefined ){
                            var mytr=$("#int_tbl1").find("tr:nth-child("+row+")");
                        }
                    }*/
                }
                google.load("visualization", "1", {packages:["corechart"],'callback': drawChart3});

            }
                   
            $("#int_tbl"+i_id).find(".display_int").attr("checked","true");
            $("#selectionDiv").trigger("click");
            
            
        } else {
            var patt = /[^/]*$/g;
            var trajFile = patt.exec(traj_path);
            var noInt_msg="<div class='int_tbl' id=int_tbl"+i_id+" style='border:1px solid #F3F3F3;padding:10px;'>\
             <div style='font-size:12px;margin-bottom:5px' ><b>Threshold:</b> "+thr_ok+" &#8491;  ("+dist_scheme_name+"), <b>Trajectory:</b> "+trajFile+"</div>\
                    <div style='margin-bottom:5px 5px 5px 0'>No interactions found.</div>\
                <div style='display:inline-block;margin:5px;color:#DC143C;cursor:pointer;'>\
                    <span title='Delete' class='glyphicon glyphicon-trash delete_int_tbl' data-int_id='"+int_id+"'></span>\
                </div>\
            </div>";
            $("#int_info").append(noInt_msg);
        }
        i_id+=1;

        return i_id
    }

    var i_id=1;
    if (is_ligprotint_default && predef_int_data){
        var traj_path=predef_int_data["traj_path"];
        var thr_ok=predef_int_data["threshold"];
        var dist_scheme_name=predef_int_data["dist_scheme"];
        i_id=build_ligresint_result(predef_int_data,traj_path,thr_ok,dist_scheme_name,i_id);
    }

    var lig_sel_str;
    $("#gotoInt").click(function(){
        $("#int_stride_parent").removeClass("has-warning");
        numComputedI = $("#int_info").children().length;
        if (numComputedI < 15){
            var inp_is_num=true;
            var thr=$("#int_thr").val();
            var correctinput=true;
            if (thr==""){
                var thr_ok="3";
            } else if (/^(\d+(\.\d+)?)$/.test(thr)){
                var thr_ok=thr;
            } else {
                correctinput=false;
            }
            if (correctinput){
                if (thr==""){
                    var thr_ok="3";
                }else{
                    var thr_ok=thr;
                }
                var traj_path = $(".trajForInt:selected").attr("name");
                if (traj_path){
                    var intof=$(".ligInt:selected").val();
                    if (intof=="allLig"){
                        var all_lig_sel=[];
                        $(".unitInt").each(function(){
                            var lig_s=$(this).val();
                            all_lig_sel[all_lig_sel.length]=lig_s;        
                        });
                    } else {
                        all_lig_sel=[intof];
                    }
                    var dist_scheme= $(".dist_scheme_opt:selected").val();
                    var dist_scheme_name;
                    if (dist_scheme=="closest"){
                        dist_scheme_name="All atoms";
                    } else {
                        dist_scheme_name="Heavy atoms only";
                    }
                    var stride = strideVal("#int_stride");
                    $("#int_alert , #int_thr_error").html("");
                    ///AJAX!!!
                    $("#int_info").after("<p style='margin-top:5px;padding:5px;background-color:#e6e6ff;border-radius:3px;' id='wait_int'><span class='glyphicon glyphicon-time'></span> Computing interaction...</p>");
                    $("#gotoInt").addClass("disabled");
                    $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int, #downl_json_hb").addClass("disabled");
                    act_int_tbls=[];
                    $("#int_info").children(".int_tbl").each(function(){
                        act_int_tbls.push($(this).data("int_id"));
                    });
                    var t0= performance.now();
                    $.ajax({
                        type: "POST",
                        url: "/view/"+dyn_id+"/", 
                        dataType: "json",
                        data: { 
                          "all_ligs": all_lig_sel.join(),
                          "thresh":thr_ok,
                          "traj_p": traj_path,
                          "struc_p": struc,
                          "dist_scheme": dist_scheme,
                          "no_rv" : act_int_tbls.join(),
                          "stride" : stride,
                        },
                        success: function(int_data) {
                            if ($.active<=1){
                                $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int, #downl_json_hb").removeClass("disabled");
                            }
                            $("#wait_int").remove();
                            $("#gotoInt").removeClass("disabled");
                            var success=int_data.success;
                            if (success){ 
                                i_id=build_ligresint_result(int_data,traj_path,thr_ok,dist_scheme_name,i_id);
                            }else{
                                var int_error=int_data.e_msg;
                                add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>'+ int_error;
                                $("#int_alert").html(add_error);    
                            }
                            var t1= performance.now();
                        },
                        error: function(){
                            add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>An unexpected error occurred.';
                            $("#int_alert").html(add_error); 
                            if ($.active<=1){
                                $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int, #downl_json_hb").removeClass("disabled");
                            }
                            $("#wait_int").remove();
                            $("#gotoInt").removeClass("disabled");
                        },
                        timeout: 600000
                        
                    });
                } else {
                    //$("#int_traj_error").text("Please select a trajectory.");
                    add_error_d='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>Some fields are empty or contain errors.';
                    $("#int_alert").html(add_error_d);
                }
            } else {
                $("#int_thr_error").text("Threshold must be an integer.");
                add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>Some fields are empty or contain errors.';
                $("#int_alert").html(add_error);   
            }
        }else{
            add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>Please, remove some interaction results to obtain new ones.';
            $("#int_alert").html(add_error);   
        }
    });
    
    $('body').on('click','.delete_int_tbl', function(){
        var isChecked=$(this).closest(".int_tbl").find(".display_int").is(":checked");
        var IntToRv=$(this).parents(".int_tbl").attr("id");
        $('#'+IntToRv).remove();
        if (isChecked){
            $("#selectionDiv").trigger("click");
        }
    });
    
    
    function displayIntResids(){
        var int_res_li=[];
        var int_res_li_check=[];
        $(".int_tbl").each(function(){
            if ($(this).find(".display_int").is(":checked")){
                $(this).find(".int_results_tbl > tbody > tr").each(function(){
                    var pos_sel=$(this).children(".AA_td");
                    var pos = pos_sel.html();
                    var chain=$(this).children(".chain_td").html();
                    var freq=$(this).children(".freq_td").html();
                    var isChecked=pos_sel.hasClass("showInP");
                    var pos_aa = /\d*$/.exec(pos)[0];
                    if (isChecked){
                        int_res_li_check.push([pos_aa, chain,freq]);
                    } else {
                        int_res_li.push([pos_aa, chain,freq]);
                    }

                });
            }  
        });
        int_res_li=uniq(int_res_li);
        int_res_li_check=uniq(int_res_li_check);
        return ([int_res_li,int_res_li_check]);
    }

    
    $("#int_info").on("change" ,".display_int" , function(){
        $("#selectionDiv").trigger("click");
    });
    

    $("#int_info").on("mouseenter", ".AA_td", function() {
        if ($(this).hasClass("showInP")){
            $(this).css("background-color","#9dd0e1");
        } else {
            $(this).css("background-color","#f2f2f2");
        }
    });
    $("#int_info").on("mouseleave", ".AA_td", function() {
        if ($(this).hasClass("showInP")){
            $(this).css("background-color","#c5e3ed");
        } else {
            $(this).css("background-color","transparent");
        }
    });


    $("#int_info").on("click",".AA_td",function(){
        var isclicked = $(this).hasClass("showInP");
        if (isclicked) {
            $(this).css("background-color","transparent").removeClass("showInP");
        } else {
            $(this).css("background-color","#c5e3ed").addClass("showInP");
        }
        if ($(this).closest(".int_tbl").find(".display_int").is(":checked")){
            $("#selectionDiv").trigger("click");
        }
    });

    $("#int_info").on("click",".clear_int_tbl",function(){
        var int_tbl_el=$(this).closest(".int_tbl");
        var found_sel =int_tbl_el.find(".AA_td.showInP");
        if (found_sel.length >0){
            found_sel.each(function(){
                $(this).css("background-color","transparent").removeClass("showInP");
            })
            if ((int_tbl_el).find(".display_int").is(":checked")){
                $("#selectionDiv").trigger("click");                
            }
        }
    });
//-------- Dist between residues --------

    var i_dist=1;
    $(".dist_btw").on("click",".add_btn2",function(){ 
        if ($(".dist_btw").children().length < 20){
            $(".dist_btw").find(".only1st").css("visibility","hidden");
            var row_d='<div class="dist_pair" id=row2_'+i_dist+'>\
                  <span class="tick2" ></span>\
                  <span class="always2" style="margin-left:14px">\
                     Compute distance between \
                     <select class="dist_el_sel">\
                        <option class="dist_el_opt" name="dist_el" value="atoms" selected >atoms</option>\
                        <option class="dist_el_opt" name="dist_el" value="residues">residues</option>\
                     </select>\
                     <span class="dist_from_parent">\
                         <input class="form-control input-sm dist_from" title="Introduce atom index" type="text" style="width:50px;padding-left:7px;margin-bottom:5px">\
                     </span>\
                     <span class="dist_from_res_parent dis_res_bth_parent" style="display:none">\
                        <input class="form-control input-sm dist_from_res dis_res_bth" type="text" title="Introduce residue number and chain name (ex. 50:P)" style="width:50px;padding-left:7px;margin-bottom:5px;" placeholder="xx:C">\
                    </span>\
                     <span class="dist_from_atomNm_parent"></span>\
			and\
			         <span class="dist_to_parent">\
                         <input class="form-control input-sm dist_to" title="Introduce atom index" type="text" style="width:50px;padding-left:7px;margin-bottom:5px">\
                     </span>\
                     <span class="dist_to_res_parent dis_res_bth_parent" style="display:none">\
                        <input class="form-control input-sm dist_to_res dis_res_bth" type="text" title="Introduce residue number and chain name (ex. 50:P)" style="width:50px;padding-left:7px;margin-bottom:5px;" placeholder="xx:C">\
                     </span>\
                     <span class="dist_to_atomNm_parent"></span>\
                     <button class="btn btn-link del_btn2" style="color:#DC143C;font-size:20px;margin:0;padding:0" ><span class="glyphicon glyphicon-remove-sign"></span></button>\
                     <button class="btn btn-link only1st add_btn2" style="color:#57C857;font-size:20px;margin:0;padding:0" ><span class="glyphicon glyphicon-plus-sign"></span></button>\
                     <button title="Import from the structure." class="btn btn-link only1st imp_btn2" style="color:#1e90ff;font-size:20px;margin:0;padding:0" ><span class="glyphicon glyphicon-circle-arrow-down"></span></button>\
                   </span>\
                  </div>';
            $(".dist_btw").append(row_d);
            i_dist+=1;
        }
    });
    
    $(".dist_btw").on("change" , ".dist_el_sel" , function(){
        $(".dist_btw").find(".has-error").each(function(){
            $(this).removeClass("has-error");
        });
        var selection=$(this).val();
        var drow = $(this).closest(".dist_pair");
        if (selection == "residues"){
            var atomNm_from = '<select class="dist_atomNm_from_sel">\
                                <option class="dist_atomNm_from_opt" name="dist_atomNm_from" value="CA" selected >CA</option>\
                                <option class="dist_atomNm_from_opt" name="dist_atomNm_from" value="CB">CB</option>\
                             </select>';
            var atomNm_to = '<select class="dist_atomNm_to_sel">\
                                <option class="dist_atomNm_to_opt" name="dist_atomNm_to" value="CA" selected >CA</option>\
                                <option class="dist_atomNm_to_opt" name="dist_atomNm_to" value="CB">CB</option>\
                             </select>';
            drow.find(".dist_from_atomNm_parent").html(atomNm_from);
            drow.find(".dist_to_atomNm_parent").html(atomNm_to);
            drow.find(".dist_from_parent").css("display","none");
            drow.find(".dist_to_parent").css("display","none");
            drow.find(".dist_from_res_parent").css("display","inline");
            drow.find(".dist_to_res_parent").css("display","inline");
            
        } else {
            drow.find(".dist_from_atomNm_parent").html("");
            drow.find(".dist_to_atomNm_parent").html("");
            drow.find(".dist_from_parent").css("display","inline");
            drow.find(".dist_to_parent").css("display","inline");
            drow.find(".dist_from_res_parent").css("display","none");
            drow.find(".dist_to_res_parent").css("display","none");
        
        } 
    });
    
    function addClickedDistInputs(clickedDist){
        for (dpairN=0 ; dpairN < clickedDist.length ; dpairN++){
            var dpair0 = clickedDist[dpairN][0];
            var dpair1 = clickedDist[dpairN][1];
            if ($(".dist_btw").children().length < 20){
                if( /^[\d]+$/.test(dpair0 + dpair1)){
                    $(".dist_btw").find(".only1st").css("visibility","hidden");
                    var row_d='<div class="dist_pair d_ok" id=row2_'+i_dist+'>\
                          <span class="tick2"><span class="glyphicon glyphicon-ok" style="font-size:10px;color:#7acc00;padding:0;margin:0"></span></span>\
                          <span class="always2">\
                     Compute distance between \
                     <select class="dist_el_sel">\
                        <option class="dist_el_opt" name="dist_el" value="atoms" selected >atoms</option>\
                        <option class="dist_el_opt" name="dist_el" value="residues">residues</option>\
                     </select>\
                     <span class="dist_from_parent">\
                         <input class="form-control input-sm dist_from" title="Introduce atom index" type="text" style="width:50px;padding-left:7px;margin-bottom:5px" value="'+dpair0+'">\
                     </span>\
                     <span class="dist_from_res_parent dis_res_bth_parent" style="display:none">\
                        <input class="form-control input-sm dist_from_res dis_res_bth" type="text" title="Introduce residue number and chain name (ex. 50:P)" style="width:50px;padding-left:7px;margin-bottom:5px;" placeholder="xx:C">\
                    </span>\
                     <span class="dist_from_atomNm_parent"></span>\
			and\
			         <span class="dist_to_parent">\
                         <input class="form-control input-sm dist_to" title="Introduce atom index" type="text" style="width:50px;padding-left:7px;margin-bottom:5px" value="'+dpair1+'">\
                     </span>\
                     <span class="dist_to_res_parent dis_res_bth_parent" style="display:none">\
                        <input class="form-control input-sm dist_to_res dis_res_bth" type="text" title="Introduce residue number and chain name (ex. 50:P)" style="width:50px;padding-left:7px;margin-bottom:5px;" placeholder="xx:C">\
                     </span>\
                     <span class="dist_to_atomNm_parent"></span>\
                             <button class="btn btn-link del_btn2" style="color:#DC143C;font-size:20px;margin:0;padding:0" ><span class="glyphicon glyphicon-remove-sign"></span></button>\
                             <button class="btn btn-link only1st add_btn2" style="color:#57C857;font-size:20px;margin:0;padding:0" ><span class="glyphicon glyphicon-plus-sign"></span></button>\
                             <button title="Import from the structure." class="btn btn-link only1st imp_btn2" style="color:#1e90ff;font-size:20px;margin:0;padding:0" ><span class="glyphicon glyphicon-circle-arrow-down"></span></button>\
                          </span>\
                          </div>';                          
                    $(".dist_btw").append(row_d);
                    i_dist+=1;
               }
            }
        }
    }
    
            
    
    
    function obtainDistInputed(clickedDist_pre){
        var dPairsInp = [];
        $(".dist_btw").find(".dist_pair").each(function(){ 
            var d_from=$(this).find(".dist_from").val();
            var d_to=$(this).find(".dist_to").val();
            dPairsInp.push([d_from,d_to]);
        });
        str_dPairsInp=JSON.stringify(dPairsInp);       
        var clickedDist=[];
        for (addPosN=0 ; addPosN < clickedDist_pre.length ; addPosN++){
            var addpos=clickedDist_pre[addPosN];
            if (str_dPairsInp.indexOf(JSON.stringify(addpos)) == -1){
                clickedDist.push(addpos);
            }
        }
        return(clickedDist);
    }
    
    var clickedDistToAnalysis =function(clickedDist_pre){
        if (clickedDist_pre.length > 0){
            clickedDist=obtainDistInputed(clickedDist_pre);        
            var last_from_sel=$(".dist_btw").find(".dist_from:last");
            var last_from=last_from_sel.val();
            var last_to_sel=$(".dist_btw").find(".dist_to:last");
            var last_to=last_to_sel.val();
            var selElm = $(".dist_btw").find(".dist_el_sel").val();
            if ( selElm=="atoms" && last_from=="" && last_to==""){                
                var fstRow0 =clickedDist[0][0];
                var fstRow1 =clickedDist[0][1];
                last_from_sel.val(fstRow0);
                last_to_sel.val(fstRow1);
                if( /^[\d]+$/.test(fstRow0 + fstRow1)){
                    var last_row=$(".dist_btw").find(".dist_pair:last");
                    last_row.find(".tick2").html('<span class="glyphicon glyphicon-ok" style="font-size:10px;color:#7acc00;padding:0;margin:0"></span>');
                    last_row.find(".always2").attr("style","");
                    last_row.addClass("d_ok");
                }  
                if (clickedDist.length > 1){
                    addClickedDistInputs(clickedDist.slice(1));
                }
            } else {
                addClickedDistInputs(clickedDist);
            }
        }
    }
    window.clickedDistToAnalysis=clickedDistToAnalysis;    
    
    
    $(".dist_btw").on("click", ".del_btn2" , function(){ 
        var numDistRows = $(".dist_btw").children().length;
        if(numDistRows==1){
            var drow=$(".dist_btw");
            drow.find(".dist_from").val("");
            drow.find(".dist_to").val("");
            drow.find(".dis_res_bth").val("");
            drow.find(".fist_from_parent, .dist_to_parent, .dis_res_bth_parent").removeClass("has-error");
            var dpair = $(this).closest(".dist_pair");
            dpair.find(".tick2").html("");
            dpair.find(".always2").attr("style","margin-left:14px");
            dpair.removeClass("d_ok");
        }else{
            var dBlock =$(this).closest(".dist_pair");
            if (dBlock.is(':last-child')){
                dBlock.remove();
                $(".dist_btw").find(".add_btn2:last , .imp_btn2:last").css("visibility","visible");
            } else {
                dBlock.remove();
            }
        }
    });


    $(".dist_btw").on("blur", ".dist_from, .dist_to" ,function(){
        var dpair = $(this).closest(".dist_pair");
        if ($(this).attr("class").indexOf("dist_from") > -1){
            var d_from=$(this).val().replace(/\s+/g, '');
            var d_to = $(this).closest(".always2").find(".dist_to").val().replace(/\s+/g, '');
            if (d_from=="" || /^[\d]+$/.test(d_from)){
                $(this).parent().removeClass("has-error");            
            }else {
                $(this).parent().addClass("has-error");
            }
        } else {
            var d_from = $(this).closest(".always2").find(".dist_from").val().replace(/\s+/g, '');
            var d_to=$(this).val().replace(/\s+/g, '');
            if (d_to=="" || /^[\d]+$/.test(d_to)){
                $(this).parent().removeClass("has-error");            
            }else {
                $(this).parent().addClass("has-error");
            }
        }
        dpair.find(".dist_from").val(d_from);
        dpair.find(".dist_to").val(d_to);
        if (d_from && d_to && /^[\d]+$/.test(d_from + d_to)) {
            dpair.find(".tick2").html('<span class="glyphicon glyphicon-ok" style="font-size:10px;color:#7acc00;padding:0;margin:0"></span>');
            dpair.find(".always2").attr("style","");
            dpair.addClass("d_ok");
        } else {
            if (dpair.attr("class").indexOf("d_ok") > -1){
                dpair.find(".tick2").html("");
                dpair.find(".always2").attr("style","margin-left:14px");
                dpair.removeClass("d_ok");
            }
        }
        
    });



    $(".dist_btw").on("change", ".dis_res_bth" ,function(){
        var dpair = $(this).closest(".dist_pair");
        var myres= $(this).val().replace(/\s+/g, '');
        var isOk = /^\d{1,5}:[a-zA-Z]$/.test(myres);
        if (isOk){
            $(this).parent().removeClass("has-error");
            var siblRes = $(this).parent().siblings(".dis_res_bth_parent").children(".dis_res_bth").val().replace(/\s+/g, '');
            var isSiblOk =/^\d{1,5}:[a-zA-Z]$/.test(siblRes); 
            if (isSiblOk){
                if (! dpair.hasClass("d_ok")){
                    dpair.find(".tick2").html('<span class="glyphicon glyphicon-ok" style="font-size:10px;color:#7acc00;padding:0;margin:0"></span>');
                    dpair.find(".always2").attr("style","");
                    dpair.addClass("d_ok");
                }
             }
        } else {
            $(this).parent().addClass("has-error");
            if (dpair.hasClass("d_ok")){
                dpair.find(".tick2").html("");
                dpair.find(".always2").attr("style","margin-left:14px");
                dpair.removeClass("d_ok");
             }
        }
    });
    
    $(".dist_btw").on("change", ".dist_el_sel", function(){
        var dpair = $(this).closest(".dist_pair");
        if ( $(this).val() == "atoms"){
            var d_from = $(this).siblings(".dist_from_parent").children(".dist_from").val();
            var d_to = $(this).siblings(".dist_to_parent").children(".dist_to").val();
            if (d_from && d_to && /^[\d]+$/.test(d_from + d_to)) {
                dpair.find(".tick2").html('<span class="glyphicon glyphicon-ok" style="font-size:10px;color:#7acc00;padding:0;margin:0"></span>');
                dpair.find(".always2").attr("style","");
                dpair.addClass("d_ok");
            } else {
                if (dpair.attr("class").indexOf("d_ok") > -1){
                    dpair.find(".tick2").html("");
                    dpair.find(".always2").attr("style","margin-left:14px");
                    dpair.removeClass("d_ok");
                }
            }
            
        } else {
            var res_from = $(this).siblings(".dist_from_res_parent").children(".dist_from_res").val();
            var res_to = $(this).siblings(".dist_to_res_parent").children(".dist_to_res").val();
            var isOK_from= /^\d{1,5}:[a-zA-Z]$/.test(res_from);
            var isOK_to= /^\d{1,5}:[a-zA-Z]$/.test(res_to);
            if (isOK_from && isOK_to){
                dpair.find(".tick2").html('<span class="glyphicon glyphicon-ok" style="font-size:10px;color:#7acc00;padding:0;margin:0"></span>');
                dpair.find(".always2").attr("style","");
                dpair.addClass("d_ok");
            } else {
                dpair.find(".tick2").html("");
                dpair.find(".always2").attr("style","margin-left:14px");
                dpair.removeClass("d_ok");
            }
        }
    });


/*    $(".dist_btw").on("blur", ".dist_pair" ,function(){
        var d_from=$(this).find(".dist_from").val().replace(/\s+/g, '');
        var d_to=$(this).find(".dist_to").val().replace(/\s+/g, '');
        $(this).find(".dist_from").val(d_from);
        $(this).find(".dist_to").val(d_to);
        if (d_from && d_to && /^[\d]+$/.test(d_from + d_to)) {
            $(this).find(".tick2").html('<span class="glyphicon glyphicon-ok" style="font-size:10px;color:#7acc00;padding:0;margin:0"></span>');
            $(this).find(".always2").attr("style","");
            $(this).addClass("d_ok");
        } else {
            if ($(this).attr("class").indexOf("d_ok") > -1){
                $(this).find(".tick2").html("");
                $(this).find(".always2").attr("style","margin-left:14px");
                $(this).removeClass("d_ok");
            }
        }
    }); */

    function obtainDistToComp(){
        var distToComp=[];
        $(".dist_btw").find(".dist_pair.d_ok").each(function(){ 
            if ($(this).find(".dist_el_sel").val() == "atoms"){
                var d_from=$(this).find(".dist_from").val();
                var d_to=$(this).find(".dist_to").val();
                distToComp.push(d_from+"-"+d_to);
            } else {
                var d_from=$(this).find(".dist_from_res").val();
                var an_from=$(this).find(".dist_atomNm_from_sel").val();
                var d_to=$(this).find(".dist_to_res").val();
                var an_to=$(this).find(".dist_atomNm_to_sel").val();
                distToComp.push(d_from+":"+an_from+"-"+d_to+":"+an_to);
            }
        });
        return distToComp.join();

    }

    function obtainTrajUsedInDistComputatiion(res_ids){
        if (res_ids){
            var traj_id = $(".trajForDist:selected").val();
            var traj_path = $(".trajForDist:selected").attr("name");
            if (traj_id){
                return ([traj_path,traj_id]);
            }
        }
        return (false);
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


    function updateframeFromPlot(mychart,array_f){
        var mysel = mychart.getSelection()[0];
        if (mysel){        
            var frame_num=array_f[mysel.row+1][0];
            //var frameinput_sel=$('#embed_mdsrv')[0].contentWindow.$("#trajRange");
            //frameinput_sel.val(frame_num);
            //frameinput_sel.slider("refresh");
            $('#embed_mdsrv')[0].contentWindow.$('body').trigger('changeframeNGL', [ frame_num ]);
        }
    }


    $(".analysis_traj_sel").change(function(){
        if (trajidtoframenum){
            var seltrajid=$(this).children(":selected").data("trajid");
            var newstride=trajidtoframenum[seltrajid][1];
            newstride=newstride.toString();
            var selector_strideinp=$(this).data("analysisstride");
            var strideinp_obj=$(selector_strideinp);
            strideinp_obj.data("default",newstride);
            strideinp_obj.attr("placeholder",newstride)
        }
    })

    var chart_img={};
    var d_id=1;
    $("#gotoDistPg").click(function(){ // if fistComp="" or no traj is selected do nothing
        numComputedD = $("#dist_chart").children().length;
        $("#dist_stride_parent").removeClass("has-warning");

        $(".dist_btw dist_from_parent").removeClass("has-error");
        $(".dist_btw .has-error").removeClass("has-error");

        if (numComputedD < 15){
            $(".dist_btw input").each(function(){ 
                if (!$(this).val()){
                    $(this).parent().addClass("has-error");
                }
            });
            var res_ids = obtainDistToComp();
            if ($(this).attr("class").indexOf("withTrajs") > -1){
                var traj_results=obtainTrajUsedInDistComputatiion(res_ids);
                if (traj_results){        
                    var traj_p=traj_results[0];
                    var traj_id=traj_results[1];
                    
                    var stride = strideVal("#dist_stride");
                    $("#dist_chart").append("<p style='margin-top:5px;padding:5px;background-color:#e6e6ff;border-radius:3px;' id='wait_dist'><span class='glyphicon glyphicon-time'></span> Computing distances...</p>");
                    $("#gotoDistPg").addClass("disabled");
                    $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int, #downl_json_hb").addClass("disabled");
                    act_dis_plots=[];
                    $("#dist_chart").children(".dist_plot").each(function(){
                        act_dis_plots.push($(this).data("dist_id"));
                    });
                    var t0= performance.now();
                    $.ajax({
                        type: "POST",
                        url: "/view/"+dyn_id+"/",  //Change 1 for actual number
                        dataType: "json",
                        data: { 
                          "distStrWT": struc,
                          "distTraj": traj_p,
                          "dist_atmsWT": res_ids,
                          "no_rv" :act_dis_plots.join(),
                          "stride" : stride,
                        },
                        success: function(data_dist_wt) {
                            $("#wait_dist").remove();
                            $("#gotoDistPg").removeClass("disabled");
                            var success=data_dist_wt.success;
                            if (success){
                                var small_error=data_dist_wt.msg;
                                var strided=data_dist_wt.strided;
                                var isEmpty = data_dist_wt.isEmpty;
                                var dist_pair_new=data_dist_wt.dist_pair_new;
                                var strideText="";
                                if (Number(strided)> 1){
                                    strideText = ", str: "+strided;
                                }
                                if (isEmpty){
                                    var errors_html="";
                                    for (error_msg=0; error_msg< small_error.length; error_msg++){
                                        errors_html+="<p>"+small_error[error_msg]+"</p>";
                                    }
                                    errors_html_div='<div style="margin:3px;clear:left" class="alert alert-warning"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>'+errors_html+'</div>';
                                    
                                    var patt = /[^/]*$/g;
                                    var trajFile = patt.exec(traj_p);
                                    var noDist_msg="<div class='empty_dist_plot' style='border:1px solid #F3F3F3;padding:10px;'>\
                                            <div style='font-size:12px;margin-bottom:5px' ><b>Residue Distance ("+trajFile+")</b></div>"
                                            +errors_html_div+
                                            "<div style='display:inline-block;margin:5px;color:#DC143C;cursor:pointer;vertical-align:-2px'>\
                                                <span title='Delete' class='glyphicon glyphicon-trash delete_empty_dist_plot' ></span>\
                                            </div>\
                                    </div>";
                                    $("#dist_chart").append(noDist_msg);
                                    
                                } else {
                                    var dist_array_t=data_dist_wt.result_t;
                                    var dist_array_f=data_dist_wt.result_f;
                                    var dist_id=data_dist_wt.dist_id;
                                    function drawChart(){
                                        var patt = /[^/]*$/g;
                                        var trajFile = patt.exec(traj_p);
                                        var data_t = google.visualization.arrayToDataTable(dist_array_t,false);
                                        var data_f = google.visualization.arrayToDataTable(dist_array_f,false);
                                        /*var widthval = (dist_array_t.length -1)*1.18;
                                        if (widthval < 640){
                                            widthval = 640;
                                        }
                                        */
                                        var options_t = {'title':'Residue Distance ('+trajFile+strideText+')',
                                            "height":350, "width":640, "legend":{"position":"right","textStyle": {"fontSize": 10}}, 
                                            "chartArea":{"right":"120","left":"65","top":"50","bottom":"60"},hAxis: {title: "Time (ns)"},vAxis: {title: 'Distance (angstroms)'},
                                            "tooltip": { "trigger": 'selection' }
                                        };
                                        var options_f = {'title':'Residue Distance ('+trajFile+strideText+')',
                                            "height":350, "width":640, "legend":{"position":"right","textStyle": {"fontSize": 10}}, 
                                            "chartArea":{"right":"120","left":"65","top":"50","bottom":"60"},hAxis: {title: "Frame number"},vAxis: {title: 'Distance (angstroms)'},
                                            "tooltip": { "trigger": 'selection' }
                                        };
                                        newgraph_sel="dist_chart_"+d_id.toString();
                                        var plot_html;
                                        var dyn_id=$(".str_file").data("dyn_id");
                                        if ($.active<=1){
                                            plot_html="<div class='dist_plot' id='all_"+newgraph_sel+"' data-dist_id="+dist_id+" style='border:1px solid #F3F3F3;overflow:auto;overflow-y:hidden;-ms-overflow-y: hidden;'>\
                                                            <div class='dist_time' id='"+newgraph_sel+"t'></div>\
                                                            <div class='dist_frame' id='"+newgraph_sel+"f'></div>\
                                                            <div class='settings' style='margin:5px'>\
                                                                <div class='plot_dist_by_sel_cont' style='font-size:12px;margin-left:5px'>\
                                                                  <p>Plot distance by</p>\
                                                                    <span >\
                                                                        <select class='plot_dist_by_sel' name='frame_time'>\
                                                                            <option class='plot_dist_by' selected value='time'>time</option>\
                                                                            <option class='plot_dist_by' value='frame'>frame</option>\
                                                                        </select>\
                                                                    </span>\
                                                                </div>\
                                                                <div style='display:inline-block;margin:5px;cursor:pointer;'>\
                                                                    <a role='button' class='btn btn-link save_img_dist_plot settingsB' href='#' target='_blank' style='color:#585858;margin-right:0;margin-left;padding-right:0;padding-left:0;margin-bottom:3px'>\
                                                                        <span  title='Save plot as image' class='glyphicon glyphicon-stats'></span>\
                                                                    </a>\
                                                                </div>\
                                                                <div style='display:inline-block;margin:5px;'>\
                                                                    <a role='button' class='btn btn-link href_save_data_dist_plot settingsB' href='/view/dwl/"+dyn_id+"/"+dist_id+"' style='color:#585858;margin-right:0;margin-left;padding-right:0;padding-left:0;margin-bottom:3px'>\
                                                                        <span  title='Save data' class='glyphicon glyphicon-download-alt save_data_dist_plot'></span>\
                                                                    </a>\
                                                                </div>\
                                                                <div style='display:inline-block;margin:5px;color:#DC143C;cursor:pointer;vertical-align:-2px'>\
                                                                    <span title='Delete' class='glyphicon glyphicon-trash delete_dist_plot' data-dist_id='"+dist_id+"'></span>\
                                                                </div>\
                                                                <div class='checkbox' style='font-size:12px;display:inline-block'>\
		                                                            <label><input type='checkbox' name='view_this_dist' checked class='display_this_dist' data-this_dist="+dist_pair_new+" data-traj_id="+traj_id+">Display distance</label>\
                                                                </div>\
                                                            </div>\
                                                        </div>";
                                        }else{
                                            plot_html="<div class='dist_plot' id='all_"+newgraph_sel+"' data-dist_id="+dist_id+" style='border:1px solid #F3F3F3;overflow:auto;overflow-y:hidden;-ms-overflow-y: hidden;'>\
                                                            <div class='dist_time' id='"+newgraph_sel+"t'></div>\
                                                            <div class='dist_frame' id='"+newgraph_sel+"f'></div>\
                                                            <div class='settings' style='margin:5px'>\
                                                                <div class='plot_dist_by_sel_cont' style='font-size:12px;margin-left:5px'>\
                                                                  <p>Plot distance by</p>\
                                                                    <span >\
                                                                        <select  name='frame_time' class='plot_dist_by_sel'>\
                                                                            <option class='plot_dist_by' selected value='time'>time</option>\
                                                                            <option class='plot_dist_by' value='frame'>frame</option>\
                                                                        </select>\
                                                                    </span>\
                                                                </div>\
                                                            <div style='margin:5px'>\
                                                                <div style='display:inline-block;margin:5px;cursor:pointer;'>\
                                                                    <a role='button' class='btn btn-link save_img_dist_plot settingsB' href='#' target='_blank' style='color:#585858;margin-right:0;margin-left;padding-right:0;padding-left:0;margin-bottom:3px'>\
                                                                        <span  title='Save plot as image' class='glyphicon glyphicon-stats'></span>\
                                                                    </a>\
                                                                </div>\
                                                                <div style='display:inline-block;margin:5px;'>\
                                                                    <a role='button' class='btn btn-link href_save_data_dist_plot disabled settingsB' href='/view/dwl/"+dyn_id+"/"+dist_id+"' style='color:#585858;margin-right:0;margin-left;padding-right:0;padding-left:0;margin-bottom:3px'>\
                                                                        <span  title='Save data' class='glyphicon glyphicon-download-alt save_data_dist_plot'></span>\
                                                                    </a>\
                                                                </div>\
                                                                <div style='display:inline-block;margin:5px;color:#DC143C;cursor:pointer;vertical-align:-2px'>\
                                                                    <span title='Delete' class='glyphicon glyphicon-trash delete_dist_plot' data-dist_id='"+dist_id+"'></span>\
                                                                </div>\
                                                                <div class='checkbox' style='font-size:12px;display:inline-block'>\
		                                                            <label><input type='checkbox' name='view_this_dist' checked class='display_this_dist' data-this_dist="+dist_pair_new+" data-traj_id="+traj_id+">Display distance</label>\
                                                                </div>\
                                                            </div>\
                                                        </div>";                            
                                        } 
                                        $("#dist_chart").append(plot_html);
                                        var chart_cont_li =[[newgraph_sel+"f",data_f,options_f],[newgraph_sel+"t",data_t,options_t]];

                                        var chart_cont=chart_cont_li[0][0];
                                        var data=chart_cont_li[0][1];
                                        var options=chart_cont_li[0][2];
                                        var chart_div = document.getElementById(chart_cont);
                                        var chart0 = new google.visualization.LineChart(chart_div);                                
                                        google.visualization.events.addListener(chart0, 'ready', function () {
                                            var img_source =  chart0.getImageURI(); 
                                            $("#"+chart_cont).attr("data-url",img_source);
                                        });                                
                                        chart0.setAction({
                                          id: "c0",
                                          text: 'Display frame on viewer',
                                          action: function() {
                                            updateframeFromPlot(chart0,dist_array_f);
                                          }
                                        });
                                        chart0.draw(data, options);                                
//                                        google.visualization.events.addListener(chart0, 'select', function(){  
//                                            updateframeFromPlot(chart0,dist_array_f);
//                                        });


                                        var chart_cont=chart_cont_li[1][0];
                                        var data=chart_cont_li[1][1];
                                        var options=chart_cont_li[1][2];
                                        var chart_div = document.getElementById(chart_cont);
                                        var chart1 = new google.visualization.LineChart(chart_div);                                
                                        google.visualization.events.addListener(chart1, 'ready', function () {
                                            var img_source =  chart1.getImageURI(); 
                                            $("#"+chart_cont).attr("data-url",img_source);
                                        }); 

                                        chart1.setAction({
                                          id: "c1",
                                          text: 'Display frame on viewer',
                                          action: function() {
                                            updateframeFromPlot(chart1,dist_array_f);
                                          }
                                        });


                                        chart1.draw(data, options);                                    
//                                        google.visualization.events.addListener(chart1, 'select', function(){  
//                                            updateframeFromPlot(chart1,dist_array_f);
//                                        });

///////////////////
//                                        for (chartN=0 ; chartN < chart_cont_li.length ; chartN++){
//                                            var chart_cont=chart_cont_li[chartN][0];
//                                            var data=chart_cont_li[chartN][1];
//                                            var options=chart_cont_li[chartN][2];
//                                            var chart_div = document.getElementById(chart_cont);
//                                            var chart = new google.visualization.LineChart(chart_div);                                
//                                            google.visualization.events.addListener(chart, 'ready', function () {
//                                                var img_source =  chart.getImageURI(); 
//                                                $("#"+chart_cont).attr("data-url",img_source);
//                                            });                                
//                                            chart.draw(data, options);                                    
//
//                                        }
///////////////////
                                        $("#"+newgraph_sel+"f").css("display","none");  
                                        var img_source_t=$("#"+newgraph_sel+"t").data("url");
                                        $("#"+newgraph_sel+"t").siblings(".settings").find(".save_img_dist_plot").attr("href",img_source_t);
                                        
                                        if (small_error){
    //////////////////
                                            var errors_html="";
                                            for (error_msg=0 ; error_msg < small_error.length ; error_msg++){
                                                errors_html+="<p>"+small_error[error_msg]+"</p>";
                                            }
                                            errors_html_div='<div style="margin:3px;clear:left" class="alert alert-warning"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>'+errors_html;
                                                                    
    /////////////////
                                        
                                            //var di_Serror='<div style="margin:3px;clear:left" class="alert alert-warning"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a><p>'+small_error+'</p></div>';
                                            $("#all_"+newgraph_sel).find(".settings").after(errors_html_div);
                                        }
                                        
                                        $("#all_"+newgraph_sel).find(".display_this_dist").attr("checked","true");
                                        $("#selectionDiv").trigger("click");
                                        
                                        d_id+=1;
                                        
                                    }
                                    google.load("visualization", "1", {packages:["corechart"],'callback': drawChart});
                                }
                            } else {
                                var msg=data_dist_wt.msg;
                                add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>'+ msg;
                                $("#dist_alert").html(add_error);                
                            }
                            if ($.active<=1){
                                $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int, #downl_json_hb").removeClass("disabled");
                            }
                            var t1=performance.now();
                        },
                        error: function() {
                            $("#gotoDistPg").removeClass("disabled");
                            $("#wait_dist").remove();
                            if ($.active<=1){
                                $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int, #downl_json_hb").removeClass("disabled");
                            }
                            add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>An unexpected error occurred.';
                            $("#dist_alert").html(add_error);                
                        },
                        timeout: 600000
                    });
                    $("#dist_alert").html("");
                } else {
                    add_error_d='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>Some fields are empty or contain errors. E.g. select a pair of atoms in the GPCRmd viewer and import the distance by clicking on the <span class="glyphicon glyphicon-circle-arrow-down" style="color:#1e90ff;font-size:10px;margin:0;padding:0"></span> icon.';
                    $("#dist_alert").html(add_error_d);
                }
            } else {
                if (res_ids){
                    $("#dist_alert").html("");
                    $.ajax({
                        type: "POST",
                        url: "/view/"+dyn_id+"/",  
                        dataType: "json",
                        data: { 
                          "distStr": struc,
                          "dist_resids": res_ids,
                        },
                        success: function(data_dist) {
                            var success=data_dist.success;
                            if (success){
                                dist_result=data_dist.result;
                            }else{ 
                                var msg=data_dist.msg;
                                add_error_d='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>'+ msg;
                                $("#dist_alert").html(add_error_d);       
                            }
                        },
                        error: function() {
                            
                            $("#dist_alert").html(add_error_d);             
                        },
                        timeout: 600000
                    });
                } else {
                    add_error_d='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>Some fields are empty or contain errors. E.g. select a pair of atoms in the GPCRmd viewer and import the distance by clicking on the <span class="glyphicon glyphicon-circle-arrow-down" style="color:#1e90ff;font-size:10px;margin:0;padding:0"></span> icon.';
                    $("#dist_alert").html(add_error_d);
                }
            }
        } else {
            add_error_d='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>Please, remove some distance results to obtain new ones.';
            $("#dist_alert").html(add_error_d);
        }
    });

    $("#dist_chart").on("change",".plot_dist_by_sel", function(){
        xAxis=$(this).val();
        var dist_frame_cont=$(this).closest(".settings").siblings(".dist_frame");
        var dist_time_cont=$(this).closest(".settings").siblings(".dist_time");
        if (xAxis == "time"){
            dist_frame_cont.css("display","none");
            dist_time_cont.css("display","inline");            
            var img_source=dist_time_cont.data("url");
            $(this).closest(".settings").find(".save_img_dist_plot").attr("href",img_source);

        } else {            
            dist_time_cont.css("display","none");
            dist_frame_cont.css("display","inline");
            var img_source=dist_frame_cont.data("url");
            $(this).closest(".settings").find(".save_img_dist_plot").attr("href",img_source);
        }
    });

    $('body').on('click','.delete_dist_plot', function(){
        var isChecked=$(this).closest(".dist_plot").find(".display_this_dist").is(":checked");
        var plotToRv=$(this).parents(".dist_plot").attr("id");
        $('#'+plotToRv).remove();
        if (isChecked){
            $("#selectionDiv").trigger("click");
        }
    });
    
    $('body').on('click','.delete_empty_dist_plot', function(){
        $(this).closest(".empty_dist_plot").remove();
    });
   

    function displayCheckedDists(){
        var dist_li=[];
        $(".display_this_dist:checked").each(function(){
            dist_li[dist_li.length]=$(this).data("this_dist");
            var tr_id_act=$(this).data("traj_id");
            $("#traj_id_"+tr_id_act)[0].checked=true;
        });
        return uniq(dist_li);
    }
    
    $("#dist_chart").on("change" ,".display_this_dist" , function(){
        $("#selectionDiv").trigger("click");
    });
//-------- Select protein segment to highligh/select from the sequence --------

    var firstsel=true;
    function selectFromSeq(seqcellClass,sectionSel,prefix,hideApplyBtn,isEDmap){//
        //seqcellClass: name of class of the cells cotnianing the sequence positions (without the ".")
        //sectionSel: selector of the section of the Sequence selection. Ex: '#seqselection_all'
        //hideApplyBtn is true if apply button is hidden when no selection is made. If this is set for more than one sequence selection instance, var firstsel have to be made independent for each of them.
        var seqcellSel="."+seqcellClass;
        var click_n=1;
        var seq_pos_1;
        var seq_pos_fin;
        var pos_li=[];
        $(seqcellSel).click(function(){    
            if (click_n==1){
                var range=$(this).attr("class"); 
                if(range.indexOf("-") == -1){     //Start a new selection
                    $(this).css("background-color","#337ab7"); 
                    var cell1_ind = $(this).attr("id");
                    seq_pos_1=cell1_ind.replace(prefix,"");
                    click_n=2;
                } else {      // Remove an old selection
                    var selRange= range.match(/(\d)+/g);
                    i=Number(selRange[0]);
                    end=Number(selRange[1]);
                    while (i <= end) {
                        var mid_id="#" +prefix+ String(i);
                        $(mid_id).css("background-color","#f2f2f2");
                        $(mid_id).attr("class", seqcellClass);
                        i++;
                    }
                    if (hideApplyBtn){
                        if ($( seqcellSel+".sel").length== 0){
                            $(sectionSel).find(".hideIfNone").css("display","none");
                            firstsel=true;
                        }
                    }
                    if (isEDmap){
                        if ($("#ED_addToSel").hasClass("active")){
                            applyEDSeqsel(".ed_seq_sel","#ED_addToSel");
                            //createEDReps(true);
                            $("#EDselectionDiv").trigger("click");
                            //$("#selectionDiv").trigger("click");
                        }
                    }
                }
            } else  {
                // Finish a selection
                click_n=1;
                var cellfin_ind=$(this).attr("id");
                seq_pos_fin = Number(cellfin_ind.replace(prefix,""));
                var i = Number(seq_pos_1);
                while (i <= seq_pos_fin){
                    var mid_id="#" +prefix+ String(i);
                    $(mid_id).css("background-color","#34b734");
                    $(mid_id).children().css("background-color","");
                    $(mid_id).attr("class", seqcellClass+" sel " + seq_pos_1+"-"+seq_pos_fin); 
                    i++;
                }
                if (hideApplyBtn){
                    var applyselbtn=$(sectionSel).find(".hideIfNone");
                    if (firstsel){
                        applyselbtn.css("display","inline");
                        firstsel=false;
                    }
                    applyselbtn.popover('show');
                    setTimeout(function() {
                        applyselbtn.popover('hide');
                    }, 1000);
                }
                if (isEDmap){
                    if ($("#ED_addToSel").hasClass("active")){
                        applyEDSeqsel(".ed_seq_sel","#ED_addToSel");
                        //createEDReps(true);
                        $("#EDselectionDiv").trigger("click");
                        //$("#selectionDiv").trigger("click");
                    } else {
                        $("#ED_addToSel").popover('show');
                        setTimeout(function() {
                            $("#ED_addToSel").popover('hide');
                        }, 1000);
                    }
                }

            }
        });
   
        $(seqcellSel).hover(function(){
            if (click_n==2) {
                var cell2_ind=$(this).attr("id");
                var seq_pos_2 =Number(cell2_ind.replace(prefix,""));
                var i = Number(seq_pos_1);
                while (i <= seq_pos_2){
                    var mid_id="#"+prefix + String(i);
                    $(mid_id).children().css("background-color","#337ab7");
                    i++;
                }
            } else {
                if (! $(this).hasClass("sel")){
                    $(this).children().css("background-color","#D3D3D3");
                }
            }
        }, function(){
            if (click_n==2) {
                var cell2_ind=$(this).attr("id");
                var seq_pos_2 =Number(cell2_ind.replace(prefix,""));
                var i = Number(seq_pos_1);
                while (i <= seq_pos_2){
                    var mid_id="#"+prefix + String(i);
                    $(mid_id).children().css("background-color","");
                    i++;
                }
            } else {
                if (! $(this).hasClass("sel")){
                    $(this).children().css("background-color","");
                }
            }
        });
    }
    selectFromSeq("seq_sel","#seq_sel_div","",true,false);
    selectFromSeq("ed_seq_sel","#ed_seq_sel_div","ed_",false,true);

    function fromIdsToPositions(id_l, id_r){
        var pos_l=$(id_l).children("#ss_pos").text();
        var pos_r=$(id_r).children("#ss_pos").text();
        return [pos_l, pos_r];
    }

    function fromIdsToPositionsInChain(id_l, id_r){
        var pos_l=$(id_l).children("#ss_pos").text();
        var pos_r=$(id_r).children("#ss_pos").text();
        var chain_l = $(id_l).children("#ss_pos").attr("class");            
        var chain_r = $(id_r).children("#ss_pos").attr("class");
        if (chain_l==chain_r){
            var pos_chain_str=pos_l + "-" +pos_r+":"+chain_l;
        } else {
            start=all_chains.indexOf(chain_l);
            end=all_chains.indexOf(chain_r);
            var middle_str="";
            considered_chains=all_chains.slice(start+1,end);
            for (chain=0; chain < considered_chains.length ; chain++){
                middle_str += " or :"+ considered_chains[chain];
            }
            var pos_chain_str= pos_l + "-:"+chain_l +middle_str +" or 1-"+pos_r+":" +chain_r;
        }
        return pos_chain_str;
    }


    function joinContiguousRanges(sel_ranges){
        var sel_ranges_def=[];
        var o_max;
        var o_min;
        sel_ranges=uniq(sel_ranges);
        if (chains_str == ""){
            for (p=0 ; p < sel_ranges.length ; p++){
                var my_range_str=sel_ranges[p];
                var my_range = my_range_str.match(/(\d)+/g);
                var my_min=my_range[0];
                var my_max=my_range[1];
                if (o_min > 0 && Number(my_min) == Number(o_max)+1){ //CHeck what is 1st pos is old last +1
                    var pos_lr=fromIdsToPositions("#"+o_min, "#"+my_max);
                    sel_ranges_def[sel_ranges_def.length -1]= pos_lr[0]+"-"+pos_lr[1];
                    o_max = my_max;
                } else {
                    var pos_lr=fromIdsToPositions("#"+my_min, "#"+my_max);
                    sel_ranges_def[sel_ranges_def.length]=pos_lr[0]+"-"+pos_lr[1];
                    o_max = my_max;
                    o_min = my_min;
               }
            }
        } else { 
            for (p=0 ; p < sel_ranges.length ; p++){
                var my_range_str=sel_ranges[p];
                var my_range = my_range_str.match(/(\d)+/g);
                var my_min=my_range[0];
                var my_max=my_range[1];
                if (o_min > 0 && Number(my_min) == Number(o_max)+1){ //CHeck what is 1st pos is old last +1
                    var pos_chain_str=fromIdsToPositionsInChain("#"+o_min, "#"+my_max);
                    sel_ranges_def[sel_ranges_def.length -1]= pos_chain_str;
                    o_max = my_max;
                } else {
                    var pos_chain_str=fromIdsToPositionsInChain("#"+my_min, "#"+my_max);
                    sel_ranges_def[sel_ranges_def.length]=pos_chain_str;
                    o_max = my_max;
                    o_min = my_min;
               }
            }
        }
        return sel_ranges_def;
    }


    function obtainSelectedAtSeq(sectionSel){
        var sel_ranges=[];
        $(sectionSel+".sel").each(function(){
            var class_str=$(this).attr("class");
            var id_range= class_str.match(/(\d)+/g);
//            var sel_range=clickSelRange($(this).attr("class"));
            sel_ranges[sel_ranges.length]=id_range[0]+"-"+id_range[1];
        });
        return(sel_ranges);
    }

    function obtainSelectionFromRanges(sel_ranges_ok){
        var pos_str="";
        p=0;
        while (p < (sel_ranges_ok.length -1)) {
            pos_str += sel_ranges_ok[p] + " or ";
            p ++;
        }
        pos_str += sel_ranges_ok[sel_ranges_ok.length-1];
        var fin_val = "protein and ("+ pos_str +")";
        return (fin_val);
    };

    $("#addToSel").click(function(){ 
        $("#seq_input_all").css("display","inline");
        $("#seq_input_all").find(".si_add_btn:last").css("visibility","visible");
        sel_ranges=obtainSelectedAtSeq(".seq_sel");
        if (sel_ranges.length > 0){
            sel_ranges_ok=joinContiguousRanges(sel_ranges);
            var fin_val=obtainSelectionFromRanges(sel_ranges_ok);

            var sel_input_cont=$(".seq_input_row:last-child").find(".seq_input");
            var act_val=sel_input_cont.val();
            if (act_val){
                var fin_val = "("+act_val + ") or "+fin_val;
            } 
            sel_input_cont.val(fin_val);
            seq_ids.length = 0
            $('.sel').each(function(){
                seq_ids.push(Number(this.id));
            });

            residueslist=[]
            for (i=0;i<seq_ids.length;i++){
                parentid='#'+seq_ids[i].toString();
                residue=$(parentid).children('#ss_seq').html()+$(parentid).children('#ss_pos').html()
                residueslist.push(residue);
            }

            var basehtml='<input type="radio" name="sasa_sel" value="sequence"> Sequence Selection '
            if (residueslist.length < 4){
                $('#show_seq_sel').html(basehtml+'('+residueslist.join(', ')+')');
            }else{
                shortlist=residueslist[0]+', ... , '+residueslist[residueslist.length-1];
                $('#show_seq_sel').html(basehtml+'('+shortlist+')');
            }
            $("#selectionDiv").trigger("click");
        }
    });    

    /*$("#rmds_my_sel_id").click(function(){
        if ($("#rmsd_my_sel_sel").val() == ""){
            rmsdMySel=$(".sel_input").val();
            if (rmsdMySel){
                $("#rmsd_my_sel_sel").val(rmsdMySel);
            }
        }
    });*/

//-------- H bonds computation --------


    function showErrorInblock(selector, error_msg){
         var sel_fr_error="<div style='color:#DC143C'>" + error_msg + "</div>";
         $(selector).html(sel_fr_error);
    }
    
    function showBigError(msg,selector){
        add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>'+ msg;
        $(selector).html(add_error);  
    }
    

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
    


    function hbond_dict_to_sorted_li(hbonds){
        var hbonds_li=[];
        for (don_res in hbonds){
            var acc_li=hbonds[don_res];
            for (aN=0;aN<acc_li.length;aN++){
                var acc_info=acc_li[aN];
                var acc_res=acc_info[0];
                var freq=acc_info[1];
                var atom0=acc_info[2];
                var atom1=acc_info[3];
                var chain0=acc_info[4];
                var chain1=acc_info[5];
                hbonds_li[hbonds_li.length]=[don_res,acc_res,freq,atom0,atom1,chain0,chain1];
            }
        }
        hbonds_li.sort(function(a, b){return Number(b[2]) - Number(a[2])});
        return hbonds_li
    }


    function hb_sb_transfballes(balles){    
        if (balles=="-"){
            balles="";
        } else {
            balles=' | '+balles;
        }
        return balles;
    }


    function changeDownloadURLS(mytraj,sel_li){//
        for (var i=0;i<sel_li.length;i++){
            var mysel=sel_li[i];
            var linkel=$(mysel);
            var linkroot=linkel.data("linkroot");
            linkel.attr("href",linkroot+"/"+mytraj);    
        }
    }

    function check_res_isheavy(acceptor_str){
        for (cl=0; cl<comp_loadheavy.length; cl++){
            var heavycomp=comp_loadheavy[cl];
            if (Number(heavycomp.slice(-1))){ //If ends by number
                if (acceptor_str.startsWith(heavycomp)){
                    return true
                }
            } else {
                acceptor_resname=acceptor_str.replace(/\d+$/,"");
                if (acceptor_resname == heavycomp){
                    return true
                }

            }
        }
        return false
    }

    $("#analysis_bonds").on("click",".hbond_openchose_click", function(){
        var target=$(this).attr("data-target");
        var upOrDown=$(target).attr("class");
        var hbonds_type=$(this).closest(".hbonds_both");
        var type_btn_id=hbonds_type.attr("id") + "_btn";
        var btns_el=hbonds_type.siblings("#"+type_btn_id);
        var arrow=$(this).find(".hbond_openchose_arrow");
        if(upOrDown.indexOf("in") > -1){
            arrow.removeClass("glyphicon-chevron-up");
            arrow.addClass("glyphicon-chevron-down");
            btns_el.css("display","none");
        } else {
            arrow.removeClass("glyphicon-chevron-down");
            arrow.addClass("glyphicon-chevron-up");
            btns_el.css("display","block");
        }
    })

    var r_id=1;

    $("#ComputeHbonds").click(function(){
        $("#bonds_alert").html("");
        $("#hbonds_sel_frames_error").html("");
        $('#ShowAllHbInter').css("visibility","hidden");
        $('#ShowAllHbIntra').css("visibility","hidden");
        var struc = $(".str_file").data("struc_file");
        var dyn_id=$(".str_file").data("dyn_id");
        rmsdTraj=$("#hbonds_traj").val();
        backbone=$("#bonds_backbone input[name=backbone]:checked").val()=='all';
        neigh=$("#bonds_backbone input[name=neighbours]:checked").length>0;
        rmsdFrames=$("#bonds_sel_frames_id input[name=bonds_sel_frames]:checked").val();
        cutoff=$("#hbonds_cutoff").val();
        if (cutoff == ""){
            cutoff =$("#hbonds_cutoff").attr("placeholder");
        }
        if (rmsdFrames=="bonds_frames_mine"){
            frameFrom=$("#bonds_frame_1").val();
            frameTo=$("#bonds_frame_2").val();
            var framesOk=true;
            if (!frameFrom){
                $("#bonds_frame_1").parent().addClass("has-error");
                framesOk=false;
            }
            if (!frameTo){
                $("#bonds_frame_2").parent().addClass("has-error");
                framesOk=false;
            }
            if (framesOk) {
                if (/^[\d]+$/.test(frameFrom + frameTo)){
                    if (Number(frameFrom) < Number(frameTo)){
                        rmsdFrames=frameFrom + "-" + frameTo;
                    } else {
                        showErrorInblock("#hbonds_sel_frames_error", "Initial frame must be lower than final frame.");
                        rmsdFrames=false;
                    }
                } else {
                    showErrorInblock("#hbonds_sel_frames_error", "Input must be a number.");
                    rmsdFrames=false;
                }
            } else {
                rmsdFrames=false;
            }
        }else{
            frameFrom=0;
            frameTo=-1;
        }
        if (rmsdFrames == false){
            var msn="Some fields are empty or contain errors";
            showBigError(msn, "#bonds_alert");
        } else {
            $(".hbond_openchose_click").each(function(){
                //if (!($(this).hasClass("collapsed"))){
                if ($(this).attr("aria-expanded") =="true"){
                    $(this).trigger("click");
                }
            })

            if ($("#bondsresult_par").css("display")!="none"){
                $("#blockbondsresult").css("display","block");
            }
            $("#ComputeHbonds").addClass("disabled");
            $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int, #downl_json_hb").addClass("disabled"); 
            $("#bondsresult_par").before("<p style='margin-top:5px;padding:5px;background-color:#e6e6ff;border-radius:3px;clear:left' id='wait_hbonds'><span class='glyphicon glyphicon-time'></span> Computing hydrogen bonds...</p>");   
            $.ajax({
                    type: "POST",
                    data: { "frames[]": [frameFrom,frameTo,cutoff,rmsdTraj,struc,dyn_id,backbone,neigh] },
                    url:"/view/hbonds/", 
                    dataType: "json",
                    success: function(data) {
                        $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int, #downl_json_hb").removeClass("disabled"); 
                        $("#wait_hbonds").remove();
                        changeDownloadURLS(rmsdTraj,[".href_save_data_hbp",".href_save_data_hbo"]);
                        $("#blockbondsresult").css("display","none");
                        $("#ComputeHbonds").removeClass("disabled");
                        hbonds=data.hbonds;
                        hbonds_np=data.hbonds_notprotein;
                        var regex = /\d+/g;
                        var table='<div class="hbond_openchose_click" data-toggle="collapse" data-target="#protprot_tablecont" style="font-size:14px; cursor:pointer;border-bottom:1px solid lightgray;background-color:f2f2f2;height:30px;border-radius:5px 0;">\
                                        <div style="padding:5px 10px">\
                                            <p>Protein-protein hydrogen bonds</p>\
                                            <span style="float:right;margin-right:5px;" class="glyphicon arrow glyphicon-chevron-down hbond_openchose_arrow"></span>\
                                        </div>\
                                     </div>\
                                    <div class="scrolldowndiv collapse"  id="protprot_tablecont" style="padding:5px">\
                                        <table id="intramol" class="table table-condesed" style="font-size:12px;">\
                                            <thead>\
                                                <tr>\
                                                    <th>Donor</th>\
                                                    <th>Acceptor</th>\
                                                    <th>Frequency</th>\
                                                    <th></th>\
                                            </thead><tbody>';
                        //gnumFromPosChain(pos, chain)
                        var sort_by="freq";
                        if (sort_by=="freq"){
                            var hbonds_li_sorted=hbond_dict_to_sorted_li(hbonds);
                            for (hN=0;hN<hbonds_li_sorted.length;hN++){
                                var donor_str=hbonds_li_sorted[hN][0];
                                var acceptor_str=hbonds_li_sorted[hN][1];
                                var freq=hbonds_li_sorted[hN][2];
                                var atom0=hbonds_li_sorted[hN][3];
                                var atom1=hbonds_li_sorted[hN][4];
                                var chain0=hbonds_li_sorted[hN][5];
                                var chain1=hbonds_li_sorted[hN][6];

                                var donor = donor_str.match(regex)[0];  // creates array from matches
                                var acceptor = acceptor_str.match(regex)[0];  // creates array from matches
                                donorballes=gnumFromPosChain(String(donor),chain0)
                                donorballes=hb_sb_transfballes(donorballes);
                                acceptorballes=gnumFromPosChain(String(acceptor),chain1)
                                acceptorballes=hb_sb_transfballes(acceptorballes);
                                table=table+'<tr> \
                                                <td>'+ donor_str+donorballes+'</td>\
                                                <td> '+acceptor_str+acceptorballes+'</td>\
                                                <td> '+freq+'% </td>\
                                                <td>\
                                                    <button class="showhb btn btn-default btn-xs clickUnclick"  data-resids='+ donor + '$%$' + acceptor +' \
                                                        data-atomindexes='+atom0+'$%$'+atom1+'>Show Hbond</button>' ;
                            }

                        } else if (sort_by=="donor-acceptor"){ // I leave it in case in the future I want to add the option to switch between sorting methods
                            for (var property in hbonds) {
                                if (hbonds.hasOwnProperty(property)) {
                                    var string =property;
                                    var string2 =hbonds[property][0][0];
                                    var donor = string.match(regex)[0];  // creates array from matches
                                    var acceptor = string2.match(regex)[0];  // creates array from matches
                                    donorballes=gnumFromPosChain(String(donor),hbonds[property][0][4])
                                    donorballes=hb_sb_transfballes(donorballes);
                                    acceptorballes=gnumFromPosChain(String(acceptor),hbonds[property][0][5])
                                    acceptorballes=hb_sb_transfballes(acceptorballes);

                                    table=table+'<tr> \
                                                    <td rowspan='+ hbonds[property].length.toString() + '>'+ property+donorballes+'</td>\
                                                    <td> '+hbonds[property][0][0]+acceptorballes+'</td>\
                                                    <td> '+hbonds[property][0][1]+'% </td>\
                                                    <td><button class="showhb btn btn-default btn-xs clickUnclick"  data-resids='+ donor + '$%$' + acceptor +' data-atomindexes='+hbonds[property][0][2]+'$%$'+hbonds[property][0][3]+'>Show Hbond</button>' ;
                                    for (index = 1; index < hbonds[property].length; ++index) {
                                        var string2 =hbonds[property][index][0];
                                        var acceptor = string2.match(regex)[0];  // creates array from matches
                                        acceptorballes=gnumFromPosChain(String(acceptor),hbonds[property][index][5])
                                        acceptorballes=hb_sb_transfballes(acceptorballes);
                                        table=table+'<tr>\
                                            <td>'+hbonds[property][index][0]+acceptorballes+' </td>\
                                            <td>'+hbonds[property][index][1]+'% </td>\
                                            <td><button class="showhb btn btn-default btn-xs clickUnclick" data-resids='+ donor + '$%$' + acceptor +' data-atomindexes='+hbonds[property][index][2]+'$%$'+hbonds[property][index][3]+'>Show Hbond</button></td>';
                                    }
                                }
                            }
                        }
                        table=table+'</table></div><center>';
                        $('#ShowAllHbIntra').css("visibility","visible");
                        $('#hbonds').html(table);

                        var tablenp='<div class="hbond_openchose_click" data-toggle="collapse" data-target="#protlip_tablecont" style="font-size:14px; cursor:pointer;border-bottom:1px solid lightgray;background-color:f2f2f2;height:30px;border-radius:5px 0;">\
                                        <div style="padding:5px 10px">\
                                            <p>Protein-lipid hydrogen bonds and other</p>\
                                            <span style="float:right;margin-right:5px;" class="glyphicon arrow glyphicon-chevron-down hbond_openchose_arrow"></span>\
                                        </div>\
                                     </div>\
                                        <div class="scrolldowndiv collapse" id="protlip_tablecont" style="padding:5px" >\
                                            <table id="intermol"  class="table table-condesed" style="font-size:12px;">\
                                                <thead>\
                                                    <tr>\
                                                        <th>Residue1</th>\
                                                        <th>Residue2</th>\
                                                        <th>Frequency</th>\
                                                        <th></th>   \
                                                    </tr>\
                                                </thead>\
                                                <tbody>';
                        
                        if (sort_by=="freq"){
                            var hbonds_li_sorted=hbond_dict_to_sorted_li(hbonds_np);
                            for (hN=0;hN<hbonds_li_sorted.length;hN++){
                                var donor_str=hbonds_li_sorted[hN][0];
                                var acceptor_str=hbonds_li_sorted[hN][1];
                                var acceptor_isheavy=check_res_isheavy(acceptor_str);
                                var leadheavyclass="";
                                if (acceptor_isheavy){
                                    leadheavyclass="load_heavy";
                                }
                                var freq=hbonds_li_sorted[hN][2];
                                var atom0=hbonds_li_sorted[hN][3];
                                var atom1=hbonds_li_sorted[hN][4];
                                var chain0=hbonds_li_sorted[hN][5];
                                var chain1=hbonds_li_sorted[hN][6];

                                var donor = donor_str.match(regex)[0];  // creates array from matches
                                var acceptor = acceptor_str.match(regex)[0];  // creates array from matches
                                donorballes=gnumFromPosChain(String(donor),chain0)
                                donorballes=hb_sb_transfballes(donorballes);
                                acceptorballes=gnumFromPosChain(String(acceptor),chain1)
                                acceptorballes=hb_sb_transfballes(acceptorballes);

                                tablenp=tablenp+'<tr> \
                                        <td>'+ donor_str+donorballes+'</td>\
                                        <td> '+acceptor_str+acceptorballes+' </td>\
                                        <td> '+freq+'% </td>\
                                        <td>\
                                            <button class="showhb_inter btn btn-default btn-xs clickUnclick '+leadheavyclass+'"  \
                                            data-resids='+ donor + '$%$' + acceptor +' \
                                            data-atomindexes='+atom0+'$%$'+atom1+'>Show Hbond</button></td>';
                            }

                        } else if (sort_by=="donor-acceptor"){
                            for (var property in hbonds_np) {
                                if (hbonds_np.hasOwnProperty(property)) {
                                    var string =property;
                                    var string2 =hbonds_np[property][0][0];
                                    if (/^\d/.test(string2)){
                                        var acceptor ="["+string2.replace(/\d*$/g,"")+"]";
                                        acceptorballes="";
                                    } else {
                                        var acceptor = string2.match(regex)[0];  // creates array from matches
                                        acceptorballes=gnumFromPosChain(String(acceptor),hbonds_np[property][0][5]) 
                                        acceptorballes=hb_sb_transfballes(acceptorballes);
                                    }
                                    
                                    var donor = string.match(regex)[0];  // creates array from matches
                                    donorballes=gnumFromPosChain(String(donor),hbonds_np[property][0][4])
                                    donorballes=hb_sb_transfballes(donorballes);

                                    tablenp=tablenp+'<tr> \
                                            <td rowspan='+ hbonds_np[property].length.toString() + '>'+ property+donorballes+'</td>\
                                            <td> '+hbonds_np[property][0][0]+acceptorballes+' </td>\
                                            <td> '+hbonds_np[property][0][1]+'% </td>\
                                            <td><button class="showhb_inter btn btn-default btn-xs clickUnclick"  data-resids='+ donor + '$%$' + acceptor +' data-atomindexes='+hbonds_np[property][0][2]+'$%$'+hbonds_np[property][0][3]+'>Show Hbond</button></td>';
                                    for (index = 1; index < hbonds_np[property].length; ++index) {
                                        var string2 =hbonds_np[property][index][0];
                                        if (/^\d/.test(string2)){
                                            var acceptor ="["+string2.replace(/\d*$/g,"")+"]";
                                            acceptorballes="-";
                                        } else {
                                            var acceptor = string2.match(regex)[0];  // creates array from matches
                                            acceptorballes=gnumFromPosChain(String(acceptor),hbonds_np[property][index][5])
                                            acceptorballes=hb_sb_transfballes(acceptorballes);
                                        }
                                        
                                        tablenp=tablenp+'<tr>\
                                            <td>'+hbonds_np[property][index][0]+acceptorballes+' </td>\
                                            <td>'+hbonds_np[property][index][1]+'% </td>\
                                            <td><button class="showhb_inter btn btn-default btn-xs clickUnclick"  data-resids='+ donor + '$%$' + acceptor +' data-atomindexes='+hbonds_np[property][index][2]+'$%$'+hbonds_np[property][index][3]+'>Show Hbond</button></td>';
                                    }
                                }
                            }
                        }

                        tablenp=tablenp+'</table></div><center>';
                        $('#ShowAllHbInter').css("visibility","hidden");;
                        $("#bondsresult_par").attr("style", "margin-top: 10px; margin-bottom: 15px; border:1px solid #F3F3F3;display:block;padding:0;border-radius:5px");
                        $('#hbondsnp').html(tablenp);
                        $('#ShowAllHbInter').css("visibility","visible");
                        $("#selectionDiv").trigger("click");
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                        $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int, #downl_json_hb").removeClass("disabled"); 
                        $("#wait_hbonds").remove();
                        $("#blockbondsresult").css("display","none");
                        $("#ComputeHbonds").removeClass("disabled");
                        if (XMLHttpRequest.readyState == 4) {
                            var responsetext = XMLHttpRequest.responseText;

                            alert(textStatus.substr(0,1).toUpperCase()+textStatus.substr(1)+":\nStatus: " + XMLHttpRequest.textStatus+". "+errorThrown+".\n"+responsetext);
                            showBigError("An error occurred.", "#bonds_alert");
                        }
                        else if (XMLHttpRequest.readyState == 0) {
                            var msn="Connection error. Please, try later and check that your file is not larger than 50 MB.";
                            showBigError(msn, "#bonds_alert");
                        }
                        else {
                            var msn="Unknown error.";
                            showBigError(msn, "#bonds_alert");
                        }
                    },
                    timeout: 600000
            }); 
        }
    });
    
//-------- Salt bridges computation --------

    $("#ComputeSaltBridges").click(function(){
        $("#salt_sel_frames_error").html("");
        $("#salt_alert").html("");
        var struc = $(".str_file").data("struc_file");
        var dyn_id=$(".str_file").data("dyn_id");
        rmsdTraj=$("#salt_traj").val();
        rmsdFrames=$("#salt_sel_frames_id input[name=salt_sel_frames]:checked").val();
        cutoff=$("#salt_cutoff").val();
        if (cutoff == ""){
            cutoff=$("#salt_cutoff").attr("placeholder");
        }
        if (rmsdFrames=="salt_frames_mine"){
            frameFrom=$("#salt_frame_1").val();
            frameTo=$("#salt_frame_2").val();
            var framesOk=true;
            if (!frameFrom){
                $("#salt_frame_1").parent().addClass("has-error");
                framesOk=false;
            }
            if (!frameTo){
                $("#salt_frame_2").parent().addClass("has-error");
                framesOk=false;
            }
            if (framesOk) {
                if (/^[\d]+$/.test(frameFrom + frameTo)){
                 //   if (Number(frameFrom) >= 1){
                    if (Number(frameFrom) < Number(frameTo)){
                        rmsdFrames=frameFrom + "-" + frameTo;
                    } else {
                        showErrorInblock("#salt_sel_frames_error", "Initial frame must be lower than final frame.");
                        rmsdFrames=false;
                    }
                    //} else {
                    //    showErrorInblock("#rmsd_sel_frames_error", "Initial frame must be at least 1.");
                    //    rmsdFrames=false;
                    //}
                } else {
                    showErrorInblock("#salt_sel_frames_error", "Input must be a number.");
                    rmsdFrames=false;
                }
            } else {
                rmsdFrames=false;
            }
        }else{
            frameFrom=0;
            frameTo=-1;
        }
        if (rmsdFrames == false){
            var msn="Some fields are empty or contain errors.";
            showBigError(msn, "#salt_alert");
        }else{
            $('#ShowAllSb').css("visibility","hidden");
            $("#saltresult_par").before("<p style='margin-top:5px;padding:5px;background-color:#e6e6ff;border-radius:3px;clear:left' id='wait_saltb'><span class='glyphicon glyphicon-time'></span> Computing salt bridges...</p>"); 
            $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int, #downl_json_hb").addClass("disabled"); 
            $("#ComputeSaltBridges").addClass("disabled");
            if ($("#saltresult_par").css("display")!="none"){
                $("#blockSBbondsresult").css("display","block");
            }
            $.ajax({
                    type: "POST",
                    data: { "frames[]": [frameFrom,frameTo,cutoff,rmsdTraj,struc,dyn_id]},
                    url:"/view/saltbridges/", 
                    dataType: "json",
                    success: function(data) {
                        $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int, #downl_json_hb").removeClass("disabled"); 
                        $("#wait_saltb").remove();
                        $("#ComputeSaltBridges").removeClass("disabled");
                        $("#blockSBbondsresult").css("display","none");
                        changeDownloadURLS(rmsdTraj,[".href_save_data_sb"]);
                        var regex = /\d+/g;
                        salty=data.salt_bridges;
                        var salt='<center>\
                                    <table class="table table-condesed" style="font-size:12px;">\
                                        <thead>\
                                            <tr>\
                                                <th>Residue1</th>\
                                                <th>Residue2</th>\
                                                <th>Frequency</th>\
                                                <th></th><tbody>';
                        


                        var sort_by="freq";
                        if (sort_by=="freq"){
                            var salty_li_sorted=hbond_dict_to_sorted_li(salty);
                            for (hN=0;hN<salty_li_sorted.length;hN++){
                                var donor_str=salty_li_sorted[hN][0];
                                var acceptor_str=salty_li_sorted[hN][1];
                                var acceptor_isheavy=check_res_isheavy(acceptor_str);
                                var donor_isheavy=check_res_isheavy(donor_str);
                                var leadheavyclass="";
                                if (acceptor_isheavy || donor_isheavy){
                                    leadheavyclass="load_heavy";
                                }
                                var freq=salty_li_sorted[hN][2];
                                var atom0=salty_li_sorted[hN][3];
                                var atom1=salty_li_sorted[hN][4];
                                var chain0=salty_li_sorted[hN][5];
                                var chain1=salty_li_sorted[hN][6];

                                var donor = donor_str.match(regex)[0];  // creates array from matches
                                var acceptor = acceptor_str.match(regex)[0];  // creates array from matches
                                donorballes=gnumFromPosChain(String(donor),chain0)
                                donorballes=hb_sb_transfballes(donorballes);
                                acceptorballes=gnumFromPosChain(String(acceptor),chain1)
                                acceptorballes=hb_sb_transfballes(acceptorballes);
                                salt=salt+'<tr> \
                                                <td>'+ donor_str+donorballes+'</td>\
                                                <td> '+acceptor_str+acceptorballes+'</td>\
                                                <td> '+freq+'% </td>\
                                                <td>\
                                                    <button class="showsb btn btn-default btn-xs clickUnclick '+leadheavyclass+'"  data-resids='+ donor + '$%$' + acceptor +' \
                                                        data-atomindexes='+atom0+'$%$'+atom1+'>Show Salt Bridge</button>' ;
                            }

                        } else if (sort_by=="donor-acceptor"){ // I leave it in case in the future I want to add the option to switch between sorting methods
                            for (var property in salty) {
                                if (salty.hasOwnProperty(property)) {
                                    var string =property;
                                    var string2 =salty[property][0][0];
                                    var donor = string.match(regex)[0];  // creates array from matches
                                    var acceptor = string2.match(regex)[0];  // creates array from matches
                                    donorballes=gnumFromPosChain(String(donor),salty[property][0][4]);
                                    donorballes=hb_sb_transfballes(donorballes);
                                    acceptorballes=gnumFromPosChain(String(acceptor),salty[property][0][5]);
                                    acceptorballes=hb_sb_transfballes(acceptorballes);
                                    salt=salt+'<tr> \
                                                <td rowspan='+ salty[property].length.toString() + '>'+ property+donorballes+'</td>\
                                                <td> '+salty[property][0][0]+acceptorballes+'</td>\
                                                <td> '+salty[property][0][1]+'% </td>\
                                                <td><button class="showsb btn btn-default btn-xs clickUnclick"  data-resids='+ donor + '$%$' + acceptor +' data-atomindexes='+salty[property][0][2]+'$%$'+salty[property][0][3]+'>Show Salt Bridge</button></td>';
                                    for (index = 1; index < salty[property].length; ++index) {
                                        string2=salty[property][index][0]
                                        acceptor = string2.match(regex)[0];
                                        acceptorballes=gnumFromPosChain(String(acceptor),salty[property][index][5]);
                                        acceptorballes=hb_sb_transfballes(acceptorballes);
                                        salt=salt+'<tr>\
                                                    <td>'+salty[property][index][0]+acceptorballes+'</td>\
                                                    <td>'+salty[property][index][1]+'% </td>\
                                                    <td><button class="showsb btn btn-default btn-xs clickUnclick" data-resids='+ donor + '$%$' + acceptor +' data-atomindexes='+salty[property][index][2]+'$%$'+salty[property][index][3]+'>Show Salt Bridge</button></td>';
                                    }
                                }
                            }

                        }



                        salt=salt+'</table></center>';
                        $('#ShowAllSb').css("visibility","visible");
                        $('#saltbridges').html(salt);
                        $("#saltresult_par").attr("style","border:1px solid #F3F3F3;padding-top:5px;display:block;margin-top:10px");
                        $("#selectionDiv").trigger("click");
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                        $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int, #downl_json_hb").removeClass("disabled"); 
                        $("#wait_saltb").remove();
                        $("#ComputeSaltBridges").removeClass("disabled");
                        $("#blockSBbondsresult").css("display","none");
                        if (XMLHttpRequest.readyState == 4) {
                            var responsetext = XMLHttpRequest.responseText;

                            alert(textStatus.substr(0,1).toUpperCase()+textStatus.substr(1)+":\nStatus: " + XMLHttpRequest.textStatus+". "+errorThrown+".\n"+responsetext);
                            showBigError("An error occurred.", "#salt_alert");
                        }
                        else if (XMLHttpRequest.readyState == 0) {
                            var msg="Connection error. Please, try later and check that your file is not larger than 50 MB.";
                            showBigError(msg, "#salt_alert");
                        }
                        else {
                            showBigError("Unknown error.", "#salt_alert");
                        }
                    },
                    timeout: 600000
            }); 
        }
    });
    
//-------- SASA computation --------
    
    $("#ComputeGrid").click(function(){
        $("#sasa_alert").html("");
        $("#grid_sel_frames_error").html("");
        var struc = $(".str_file").data("struc_file");
        var dyn_id=$(".str_file").data("dyn_id");
        rmsdTraj=$("#grid_traj").val();
        rmsdFrames=$("#grid_sel_frames_id input[name=grid_sel_frames]:checked").val();
        cutoff=$("#grid_cutoff").val();
        sasa_sel=$("#sasa_atoms input[name=sasa_sel]:checked").val();
        if (rmsdFrames=="grid_frames_mine"){
            frameFrom=$("#grid_frame_1").val();
            frameTo=$("#grid_frame_2").val();
            if (frameFrom && frameTo) {
                if (/^[\d]+$/.test(frameFrom + frameTo)){
                 //   if (Number(frameFrom) >= 1){
                    if (Number(frameFrom) < Number(frameTo)){
                        rmsdFrames=frameFrom + "-" + frameTo;
                    } else {
                        showErrorInblock("#grid_sel_frames_error", "Initial frame must be lower than final frame.");
                        rmsdFrames=false;
                    }
                    //} else {
                    //    showErrorInblock("#rmsd_sel_frames_error", "Initial frame must be at least 1.");
                    //    rmsdFrames=false;
                    //}
                } else {
                    showErrorInblock("#grid_sel_frames_error", "Input must be a number.");
                    rmsdFrames=false;
                }
            } else {
                rmsdFrames=false;
            }
        }else{
            frameFrom=0;
            frameTo=-1;
        }
        if (rmsdFrames == false){
            var msn="Some fields are empty or contain errors";
            showBigError(msn, "#sasa_alert");
        } else {
            
            $("#sasa_par").before("<p style='margin-top:5px;padding:5px;background-color:#e6e6ff;border-radius:3px;clear:left' id='wait_sasa'><span class='glyphicon glyphicon-time'></span> Computing SASA. This may take a while...</p>");   
            $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int, #downl_json_hb").addClass("disabled"); 
            $.ajax({
                    type: "POST",
                    data: { "frames[]": [frameFrom,frameTo,cutoff,rmsdTraj,struc,dyn_id,sasa_sel,seq_ids]},
                    url:"/view/grid/", 
                    dataType: "json",
                    success: function(data) {
                        $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int, #downl_json_hb").removeClass("disabled"); 
                        $("#wait_sasa").remove();
                        atomshb=[];
                        all_resids=[];
                        atomshb_inter=[];
                        atomssb=[];
                        all_resids_sb=[];
                        all_resids_sasa=data.selected_residues
                        results=drawBasic(data.sasa,'Time (ns)','SASA (nm^2)');
                        data_graph=results[0];
                        options=results[1];
                        newid='sasa_chart_'+data.sasa_id.toString();
                        titlegraph=['From Frame:',frameFrom,'To Frame:',frameTo,'Trajectory:',rmsdTraj,'Selection:',sasa_sel].join(' ');
                        $("#sasa_container").append('<hr><center>'+titlegraph+'</center><br><div class="col-md-12;clear:left;" id="'+newid+'" ></div>');
                        var chart_sasa = new google.visualization.LineChart(document.getElementById(newid));
                        google.visualization.events.addListener(chart_sasa, 'ready', function () {
                            var img_source =  chart_sasa.getImageURI(); 
                            $("#"+newid).attr("data-url",img_source);
                        });
                        chart_sasa.draw(data_graph, options);
                        $("#"+newid).append('<a href='+$("#"+newid).attr("data-url")+'>Download graph as image</a>');
                        $("#selectionDiv").trigger("click");
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                        $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int, #downl_json_hb").removeClass("disabled"); 
                        $("#wait_sasa").remove();
                        if (XMLHttpRequest.readyState == 4) {
                            var responsetext = XMLHttpRequest.responseText;

                            alert(textStatus.substr(0,1).toUpperCase()+textStatus.substr(1)+":\nStatus: " + XMLHttpRequest.textStatus+". "+errorThrown+".\n"+responsetext);
                            showBigError("An error occurred.", "#sasa_alert");
                        }
                        else if (XMLHttpRequest.readyState == 0) {
                            var msg="Connection error. Please, try later and check that your file is not larger than 50 MB.";
                            showBigError(msg, "#sasa_alert");
                        }
                        else {
                            showBigError("Unknown error.", "#sasa_alert");
                        }
                    },
                    timeout: 1200000
            }); 
        }
    });


//-------- Selecton of HB and SB interactions to display --------

    $(document).on('click', "#ShowAllHbIntra",function(){
        $("#bondsresult_par").find(".showhb:not(.active)").each(function(){
            $(this).addClass("active");
        });
        $("#selectionDiv").trigger("click");
    });

    $(document).on('click', "#ShowAllHbInter",function(){
        $("#bondsresult_par").find(".showhb_inter:not(.active)").each(function(){
            $(this).addClass("active");
        });
        $("#selectionDiv").trigger("click");
    });

    $(document).on('click', "#ShowAllSb",function(){
        $("#saltresult_par").find(".showsb:not(.active)").each(function(){
            $(this).addClass("active");
        });
        $("#selectionDiv").trigger("click");
    });


    $(document).on('click',".clearAnalysisView",function(){
        identif=$(this).attr("id");
        selclass=identif.replace("clear_","");
        $(document).find("."+selclass).each(function(){
            $(this).removeClass("active");
        });
        $("#selectionDiv").trigger("click");
    });


    function selectionHBSB(){
        var atomshb=[];
        var all_resids=[];
        var all_resids_sb=[];
        var atomshb_inter=[];
        var atomssb=[];
        var all_resids_sasa=[];
        var all_resids_inter=[];
        var load_heavy_hbsb=false;
        $("#analysis_bonds").find(".showhb.active").each(function(){
            var atoms_pre=$(this).data('atomindexes').split('$%$');
            var atoms_pre2=[Number(atoms_pre[0]),Number(atoms_pre[1])];
            atomshb.push(atoms_pre2);
            var resids=$(this).data('resids').split('$%$');
            all_resids.push(Number(resids[0]));
            all_resids.push(Number(resids[1]));
        });
        
        $("#analysis_bonds").find(".showhb_inter.active").each(function(){
            var atoms_pre=$(this).data('atomindexes').split('$%$');
            var atoms_pre2=[Number(atoms_pre[0]),Number(atoms_pre[1])];
            atomshb_inter.push(atoms_pre2);
            var resids=$(this).data('resids').split('$%$');
            all_resids_inter.push(Number(resids[0]));
            all_resids_inter.push(resids[1]);
            if ($(this).hasClass("load_heavy")){
                load_heavy_hbsb=true;
            }
        });
        
        $("#analysis_salt").find(".showsb.active").each(function(){
            var atoms_pre=$(this).data('atomindexes').split('$%$');
            var atoms_pre2=[Number(atoms_pre[0]),Number(atoms_pre[1])];
            atomssb.push(atoms_pre2);
            var resids=$(this).data('resids').split('$%$');
            all_resids_sb.push(Number(resids[0]));
            all_resids_sb.push(Number(resids[1]));
            if ($(this).hasClass("load_heavy")){
                load_heavy_hbsb=true;
            }
        });        
        return({
                "atomshb":atomshb,
                "atomshb_inter":atomshb_inter,
                "atomssb":atomssb,
                "all_resids":all_resids,
                "all_resids_inter": all_resids_inter,
                "all_resids_sb":all_resids_sb,
                "load_heavy":load_heavy_hbsb
                })
    }
    

//-------- RMSD computation --------

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
                $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int, #downl_json_hb").addClass("disabled"); 
                act_rmsd_plots=[];
                $("#rmsd_chart").children(".rmsd_plot").each(function(){
                    act_rmsd_plots.push($(this).data("rmsd_id"));
                });
                var stride = strideVal("#rmsd_stride");
                var t0=performance.now();
                $.ajax({
                    type: "POST",
                    url: "/view/"+dyn_id+"/",  
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
                                if ($.active<=1){
                                    RMSDplot_html="<div class='rmsd_plot' id='all_"+newRMSDgraph_sel+"' data-rmsd_id='"+rmsd_id+"' style='border:1px solid #F3F3F3;overflow:auto;overflow-y:hidden;-ms-overflow-y: hidden;'>\
                                                    <div class='rmsd_time' id='"+newRMSDgraph_sel+"t'></div>\
                                                    <div class='rmsd_frame' id='"+newRMSDgraph_sel+"f'></div>\
                                                    <div class='rmsd_settings' id='opt_"+newRMSDgraph_sel+"' style='margin:5px'>\
                                                        <div class='plot_rmsd_by_sel_cont' style='font-size:12px;margin-left:5px'>\
                                                          <p>Plot RMSD by</p>\
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
                                                            <a role='button' class='btn btn-link href_save_data_rmsd_plot settingsB' href='/view/dwl/"+dyn_id+"/"+rmsd_id+"' style='color:#585858;margin-right:0;margin-left;padding-right:0;padding-left:0;margin-bottom:3px'>\
                                                                <span  title='Save data' class='glyphicon glyphicon-download-alt save_data_rmsd_plot'></span>\
                                                            </a>\
                                                        </div>\
                                                        <div style='display:inline-block;margin:5px;color:#DC143C;cursor:pointer;'>\
                                                            <span title='Delete' class='glyphicon glyphicon-trash delete_rmsd_plot' data-rmsd_id='"+rmsd_id+"'></span>\
                                                        </div>\
                                                    </div>\
                                                </div>";//color:#239023
                                }else{
                                    RMSDplot_html="<div class='rmsd_plot' id='all_"+newRMSDgraph_sel+"' data-rmsd_id='"+rmsd_id+"' style='border:1px solid #F3F3F3;overflow:auto;overflow-y:hidden;-ms-overflow-y: hidden;'>\
                                                    <div class='rmsd_time' id='"+newRMSDgraph_sel+"t'></div>\
                                                    <div class='rmsd_frame' id='"+newRMSDgraph_sel+"f'></div>\
                                                    <div id='opt_"+newRMSDgraph_sel+"' class='rmsd_settings' style='margin:5px'>\
                                                        <div class='plot_rmsd_by_sel_cont' style='font-size:12px;margin-left:5px'>\
                                                          <p>Plot RMSD by</p>\
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
                                                            <a role='button' class='btn btn-link href_save_data_rmsd_plot disabled settingsB' href='/view/dwl/"+dyn_id+"/"+rmsd_id+"' style='color:#585858;margin-right:0;margin-left;padding-right:0;padding-left:0;margin-bottom:3px'>\
                                                                <span  title='Save data' class='glyphicon glyphicon-download-alt save_data_rmsd_plot'></span>\
                                                            </a>\
                                                        </div>\
                                                        <div style='display:inline-block;margin:5px;color:#DC143C;cursor:pointer;'>\
                                                            <span title='Delete' class='glyphicon glyphicon-trash delete_rmsd_plot' data-rmsd_id='"+rmsd_id+"' ></span>\
                                                        </div>\
                                                    </div>\
                                                </div>"  ;                          
                                } 
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
                                    updateframeFromPlot(chart0r,rmsd_array_f);
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
                                    updateframeFromPlot(chart1r,rmsd_array_f);
                                  }
                                });
                                chart1r.draw(data, options);   
//                                google.visualization.events.addListener(chart1r, 'select', function(){  
//                                    updateframeFromPlot(chart1r,rmsd_array_f);
//                                });


//                                for (chartN=0 ; chartN < chart_cont_li.length ; chartN++){
//                                    var chart_cont=chart_cont_li[chartN][0];
//                                    var data=chart_cont_li[chartN][1];
//                                    var options=chart_cont_li[chartN][2];
//                                    var rmsd_chart_div = document.getElementById(chart_cont);
//                                    var chart = new google.visualization.LineChart(rmsd_chart_div);    
//                                    google.visualization.events.addListener(chart, 'ready', function () {
//                                        var rmsd_img_source =  chart.getImageURI(); 
//                                        $("#"+chart_cont).attr("data-url",rmsd_img_source);
//                                    });
//                                    chart.draw(data, options);   
//                                }
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
                            $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int, #downl_json_hb").removeClass("disabled");
                        }
                    var t1= performance.now();
                    },
                    error: function() {
                        $("#gotoRMSDPg").removeClass("disabled");
                        $("#wait_rmsd").remove();
                        add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>An unexpected error occurred.';
                        $("#rmsd_alert").html(add_error);  
                        if ($.active<=1){
                            $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int, #downl_json_hb").removeClass("disabled");
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
    
    function add_row_EDReps(selToAdd,colorVal,inpType){
        last_input_row=$("#text_input_all").find(".text_input:last");
        if (! last_input_row.hasClass(inpType)){
            var last_input_txt=last_input_row.find(".sel_input").val()
            if (last_input_txt.length>0){
                //last_input_row.find(".ti_add_btn").trigger("click");                
                createNewTextInput();
                last_input_row=$("#text_input_all").find(".text_input:last");
            }
            last_input_row.addClass("ed_input_rep "+ inpType);
            last_input_row.find(".sel_input").val(selToAdd);
            changeLastInputColor(colorVal,last_input_row);
            if ((inpType.indexOf("ed_input_rep_lig")<0) && (inpType.indexOf("ed_input_rep_sel")<0)){
                last_input_row.find(".high_type").val("line")
            }
        }

    }

    function lig_sel_if_starts_num(lig_nm){
        if (lig_nm){
            if (lig_nm.match(/^\d/)) {
                var lig_nm="["+lig_nm+"]";
            } 
        }
        return lig_nm
    }

    function createEDReps(add_reps,highlight_sel){
        if ($("#EdrepsOn").hasClass("active")){
            if (add_reps){
                //Hide quick reps
                $("#receptor,.rep_elements,.tmsel").not("#bindingSite").removeClass("active");

                //Add GPCR
                prot_sel=gpcr_selection();
                if ($("#text_input_all").find(".ed_input_rep_GPCR").length ==0){
                    if (prot_sel != highlight_sel){
                        add_row_EDReps(prot_sel,"#b8b8b8","ed_input_rep_GPCR");                
                    }
                }

                //Add other prot
                if (prot_sel!="protein"){
                    if ($("#text_input_all").find(".ed_input_rep_otherprot").length ==0){
                        var otherprot="protein and not ("+prot_sel+")";
                        add_row_EDReps(otherprot,"#dfdbdb","ed_input_rep_otherprot");
                    }
                }

                //Add ligand
                var lig_li=[]
                $(".ed_ligand").each(function(){
                    var lig_nm=$(this).data("shortn");
                    lig_nm=lig_sel_if_starts_num(lig_nm);
                    lig_li[lig_li.length]=lig_nm
                    var class_nm="ed_input_rep_lig_"+lig_nm;
                    if ($("#text_input_all").find("."+class_nm).length ==0){
                        add_row_EDReps(lig_nm,"#797979",class_nm);
                    }
                })
                /*var lig_nm=$(".ed_ligand").data("shortn");
                if ($("#text_input_all").find(".ed_input_rep_lig").length ==0){
                    add_row_EDReps(lig_nm,"#797979","ed_input_rep_lig");
                }*/

                //Highlight selection
                var prev_high=$("#text_input_all").find(".ed_input_rep_sel");
                if (prev_high.length > 0){
                    rmTextInputRow(prev_high);
                }
                if (highlight_sel){
                    if (lig_li.indexOf(highlight_sel)<0){
                        add_row_EDReps(highlight_sel,"#efa816","ed_input_rep_sel");
                    }
                }

            } else {
                $("#text_input_all").find(".ed_input_rep").each(function(){
                    $("#receptor,.Ligand").addClass("active");
                    rmTextInputRow($(this));
                });
            }
        } else {
            var prev_ed_inp=$("#text_input_all").find(".ed_input_rep");
            if (prev_ed_inp.length >0){
                prev_ed_inp.each(function(){
                    $("#receptor,.Ligand").addClass("active");
                    rmTextInputRow($(this));
                });
            }
        }
        $("#selectionDiv").trigger("click")
    }


//-------- Pockets --------

var pocketsTable = $('#analysis_pockets_table').DataTable(
    {
    //"dom":"<'mybuttons'B><'mylength'l>rtip",
    "dom":"<'mybuttons'B>rtip",
    "buttons": [
        'selectAll',
        'selectNone',
    ],
    //Don't give option to sort or search by column 1 (color)
    "columnDefs": [ { "orderable": false, "searchable": false, "targets": 1  }],   
    "select": {
        style: 'multi'
    },
     "order": [],
     "stripeClasses": [],
     "bFilter": false, // no search
    }
);

// Button to plot the selected pockets' plot
$("#pocket_plot_button").on("click", function() {

    if (pocketsTable.rows( { selected: true } )[0].length == 0) {
        alert("Please, select at least one pocket from the table.");
        return;
    }

    let htmlPocketData = getPocketHTMLdata(); 
    console.log(htmlPocketData);
    requestPocketPlot(htmlPocketData);
});

/**
 * Obtains user selected and system data from the HTML and returns an object
 * containing variables needed for representing the pockets.
 * 
 * @return {Object} - Contains different variables related to the pockets.
 */
function getPocketHTMLdata() {

    // Get data from HTML
    let dynID = $(".str_file").data("dyn_id");
    let trajID = $(".traj_element.tsel").attr("id").replace("traj_id_","");
    let trajName_list = $(".traj_element.tsel").data("tpath").split("/");
    let trajName = trajName_list.pop();
    let smoothingWindowSize = $("#smoothing_window_size").val();
    let showNearbyResidues = $("#show_nearby_residues").prop('checked');

    // Take selection from the DataTable
    let mustPlotEveryPocket = false;
    let pocketIDsList = [];
    pocketsTable.rows( { selected: true } )[0].map( id => pocketIDsList.push(id) );
    if (pocketIDsList.length == 0) {
        mustPlotEveryPocket = true;
    }

    // Catch data from table according to user input
    let pocketIDAndColorList = [];
    pocketsTable.rows().data().each( function(row, index) {
        let rowPocketNum = row[0];
        // Text within these strings is the hexadecimal code color
        let rowColor = row[1].split("background-color:")[1].split(";border-radius:")[0];

        // Include the pocket to display if it's in the user-selected list
        if (mustPlotEveryPocket || pocketIDsList.includes(rowPocketNum)) {
            pocketIDAndColorList.push({"id": rowPocketNum, "color": rowColor});
        }
    });

    return {
        "dynID"               : dynID,
        "trajID"              : trajID,
        "trajName"            : trajName,
        "pocketIDAndColorList": pocketIDAndColorList,
        "smoothingWindowSize" : smoothingWindowSize,
        "showNearbyResidues"  : showNearbyResidues,
    };
}


/**
 * Takes data from the HTML and requests Django to create a pockets' plot with
 * Bokeh. This plot is returned and embeded in "#pocket_plot" div. It also
 * represents the pocket in the viewer.
 * 
 * @param {Object} htmlData - Data from the HTML, either user selected or
 *     simulation specific.
 */
function requestPocketPlot(htmlData) {

    // Delete old vertical line (if any)
    delete Bokeh.documents[0];
    Bokeh.documents.shift();

    // Delete old plot
    $("#pocket_plot").html("");

    // Make post request to create the plot and retrieve the pocket PDB files
    $.ajax({
        type: "POST",
        url: "/view/get_pocket_plot_and_files/", 
        dataType: "json",
        data: { 
            "all_pocket_data": JSON.stringify(window.allPocketData),
            "traj_id": htmlData["trajID"],
            "traj_name": htmlData["trajName"],
            "pocketid_and_color_list": JSON.stringify(htmlData["pocketIDAndColorList"]),
            "smoothing_window_size": htmlData["smoothingWindowSize"],
        },                
        success: function(result) {
            // Embed new plot
            Bokeh.embed.embed_item(result["plot"], "pocket_plot");

            // Show pockets in viewer
            $('#embed_mdsrv')[0].contentWindow.triggerEmbededCustomEvent("pocket_trigger",
                {
                    "trajID"               : htmlData["trajID"],
                    "pocketIDAndColorList" : JSON.stringify(htmlData["pocketIDAndColorList"]),
                    "showNearbyResidues"   : htmlData["showNearbyResidues"],
                });
        },
        error: function(error){
            alert("Something went wrong. Please, try again later.")
        },
    });
}

/**
 * When the user opens the pockets tab for the first time, request the data
 * from the server and load it on the global variable "allPocketData". After
 * that, fill the table.
 */
var allPocketData;
$("#analysis_pockets_pan").on("click", function() {
    if (! window.allPocketData) {

        $.ajax({
            type: "POST",
            url: "/view/get_pocket_and_dyn_data/", 
            dataType: "json",
            data: { 
                "dyn_id": $(".str_file").data("dyn_id"),
            },                
            success: function(result) {
                window.allPocketData = result["dyn_data"];
                update_pocket_table();
            },
            error: function(error){
                alert("Something went wrong. Please, try again later.");
            }, 
        });

    }
});


// Update frame line of pocket volume plot whenever there is a frame change
$("#analysis_pockets").bind('update_pocket_frame', function(e, frame) {
    // if there is a chart loaded
    if ($("#pocket_plot .bk-canvas")[0]){
        let pocket_frameslider = Bokeh.documents[0].get_model_by_name("pocket_frameslider");
        pocket_frameslider.value = frame;
    }
});

// Cleans every pocket related info: plot and viewer
$("#reset_pocket_plot").on("click", function() {

    let trajID = $(".traj_element.tsel").attr("id").replace("traj_id_","");

    // Clear the plot
    $("#pocket_plot").html("");

    // Uncheck the "show nearby residues" button
    $( "#show_nearby_residues" ).prop( "checked", false );

    // Clear the pockets from the viewer
    $('#embed_mdsrv')[0].contentWindow.triggerEmbededCustomEvent("pocket_trigger",
        {
            "trajID"               : trajID,
            "pocketIDAndColorList" : JSON.stringify([]), // Empty list = show no pockets
            "showNearbyResidues"   : false,
        });

    // Deselect all rows
    pocketsTable.rows().deselect();
});


/**
 * Updates the shown information for the current trajectory. Table is updated
 * with the trajectory's data, plot is reset, pockets visualization
 * in the viewer are discarded and downlaod link is updated.
 * 
 * This function is mainly called from the viewer iframe: "embed.html".
 */
window.update_pocket_table = function() {
    if (pocketsTable && window.allPocketData) { // TODO: Check if it works if no table available         
        let trajID = $(".traj_element.tsel").attr("id").replace("traj_id_","");

        // Clear the plot
        $("#pocket_plot").html("");

        // Clear the pockets from the viewer
        $('#embed_mdsrv')[0].contentWindow.triggerEmbededCustomEvent("pocket_trigger",
            {
                "trajID"               : trajID,
                "pocketIDAndColorList" : JSON.stringify([]), // Empty list = show no pockets
                "showNearbyResidues"   : false,
            });

        // Redraw the table with the new trajectory data
        for (const [trajIDfromList, descriptorsObject] of Object.entries(window.allPocketData["pocket_data"][0])) {

            if (+trajIDfromList != +trajID) continue; // Skip if its not the current trajectory

            pocketsTable.clear();
            for (let descriptors of descriptorsObject["data"]) {

                let colorSpan = '<span style="height:20px;width:20px;background-color:'
                              + tunnel_color_from_clusternum(descriptors["name"])
                              + ';border-radius: 50%;display: inline-block;"></span>'

                pocketsTable.row.add([ descriptors["name"],
                                       colorSpan,
                                       descriptors["average_volume"],
                                       descriptors["average_Polarity_score"],
                                       descriptors["average_hydrophobicity_Density"],
                                       descriptors["average_hydrophobicity_score"],
                                       descriptors["perc_druggability"]]);
            }
            pocketsTable.draw();
        }

        // Change download button href
        download_btn = $("#download_pockets_pdbs");
            // TODO: relative path
        download_btn.attr('href',"/dynadb/files/Precomputed/MDpocket/Downloads/" + "pockets_dyn" + dyn_id + "_traj" + trajID + ".zip");
    }
}

/**
 * When you change the state of the checkbox "Show nearby residues",
 * update the viewer.
 */
$("#show_nearby_residues").on("change", function() {
    if (pocketsTable.rows( { selected: true } )[0].length != 0) {
        $("#pocket_plot_button").trigger("click");
    }
});


//-------- Buttons --------
    $("#ed_ctrl").on("click",".EdrepsSet:not(.active)",function(){
        $(this).addClass("active");
        $(this).siblings(".EdrepsSet").removeClass("active");
        var some_input_ok=false;

        if ($(".ed_map_el.active").length>0){
            //createEDReps(true);
            var results_ED=obtainURLinfo_ED(true)
            //$("#selectionDiv").trigger("click");
        }
    });


    $("#analysis_variants").on("click",".analysis_variants_display:not(.active)",function(){
        $(this).addClass("active");
        $(this).siblings(".analysis_variants_display").removeClass("active");
        var btnaction=$(this).data("action");
        var selected_onclick=$(".onclickshow.is_active").data("short");
        if (btnaction=="on"){
            //If we activate the display, the onlick mode "vars" is activated
            if (selected_onclick !="vars"){
                $("#showvars").trigger("click");
            }
        } else {
            //If we inactivate the display, if the  onlick mode "vars" was active, it's changed to dist.
            if (selected_onclick=="vars"){
                $("#showdists").trigger("click");          
            }

        }
    });

    var variants_table = $('#analysis_variants_table').DataTable(
        {
         "order": [],
         "stripeClasses": [],
         "columnDefs": [ 
                        { "orderable": false, "searchable": false, "targets": 0 },   //Don't give option to sort or search by column 0
                        { targets: [0, 1, 2, 3, 4, 5, 9, 12, 14, 15], visible: true },
                        { targets: '_all', visible: false }
                        ],
         dom:"<'myfilter'f><'mylength'l>rtip",
        }
    );

    $('#analysis_variants_table').css("display","table");
    $('#analysis_variants_table').css("width","100%");


    $("body").on("click",".zoom_to_nglsel",function(){
        var mysel=$(this).data("nglsel")
        $('#embed_mdsrv')[0].contentWindow.zoomandreptorsel(mysel);
    })

    function toggleButtonGetStatus(button) {
        if (button.hasClass("active")) {
            button.removeClass("active");
            return false;
        } else {
            button.addClass("active");
            return true;
        }
    }

    $("#variant_color_by").on("change", function() {
        if ($("#analysis_variants_display_off").hasClass("active")) {
            $("#analysis_variants_display_on").trigger("click");
        } else {
            $("#showvars").trigger("click");
        }
    });


    $("#filter_only_disease").on("click", function() {
        if (toggleButtonGetStatus($(this))) {
            variants_table.column(-1).search(".", true).draw();
        } else {
            variants_table.column(-1).search("").draw();
        }        
    })

    $("#filter_aa_change").on("change", function() {
        variants_table.column(5).search(this.value).draw();
    });

    $("#filter_functional_site").on("change", function() {
        // Don't use regular expressions, smart search and be case sensitive
        // This is a fix to avoid "Binding site" selection showing
        // "Intracellular binding site" variants as well
        variants_table.column(9).search(this.value, false, false, false).draw();
    });

    $("#filter_predicted_impact").on("change", function() {
        variants_table.column(-4).search(this.value, true).draw();
    });

    $("#variant_columns_shown").on("click", "button", function(e) {
       //e.preventDefault(); // is it neccesary? check

        toggleButtonGetStatus($(this));
        let column = variants_table.column($(this).attr('data-column'));
        column.visible(!column.visible());
    });

    $("#is-licorice").on("change", function() {
        if ($("#analysis_variants_display_on").hasClass("active")) {
            $("#showvars").trigger("click");
        }
    });

    $("#is-disease-label").on("change", function() {
        if ($("#analysis_variants_display_on").hasClass("active")) {
            $("#showvars").trigger("click");
        }
    });

    window.getVariantsOnTable = function () {
        let variantsOnTable = new Set();
        variants_table
        .column(1, {search:"applied"}).data()
        .map( v => variantsOnTable.add(v) );
        return variantsOnTable;
    }

    let timeoutID;
    $('#analysis_variants_table').on("draw.dt", function() {
        if ($("#analysis_variants_display_on").hasClass("active")) {
            if (timeoutID) clearTimeout(timeoutID);
            timeoutID = setTimeout( () => {
                $("#showvars").trigger("click");
                clearTimeout(timeoutID);
            }, 250);
        }
    });

    click_unclick(".high_pdA");
    click_unclick(".high_pdB");
    click_unclick(".high_pdC");
    click_unclick(".high_pdF");
    click_unclick(".rep_elements");
    click_unclick("#col_btn");
    click_unclick("#receptor");
    click_unclick(".clickUnclick")
    $("#btn_all").click(function(){
        $(".rep_elements:not(.tmsel)").addClass("active");
        $("#receptor").addClass("active");
        $("#selectionDiv").trigger("click");
    });
    

    function applyEDinput(inputEl){
        var pre_sel = inputEl.val();
        var rownum=inputEl.parents(".ed_input_row").attr("id");
        var sel =inputText(gpcr_pdb_dict,pre_sel,rownum,"main",".ed_ti_alert");
        if (sel.length>0){
            var is_ok_ngl=$('#embed_mdsrv')[0].contentWindow.checkNGLSel(sel);
            if (! is_ok_ngl){      
                sel="";
                addErrorToInput("#"+rownum,"main",".ed_ti_alert_ngl","html","Invalid selection");
            }

        } else {
            sel="";
        }
        inputEl.data("sel",sel)
    }

    function applyEDSeqsel(seqcellSel,applyToSel){
        var sel_ranges=obtainSelectedAtSeq(seqcellSel);
        var fin_val="";
        if (sel_ranges.length > 0){
            sel_ranges_ok=joinContiguousRanges(sel_ranges);
            fin_val=obtainSelectionFromRanges(sel_ranges_ok);
        }
        $(applyToSel).data("sel",fin_val);
    }

    $(".ed_map_el").click(function(){
        if ($(this).hasClass("active")){
            $(this).removeClass("active");
            //createEDReps(false);
            //$("#EDselectionDiv").trigger("click");
            //$("#selectionDiv").trigger("click");
        }else{
            if ($(this).hasClass("act_input")){
                var btn_id=$(this).attr("id");
                var input_id=btn_id.replace("_btn","");
                var inputEl=$("#"+input_id);
                applyEDinput(inputEl);
            } 
            if ($(this).hasClass("act_seq_input")){
                var btn_id=$(this).attr("id");
                applyEDSeqsel(".ed_seq_sel","#"+btn_id);
            }
            $(this).addClass("active");
            $(".ed_map_el").not(this).removeClass("active");
            //createEDReps(true);
        }
        $("#EDselectionDiv").trigger("click");
        //$("#selectionDiv").trigger("click");
    });



    $(".ed_input").change(function(){ 
        var input_id=$(this).attr("id");
        var input_btn=$("#"+input_id+"_btn");
        if (input_btn.hasClass("active")){
            applyEDinput($(this));
            //createEDReps(true);
            $("#EDselectionDiv").trigger("click");
            //$("#selectionDiv").trigger("click");

        } else {
            input_btn.popover('show');
            setTimeout(function() {
                input_btn.popover('hide');
            }, 1000);
        }
    })




    function removeCompBtns(){
        $(".rep_elements").removeClass("active");
        $("#receptor").removeClass("active");
    }
    
    function removeEDCompBtns(){
        $(".ed_map_el").removeClass("active");
    }


    $("#btn_clear").click(function(){
        removeCompBtns();
        $("#selectionDiv").trigger("click");
    });

    $("#btn_clear_tms").click(function(){
        $(".tmsel").removeClass("active");
        $("#selectionDiv").trigger("click");
    });
    
    
    $(".showHSet").click(function(){
        if (! $(this).hasClass("active")){
            $(this).addClass("active");
            $(this).siblings(".showHSet").removeClass("active");
        }
        $("#selectionDiv").trigger("click");
    });

//-------- Pass data to MDsrv --------
    var gpcr_selection = function(){
    //function gpcr_selection(){
        if (chains_str == ""){
            receptorsel="protein";
        } else {
            var chains_s=/:(.*)$/.exec(chains_str)[1];
            var chains_l = chains_s.match(/\w+/g);
            receptorsel="protein and (";
            for (cN=0 ; cN < chains_l.length ;cN++){
                receptorsel+=":"+chains_l[cN]+ " , ";
            }
            receptorsel=receptorsel.slice(0,-3) +")";
        }
        return (receptorsel);
    }
    //window.gpcr_selection=gpcr_selection;

    function gpcr_selection_active(edMap){
        if (! edMap && $("#receptor").hasClass("active")){
            var receptorsel=gpcr_selection();
        } else if (edMap && $("#ed_receptor").hasClass("active")) {
            var receptorsel=gpcr_selection();
        } else {
            var receptorsel="";
        }
        return (receptorsel);
    }




    var seq_ids=[];
    
    var atomshb=[];//
    var grid=[];
    var grid_shape=[];
    var grid_atoms=[];
    var all_resids=[];//
    var all_resids_sb=[];//
    var atomshb_inter=[];//
    var atomssb=[];//
    var all_resids_sasa=[];//
    
    function obtainURLinfo_ED(launchCreateEDReps){
        var loadEd=false;
        var ed_finsel="";
        var ligsel_ed=$(".ed_ligand.active").data("shortn");
        ligsel_ed=lig_sel_if_starts_num(ligsel_ed);
        if (ligsel_ed){
            loadEd=true;
            ed_finsel=ligsel_ed;
        } 
        if ($(".ed_tmsel.active").length>0){
            loadEd=true;
            ed_finsel=obtainTMs("em");
        }
        var receptorsel_ed=gpcr_selection_active(true);
        if (receptorsel_ed){
            loadEd=true;
            ed_finsel=receptorsel_ed;
        } 

        if ($(".act_input.active").length>0){
            var input_btn_id=$(".act_input.active").attr("id");
            var input_id=input_btn_id.replace("_btn","");
            ed_finsel=$("#"+input_id).data("sel");
            loadEd=true;
        }
        if ($(".act_seq_input.active").length>0){ 
            var ed_finsel=$(".act_seq_input").data("sel");
            loadEd=true;
        }

        var ed_cons_pos=getSelectedPosLists(".high_pd.ed_map_el.active",{})[0];
        if (ed_cons_pos.length>0){
            var ed_finsel="protein and ("+ed_cons_pos.join(",")+")";
            loadEd=true;
        }

        if (loadEd){
            if (launchCreateEDReps){
                createEDReps(true,ed_finsel);
            }
            $(".EDdisplay").prop('disabled', false);
            $("#ed_no_sel_warning").css("display","none");
        } else {
            if (launchCreateEDReps){
                createEDReps(false,false);
            }
            $(".EDdisplay").prop('disabled', true);
            $("#ed_no_sel_warning").css("display","block");
        }
        return ({"loadEd":loadEd,
                 "ed_sel":ed_finsel})
    }

    function obtainURLinfo(gpcr_pdb_dict){ //ADD load_heavy info in returned dict here
        var layers_res =obtainTextInput();
        var layers_li=layers_res[0];
        var layers_row_li=layers_res[1];
        var customsel_hasOKval=layers_res[2];
        
        /*var free_load_heavy=false;
        var loadh_custom_checkbox= $("#load_heavy_textinput");
        var loadh_custom_checkbox_ischecked=loadh_custom_checkbox.is(":checked");
        if (customsel_hasOKval && loadh_custom_checkbox_ischecked ){
            free_load_heavy=true;
        }*/
        //load_heavy_textinput
        var dist_groups_li=displayCheckedDists();
        var int_res_li_res=displayIntResids();
        var int_res_li=int_res_li_res[0];
        var int_res_li_ch = int_res_li_res[1];
        cp_result = obtainCompounds();
        cp=cp_result[0]
        cp_load_heavy=cp_result[1]
        nonGPCR=obtainNonGPCRchains(".nonGPCR.active");// list of strings, each string contains the chains of a non-GPCR prot selected.
        if (gpcr_pdb_dict=="no"){
            high_pre = [];
        } else {
            high_pre = obtainPredefPositions();
        }
        var traj = $("#selectedTraj").data("tpath");
        var receptorsel=gpcr_selection_active(false);
        bs_info=obtainBS();
        var water_dist = obtainWaterDist()[1];
        var water_check = obtainWaterDist()[0]
        var waterbox = obtainWaterBox();
        var polar_check = obtainPolar();
        var resultHBSB=selectionHBSB();
        var hbdb_load_heavy=resultHBSB["load_heavy"]
        fpSelInt_send={};
        FpSelPos_send = {};
        if ($("#FPdisplay").hasClass("active")){
            fpSelInt_send=fpSelInt;
            FpSelPos_send = FpSelPos
        }
        var showH = false;
        if ($("#showHOn.active").length >0){
            showH=true;
        } 
        var url_load_heavy=false;
        if (cp_load_heavy || water_check || hbdb_load_heavy){
            url_load_heavy=true;
        }
        /*block_loadh_custom_checkbox=false;
        if (cp_load_heavy || water_check || hbdb_load_heavy){
            block_loadh_custom_checkbox=true;
        }*/  
        var cs_repr_resatoms_show=[];
        for (resatom in cs_repr_resatoms){
            if (cs_repr_resatoms[resatom]["display"]){
                cs_repr_resatoms_show[cs_repr_resatoms_show.length]=[resatom,cs_repr_resatoms[resatom]["color"]]
            }
        }
        return ({"cp":cp ,
                "layers_li":layers_li,
                "layers_row_li":layers_row_li,
                "dist_groups_li":dist_groups_li,
                "int_res_li":int_res_li,
                "int_res_li_ch":int_res_li_ch,
                "nonGPCR":nonGPCR,
                "high_pre":high_pre,
                "traj":traj,
                "receptorsel":receptorsel,
                "bs_info" :bs_info,
                "water_dist":water_dist,
                "water_check": water_check,
                "waterbox": waterbox,
                "polar_check": polar_check,
                "hbondarray":resultHBSB["atomshb"],
                "hb_inter":resultHBSB["atomshb_inter"],
                "sbondarray":resultHBSB["atomssb"],
                "allresidshb":resultHBSB["all_resids"],
                //"allresidshbInt":resultHBSB["all_resids_inter"],
                "allresidssb":resultHBSB["all_resids_sb"],
                "all_resids_sasa":all_resids_sasa,
                "fpSelInt":fpSelInt_send,
                "FpSelPos":FpSelPos_send,
                "showH":showH,
                "load_heavy":url_load_heavy,
                "cs_repr_resatoms":cs_repr_resatoms_show,
                //"block_loadh_custom_checkbox":block_loadh_custom_checkbox
        });
    }
    
    var passInfoToIframe_ED = function(){
        var results_ED=obtainURLinfo_ED(true);
        window.results_ED=results_ED;
    }
    window.passInfoToIframe_ED=passInfoToIframe_ED;

    var passInfoToIframe = function(){
        var results = obtainURLinfo(gpcr_pdb_dict);
        window.results=results;
        var pd = "n";
        var legend_el=[];
        for (key in high_pre){
            if (high_pre[key].length > 0){
                pd = "y";
                legend_el[legend_el.length]=key;
            }
        }
        window.pd=pd;
        var dist_sel_res=obtainDistSel();  
        var dist_of=dist_sel_res[0];  
        var dist_load_heavy=dist_sel_res[1];  
        window.dist_of=dist_of;
        //obtainLegend(legend_el);
        final_load_heavy=false;
        if (results["load_heavy"] || dist_load_heavy ){
            final_load_heavy=true;
        }
        /*block_loadh_custom_checkbox=results["block_loadh_custom_checkbox"];
        if (block_loadh_custom_checkbox || dist_load_heavy){
            $("#load_heavy_textinput").attr("disabled", true);
            $("#load_heavy_textinput").prop("checked",true);
        } else {
            $("#load_heavy_textinput").removeAttr("disabled");
        }*/
        window.final_load_heavy=final_load_heavy;
    }    
    window.passInfoToIframe=passInfoToIframe;
    
    
    var passinfoToPlayTraj= function(){ //defined in the parent 
        var bs_info=obtainBS();
        window.bs_info=bs_info;
        var dist_sel_res=obtainDistSel();  
        var dist_of=dist_sel_res[0];  
        window.dist_of=dist_of;
        var water_dist=obtainWaterDist()[1];     //
        window.water_dist=water_dist;
        var water_check = obtainWaterDist()[0];
        window.water_check = water_check; 
    }
    window.passinfoToPlayTraj=passinfoToPlayTraj;
    
    function join_lil(myLil){
         var myLi=[];
         for (e=0 ; e < myLil.length ; e++ ){
             var res_s = myLil[e].join("-");
             myLi[myLi.length]=res_s.slice(0, -1);
         }
         var my_str = myLi.join();
         return (my_str);
    }
    



    function getCorrectSettingVal(settingsVal,defaultVal){
        if (settingsVal && settingsVal != defaultVal){// If it's the default we don't need to sent it to MDsrv
            settingsVal = Number(settingsVal);
            var pos = Math.abs(settingsVal)
            var rounded= Math.round(pos);
            if (rounded <= 0){
                var rounded = 1;
            } 
            if (settingsVal != rounded){
                settingsVal = rounded;
            }
            return (settingsVal.toString());
        } else {
            return ("");
        }
    }
    //Warnings
    saveNotShowWarningInCache = function(warning_type){
        $.ajax({
            type: "POST",
            url: "/view/"+dyn_id+"/", 
            dataType: "json",
            data: { 
              "warning_type":warning_type
            },
            timeout: 600000
            
        });
    }
    window.saveNotShowWarningInCache=saveNotShowWarningInCache;

    //Control representations
    $("#to_mdsrv").click(function(){
        var results = obtainURLinfo(gpcr_pdb_dict);
        var cp = results["cp"];
        var high_pre=results["high_pre"];
        var layers_lil = results["layers_li"];
        var traj =results["traj"];
        var nonGPCR =results["nonGPCR"];
        var nonGPCR = nonGPCR.join("-");
        var int_res_lil =results["int_res_li"];
        var int_res_lil_ch =results["int_res_li_ch"];
        var dist_groups_li=results["dist_groups_li"];
        var receptorsel = results["receptorsel"]; 
        var bs_info = results["bs_info"];
        var hbonds= results["hbondarray"];
        var atomssb=results["sbondarray"];
        var atomshb_inter=results[ "hb_inter"];
        var all_resids=results["allresidshb"];
        var all_resids_sb=results["allresidssb"];
        //var all_resids_inter=results[ "allresidshbInt"];
        var showH=results["showH"];
        var showHShort="f";
        if (showH){showHShort="t"};
/*
         var show_dots= $(".onclickshow.is_active").data("short");
         if (show_dots=="vars"){
            var pdb_vars= $("#view_screen").data("pdb_vars");
         } else if (show_dots=="muts"){
            var pdb_muts= $("#view_screen").data("pdb_muts");
            var pos_li=Object.keys(pdb_muts);
            var sel=".CA and ("+pos_li.join(" or ")+")";
         }*/

        //ED maps
        var results_ED=obtainURLinfo_ED(false);
        var loadEd=results_ED["loadEd"];
        if (loadEd){
            var ed_sel=results_ED["ed_sel"];
        } else {
            var ed_sel="";
        }
        var ed_Disp=$(".EDdisplay:checked");
        var ed_DispVs="";
        if (ed_Disp.length ==0){
            var ed_sel="";
        } else if (ed_Disp.length ==1){
            var ed_DispV=ed_Disp.val();
            ed_DispVs=ed_DispV[0];//To make it short, will be "2" or "f". If empty, show all
        }
        var edcol_li =edSt_li =ediso=edz=pdbid="";
        if (ed_sel){
            var pdbid=$("#pdbid").text();
            pdbid=pdbid.split(".")[0];

            var col2fofc=retrieveRowCol($("#ED2fofcColor"));
            if (col2fofc=="#87ceeb"){
                col2fofc="";
            }
            var colfofcP=retrieveRowCol($("#EDfofcColorPos"));
            if (colfofcP=="#3cb371"){
                colfofcP="";
            }
            var colfofcN=retrieveRowCol($("#EDfofcColorNeg"));
            if (colfofcN=="#ff6347"){
                colfofcN="";
            }
            edcol_li=[col2fofc,colfofcP,colfofcN].join(";");
            if (edcol_li.length==2){
                edcol_li="";
            }
            var edSt2fofc=$("#EDmapStype2fofc").val();
            if (edSt2fofc=="contour"){
                edSt2fofc=""
            } else{
                edSt2fofc=edSt2fofc[0]
            }
            var edStfofc=$("#EDmapStypefofc").val()
            if (edStfofc=="contour"){
                edStfofc=""
            } else{
                edStfofc=edStfofc[0]
            }
            edSt_li=[edSt2fofc,edStfofc].join(";");
            if (edSt_li.length==1){
                edSt_li="";
            }
            var ediso2fofc=$("#slider_val_2fofc").html()
            var edisofofc=$("#slider_val_fofc").html()
            var ediso=[ediso2fofc,edisofofc].join(";");
            var edz=$("#EDmapzoom_val").html();

            var edselSel=$("#edSel");
            var trajmat_dict=edselSel.data("trajmat_dict");
            var traj_id=$("#selectedTraj").find("#selectedTraj_id").text();
            var mat_info=trajmat_dict[traj_id];
            var r_angl=mat_info[0].join(";");
            var transl=mat_info[1].join(";");
            //var r_angl=edselSel.data("r_angl").join(";");
            //var transl=edselSel.data("transl").join(";");
        }

        int_res_s=join_lil(int_res_lil);
        int_res_s_ch=join_lil(int_res_lil_ch);
        var pd = "n";
        for (key in high_pre){
            if (key != "rep"){
                if (high_pre[key].length > 0){
                    pd = "y";
                    break;
                }
            }
        }
        var layers_li=[];
        var add_fpsegStr=false;
        for (layN=0 ; layN < layers_lil.length ;layN++){
            layer_l =layers_lil[layN];
            if (layer_l.indexOf("FPscheme") != -1){
                add_fpsegStr=true;
            }
            layer_l=layer_l.join("-,,-");
            layers_li.push(layer_l);
        }
        layers_li=layers_li.join("-;;-");
        if (receptorsel){
            add_fpsegStr=true;
        }
        if ($(".tmsel.active").length >0){
            add_fpsegStr=true;
        }
        var fpsegStr_send=[];
        if (add_fpsegStr){
            fpsegStr_send = fpsegStr;
        }
        var dist_sel_res=obtainDistSel();  
        var dist_of=dist_sel_res[0];  
        //var dist_load_heavy=dist_sel_res[1];  

        for (dN=0 ; dN < dist_of.length ; dN++){
            dn_pre=dist_of[dN];
            dn_now=dn_pre.replace(/-\w*$/,"");
            dist_of[dN]=dn_now
        }
        var projection="";
        if ($("#projOrtho").hasClass("active")){
            projection="o"
        }
        ////////// [!] CHECK IF IS OK AND CONTINUE!!! : 
        
        var spin="";
        if ($("#spinOn").hasClass("active")){ spin="y"}
        var intType="";
        if ($("#trajIntType").val() == "spline"){
            intType="s";
        } else if ($("#trajIntType").val() == "linear"){
            intType="l";
        }
        var trajStepSend=getCorrectSettingVal($("#trajStep").val(),"3");
        var trajTimeOutSend=getCorrectSettingVal($("#trajTimeOut").val(),"50");
        
        var high_pre_colors_li=[];
        for (pos in high_pre["colors"]){
            high_pre_colors_li[high_pre_colors_li.length]=pos+"-"+high_pre["colors"][pos]
        }
        high_pre_colors_s=high_pre_colors_li.join(",");

        /////////
        var url_mdsrv=mdsrv_url+"/html/mdsrv_emb.html?struc=" + encode(struc) + "&pd=" + pd;    

        var add_url_var ={"traj":encode(traj) ,
                            "fp":encode(fpsegStr_send),
                            "ly":encode(layers_li) , 
                            "cp":encode(cp),
                            "la":encode(high_pre["A"]),
                            "lb":encode(high_pre["B"]),
                            "lc":encode(high_pre["C"]),
                            "lf":encode(high_pre["F"]), 
                            "lz":encode(high_pre_colors_s), 
                            "wtn":encode(dist_of) , 
                            "in":encode(int_res_s),
                            "ih":encode(int_res_s_ch),
                            "ng":encode(nonGPCR) , 
                            "dc":encode(dist_groups_li),
                            "rs":encode(receptorsel),
                            "bs":encode(bs_info),
                            "hb":encode(hbonds),
                            "sb":encode(atomssb),
                            "ib":encode(atomshb_inter),
                            "ar":encode(all_resids),
                            "as":encode(all_resids_sb),
                            //"ai" : encode(all_resids_inter),
                            "pj": projection,
                            "ha": showHShort,
                            "sp":spin,
                            "ti":intType,
                            "ts":trajStepSend,
                            "tt":trajTimeOutSend,
                            "eds":encode(ed_sel),
                            "edd":ed_DispVs,
                            "edc":encode(edcol_li),
                            "edi":ediso,
                            "edz":edz,
                            "pdb":pdbid,
                            "edr":encode(r_angl),
                            "edt":encode(transl)

                            }        
  
        for (varn in add_url_var){
            var myvar =add_url_var[varn];
            if (myvar.length > 0){
                url_mdsrv += "&"+varn+"="+myvar;
            }
        }
        $(this).attr("href", url_mdsrv);
    });   
    

    $("#clearAll").click(function(){
        all_resids_sasa=[];
        atomshb=[];
        all_resids=[];
        atomshb_inter=[];
        atomssb=[];
        all_resids_sb=[];
        removeCompBtns();
        $(".tmsel").removeClass("active");
        $(".sel_input, .dist_from, .dist_to, #rmsd_frame_1, #rmsd_frame_2, #rmsd_ref_frame, #int_thr, .seq_input, .inp_stride, .dis_res_bth").val("");
        $(".sel_within").find(".inputdist").val("");
        $(".sel_within").find(".user_sel_input").val("");
        $(".sel_within").find(".dist_sel:not(:first-child)").each(function(){
            $(this).remove();
            $(".sel_within").find(".add_btn:last").css("visibility","visible");            
        });
        var last_selWth_row=$(".sel_within").find(".dist_sel");
        inactivate_row(last_selWth_row,false);
        last_selWth_row.find(".alert_sel_wth_gnum").html("");
        last_selWth_row.find(".alert_sel_wth_ngl").html("");
        last_selWth_row.find("input").css("border-color","");
        $(".seq_sel.sel").each(function(){
            $(this).css("background-color","#f2f2f2");
            $(this).attr("class", "seq_sel");
        });
        $(".high_pd.active").each(function(){
            $(this).removeClass("active");
        });
        $(".traj_element").each(function(){
            $(this).attr("checked",false);
        });
        $(".dist_btw").find(".dist_pair:not(:first-child)").each(function(){
            $(this).remove();
            $(".dist_btw").find(".add_btn2:last , .imp_btn2:last").css("visibility","visible");
        });
        $(".dist_btw").find(".dist_pair").each(function(){
            $(this).find(".tick2").html("");
            $(this).find(".always2").attr("style","margin-left:14px");
            $(this).removeClass("d_ok"); 
        });
        $("#dist_chart").find(".display_this_dist").each(function(){
            $(this).attr("checked",false);
        });
        $("#int_info").find(".display_int").each(function(){
            $(this).attr("checked",false);
        });
        $("#int_info").find(".AA_td.showInP").each(function(){
            $(this).css("background-color","transparent").removeClass("showInP");
        });

        $("#text_input_all").find(".text_input:not(:first-child)").each(function(){
            $(this).remove();            
        });
        $("#text_input_all").find(".ti_add_btn:last").css("visibility","visible");
        $("#text_input_all").find(".input_dd_color").val("");
        var text_inp_row_alert=$("#text_input_all").find(".ti_alert");
        text_inp_row_alert.find(".ti_alert_gnum").html("");
        text_inp_row_alert.find(".ti_alert_ngl").html("");
        $("#text_input_all").find(".sel_input").css("border-color","");
        $("#seq_input_all").find(".seq_input_row:not(:first-child)").each(function(){
            $(this).remove();            
        });
        $("#seq_input_all").css("display","none");
        $("#seq_input_all").find(".si_add_btn").css("visibility","hidden");
        $("#seq_input_all").find(".seq_input").val("");
        $("#seq_input_all").find(".input_dd_color").val("");
        var seq_inp_row_alert=$("#seq_input_all").find(".si_alert");
        seq_inp_row_alert.find(".si_alert_gnum").html("");
        seq_inp_row_alert.find(".si_alert_ngl").html("");
        $("#seq_input_all").find("input").css("border-color","");
        
        $("#allSelTools").find(".input_dd_color").css("background-color","");
        $("#allSelTools").find(".span_morecolors").removeClass("has-error");
        
        $("#addToSel").css("display","none");
        firstsel=true;
        $("#analysis_bonds").find(".showhb_inter.active").removeClass("active");
        $("#analysis_salt").find(".showsb.active").removeClass("active");
        $("#analysis_bonds").find(".showhb.active").removeClass("active");
        $(".WaterDisplay , .WaterDistDisplay").prop("checked",false);
        $('#embed_mdsrv')[0].contentWindow.hideAllWaterMaps();
        //$("#FPdisplay").removeClass("active");
        //$("#FPdisplay").text("Display interactions");
        emptyFPsels();

        fpSelInt={};
        FpSelPos={};
        
        $("#selectionDiv").trigger("click");

        //Clear ED Reos:
        removeEDCompBtns();
        $("#text_input_all").find(".ed_input_rep").each(function(){
            rmTextInputRow($(this));
        });
        $(".ed_input").val("").css("border-color","");
        $(".ed_alert_inst").html("");
        $(".ed_seq_sel.sel").each(function(){
            $(this).css("background-color","#f2f2f2");
            $(this).attr("class", "ed_seq_sel");
        });
        $("#EDselectionDiv").trigger("click");
        $(".hide_all_tun").trigger("click");
    }); 


    $('#varinfo_par').tooltip({
        selector: '.showtooltip',
        trigger:"hover",
        html:true,
        container: "#view_screen"

    });  

    $('body').tooltip({
        selector: '.basictooltip',
        trigger:"hover",
        html:true,
        container: "body"
    });  

    $("#varinfo_par").on("click", ".close_var_mut" , function(){
        $("#varinfo_par").html("");
        //$('.popover').popover("hide");                    
    });


    $('.selectpicker').selectpicker();

//    $("#content:not(#varinfo_par)").on("click", function(){
//        $("#varinfo_par").html("");
//    });

//    $("body:not(#varinfo_par)").on("mousedown" , function(){
//        $("#varinfo_par").html("");
//    });

// ---------- Tunnels

    var tunnels_dict=$("#analysis_tunnels").data("tunnels");
    //var dyn_clu_merge=$("#analysis_tunnels").data("dyn_clu_merge");
    var tun_clust_rep_avail=$("#analysis_tunnels").data("tun_clust_rep_avail");


    function tunnel_color_from_clusternum(cluster_num){
        tun_color_li=["#0080ff","#009900","#ff0000" ,"#00ffff","#ffff00","#ff00ff","#ffa500","#d2b48c","#ffc0cb","#990099","#00ff00","#b784a7",'#ADB57B', '#16BF33', '#1DE1DF', '#A30E0A', '#94EF24', '#01296D', '#E46EA6', '#41B664', '#A4CDD8', '#3682AA', '#C107E4', '#C7A5AA', '#CB3851', '#6C6010', '#BB8298', '#25A811', '#8EAAAE', '#F355DB']
        if( cluster_num>=tun_color_li.length){
            var color_num=cluster_num % tun_color_li.length; 
        } else {
            var color_num=cluster_num
        }
        var color_code=tun_color_li[color_num];
        return color_code
    }

    
    update_tunnelfiles = function(traj_id_s){
        //When trajectory changes, the list of clusters and associated filesZ is updated
        if (tunnels_dict){
            var traj_id=Number(traj_id_s);
            var cluster_li=tunnels_dict[traj_id];
            var td_btns="<td></td>\
                         <td style='text-align:center'>\
                             <button type='button' class='btn btn-default btn-xs changefocus tun_display_btn show_all_tun' data-target='.tun_cluster_display_clus' >Show<br>all</button>\
                             <button type='button' class='btn btn-default btn-xs changefocus tun_display_btn hide_all_tun' data-target='.tun_cluster_display_clus'>Hide<br>all</button>\
                         </td>";
            var td_style="<td  style='text-align:right;font-weight:bold'>Style</td>\
                            <td style='text-align:center'>\
                                <select class='form-control input-sm tun_display_style' data-target='.tun_cluster_display_clus' style='padding:0;font-size:14px;margin:1px'>\
                                   <option selected='' value='line'>Line</option>\
                                   <option value='spacefill'>Spacefill</option>\
                                   <option value='line+spacefill'>Ball+stick</option>\
                                   <option value='licorice'>Licorice</option>\
                                   <option value='surfaceWireframe'>Surface wireframe</option>\
                                   <option value='surfaceOpaque'>Surface opaque</option>\
                                </select>\
                                <span id='loading_tun_style_clus' style='display:none' ><img src='/static/view/images/loading-gear.gif' style='width:17px;height:17px;'/></span>\
                            </td>";
            /*var td_opacity="<td style='text-align:center'>\
                                  <center>\
                                    <div style='max-width:150px;display:inline-block'>\
                                      <input id='slider_tunnel_clusters' class='slider slider_tunnel' data-tuntype='clust' value='100' min='0' max='100' step='1' type='range'>\
                                    </div>\
                                    <div  id='slider_val_tunnel_clusters' class='slider_val_tunnel' style='width:20px;display:inline-block;color:#b3b3b3'>100</div>\
                                  </center>\
                                </td>";    */                      
            if (tun_clust_rep_avail){
                td_btns+="<td style='text-align:center'>\
                            <button type='button' class='btn btn-default btn-xs changefocus tun_display_btn show_all_tun'  data-target='.tun_cluster_display_repr'>Show<br>all</button>\
                            <button type='button' class='btn btn-default btn-xs changefocus tun_display_btn hide_all_tun' data-target='.tun_cluster_display_repr'>Hide<br>all</button>\
                          </td>";
                td_style+="<td style='text-align:center'>\
                                -\
                            </td>";
                /*td_opacity+="<td style='text-align:center'>\
                                  <center>\
                                    <div class='' style='max-width:150px;display:inline-block'>\
                                      <input id='slider_tunnel_ht' class='slider slider_tunnel' data-tuntype='repr' value='100' min='0' max='100' step='1' type='range'>\
                                    </div>\
                                    <div  id='slider_val_tunnel_ht' class='slider_val_tunnel' style='width:20px;display:inline-block;color:#b3b3b3'>100</div>\
                                  </center>\
                                  </td>";*/
            }
            var tbody_html="<tr style='background-color:#FCFCFC'>\
                            "+td_btns+"\
                            </tr>\
                            <tr style='background-color:#FCFCFC'>\
                            "+td_style+"\
                            </tr>";
            for (c=0;c < cluster_li.length; c++){
                var clurser_num=c+1;
                var cluster=cluster_li[c];
                var rep_tun_frame=cluster[1][1];
                var cluster_clu=JSON.stringify( cluster[0]);
                var td_viewtun="<td style='text-align:right;font-weight:bold'>\
                                  <div style='width: 36px;float: right;'>\
                                    <div style='float:left'>\
                                      c"+clurser_num+"\
                                    </div>\
                                    <div style='float:right;display: block;margin: 7px 0 7px 7px'>\
                                      <span style='height: 5px;width:5px;background-color:"+tunnel_color_from_clusternum(clurser_num)+";border-radius: 50%;display: inline-block;'></span>\
                                    </div>\
                                  </div>\
                                </td>\
                                <td style='text-align:center'>\
                                  <label class='checkbox' style='margin:0'>\
                                    <input  type='checkbox'  class='tun_cluster_display tun_cluster_display_clus' value='clustering_c"+clurser_num+"' style='margin-left:-5px;margin-top:0,margin-bottom:0' data-file_li='"+cluster_clu+"' data-traj_id='"+traj_id+"'>\
                                  </label>\
                                </td>";
                if  (tun_clust_rep_avail){
                    td_viewtun+="<td style='padding:0 0 5px 0' >\
                                  <center>\
                                    <div style='width:100px'>\
                                      <div style='float:left;top:-10px;width:20px;padding-top:5px'>\
                                          <label class='checkbox' style='margin:0'>\
                                            <input  type='checkbox'  class='tun_cluster_display tun_cluster_display_repr' value='repr_c"+clurser_num+"' style='margin-left:-5px;margin-top:0,margin-bottom:0;display:block;position:relative' data-traj_id='"+traj_id+"'  >\
                                          </label>\
                                      </div>\
                                    <div style='display:block;width:80px;float:left;margin-top:5px'>\
                                      <button class='btn btn-default btn-xs display_rep_tunnel_fr' type='button' style='width:80px' data-frameNum='"+rep_tun_frame+"'>\
                                        Display<br>frame "+rep_tun_frame+"\
                                      </button>\
                                     </div>\
                                    </div>\
                                  </center>\
                                </td>";
                }
                var cl_row="<tr>\
                            "+td_viewtun+"\
                            </tr>";
                tbody_html+=cl_row;
            }
            $("#tunnel_options tbody").html(tbody_html)

        }

    }
    window.update_tunnelfiles=update_tunnelfiles;


    $('#tun_repr_tooltip').tooltip();  
    //$('.structuresel_tooltip').tooltip();  
    



//-------- Flare Plots --------
    function showHideTitle(titletext,newWord){
        if (newWord == "display"){
            var newtitle=titletext.replace("hide", newWord);
        } else {
            var newtitle=titletext.replace("display", newWord);
        }
        return (newtitle);
    }

   

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
                $("#fp_int_type_info").html('<p class="fp_int_type_info_pf">Hydrogen bonds:</p><p class="fp_int_type_info_p">'+$(this).text()+'</p>');
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
    

  /*  $(".fpShowResSet").on("click",function(){
        if ($(this).hasClass("active")){
            var newtitle=showHideTitle($(this).attr("title"),"display");
            $(this).removeClass("active").attr("title",newtitle);
            
            var siblBtn= $(this).siblings(".fpShowResSet");
            if (! siblBtn.hasClass("active")){
                var newtitle=showHideTitle(siblBtn.attr("title"),"hide");
                siblBtn.addClass("active").attr("title",newtitle);
            }
        } else {
            var newtitle=showHideTitle($(this).attr("title"),"hide");
            $(this).addClass("active").attr("title",newtitle);
        }
        
        //create new FP but saving the selected contacts
        
        //$("#selectionDiv").trigger("click");
        changeContactsInFplot()
    });*/
    
    //-------------------
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
            
            if (is_network_default){
                FPselectALLnodes();
            }  else {
                for (nN=0;nN<pre_resSelected.length;nN++){//Select at plot the residues selected before
                    var mynodenum=pre_resSelected[nN];
                    if ($("#node-"+mynodenum).length > 0){
                        plot.toggleNode(mynodenum);
                    } 
                }

            }

            updateFPInt()// //Update fpSelInt depending on what is in the fplot.
            updateFPpos()
            $("#selectionDiv").trigger("click");
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

    function createFlareplotCustom(fpsize, jsonData, fpdiv, showContacts){
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
        plot=createFlareplot(fpsize, fpjson, fpdiv,true);
        hoverlabelsFP()
        hoverLinksFP()
        plot.addEdgeToggleListener( function(d){
            clickEdgeSelectNodes(d);
        });

        return(plot);
    }




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

    function FPselectALLnodes(){
        $("#flare-container").find("g.node").each(function(){
            var nodename=$(this).attr("id");
            if (nodename.indexOf("node-") !== -1){
                var nodenum=nodename.split("-")[1];                
                plot.toggleNode(nodenum);
            }
        })
        updateFPInt();
        updateFPpos()
    }

    var show_fp=$("#fpdiv").data("show_fp");
    var fpfile = $("#selectedTraj").data("fplot_file");
    //fpfile="10140_trj_4_hbonds.json";//

    var plot, allEdges, numfr;
    var fpSelInt={};
    var FpSelPos={};
    if (show_fp && fpfile){
        var fpsize=setFpNglSize(true); 
        showContacts=$(".fp_display_element_type.is_active").data("tag");       
        d3.json(fpfile, function(jsonData){
            plot = createFlareplotCustom(fpsize, jsonData, "#flare-container" , showContacts);
            $("#loading_fp").css({"display":"none","position":"absolute"})
            allEdges= plot.getEdges()
            numfr = plot.getNumFrames();
            if (is_network_default){
                FPselectALLnodes()
            }

        });

    } else {
        $("#loading_fp").css("display","none")
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
        }
        return(fpSelInt_send)
    }
    window.updateFlarePlotFrame=updateFlarePlotFrame; 
      
//////////////    
    var fpgpcrdb_dict;
    for (gpcr_id in all_gpcr_dicts){
        fpgpcrdb_dict=all_gpcr_dicts[gpcr_id]["gpcrDB_num"];
    }
    
    
    function captureClickedFPInt(nodenum,nodeclass){
        //If the node was not clicked before: Takes a given node and search for all the residues with which it interacts. If the num of interacting res > 0, adds the info of the node + int. nodes to fpSelInt. If the node was clicked before: removes it from fpSelInt.
        var nodepos=fpgpcrdb_dict[nodenum].join(":");
        if (nodeclass.indexOf("toggledNode") == -1){
            delete fpSelInt[nodepos];
        } else {
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
                fpSelInt[nodepos]=edges;
            }
        }
        $("#selectionDiv").trigger("click");    
    }

    function captureClickedFPPos(){
        //Find selected positions in flareplot
        selected_pos = []
        FpSelPos = [];
        $(".node.toggledNode text", window.parent.document).each(function(){
            selected_pos.push($(this).html())
        });

        //Translate them from ballesteros to chainid:resid
        selected_pos.forEach(function(pos){
            var nodepos=fpgpcrdb_dict[pos].join(":");
            FpSelPos.push(nodepos) 
        });

        // Save selected positions in iframe and trigger change
        body_iframe = $('#embed_mdsrv')[0].contentWindow.$('body')
        body_iframe.attr('sel', FpSelPos.join(' or '))
        body_iframe.trigger('updFpReps');
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
        captureClickedFPPos()
    });

    function updateFPInt(){
        //Updates the fpSelInt dict depending on the nodes that are clicked
        allEdges= plot.getEdges()
        var updFpSelInt={}
        $("#flare-container").find("g.node.toggledNode").each(function(){
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
            updateFPpos();
        }
        $("#selectionDiv").trigger("click");
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
            updateFPpos();
        }
        $("#selectionDiv").trigger("click");
    });
    
    $("#fpdiv").on("click","#FPclearSel",function(){
        emptyFPsels();
        fpSelInt={};
        FpSelPos = {}
        //plot.setFrame(pg_framenum);
        $("#selectionDiv").trigger("click");
    });

    $("#analysisDiv").click(function(){
        $("#flare-container").find("g.trackElement").each(function(){
            var nodeid=$(this).attr("id");
            var nodenum=nodeid.split("-")[1];
            $(this).attr("title",nodenum);
        });
    })

    $(".clear_auto").click(function(){
        var thisclear=$(this);
        $(thisclear.data("target")).html("")
        if (thisclear.data("hide_btn")){
            thisclear.css("display","none")
        }
    })

    function prepare_multisel_for_ajax(multisel){
        var res="";
        if (multisel){
            res=multisel.join(";");
        } 
        return res;
    }


//-------- Chemical shift --------

    //Atoms per residue analyzed in shiftx2 and Sparta (the two softwares we use to calculate CS)
    anames_resname ={
        //shiftx2
        "" : {"ALA":["C","CA","CB","H","HA","HB","HB2","HB3","N"],
                        "ARG":["C","CA","CB","CD","CG","CZ","H","HA","HB2","HB3","HD2","HD3","HE","HG2","HG3","N"],
                        "ASN":["C","CA","CB","CG","H","HA","HB2","HB3","HD21","HD22","N"],
                        "ASP":["C","CA","CB","CG","H","HA","HB2","HB3","N"],
                        "CYS":["C","CA","CB","H","HA","HB2","HB3","N",],
                        "GLU":["C","CA","CB","CD","CG","H","HA","HB2","HB3","HG2","HG3","N"],
                        "GLN":["C","CA","CB","CD","CG","H","HA","HB2","HB3","HE21","HE22","HG2","HG3","N"],
                        "GLY":["C","CA","H","HA","HA2","HA3","N"],
                        "HIS":["C","CA","CB","CD2","CE1","CG","H","HA","HB2","HB3","HD2","HE1","N"],
                        "ILE":["C","CA","CB","CD1","CG1","CG2","H","HA","HB","HD1","HG12","HG13","HG2","N"],
                        "LEU":["C","CA","CB","CD1","CD2","CG","H","HA","HB2","HB3","HD1","HD2","HG","N"],
                        "LYS":["C","CA","CB","CD","CE","CG","H","HA","HB2","HB3","HD2","HD3","HE2","HE3","HG2","HG3","HZ","N"],
                        "MET":["C","CA","CB","CE","CG","H","HA","HB2","HB3","HE","HG2","HG3","N"],
                        "PHE":["C","CA","CB","CD1","CD2","CE1","CE2","CG","CZ","H","HA","HB2","HB3","HD1","HD2","HE1","HE2","HZ","N"],
                        "PRO":["C","CA","CB","CD","CG","HA","HB2","HB3","HD2","HD3","HG2","HG3"],
                        "SER":["C","CA","CB","H","HA","HB2","HB3","N"],
                        "THR":["C","CA","CB","CG2","H","HA","HB","HG2","N"],
                        "TRP":["C","CA","CB","CD1","CD2","CE2","CG","H","HA","HB2","HB3","HD1","HE1","HE3","N"],
                        "TYR":["C","CA","CB","CD1","CD2","CE1","CE2","CG","CZ","H","HA","HB2","HB3","HD1","HD2","HE1","HE2","N"],
                        "VAL":["C","CA","CB","CG1","CG2","H","HA","HB","HG1","HG2","N"]},
        //sparta
        "sparta_" : {"ALA":["C","CA","CB","H","HA","N"],
                        "ARG":["C","CA","CB","H","HA","N"],
                        "ASN":["C","CA","CB","H","HA","N"],
                        "ASP":["C","CA","CB","H","HA","N"],
                        "CYS":["C","CA","CB","H","HA","N"],
                        "GLU":["C","CA","CB","H","HA","N"],
                        "GLN":["C","CA","CB","H","HA","N"],
                        "GLY":["C","CA","H","HA2","HA3","N"],
                        "HIS":["C","CA","CB","H","HA","N"],
                        "ILE":["C","CA","CB","H","HA","N"],
                        "LEU":["C","CA","CB","H","HA","N"],
                        "LYS":["C","CA","CB","H","HA","N"],
                        "MET":["C","CA","CB","H","HA","N"],
                        "PHE":["C","CA","CB","H","HA","N"],
                        "PRO":["C","CA","CB","HA"],
                        "SER":["C","CA","CB","H","HA","N"],
                        "THR":["C","CA","CB","H","HA","N"],
                        "TRP":["C","CA","CB","H","HA","N"],
                        "TYR":["C","CA","CB","H","HA","N"],
                        "VAL":["C","CA","CB","H","HA","N"]}
    }


    var aa3to1=$("#analysis_cs").data("aa3to1");
    var cs_resid_names=$("#analysis_cs").data("residnames");
    var resid_to_resname=$("#analysis_cs").data("resid_to_resname");

    function set_active_atom_opts(atype, atom_names_u) {
        /*
        Decide, according to array "atom_names_u", which Atom Name options are to be disabled
        */
        if (atype=="2d") {
            aselect_sel = "#input_2datom1_cs,#input_2datom2_cs"
            opts_sel = "a.input_2datom1_cs_opt,a.input_2datom2_cs_opt"
        } else if (atype=='comp'){
            aselect_sel = "#input_atom_cs"
            opts_sel = "a.input_atom_cs_opt"
        } else {
            aselect_sel = "#input_satom_cs"
            opts_sel = "a.input_satom_cs_opt"
        }
        $(aselect_sel).selectpicker('deselectAll');// Deselect all for starters
        // In second atom selector of 2d we're gonna set up CA as default option (so not to coincide with first atom sleector)
        $('#input_2datom2_cs').val("CA");
        $('#input_2datom2_cs').selectpicker('refresh')
        //Hide or show options in atom selectors according to avaliable atoms in atom_names_u
        $(opts_sel).each(function(){
            opt = $(this)
            aname = opt.find(".text").html();//Extract residue name from option
            (atom_names_u.includes(aname)) ? opt.show() : opt.hide();
        })
    }

    function update_avaliable_atoms(atype, first=false) {
        /*
        Update avaliable atom names according to Residue and ResName selections
        first: first time the chemical shift thing is loaded
        */

        //First find which resnames are selected so far     
        sel_resids = []
        sel_resnames = []
        //If active CS analysis type is "single atom" (the one ressembling an RMSD plot)
        if (atype=="satom"){
            res_id= (first ? $("#input_sresid_cs").val() : $("#input_sresid_cs:visible").val());
            sel_resids.push(res_id)
            sel_resids.push($(".cs_resid_struc_sel:visible").data('resid'));
        }
        //If is the other two, select the visible (=active) one
        else {
            sel_resids = sel_resids.concat($("#input_"+atype+"resid_cs:visible").val());
            sel_resnames = sel_resnames.concat($("#input_"+atype+"resname_cs:visible").val());
            $(".cs_resid_struc_sel:visible").each(function(){
                sel_resids.push($(this).data('resid'));
            })
            //Remove any selections active in both AtomName selectors
            $("#input_atom_cs").selectpicker('deselectAll');
        }

        //Find resnames of selected resids
        sel_resids.forEach(resid => sel_resnames.push(resid_to_resname[resid]))

        //Now get active predictor and find avaliable atomnames for our selected resnames in selected predictor
        pred = $('input[name="cs_pred"]:checked').val(); 
        atom_names = []
        sel_resnames.forEach(function(resname){
            atom_names = atom_names.concat(anames_resname[pred][resname])  
        });
        atom_names_u = [...new Set(atom_names)] //Get unique atom names array
 
        // Decide active atomname options
        set_active_atom_opts(atype, atom_names_u)
    }

    function resname_to_resid(resnames){
        /*
        Find resIDs with the selected resnames
        */

        var res_ids =[];
        if (resnames){
            for (resid in resid_to_resname){
                resname = resid_to_resname[resid]
                if (resnames.includes(resname)) {
                    res_ids.push(resid)
                }
            }
        } 
        return res_ids;
    }



    function remove_cs_reps_if_any(){
        for (resatom in cs_repr_resatoms){
            if (cs_repr_resatoms[resatom]["display"]){
                cs_repr_resatoms={};
                $("#selectionDiv").trigger("click");
                break;
            }
        }
        cs_repr_resatoms={};
    }

    var cs_repr_resatoms={};
    function update_cs_plot(atype, is_loading=true){
        /*
        Generate a Chemical shift plot accoding to the selected options
        */

        //Get selected predictor
        pred = $('input[name="cs_pred"]:checked').val();

        //Check if "solution plots" option for 2d-plots is selected
        soluplots = $('input[name="cs_solution"]:checked').val()
        console.log(soluplots)

        frames_start = "all"; frames_end = "all";
        //If active CS analysis type is "single atom" (the one ressembling an RMSD plot)
        if (atype=="satom"){            
            cs_ressel_act=$(".cs_satom_tab_li.active").attr("id");

            //Delete vertical lines from previous plot (if there was any) 
            delete Bokeh.documents[0]
            Bokeh.documents.shift()

            //If using custom selector
            if (cs_ressel_act=="cs_satom_tab_free"){
                res_id=$("#input_sresid_cs").val();
                atoms=$("#input_satom_cs").val();
            //If using in-structure selector
            } else if (cs_ressel_act=="cs_satom_tab_structure"){
                var container = 'cs_satom_structure';                
                res_id=Number($(".cs_resid_struc_sel:visible").data('resid'));
                atoms=$("#"+container+" .cs_resid_struc_sel").data('natom');
            }
        }

        //If active CS analysis type is either "comparative" (Mariona's old one with the colorful lines) or Brian new "two-dimensional(2d)" plot
        else {
            active_tab_id=$(".cs_"+atype+"_tab_li.active").attr("id");
            //If using custom selector
            if (active_tab_id=="cs_"+atype+"_tab_free"){
                var res_id=prepare_multisel_for_ajax($("#input_"+atype+"resid_cs").val());
                var res_id_2=prepare_multisel_for_ajax(resname_to_resid($("#input_"+atype+"resname_cs").val()));
            //If using in-structure selector
            } else if (active_tab_id=="cs_"+atype+"_tab_structure"){
                var res_id_li=[], res_id, res_id_2;
                $(".cs_resid_struc_sel:visible").each(function(){
                    res_id_li[res_id_li.length]= Number($(this).data('resid'));
                })
                res_id=prepare_multisel_for_ajax(res_id_li);
                res_id_2="";
            }
            // Use apppropiate method to choose the atom types
            if (atype=='2d'){
                atoms=prepare_multisel_for_ajax([$("#input_2datom1_cs").val(), $("#input_2datom2_cs").val()])
                //Get frames if selected
                frameopt = $('input[name="cs_frames"]:checked').val();
                if (frameopt=="selected_frames"){
                    frames_start = $("#cs_frames_start").val()
                    frames_end = $("#cs_frames_end").val()
                }
            } 
            else {
                atoms=prepare_multisel_for_ajax($("#input_atom_cs").val());
            }
        }
        //Remove current CS plot
        $("#cs_chart_"+atype).html("");
        $(".error_cs").hide()
        //Not sure what this does
        remove_cs_reps_if_any();
        //If we have residues and atoms, lets compute the plot in the server
        if ((res_id || res_id_2) && atoms){
            var dyn_id=$(".str_file").data("dyn_id");
            var traj_id=$(".traj_element.tsel").attr("id").replace("traj_id_","");
            //Show loading thingi if this plot is currently visible
            if (is_loading){
                $(".cs_loading").show();
            }
            $("#cs_chart_satom").hide()
            //Data to submit
            $.ajax({
                type: "POST",
                url: "/view/update_bokeh/", 
                dataType: "json",
                data: { 
                    "atype" : atype,
                    "dyn_id":dyn_id,
                    "pred":pred,
                    "traj_id":traj_id,
                    "res_id": res_id,
                    "res_id_2": res_id_2,
                    "atoms":atoms,
                    "frames_start" : frames_start,
                    "frames_end" : frames_end,
                    "soluplots" : soluplots,
                },                
                success: function(cs_result) {
                    cs_repr_resatoms=cs_result["avail_res_atoms"];
                    var cs_result_str= (atype=='2d') ? cs_result['divscript_cs'] : cs_result["div_cs"]+cs_result["script_cs"];
                    $("#cs_chart_"+atype).html(cs_result_str)
                    //Autofocus only if the plot is currently visible
                    if (is_loading){
                        if (atype=="satom"){
                            $('#embed_mdsrv')[0].contentWindow.$('body').trigger('cs_focus_atom', [res_id,atoms])
                        }
                        else if (atype=='2d'){
                            $("#cs_chart_2d .traces").click(function(){
                                res = $(this).children('.legendtext').data('unformatted')
                                resid = res.split(' ')[0]
                                atomsel = atoms.replace(';',' or .')
                                $('#embed_mdsrv')[0].contentWindow.$('body').trigger('cs_focus_atom', [resid,atomsel])
                            });
                        }                        
                    }
                },
                error: function(error){
                    errordiv = $("#error_cs_"+atype);
                    if (error.statusText=='no_atoms'){
                        errordiv.html(error.responseText)
                    } else{
                        errordiv.html('An unexpected error ocurred')
                    }
                        errordiv.show()
                },complete: function(){
                    $("#cs_chart_satom").show()
                    $(".cs_loading").hide();
                },
                timeout: 600000
                
            });

        } 
    }

    // Select all option in CS selectors
    $('.cs_all').click( function () {
        option_class = $(this).data('selector');
        selector = $('#'+option_class)
        // If all options have already been selected, deselectall, mark "select" tag as deselected and untag "all" option
        if (selector.attr('allselected')){
            selector.selectpicker('deselectAll')
            selector.removeAttr('allselected')
            $(this).html("Select all")
        } else {
            selector.selectpicker('selectAll')
            selector.attr('allselected','true')
            $(this).html("Unselect all")
        }
    })

    //Ensure atom1 and atom2 in 2d plot are not the same
    $("#input_2datom1_cs, #input_2datom2_cs").change(function(){
        if ($("#input_2datom1_cs").val() == $("#input_2datom2_cs").val()){
            $("#same_atom_name").show()
            $("#cs_apply_2d").attr('disabled',true)
        }  
        else {
            $("#same_atom_name").hide()
            $("#cs_apply_2d").attr('disabled',false)            
        }
    })

    //Ensure AtomName dropdowns only displays atoms avaliable to the residues/resnames selected
    $(".cs_pred, #input_sresid_cs, #input_compresid_cs, #input_compresname_cs, #input_2dresid_cs, #input_2dresname_cs").change(function(){
        atype = $(".cs_apply:visible").val()//Active CS plot type
        update_avaliable_atoms(atype,false)
    })
    // update_avaliable_atoms('satom',true)

    $(document.body).bind('cs_resatom_clicked', function(e,res_instructins) {
        /*
        This is executed whem the bokeh JS callbacks triggers the 'cs_resatom_clicked' event, meaning that an atom has been selected or unselected in the plot. Bokeh sends the data on the atom that has been clicked/unclicked (res_instructins).
        This checks if the selected/unselected atom is already displayed in NGL, which is defined in 'cs_repr_resatoms'. If necessary, it triggers an event to re-generate the NGL representations. The data on NGL displayed atoms is updated. Also zooms in to the selected atoms.
        NGL representations will be made based on 'cs_repr_resatoms'
        */
        var resatomKey=res_instructins["resid"]+"."+res_instructins["atomname"];
        var displaythis=res_instructins["showresatom"]
        if (resatomKey in cs_repr_resatoms){
            var display_state=cs_repr_resatoms[resatomKey]["display"];
            var display_color=cs_repr_resatoms[resatomKey]["color"];
            if (display_state != displaythis){
                cs_repr_resatoms[resatomKey]["display"]=displaythis;
                $("#selectionDiv").trigger("click");
                if (displaythis){
                    $('#embed_mdsrv')[0].contentWindow.zoomtorep("chem_shift_selected");
                }
            }
        }
    });

    //Clear cs plots when clear button is clicked
    $(".cs_clear").click(function(){
        targ = $($(this).data("target"))
        targ.trigger('change') 
        targ.selectpicker('deselectAll');
    })

    //Render Cs plot (of desired type) when apply is clicked
    $(".cs_apply").on("click", function(){
        update_cs_plot($(this).val())
    })

    // On change of trajectory, 
    $(".traj_element").click(function(){
        //if new trajectory is not the same as the old ones 
        if (!($(this).hasClass("tsel"))){
            // if any chemical shift plots have been loaded, update them
            marker_satom = $("#cs_chart_satom .bk-root")
            marker_comp = $("#cs_chart_comp .bk-root")
            marker_2d = $("#cs_chart_2d .plotly")
            if (marker_satom[0]){
                update_cs_plot('satom',show_loading=marker_satom.is(":visible"))
            }
            if (marker_comp[0]){
                update_cs_plot('comp',show_loading=marker_comp.is(":visible"))                
            }
            if (marker_2d[0]){
                update_cs_plot('2d',show_loading=marker_2d.is(":visible"))
            }
        }
    });

    //Update frame of chemical shift plot whenever there is a frame change
    $("#analysis_cs").bind('update_cs_frame', function(e, frame) {
        // if there is a chart loaded
        if ($("#cs_chart_satom .bk-root")[0]){
            var cs_frameslider = Bokeh.documents[0].get_model_by_name("frameslider");
            cs_frameslider.value = frame
        }
    });

    //Predefined selections for chemical shift
    $(".predef_btn").click(function(){
        
        //Deacivate all buttons and activate this one
        $(".predef_btn").removeClass("active-btn")
        $(this).addClass("active-btn")

        //Get data from this predefined selection
        plotype = $(this).data('plotype');
        atom1 = $(this).data('atom1');
        atom2 = $(this).data('atom2');
        resname = $(this).data('resname');

        //Activate custom selection option (it will still remain hidden thougth)
        $("#cs_"+plotype+'_free').addClass('active')
        $("#cs_"+plotype+'_structure').removeClass('active')

        //If 2d plot
        $("#input_"+plotype+"resid_cs").selectpicker('deselectAll')
        $("#input_"+plotype+"resname_cs").selectpicker('val',resname)
        if (plotype=="2d"){
            $("#input_2datom1_cs").selectpicker('val',atom1)
            $("#input_2datom2_cs").selectpicker('val',atom2)
        } else {
            $("#input_atom_cs").selectpicker('val',[atom1,atom2])            
        }

    });

    //Disable or enable frame selector if option to do so is or not selected
    $(".cs_frames").on('change', function(){
        select_frames = $(this).attr('id') == 'all_frames'
        $(".cs_frames_input").prop('readonly', select_frames)
    })

    // To use the in-structure atom selectors of cs plots
    var csResidueSelFromStruc= function(resid, natom){ //defined in the parent 
        var cs_plot_resid_struc=[], container, code, resid, cell_content;
        var atype = $("#cs_atypes li.active").attr('value');
        resid = resid.toString();
        cell_content  = atype=='satom' ? resid.toString()+':'+natom : resid;
        container = 'cs_'+atype+'_structure';
        $("#"+container+" .cs_residue_struc_options_resid").each(function(){
            cs_plot_resid_struc[cs_plot_resid_struc.length]=Number($(this).find(container+" .cs_resid_struc_sel").html()).toString();
        })
        //Add also atom name if atype is satom
        if (! (cs_plot_resid_struc.indexOf(resid)>=0)){
            cs_plot_resid_struc[cs_plot_resid_struc.length]=resid;
            var residue_box='<div class="alert_custom cs_residue_struc_options_resid" >\
                             <span class="glyphicon glyphicon-remove pull-right alert_custom_close cs_residue_struc_options_resid_close"></span> \
                             <div  data-resid="'+resid+'" data-natom="'+natom+'"class="cs_resid_struc_sel">\
                                '+cell_content+'\
                              </div>\
                            </div>';
            //In satom selectors we only want a single selected cell at any moment
            if (atype == 'satom'){
                $("#cs_"+atype+"_struc_options").html(residue_box) ;
            }
            //Comparative and 2d selector can have multiple cells selected
            else {
                $("#cs_"+atype+"_struc_options").append(residue_box);
            } 
            $("#cs_"+atype+"_struc_clear").css("display","block");
        }

        //Delete residue/atom selection on-click of of small cross (remove also clear button if no positions remain visible)
        $(".cs_residue_struc_options_resid_close").click(function(){
            $(this).parent().remove()
            if (!$(".cs_residue_struc_options_resid:visible").length){
                $("#cs_"+atype+"_struc_clear").hide()
            }
        });

        //Update atom names
        update_avaliable_atoms(atype)

    }
    window.csResidueSelFromStruc=csResidueSelFromStruc;


//-------- Allosteric communications
    
    dyn_id=$(".str_file").data("dyn_id");

    //Dropdowns
    $('.dropdown-submenu').on("click", function(e){
      $(this).next('ul').toggle();
    });

    //Avoid dropdown menu to retract at click
    $('.ac_menu.dropdown-menu').on("click", function(e){
        e.stopPropagation();
    });


    //Leave marked option as text for bootstrap
    $(".dropdown-menu li label").click(function(){
      btn_element = $("#"+$(this).attr("data-btn"))
      btn_element.html($(this).text()+" <span class='caret'></span>");
      btn_element.val($(this).text());

    });

    //Mark input radio near base Residue information buttons
    $("label.ac_option").click(function(){
        id_btn = $(this).data('butt')
        $(".ac_btn").removeClass('checked')
        $("#"+id_btn).addClass('checked')
    })

    // If allosteric com option is clicked, update download link
    $(".ac_option input").on("change", function(){
        ac_value = $(this).attr('id');
        ac_download = $("#download_ac");
        ac_download.show()
        ac_download.attr('href',"/dynadb/files/Precomputed/allosteric_com/dyn"+dyn_id+"/"+ac_value+".csv");
    })



    //On click of "show only AC selected" button
    $("#ac_show_selected").click(function(){
        //Get selected pairs
        allsels = $(this).attr('data-selreps')
        $('#embed_mdsrv')[0].contentWindow.$('body').trigger('ac_load', [JSON.parse(allsels)]);            
    })

    //On click, remove AC interactions selection and restore original representatoin
    $("#ac_clearsel").click(function(){
        allsels = $(this).attr('data-allreps')
        $('#embed_mdsrv')[0].contentWindow.$('body').trigger('ac_load', [JSON.parse(allsels)]);
        //Empty selection button
        $("#ac_show_selected").attr('data-selreps',"[]")
        $(".ac_sel_cbx").prop('checked',false)
    })

    //On click of any of the AC table checkboxes
    $(document.body).bind('cbx_click',function(e, checkbox_id) {
        mycheckbox=$("#"+checkbox_id)
        mybutton = $("#ac_show_selected")
        ischecked = mycheckbox.is(":checked")
        rep = JSON.parse(mycheckbox.attr('data-reps'))
        selreps = JSON.parse(mybutton.attr('data-selreps'))
        if (ischecked) {
            selreps.push(rep)
        } else {
            io = selreps.indexOf(rep)
            selreps.splice(io)
        }
        mybutton.attr("data-selreps", JSON.stringify(selreps))
    })

    //On click of submit AC
    $('#ac_form').submit(function(e) {

        e.preventDefault(); // avoid to execute the actual submit of the form.
        var form = $(this);

        //Reset scale minimums to zero
        $(".ac_legend_min").html("0")

        //Hide error and show loading
        $("#ac_placeholder").hide()
        errordiv = $(".error_ac")
        loadingdiv = $(".ac_loading")
        legends = $(".ac_legend")
        resultsdiv = $("#ac_results")
        seloptdiv = $("#ac_sel_opt")
        nofilediv = $("#ac_nofile")
        nofilediv.hide()
        resultsdiv.hide()
        legends.hide()
        errordiv.hide()
        loadingdiv.show()
        seloptdiv.hide()
        
        $.ajax({
            url: "../ac_update/"+dyn_id+"/",
            data_type: 'json',
            type: 'POST',
            data: form.serialize(),
            success: function(ac_dict) {
                ac_dict = JSON.parse(ac_dict)
                if ('filenotfound' in ac_dict){
                    nofilediv.show()
                }
                else{
                    ac_data = ac_dict['ac_data']
                    $('#embed_mdsrv')[0].contentWindow.$('body').trigger('ac_load', [ac_data]);
                    
                    //Save ac_data in "clear selection" button (to restore original representations if required)
                    $("#ac_clearsel").attr('data-allreps', JSON.stringify(ac_data))

                    //Stablish proper minimum and maximum in legend scale
                    //wtyl for negative values, wtbl for positive
                    if (ac_dict['min'] <0){
                        $('#ac_legend_wtyl .ac_legend_max').html(ac_dict['min'])
                    } else {
                        $('#ac_legend_wtbl .ac_legend_min').html(ac_dict['min'])
                    }
                    if (ac_dict['max'] <0){
                        $('#ac_legend_wtyl .ac_legend_min').html(ac_dict['max'])
                    } else {
                        $('#ac_legend_wtbl .ac_legend_max').html(ac_dict['max'])
                    }

                    //Display legend with appropiate colors
                    ac_dict['colorscales'].forEach(function(scale){
                        $("#ac_legend_"+scale).show()
                    })

                    //Place table, and make it sortable
                    $("#ac_table_container").html(ac_dict['table'])
                    sorting_table('ac_table')

                    //Update checkbox selection
                    $("#ac_show_selected").attr('data-selreps','[]')

                    //Put name of selected AC type in appropiate div, so the user knows which one is active
                    $("#ac_sel_opt_name").html("<b>Selected option: </b>"+ac_dict['sel_opt'])

                    //Show
                    resultsdiv.show()
                    seloptdiv.show()
                }
            },
            error: function(e){
                errordiv.show()
            },
            complete: function(){
                loadingdiv.hide()
            }
        });
    });

//-------- Trigger NGL comp creation --------


    var isTriggered=true;
    window.isTriggered=isTriggered;
    
    $('body').on('iframeSet',function(){
        $('#embed_mdsrv')[0].contentWindow.$('body').trigger('iframeSetOk');
        //var screen_w = screen.width;    
        var cont_w_max=$("#main_container").css("width");
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
    

//-------- Call when everything has run --------
    createRepFromCrossGPCRpg();
});


