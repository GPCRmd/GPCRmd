$(document).ready(function(){
    
    $(".sel_input, .inputdist, .dist_from, .dist_to").val("");
    //$("#show_within").empty();
    // $("#rad_high").attr("checked",false).checkboxradio("refresh");
    // $("#rad_sel").attr("checked",true).checkboxradio("refresh");// CHECK IF WORKS, AND IF BOTH SEL AND HIGH ARE CHECKED OR ONLY SEL

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
        $(class_name).click(function(){
            pos_class=$(this).attr("class");
            if(pos_class.indexOf("active") > -1){
                $(this).removeClass("active");
            } else {
                $(this).addClass("active");
            }
            $("#selectionDiv").trigger("click");
        });
    }
  
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

    $(".settingsB").hover(function(){
        $(this).css("color","black");
    },
    function(){
        $(this).css("color","#585858");
    });
    
 /*   $("#addToSel").hover(function(){
        $(this).children().css("color","#449C44");
    },
    function(){
        $(this).children().css("color","#5CB85C");
    });*/
    
    
    $(".traj_element").hover(function(){
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
    
    /*$(".settingsB").click(function(){
        $(this).css("color","green");
        setTimeout(function(){ $(this).css("color","#585858"); }, 1000);
    });*/
    
//-------- Obtain important data from template --------
    var struc = $(".str_file").data("struc_file");
    var dyn_id=$(".str_file").data("dyn_id");
    var mdsrv_url=$("#embed_mdsrv").data("mdsrv_url");
    var sel = "";
    var sel_enc = sel;
    
    
    $(".traj_element").click(function(){
        var traj_p=$(this).data("tpath");
        var traj_n=$(this).text();
        $("#selectedTraj").data("tpath",traj_p).html(traj_n+' <span class="caret">');
        $(this).css("background-color","#FFF7F7").addClass("tsel");
        $(this).siblings().css("background-color","#FFFFFF").removeClass("tsel");
    });
    
    /*function obtainCheckedTrajs(){
        var traj = [];
        $(".traj_element").each(function(){
            traj[traj.length]=$(this).data("tpath");
        }); 
        return traj;
    }*/
    
    function obtainDicts(gpcr_pdb_dict){
        all_gpcr_dicts={};
        var num_gpcrs=0;
        for (gpcr_id in gpcr_pdb_dict){
            var bw_dict={};
            var gpcrdb_dict={};
            for (gen_num in gpcr_pdb_dict[gpcr_id]) {
                split=gen_num.split(new RegExp('[\.x]','g'));
                bw = split[0]+"."+ split[1];
                db = split[0]+"x"+ split[2];
                bw_dict[bw]=gpcr_pdb_dict[gpcr_id][gen_num];
                gpcrdb_dict[db]=gpcr_pdb_dict[gpcr_id][gen_num];
            }
            num_gpcrs++;
            all_gpcr_dicts[gpcr_id]={"combined_num":gpcr_pdb_dict[gpcr_id], "bw_num": bw_dict, "gpcrDB_num":gpcrdb_dict};
        }
        return [all_gpcr_dicts , num_gpcrs];
    }
    
    //var traj=obtainCheckedTrajs();
    $("#receptor").addClass("active");
    //$(".nonGPCR").addClass("active");

    var chains_str =$("#receptor").attr("title"); 
    var all_chains = $(".str_file").data("all_chains").split(",");

    var gpcr_pdb_dict = $(".gpcr_pdb").data("gpcr_pdb");
    var bw_dict,gpcrdb_dict,gpcr_id_name,all_gpcr_dicts,num_gpcrs;
    if (gpcr_pdb_dict !="no"){
        gpcr_id_name=$("#cons_pos_box_all").data("gpcr_id_name");
        //gpcr_pdb_dict=JSON.parse(gpcr_pdb_dict);
        dicts_results=obtainDicts(gpcr_pdb_dict);
        all_gpcr_dicts=dicts_results[0];
        num_gpcrs =dicts_results[1];
    }

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
        }
    });
//-------- Text Input --------

    function displayDropBtn(input_select){
        $(input_select).on("click",".dropbtn",function(){
            if ($(this).hasClass("opened")){
                $(this).siblings(".dropdown-content").css("display","none");
                $(this).removeClass("opened");
            }else {
                $(this).siblings(".dropdown-content").css("display","block");
                $(this).addClass("opened");
            }
        });
    }
    displayDropBtn("#text_input_all");
    displayDropBtn("#seq_input_all");
    
    function colorSel(input_select){
        $(input_select).on("click",".dropcolor",function(){
            var dCont=$(this).parent();
            var dBtn=dCont.siblings(".dropbtn");
            var dDwn=dBtn.parent();
            dCont.css("display","none");
            dBtn.removeClass("opened");
            if ($(this).hasClass("morecolors")){
            
                var clicked_color= $(this).data("color");
                var old_color=dBtn.data("color");

                $(this).css({"background-color":old_color , "border":"none"}).html("").removeClass("morecolors").data("color",old_color);
                dBtn.css({"background-color":clicked_color , "border":"1px solid #808080" /*, "vertical-align":"-3px"*/}).html('<span style="color:#696969;padding-bottom:2px" class="glyphicon glyphicon-plus-sign"></span>').addClass("morecolors").data("color",clicked_color);

                dDwn.siblings(".span_morecolors").html('<input type="text" style="font-size:12px;height:24px;margin: 3px 0 0 3px;  width:60px;padding-left:3px;padding-right:3px;" placeholder="#FFFFFF" class="form-control input-sm input_dd_color nglCallChangeTI">');

                
            } else {     
                if (dBtn.hasClass("morecolors")){
                    var clicked_color= $(this).data("color");
                    var old_color=dBtn.data("color");
                    dBtn.css({"background-color":clicked_color , "border":"none" /*, "vertical-align":"2px"*/}).html("").removeClass("morecolors").data("color",clicked_color);
                    $(this).css({"background-color":old_color , "border":"1px solid #808080"}).html('<span style="color:#696969;padding-left:1px" class="glyphicon glyphicon-plus-sign"></span>').addClass("morecolors").data("color",old_color).appendTo(dCont);
                    dDwn.siblings(".span_morecolors").html('');

                } else {
                    var clicked_color= $(this).data("color");
                    var old_color=dBtn.data("color");
                    $(this).css("background-color",old_color).data("color",old_color);
                    dBtn.css("background-color",clicked_color).data("color",clicked_color);
                }
            }
        });
    }
    colorSel("#text_input_all");
    colorSel("#seq_input_all");
    
    function obtainTextInput(){
        var layer=[];
        $("#text_input_all").find(".text_input").each(function(){
            $(this).find(".span_morecolors").removeClass("has-error");
            var pre_sel = $(this).find(".sel_input").val();
            sel_enc =inputText(gpcr_pdb_dict,pre_sel,false,"main",".ti_alert");
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
            }
        });
        
        $("#seq_input_all").find(".seq_input_row").each(function(){
            $(this).find(".span_morecolors").removeClass("has-error");
            var pre_sel = $(this).find(".seq_input").val();
            sel_enc =inputText(gpcr_pdb_dict,pre_sel,false,"main",".si_alert");
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
            }
        });
        return(layer);
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
    maxInputLength('#rmsd_my_sel_sel',"",50);
    maxInputLength("#int_thr", "",4);
    maxInputLength(".inp_stride", "",4);
    maxInputLength(".sel_within", ".user_sel_input",40);
    maxInputLength(".maxinp8","",8);



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


    var ti_i=1;
    $("#text_input_all").on("click",".ti_add_btn",function(){ 
        if ($("#text_input_all").children().length < 20){
            $("#text_input_all").find(".ti_add_btn").css("visibility","hidden");
            var row='<div  class="text_input" id="ti_row'+ti_i+'" style="margin-bottom:5px">\
                           <div  class="row">\
                              <div class="col-sm-11 ti_left" style="padding-right:3px;padding-left:3px"> \
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
                                        </select>\
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
                              <div class="col-sm-1 radio" style="padding-right:0;padding-left:0;margin-top:7px;width:48px;text-align: center">\
                                    <button class="btn btn-link ti_rm_btn" style="color:#DC143C;font-size:20px;margin:0;padding:0;"><span class="glyphicon glyphicon-remove-sign"></span></button>\
                                    <button class="btn btn-link ti_add_btn" style="color:#57C857;font-size:20px;margin:0;padding:0"><span class="glyphicon glyphicon-plus-sign"></span></button>\
                              </div>\
                          </div>\
                          <div class="ti_alert"> </div>      \
                      </div>';

            $("#text_input_all").append(row);
            ti_i+=1;
        }
    });
    
    $("#text_input_all").on("click", ".ti_rm_btn" , function(){
        var numTiRows = $("#text_input_all").children().length;
        var inpval= $(this).closest(".text_input").find(".sel_input").val();
        if(numTiRows==1){
            $("#text_input_all").find(".sel_input").val("");
        }else{
            var wBlock =$(this).closest(".text_input");
            if (wBlock.is(':last-child')){
                wBlock.remove();
                $("#text_input_all").find(".ti_add_btn:last").css("visibility","visible");
            } else {
                wBlock.remove();
            }
        }
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



///////////////

    var si_i=1;
    $("#seq_input_all").on("click",".si_add_btn",function(){ 
        if ($("#seq_input_all").children().length < 20){
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
                                           <option value="hydrophobicity">Hydrophobicity</option>\
                                        </select>\
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
                          <div class="si_alert"> </div>\
                      </div>';

            $("#seq_input_all").append(row);
            si_i+=1;
        }
    });
    
    $("#seq_input_all").on("click", ".si_rm_btn" , function(){
        var inpval= $(this).closest(".seq_input_row").find(".seq_input").val();
        var numSiRows = $("#seq_input_all").children().length;
        if(numSiRows==1){
            $("#seq_input_all").css("display","none");
            $("#seq_input_all").find(".seq_input").val("");
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
    
    function parseGPCRnum(sel,lonely_gpcrs,rownum,inpSource,alertSel){
        var add_or ="";
        if (num_gpcrs >1){
            add_or=" or ";
        }    
        for (i in lonely_gpcrs) {
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
                        to_add='<div class="alert alert-danger row" style = "margin-bottom:10px" ><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>'+my_gpcr+' not found at '+gpcr_id_name[gpcr_id]+'.</div>';
                        $(alertSel).append(to_add);
                    } else {
                        to_add='<div class="alert alert-danger row" style = "padding:5px;font-size:12px;margin-top:3px;margin-bottom:10px;margin-left:14px;width:430px" ><a href="#" class="close" data-dismiss="alert" aria-label="close" style = "font-size:15px" >&times;</a>'+my_gpcr+' not found at '+gpcr_id_name[gpcr_id]+'.</div>';
                        $("#"+rownum).find(".alert_sel_wth").html(to_add);
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
                subst_pos_all="protein and ("+subst_pos_all+")";
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
        for (i in gpcr_ranges) {
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
                for (n in gpcr_pair){
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
                            to_add='<div class="alert alert-danger row" style = "margin-bottom:10px" ><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>'+gpcr_pair_str+' not found at '+gpcr_id_name[gpcr_id]+'.</div>';
                            $(alertSel).append(to_add);
                        } else {
                            to_add='<div class="alert alert-danger row" style = "padding:5px;font-size:12px;margin-top:3px;margin-bottom:10px;margin-left:14px;width:430px" ><a href="#" class="close" data-dismiss="alert" aria-label="close" style = "font-size:15px" >&times;</a>'+gpcr_pair_str+' not found at '+gpcr_id_name[gpcr_id]+'.</div>';
                            $("#"+rownum).find(".alert_sel_wth").html(to_add);
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
                        for (chain in considered_chains){
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
        var gpcr_ranges=obtainInputedGPCRrange(pre_sel);
        if (gpcr_ranges == null){
            sel = pre_sel ;
        } else if (gpcr_pdb_dict=="no"){
            sel = "";
            if (inpSource=="main"){
                to_add='<a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>GPCR generic residue numbering is not supported for this stricture.';
                $(alertSel).attr("class","alert alert-danger row").append(to_add);
            } else {
                to_add='<div class="alert alert-danger row" style = "padding:5px;font-size:12px;margin-top:3px;margin-bottom:10px;margin-left:14px;width:430px" ><a href="#" class="close" data-dismiss="alert" aria-label="close" style = "font-size:15px" >&times;</a>GPCR generic residue numbering is not supported for this stricture.</div>';
                $("#"+rownum).find(".alert_sel_wth").html(to_add);
            }
        } else {
            sel=parseGPCRrange(pre_sel,gpcr_ranges,rownum,inpSource,alertSel);
        }
        var lonely_gpcrs=obtainInputedGPCRnum(sel);
        if (lonely_gpcrs != null){
            if (gpcr_pdb_dict=="no"){
                sel = "";
                if (inpSource=="main"){
                    to_add='<a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>GPCR generic residue numbering is not supported for this stricture.';
                    $(alertSel).attr("class","alert alert-danger row").append(to_add);
                } else {
                    to_add='<div class="alert alert-danger row" style = "padding:5px;font-size:12px;margin-top:3px;margin-bottom:10px;margin-left:14px;width:430px" ><a href="#" class="close" data-dismiss="alert" aria-label="close" style = "font-size:15px" >&times;</a>GPCR generic residue numbering is not supported for this stricture.</div>';
                    $("#"+rownum).find(".alert_sel_wth").html(to_add);
                }
            } else {
                sel=parseGPCRnum(sel,lonely_gpcrs,rownum,inpSource,alertSel);
            }
        }
        var sel_sp = sel.match(/(\s)+-(\s)+/g);
        if (sel_sp != null){ //Remove white spaces between "-" and nums
            for (i in sel_sp){
                var sp=sel_sp[i];
                sel=sel.replace(sp,"-");
            }
        }
        return sel;
    }

//-------- Text input modified signal --------

    $("#text_input_all").on("change" , ".sel_input", function(){
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



    function obtainCompounds(){
        var comp=[];
        $(".comp.active").each(function(){
            comp[comp.length]=$(this).attr("id");
        });
        return comp;
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
            var nonGPCR_chains=$(this).attr("id");
            var patt = new RegExp("protein and \\((.*)\\)");
            var nonGPCR_substr = patt.exec(nonGPCR_chains);
            if (nonGPCR_substr){
                nonGPCR_substr=nonGPCR_substr[1];
                nonGPCR_li = nonGPCR_substr.match(/[A-Z]/g);
                nonGPCR_str = nonGPCR_li.join();
                nonGPCR_chains_all.push(nonGPCR_str);
            }
        });
        return (nonGPCR_chains_all);
    }


//-------- Predefined GPCR positions --------
    $("#gpcr_sel").change(function(){
        var gpcr_id=$(this).children(":selected").val();
        var chosen_id = "#gpcr_id_"+gpcr_id;
        $(chosen_id).css("display","inline");
        $(".gpcr_prot_show_cons:not("+chosen_id+")").css("display","none");
    });

    $(".high_pd").each(function(){
        if ($(this).data("pdbpos").toString() == "None"){
            $(this).attr("disabled", true);
        }
    });
    function getSelectedPosLists(selector){
        var selPosList=[];
        $(selector).each(function(){
            range = $(this).data("pdbpos").toString();
            if (range != "None"){
                if (range.indexOf(",") > -1){
                    range_li=range.split(",");
                    for (num in range_li){
                        selPosList[selPosList.length]=" " + range_li[num];
                    }
                } else{
                    selPosList[selPosList.length]=" " + range;
                }
            }
        });

        selPosList.sort(function(x,y){
            var patt = /\d+/;
            var xp = Number(patt.exec(x));
            var yp = Number(patt.exec(y));
            return xp - yp });
        selPosList=uniq(selPosList);
        return (selPosList);
    }

    function obtainPredefPositions(){
        var high_pre={"A":[], "B":[], "C":[], "F":[]};
        high_pre["A"]=getSelectedPosLists(".high_pdA.active");
        high_pre["B"]=getSelectedPosLists(".high_pdB.active");
        high_pre["C"]=getSelectedPosLists(".high_pdC.active");
        high_pre["F"]=getSelectedPosLists(".high_pdF.active");
        return (high_pre);
    }

    $(".clear_conspos").click(function(){;
        $(".high_pd.active").each(function(){
            $(this).removeClass("active");
        });
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

    function obtainLegend(legend_el){
        var color_dict={"A":"<span style='margin-right:5px;color:#01C0E2'>Class A </span>","B":"<span style='margin-right:5px;color:#EF7D02'>Class B </span>","C":"<span style='margin-right:5px;color:#C7F802'>Class C </span>","F":"<span style='margin-right:5px;color:#F904CE'>Class F </span>"};
        var legend="";
        if (legend_el.length > 1){
            for (el in legend_el){
                var add=color_dict[legend_el[el]];
                legend+=add;
            }
            var legend_fin = "<span style='margin-top:5px'>" + legend + "</span>";
            $("#legend").html(legend_fin);
        } else {
            $("#legend").html("");
        }
    }


    
    
//-------- Residues within xA of compound --------

    var comp_lg=[];
    var comp_sh=[];
    $(".comp").each(function(){
        var comp_l=$(this).text();
        var comp_s=$(this).attr("id");
        comp_lg[comp_lg.length]=comp_l;
        comp_sh[comp_sh.length]=comp_s;
    });
    
    $(".nonGPCR").each(function(){
        var comp_l=$(this).text();
        var comp_s=$(this).attr("id");
        comp_lg[comp_lg.length]=comp_l;
        comp_sh[comp_sh.length]=comp_s;
    });

    var select="";
    for (comp_n in comp_lg){
        var option='<option value="'+comp_sh[comp_n]+'">'+comp_lg[comp_n]+'</option>';
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
                        <div class="alert_sel_wth"></div>\
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
            $(".sel_within").find(".alert_sel_wth").html("");
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
        if (isactive){
            $("#selectionDiv").trigger("click");
        }
    });


    function obtainDistSel(){
        var dist_of=[];
        //var consider_comp=[];
        $(".sel_within").find(".dist_sel").each(function(){ 
            var inp=$(this).find(".inputdist").val();
            if (inp && /^[\d.]+$/.test(inp)) {
                var comp=$(this).find(".wthComp").val();
                if (comp=="user_sel"){
                    pre_sel=$(this).find(".user_sel_input").val();
                    var rownum = $(this).attr("id");
                    var def_sel=inputText(gpcr_pdb_dict,pre_sel,rownum,"inp_wth",false);
                    if (def_sel ==""){
                        comp="none";
                        $(this).find(".user_sel_input").val("");
                    } else {
                        comp=def_sel;
                    }
                }
                if (comp != "none"){
                    var show = $(this).find(".resWthComp").val();
                    dist_of[dist_of.length]=show+"-"+inp+"-"+comp;
                    /*if (show != "protein"){
                        consider_comp[consider_comp.length]=show;
                    }*/
                }
            }

        });    
        return (dist_of);
    }

    function activate_row(row){
        row.find(".tick").html('<span class="glyphicon glyphicon-ok" style="font-size:10px;color:#7acc00;padding:0;margin:0"></span>');
        row.find(".always").attr("style","");
        row.addClass("sw_ok");
        $("#selectionDiv").trigger("click");
    }
    function inactivate_row(row){
        var active_before= row.hasClass("sw_ok");
        if (active_before){
            row.find(".tick").html("");
            row.find(".always").attr("style","margin-left:14px");
            row.removeClass("sw_ok");
            $("#selectionDiv").trigger("click");
        }
    }

    function activate_or_inactivate_row(selector){
        var row = $(selector).closest(".dist_sel");
        var inp=row.find(".inputdist").val().replace(/\s+/g, '');
        row.find(".inputdist").val(inp);
        if (inp && /^[\d.]+$/.test(inp)) {
            if (row.find(".wthComp").val()=="user_sel"){
                if (row.find(".user_sel_input").val() == ""){
                    inactivate_row(row);
                }else {
                    activate_row(row);
                }            
            } else {
                activate_row(row);
            }
        } else {
            if (row.attr("class").indexOf("sw_ok") > -1){
                inactivate_row(row);
            }
        }
    }
  
    
    $(".sel_within").on("change", ".nglCallChangeWth" ,function(){
        activate_or_inactivate_row(this);
    });    

  /*  $(".sel_within").on("change", ".inputdist" ,function(){
        activate_or_inactivate_row(this);
    });    */


    $(".sel_within").on('change', ".wthComp" ,function(){
        if ($(this).val()=="user_sel"){
            var sw_input='<input class="form-control input-sm user_sel_input nglCallChangeWth" type="text" style="width:95px;padding-left:7px">';
            $(this).siblings(".user_sel_input_p").html(sw_input);
            var row = $(this).closest(".dist_sel");
            inactivate_row(row);
        } else {
            $(this).siblings(".user_sel_input_p").html("");
            activate_or_inactivate_row(this);
        }
    });


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
    

    var i_id=1;
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
                    $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int").addClass("disabled");
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
                                $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int").removeClass("disabled");
                            }
                            $("#wait_int").remove();
                            $("#gotoInt").removeClass("disabled");
                            var success=int_data.success;
                            if (success){ 
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
                                        table_html+='<tr><td rowspan='+num_res_int+'>'+lig+'</td>';
                                        var res_int_1st=res_int[0];
                                        var res_int_1st_ok=[res_int_1st[2]+" "+res_int_1st[0].toString(),res_int_1st[1],gnumFromPosChain(res_int_1st[0].toString(), res_int_1st[1]),res_int_1st[3]+"%"];
                                        //
                                        gnum_mylist=gnumFromPosChain(res_int_1st[0].toString(), res_int_1st[1])
                                        if (gnum_mylist == "-"){
                                            gnum_mylist=res_int_1st[2]+res_int_1st[0].toString()+":"+res_int_1st[1];
                                        }
                                        mylist.push([res_int_1st[0],gnum_mylist ,res_int_1st[3] ]);
                                        //
                                        for (info in res_int_1st_ok){
                                            table_html+='<td>'+res_int_1st_ok[info]+'</td>';
                                        }
                                        table_html+='</tr>';
                                        var res_int_rest=res_int.slice(1,res_int.length);
                                        for (res_infoN in res_int_rest){
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
                                            for (infoN in res_info_ok){
                                                var info=res_info_ok[infoN];
                                                table_html+='<td>'+info+'</td>';
                                            }
                                            table_html+='</tr>';
                                        }                              
                                    }
                                    //console.log(trajFile+' - Threshold: '+thr_ok+' ('+dist_scheme_name+')');
                                    //console.log(mylist)
                                    table_html+="</tbody></table>";;
                                                                        
                                    var chart_div="int_chart_"+i_id.toString();
                                    var infoAndOpts= "<div id='"+chart_div+"'></div>\
                                        <div class='checkbox' style='font-size:12px;margin-bottom:0'>\
		                                    <label><input type='checkbox' name='view_int' class='display_int'>Display interacting residues</label>\
                                        </div>\
                                        <div class='int_settings'>\
                                            <div style='display:inline-block;margin:5px 5px 5px 0;cursor:pointer;'>\
                                                <a role='button' class='btn btn-link save_img_int_plot' href='#' target='_blank' style='color:#000000;margin-right:0;margin-left;padding-right:0;padding-left:0;margin-bottom:3px'>\
                                                    <span  title='Save plot as image' class='glyphicon glyphicon-stats'></span>\
                                                </a>\
                                            </div>\
                                            <div style='display:inline-block;margin:5px'>\
                                                <a role='button' class='btn btn-link href_save_data_int' href='/view/dwl/"+int_id+"' style='color:#000000;margin-right:0;margin-left;padding-right:0;padding-left:0;margin-bottom:3px'>\
                                                    <span  title='Save data' class='glyphicon glyphicon-file save_data_int'></span>\
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
                                        for (posN in res_int){
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
                            }else{
                                var int_error=int_data.e_msg;
                                add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>'+ int_error;
                                $("#int_alert").html(add_error);    
                            }
                            var t1= performance.now();
                            //console.log("INT : "+((t1 - t0)/1000));
                        },
                        error: function(){
                            add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>An unexpected error occurred.';
                            $("#int_alert").html(add_error); 
                            if ($.active<=1){
                                $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int").removeClass("disabled");
                            }
                            $("#wait_int").remove();
                            $("#gotoInt").removeClass("disabled");
                        }
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
    

    
    function displayCheckedIntResids(){
        var int_res_li=[];
        $(".int_tbl").each(function(){
            if ($(this).find(".display_int").is(":checked")){
                $(this).find(".int_results_tbl > tbody > tr").each(function(){
                    //If td last child has class showInP, pass; that will go in another list (when building it, take only when showInP class is present!!)
                    var td_list= $(this).children();
                    var isChecked=td_list.last().hasClass("showInP");
                    if (isChecked){
                        if(td_list.length > 4){
                            var pos = $(this).find("td:nth-child(2)").html();
                            var chain =$(this).find("td:nth-child(3)").html();
                            var freq =$(this).find("td:nth-child(5)").html();
                        } else{
                            var pos =$(this).find("td:first-child").html();
                            var chain =$(this).find("td:nth-child(2)").html();
                            var freq =$(this).find("td:nth-child(4)").html();
                        }
                        var pos_aa = /\d*$/.exec(pos)[0];
                        int_res_li.push([pos_aa, chain,freq]);
                    }
                });
            }  
        });
        int_res_li=uniq(int_res_li);
        return (int_res_li);
    }
    
    
    
    function displayIntResids(){
        var int_res_li=[];
        $(".int_tbl").each(function(){
            if ($(this).find(".display_int").is(":checked")){
                $(this).find(".int_results_tbl > tbody > tr").each(function(){
                    //If td last child has class showInP, pass; that will go in another list (when building it, take only when showInP class is present!!)
                    var td_list= $(this).children();
                    var isChecked=td_list.last().hasClass("showInP");
                    if (! isChecked){
                        if(td_list.length > 4){
                            var pos = $(this).find("td:nth-child(2)").html();
                            var chain =$(this).find("td:nth-child(3)").html();
                            var freq =$(this).find("td:nth-child(5)").html();
                        } else{
                            var pos =$(this).find("td:first-child").html();
                            var chain =$(this).find("td:nth-child(2)").html();
                            var freq =$(this).find("td:nth-child(4)").html();
                        }
                        var pos_aa = /\d*$/.exec(pos)[0];
                        int_res_li.push([pos_aa, chain,freq]);
                    }
                });
            }  
        });
        int_res_li=uniq(int_res_li);
        return (int_res_li);
    }
    
    $("#int_info").on("change" ,".display_int" , function(){
        $("#selectionDiv").trigger("click");
    });
    
    $("#int_info").on("click","td",function(){
        var isclicked = $(this).hasClass("showInP");
        if (isclicked) {
            var sibl = $(this).siblings().length;
            if (sibl == 4) {
                var hasrowspan= $(this).attr("rowspan");
                if (! hasrowspan){
                    $(this).siblings(":not([rowspan])").css("background-color","transparent").removeClass("showInP");
                    $(this).css("background-color","transparent").removeClass("showInP");
                } 
            } else {
                $(this).siblings().css("background-color","transparent").removeClass("showInP");
                $(this).css("background-color","transparent").removeClass("showInP");
            }
        } else {
            var sibl = $(this).siblings().length;
            if (sibl == 4) {
                var hasrowspan= $(this).attr("rowspan");
                if (! hasrowspan){
                    $(this).siblings(":not([rowspan])").css("background-color","#ecf6f9").addClass("showInP");
                    $(this).css("background-color","#ecf6f9").addClass("showInP");
                } 
            } else {
                $(this).siblings().css("background-color","#ecf6f9").addClass("showInP");
                $(this).css("background-color","#ecf6f9").addClass("showInP");
            }
        }
        if ($(this).closest(".int_tbl").find(".display_int").is(":checked")){
            $("#selectionDiv").trigger("click");
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
        for (dpairN in clickedDist){
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
        for (addPosN in clickedDist_pre){
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

/*    function obtainDistToComp(){
        var distToCompAtms="";
        var distToCompRes=[];
        $(".dist_btw").find(".dist_pair.d_ok").each(function(){ 
            if ($(this).find(".dist_el_sel").val() == "atoms"){
                var d_from=$(this).find(".dist_from").val();
                var d_to=$(this).find(".dist_to").val();
                distToCompAtms += d_from+"-"+d_to+"a";
            } else {
                var d_from=$(this).find(".dist_from_res").val();
                var an_from=$(this).find(".dist_atomNm_from_sel").val();
                var d_to=$(this).find(".dist_to_res").val();
                var an_to=$(this).find(".dist_atomNm_to_sel").val();
                distToCompRes.push(d_from+":"+an_from+"-"+d_to+":"+an_to);
            }
        });
        if (distToCompAtms){
            distToCompAtms.slice(0, -1);
        }
        return [distToCompAtms,distToCompRes.join()];

    }*/
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
            stride=1;
        }
        return (stride)
    }

    var chart_img={};
    var d_id=1;
    $("#gotoDistPg").click(function(){ // if fistComp="" or no traj is selected do nothing
        numComputedD = $("#dist_chart").children().length;
        $("#dist_stride_parent").removeClass("has-warning");
        if (numComputedD < 15){
            var res_ids = obtainDistToComp();
            if ($(this).attr("class").indexOf("withTrajs") > -1){
                var traj_results=obtainTrajUsedInDistComputatiion(res_ids);
                if (traj_results){        
                    var traj_p=traj_results[0];
                    var traj_id=traj_results[1];
                    
                    var stride = strideVal("#dist_stride");
                    $("#dist_chart").append("<p style='margin-top:5px;padding:5px;background-color:#e6e6ff;border-radius:3px;' id='wait_dist'><span class='glyphicon glyphicon-time'></span> Computing distances...</p>");
                    $("#gotoDistPg").addClass("disabled");
                    $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int").addClass("disabled");
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
                                    for (error_msg in small_error){
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
                                        console.log(widthval);
                                        if (widthval < 640){
                                            widthval = 640;
                                        }
                                        console.log(widthval);
                                        console.log("==========");*/
                                        var options_t = {'title':'Residue Distance ('+trajFile+strideText+')',
                                            "height":350, "width":640, "legend":{"position":"right","textStyle": {"fontSize": 10}}, 
                                            "chartArea":{"right":"120","left":"65","top":"50","bottom":"60"},hAxis: {title: "Time (ns)"},vAxis: {title: 'Distance (angstroms)'}};
                                        var options_f = {'title':'Residue Distance ('+trajFile+strideText+')',
                                            "height":350, "width":640, "legend":{"position":"right","textStyle": {"fontSize": 10}}, 
                                            "chartArea":{"right":"120","left":"65","top":"50","bottom":"60"},hAxis: {title: "Frame number"},vAxis: {title: 'Distance (angstroms)'}};
                                        newgraph_sel="dist_chart_"+d_id.toString();
                                        var plot_html;
                                        if ($.active<=1){
                                            plot_html="<div class='dist_plot' id='all_"+newgraph_sel+"' data-dist_id="+dist_id+" style='border:1px solid #F3F3F3;overflow:auto;overflow-y:hidden;-ms-overflow-y: hidden;'>\
                                                            <div class='dist_time' id='"+newgraph_sel+"t'></div>\
                                                            <div class='dist_frame' id='"+newgraph_sel+"f'></div>\
                                                            <div class='settings' style='margin:5px'>\
                                                                <div class='plot_dist_by_sel_cont' style='font-size:12px;margin-left:5px'>\
                                                                  Plot distance by\
                                                                    <span >\
                                                                        <select class='plot_dist_by_sel' name='frame_time'>\
                                                                            <option class='plot_dist_by' selected value='time'>time</option>\
                                                                            <option class='plot_dist_by' value='frame'>frame</option>\
                                                                        </select>\
                                                                    </span>\
                                                                </div>\
                                                                <div style='display:inline-block;margin:5px;cursor:pointer;'>\
                                                                    <a role='button' class='btn btn-link save_img_dist_plot' href='#' target='_blank' style='color:#000000;margin-right:0;margin-left;padding-right:0;padding-left:0;margin-bottom:3px'>\
                                                                        <span  title='Save plot as image' class='glyphicon glyphicon-stats'></span>\
                                                                    </a>\
                                                                </div>\
                                                                <div style='display:inline-block;margin:5px;'>\
                                                                    <a role='button' class='btn btn-link href_save_data_dist_plot' href='/view/dwl/"+dist_id+"' style='color:#000000;margin-right:0;margin-left;padding-right:0;padding-left:0;margin-bottom:3px'>\
                                                                        <span  title='Save data' class='glyphicon glyphicon-file save_data_dist_plot'></span>\
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
                                                                  Plot distance by\
                                                                    <span >\
                                                                        <select  name='frame_time' class='plot_dist_by_sel'>\
                                                                            <option class='plot_dist_by' selected value='time'>time</option>\
                                                                            <option class='plot_dist_by' value='frame'>frame</option>\
                                                                        </select>\
                                                                    </span>\
                                                                </div>\
                                                            <div class='checkbox' style='font-size:12px;'>\
		                                                        <label><input type='checkbox' name='view_this_dist' checked class='display_this_dist' data-this_dist="+dist_pair_new+" >Display distance</label>\
                                                            </div>\
                                                            <div style='margin:5px'>\
                                                                <div style='display:inline-block;margin:5px;cursor:pointer;'>\
                                                                    <a role='button' class='btn btn-link save_img_dist_plot' href='#' target='_blank' style='color:#000000;margin-right:0;margin-left;padding-right:0;padding-left:0;margin-bottom:3px'>\
                                                                        <span  title='Save plot as image' class='glyphicon glyphicon-stats'></span>\
                                                                    </a>\
                                                                </div>\
                                                                <div style='display:inline-block;margin:5px;'>\
                                                                    <a role='button' class='btn btn-link href_save_data_dist_plot disabled' href='/view/dwl/"+dist_id+"' style='color:#000000;margin-right:0;margin-left;padding-right:0;padding-left:0;margin-bottom:3px'>\
                                                                        <span  title='Save data' class='glyphicon glyphicon-file save_data_dist_plot'></span>\
                                                                    </a>\
                                                                </div>\
                                                                <div style='display:inline-block;margin:5px;color:#DC143C;cursor:pointer;vertical-align:-2px'>\
                                                                    <span title='Delete' class='glyphicon glyphicon-trash delete_dist_plot' data-dist_id='"+dist_id+"'></span>\
                                                                </div>\
                                                                <div class='checkbox' style='font-size:12px;display:inline-block'>\
		                                                            <label><input type='checkbox' name='view_this_dist' class='display_this_dist' data-this_dist="+dist_pair_new+" data-traj_id="+traj_id+">Display distance</label>\
                                                                </div>\
                                                            </div>\
                                                        </div>";                            
                                        } 
                                        $("#dist_chart").append(plot_html);
                                        var chart_cont_li =[[newgraph_sel+"t",data_t,options_t],[newgraph_sel+"f",data_f,options_f]];
                                        for (chartN in chart_cont_li){
                                            var chart_cont=chart_cont_li[chartN][0];
                                            var data=chart_cont_li[chartN][1];
                                            var options=chart_cont_li[chartN][2];
                                            var chart_div = document.getElementById(chart_cont);
                                            var chart = new google.visualization.LineChart(chart_div);                                
                                            google.visualization.events.addListener(chart, 'ready', function () {
                                                var img_source =  chart.getImageURI(); 
                                                $("#"+chart_cont).attr("data-url",img_source);
                                            });                                
                                            chart.draw(data, options);                                    
                                        }
                                        $("#"+newgraph_sel+"f").css("display","none");  
                                        var img_source_t=$("#"+newgraph_sel+"t").data("url");
                                        $("#"+newgraph_sel+"t").siblings(".settings").find(".save_img_dist_plot").attr("href",img_source_t);
                                        
                                        if (small_error){
    //////////////////
                                            var errors_html="";
                                            for (error_msg in small_error){
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
                                $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int").removeClass("disabled");
                            }
                            var t1=performance.now();
                            //console.log("DIST: "+((t1 - t0)/1000));
                        },
                        error: function() {
                            $("#gotoDistPg").removeClass("disabled");
                            $("#wait_dist").remove();
                            if ($.active<=1){
                                $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int").removeClass("disabled");
                            }
                            add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>An unexpected error occurred.';
                            $("#dist_alert").html(add_error);                
                        }
                    });
                    $("#dist_alert").html("");
                } else {
                    add_error_d='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>Some fields are empty or contain errors.';
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
                        }
                    });
                } else {
                    add_error_d='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>Some fields are empty or contain errors.';
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

    function selectFromSeq(){
        var click_n=1;
        var seq_pos_1;
        var seq_pos_fin;
        var pos_li=[];
        var firstsel=true;
        $(".seq_sel").click(function(){    
            if (click_n==1){
                var range=$(this).attr("class"); 
                if(range.indexOf("-") == -1){     //Start a new selection
                    $(this).css("background-color","#337ab7"); 
                    seq_pos_1 = $(this).attr("id");
                    click_n=2;
                } else {      // Remove an old selection
                    var selRange= range.match(/(\d)+/g);
                    i=Number(selRange[0]);
                    end=Number(selRange[1]);
                    while (i <= end) {
                        var mid_id="#" + String(i);
                        $(mid_id).css("background-color","#f2f2f2");
                        $(mid_id).attr("class", "seq_sel");
                        i++;
                    }
                    if ($(".seq_sel.sel").length== 0){
                        $("#addToSel").css("display","none");
                        firstsel=true;
                    }
                }
            } else  {
                // Finish a selection
                click_n=1;
                seq_pos_fin = Number($(this).attr("id"));
                var i = Number(seq_pos_1);
                while (i <= seq_pos_fin){
                    var mid_id="#" + String(i);
                    $(mid_id).css("background-color","#34b734");
                    $(mid_id).children().css("background-color","");
                    $(mid_id).attr("class", "seq_sel sel " + seq_pos_1+"-"+seq_pos_fin); 
                    i++;
                }
                if (firstsel){
                    $("#addToSel").css("display","inline");
                    firstsel=false;
                }

            }
        });
   
        $(".seq_sel").hover(function(){
            if (click_n==2) {
                var seq_pos_2 = Number($(this).attr("id"));
                var i = Number(seq_pos_1);
                while (i <= seq_pos_2){
                    var mid_id="#" + String(i);
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
                var seq_pos_2 = Number($(this).attr("id"));
                var i = Number(seq_pos_1);
                while (i <= seq_pos_2){
                    var mid_id="#" + String(i);
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
    selectFromSeq();

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
            for (chain in considered_chains){
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
            for (p in sel_ranges) {
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
            for (p in sel_ranges) {
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


    function obtainSelectedAtSeq(){
        var sel_ranges=[];
        $(".seq_sel.sel").each(function(){
            var class_str=$(this).attr("class");
            var id_range= class_str.match(/(\d)+/g);
//            var sel_range=clickSelRange($(this).attr("class"));
            sel_ranges[sel_ranges.length]=id_range[0]+"-"+id_range[1];
        });
        return(sel_ranges);
    }


    $("#addToSel").click(function(){ 
        $("#seq_input_all").css("display","inline");
        $("#seq_input_all").find(".si_add_btn:last").css("visibility","visible");
        sel_ranges=obtainSelectedAtSeq();
        if (sel_ranges.length > 0){
            sel_ranges_ok=joinContiguousRanges(sel_ranges);
            var pos_str="";
            p=0;
            while (p < (sel_ranges_ok.length -1)) {
                pos_str += sel_ranges_ok[p] + " or ";
                p ++;
            }
            pos_str += sel_ranges_ok[sel_ranges_ok.length-1];
            var sel_input_cont=$(".seq_input_row:last-child").find(".seq_input");
            var act_val=sel_input_cont.val();
            var or="";
            if (act_val){
                or = " or ";
            }
            var fin_val = act_val + or + "protein and ("+ pos_str +")";
            sel_input_cont.val(fin_val);
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
    
    var r_id=1;

    $("#ComputeHbonds").click(function(){
        $("#bonds_alert").html("");
        $("#hbonds_sel_frames_error").html("");
        $('#ShowAllHbInter').hide();
        $('#ShowAllHbIntra').hide();
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
            if (frameFrom && frameTo) {
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
            $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int").addClass("disabled"); 
            $("#bondsresult_par").before("<p style='margin-top:5px;padding:5px;background-color:#e6e6ff;border-radius:3px;clear:left' id='wait_hbonds'><span class='glyphicon glyphicon-time'></span> Computing Hbonds...</p>");   
            $.ajax({
                    type: "POST",
                    data: { "frames[]": [frameFrom,frameTo,cutoff,rmsdTraj,struc,dyn_id,backbone,neigh] },
                    url:"/view/hbonds/", 
                    dataType: "json",
                    success: function(data) {
                        $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int").removeClass("disabled"); 
                        $("#wait_hbonds").remove();
                        hbonds=data.hbonds;
                        hbonds_np=data.hbonds_notprotein;
                        var regex = /\d+/g;
                        var table='<h4>Protein-Protein Hydrogen Bonds</h4><br><center><table id="intramol" class="table table-condesed" style="width:90%;"><thead><tr><th>Donor<th>Acceptors (Frecuency)<tbody>';
                        //gnumFromPosChain(pos, chain)
                        for (var property in hbonds) {
                            if (hbonds.hasOwnProperty(property)) {
                                var string =property;
                                var string2 =hbonds[property][0][0];
                                var donor = string.match(regex)[0];  // creates array from matches
                                var acceptor = string2.match(regex)[0];  // creates array from matches
                                donorballes=gnumFromPosChain(String(donor),hbonds[property][0][4])
                                acceptorballes=gnumFromPosChain(String(acceptor),hbonds[property][0][5])

                                table=table+'<tr> <td rowspan='+ hbonds[property].length.toString() + '>'+ property+' | '+donorballes+'<td> '+hbonds[property][0][0]+' | '+acceptorballes+' ('+hbonds[property][0][1]+'%) <button class="showhb"  data-resids='+ donor + '$%$' + acceptor +' data-atomindexes='+hbonds[property][0][2]+'$%$'+hbonds[property][0][3]+'>Show Hbond</button>' ;
                                for (index = 1; index < hbonds[property].length; ++index) {
                                    var string2 =hbonds[property][index][0];
                                    var acceptor = string2.match(regex)[0];  // creates array from matches
                                    acceptorballes=gnumFromPosChain(String(acceptor),hbonds[property][index][5])
                                    table=table+'<tr><td>'+hbonds[property][index][0]+' | '+acceptorballes+' ('+hbonds[property][index][1]+'%) <button class="showhb" data-resids='+ donor + '$%$' + acceptor +' data-atomindexes='+hbonds[property][index][2]+'$%$'+hbonds[property][index][3]+'>Show Hbond</button>';
                                }
                            }
                        }
                        table=table+'</table></center><center>';
                        $('#ShowAllHbIntra').show();
                        $('#hbonds').html(table);


                        var tablenp='<h4>Other Hydrogen Bonds</h4><br><center><table id="intermol"  class="table table-condesed" style="width:90%;"><thead><tr><th>Residue1<th>Residue2 (Frecuency)<tbody>';
                        for (var property in hbonds_np) {
                            if (hbonds_np.hasOwnProperty(property)) {
                                var string =property;
                                var string2 =hbonds_np[property][0][0];
                                var donor = string.match(regex)[0];  // creates array from matches
                                var acceptor = string2.match(regex)[0];  // creates array from matches
                                donorballes=gnumFromPosChain(String(donor),hbonds_np[property][0][4])
                                acceptorballes=gnumFromPosChain(String(acceptor),hbonds_np[property][0][5])

                                tablenp=tablenp+'<tr> <td rowspan='+ hbonds_np[property].length.toString() + '>'+ property+' | '+donorballes+'<td> '+hbonds_np[property][0][0]+' |'+acceptorballes+' ('+hbonds_np[property][0][1]+'%) <button class="showhb_inter"  data-resids='+ donor + '$%$' + acceptor +' data-atomindexes='+hbonds_np[property][0][2]+'$%$'+hbonds_np[property][0][3]+'>Show Hbond</button>';
                                for (index = 1; index < hbonds_np[property].length; ++index) {
                                    var string2 =hbonds_np[property][index][0];
                                    var acceptor = string2.match(regex)[0];  // creates array from matches           
                                    acceptorballes=gnumFromPosChain(String(acceptor),hbonds_np[property][index][5])
                                    tablenp=tablenp+'<tr><td>'+hbonds_np[property][index][0]+' | '+acceptorballes+' ('+hbonds_np[property][index][1]+'%) <button class="showhb_inter"  data-resids='+ donor + '$%$' + acceptor +' data-atomindexes='+hbonds_np[property][index][2]+'$%$'+hbonds_np[property][index][3]+'>Show Hbond</button>';
                                }
                            }
                        }
                        tablenp=tablenp+'</table></center><center>';
                        $('#ShowAllHbInter').show();
                        $("#bondsresult_par").attr("style", "margin-top: 10px; margin-bottom: 15px; border:1px solid #F3F3F3;display:block;padding-top:15px");
                        $('#hbondsnp').html(tablenp);
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                        $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int").removeClass("disabled"); 
                        $("#wait_hbonds").remove();
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
            if (frameFrom && frameTo) {
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
            var msn="Some fields are empty or contain errors";
            showBigError(msn, "#salt_alert");
        }else{
            $('#ShowAllSb').hide();
            $("#saltresult_par").before("<p style='margin-top:5px;padding:5px;background-color:#e6e6ff;border-radius:3px;clear:left' id='wait_saltb'><span class='glyphicon glyphicon-time'></span> Computing salt bridges...</p>"); 
            $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int").addClass("disabled"); 
            $.ajax({
                    type: "POST",
                    data: { "frames[]": [frameFrom,frameTo,cutoff,rmsdTraj,struc,dyn_id]},
                    url:"/view/saltbridges/", 
                    dataType: "json",
                    success: function(data) {
                        $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int").removeClass("disabled"); 
                        $("#wait_saltb").remove();
                        var regex = /\d+/g;
                        salty=data.salt_bridges;
                        var salt='<center><table class="table table-condesed" style="width:90%;"><thead><tr><th>Residue1<th>Residue2 (Frecuency%)<tbody>';
                        for (var property in salty) {
                            if (salty.hasOwnProperty(property)) {
                                var string =property;
                                var string2 =salty[property][0][0];
                                var donor = string.match(regex)[0];  // creates array from matches
                                var acceptor = string2.match(regex)[0];  // creates array from matches
                                salt=salt+'<tr> <td rowspan='+ salty[property].length.toString() + '>'+ property+'<td> '+salty[property][0][0]+' ('+salty[property][0][1]+'%) <button class="showsb"  data-resids='+ donor + '$%$' + acceptor +' data-atomindexes='+salty[property][0][2]+'$%$'+salty[property][0][3]+'>Show Salt Bridge</button>';
                                for (index = 1; index < salty[property].length; ++index) {
                                    string2=salty[property][index][0]
                                    acceptor = string2.match(regex)[0];
                                    salt=salt+'<tr><td>'+salty[property][index][0]+' ('+salty[property][index][1]+'%) <button class="showsb" data-resids='+ donor + '$%$' + acceptor +' data-atomindexes='+salty[property][index][2]+'$%$'+salty[property][index][3]+'>Show Salt Bridge</button>';
                                }
                            }
                        }
                        salt=salt+'</table></center>';
                        $('#ShowAllSb').show();
                        $('#saltbridges').html(salt);
                        $("#saltresult_par").attr("style","border:1px solid #F3F3F3;padding-top:5px;display:block;margin-top:10px");
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                        $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int").removeClass("disabled"); 
                        $("#wait_saltb").remove();
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
            }); 
        }
    });
    
//-------- SASA computation --------
    
    $("#ComputeGrid").click(function(){
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
        $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int").addClass("disabled"); 
        $.ajax({
                type: "POST",
                data: { "frames[]": [frameFrom,frameTo,cutoff,rmsdTraj,struc,dyn_id,sasa_sel]},
                url:"/view/grid/", 
                dataType: "json",
                success: function(data) {
                    $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int").removeClass("disabled"); 
                    atomshb=[];
                    all_resids=[];
                    atomshb_inter=[];
                    atomssb=[];
                    all_resids_sb=[];
                    all_resids_sasa=data.selected_residues
                    results=drawBasic(data.sasa,'Time (ns)','SASA (nm^2)');
                    data=results[0];
                    options=results[1];
                    /*

                                            var chart_div = document.getElementById(chart_cont);
                                            var chart = new google.visualization.LineChart(chart_div);                                
                                            google.visualization.events.addListener(chart, 'ready', function () {
                                                var img_source =  chart.getImageURI(); 
                                                $("#"+chart_cont).attr("data-url",img_source);
                                            });                                
                                            chart.draw(data, options);                                    
                                        }
                                        $("#"+newgraph_sel+"f").css("display","none");  
                                        var img_source_t=$("#"+newgraph_sel+"t").data("url");
                                        $("#"+newgraph_sel+"t").siblings(".settings").find(".save_img_dist_plot").attr("href",img_source_t);



                    */
                    var chart_sasa = new google.visualization.LineChart(document.getElementById('sasa_chart'));    
                    chart_sasa.draw(data, options);
                    $("#selectionDiv").trigger("click");
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int").removeClass("disabled"); 
                    if (XMLHttpRequest.readyState == 4) {
                        var responsetext = XMLHttpRequest.responseText;

                        alert(textStatus.substr(0,1).toUpperCase()+textStatus.substr(1)+":\nStatus: " + XMLHttpRequest.textStatus+". "+errorThrown+".\n"+responsetext);
                    }
                    else if (XMLHttpRequest.readyState == 0) {
                        alert("Connection error. Please, try later and check that your file is not larger than 50 MB.");
                    }
                    else {
                        alert("Unknown error");
                    }
                },
        }); 
    });


    $(document).on('click', '.showhb', function(){
        all_resids_sasa=[];
        atomssb=[];
        atomshb_inter=[];
        atomshb=$(this).data('atomindexes').split('$%$');
        atomshb=[[Number(atomshb[0]),Number(atomshb[1])]];
        resids=$(this).data('resids').split('$%$');
        all_resids=[Number(resids[0]),Number(resids[1])];
        $("#selectionDiv").trigger("click");
    });

    $(document).on('click', '.showhb_inter', function(){
        all_resids_sasa=[];
        atomssb=[];
        atomshb=[];
        atomshb_inter=$(this).data('atomindexes').split('$%$');
        atomshb_inter=[[Number(atomshb_inter[0]),Number(atomshb_inter[1])]];
        resids=$(this).data('resids').split('$%$');
        all_resids=[Number(resids[0]),Number(resids[1])];
        $("#selectionDiv").trigger("click");
    });

    $(document).on('click', '.showsb', function(){
        all_resids_sasa=[];
        atomshb=[];
        atomshb_inter=[];
        atomssb=$(this).data('atomindexes').split('$%$');
        atomssb=[[Number(atomssb[0]),Number(atomssb[1])]];
        resids=$(this).data('resids').split('$%$');
        all_resids_sb=[Number(resids[0]),Number(resids[1])];
        $("#selectionDiv").trigger("click");
    });

    $('#ShowAllHbIntra').click(function(){
            all_resids_sasa=[];
            atomssb=[];
            atomshb=[];
            all_resids=[];
            atomshb_inter=[];
        $('#intramol tr button').each(function(index){
            resids=$(this).data('resids').split('$%$');
            all_resids.push(Number(resids[0]));
            all_resids.push(Number(resids[1]));
            atoms=$(this).data('atomindexes').split('$%$');
            atoms=[Number(atoms[0]),Number(atoms[1])];
            atomshb.push(atoms);
        });
        $("#selectionDiv").trigger("click");
    });

    $('#ShowAllHbInter').click(function(){
            all_resids_sasa=[];
            atomssb=[];
            atomshb=[];
            all_resids=[];
            atomshb_inter=[];
        $('#intermol tr button').each(function(index){
            resids=$(this).data('resids').split('$%$');
            all_resids.push(Number(resids[0]));
            all_resids.push(Number(resids[1]));
            atoms=$(this).data('atomindexes').split('$%$');
            atoms=[Number(atoms[0]),Number(atoms[1])];
            atomshb_inter.push(atoms);
        });
        $("#selectionDiv").trigger("click");
    });


    $('#ShowAllSb').click(function(){
            all_resids_sasa=[];
            atomshb=[];
            all_resids=[];
            atomshb_inter=[];
            atomssb=[];
            all_resids_sb=[];
        $('#saltresult tr button').each(function(index){
            resids=$(this).data('resids').split('$%$');
            all_resids_sb.push(Number(resids[0]));
            all_resids_sb.push(Number(resids[1]));
            atoms=$(this).data('atomindexes').split('$%$');
            atoms=[Number(atoms[0]),Number(atoms[1])];
            atomssb.push(atoms);
        });
        $("#selectionDiv").trigger("click");
    });

//-------- RMSD computation --------

    $("#gotoRMSDPg").click(function(){
        $("#rmsd_sel_frames_error").html("");
        $("#rmsd_ref_frames_error").html("");
        $("#rmsd_stride_parent").removeClass("has-warning");
        numComputedR = $("#rmsd_chart").children().length;
        if (numComputedR < 15){
            rmsdTraj=$("#rmsd_traj").val();
            rmsdFrames=$("#rmsd_sel_frames_id input[name=rmsd_sel_frames]:checked").val();
            if (rmsdFrames=="rmsd_frames_mine"){
                frameFrom=$("#rmsd_frame_1").val();
                frameTo=$("#rmsd_frame_2").val();
                if (frameFrom && frameTo) {
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
                $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int").addClass("disabled"); 
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
                                    "chartArea":{"right":"10","left":"60","top":"50","bottom":"60"},hAxis: {title: 'Time (ns)'},vAxis: {title: 'RMSD'}};
                                var options_f = {'title':'RMSD (traj:'+trajFile+', ref: fr '+rmsdRefFr+' of traj '+refTrajFile + strideText+', sel: '+rmsdSelOk+')',
                                    "height":350, "width":640, "legend":{"position":"none"}, 
                                    "chartArea":{"right":"10","left":"60","top":"50","bottom":"60"},hAxis: {title: 'Frame number'},vAxis: {title: 'RMSD'}};
                                newRMSDgraph_sel="rmsd_chart_"+r_id.toString();
                                var RMSDplot_html;
                                if ($.active<=1){
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
                                                            <a role='button' class='btn btn-link save_img_rmsd_plot' href='#' target='_blank' style='color:#000000;margin-right:0;margin-left;padding-right:0;padding-left:0;margin-bottom:3px'>\
                                                                <span  title='Save plot as image' class='glyphicon glyphicon-stats'></span>\
                                                            </a>\
                                                        </div>\
                                                        <div style='display:inline-block;margin:5px;'>\
                                                            <a role='button' class='btn btn-link href_save_data_rmsd_plot' href='/view/dwl/"+rmsd_id+"' style='color:#000000;margin-right:0;margin-left;padding-right:0;padding-left:0;margin-bottom:3px'>\
                                                                <span  title='Save data' class='glyphicon glyphicon-file save_data_rmsd_plot'></span>\
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
                                                          Plot RMSD by\
                                                            <span >\
                                                                <select class='plot_rmsd_by_sel' name='frame_time'>\
                                                                    <option class='plot_rmsd_by' selected value='time'>time</option>\
                                                                    <option class='plot_rmsd_by' value='frame'>frame</option>\
                                                                </select>\
                                                            </span>\
                                                        </div>\
                                                        <div style='display:inline-block;margin:5px;cursor:pointer;'>\
                                                            <a role='button' class='btn btn-link save_img_rmsd_plot' href='#' target='_blank' style='color:#000000;margin-right:0;margin-left;padding-right:0;padding-left:0;margin-bottom:3px'>\
                                                                <span  title='Save plot as image' class='glyphicon glyphicon-stats'></span>\
                                                            </a>\
                                                        </div>\
                                                        <div style='display:inline-block;margin:5px;'>\
                                                            <a role='button' class='btn btn-link href_save_data_rmsd_plot disabled' href='/view/dwl/"+rmsd_id+"' style='color:#000000;margin-right:0;margin-left;padding-right:0;padding-left:0;margin-bottom:3px'>\
                                                                <span  title='Save data' class='glyphicon glyphicon-file save_data_rmsd_plot'></span>\
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
                                for (chartN in chart_cont_li){
                                    var chart_cont=chart_cont_li[chartN][0];
                                    var data=chart_cont_li[chartN][1];
                                    var options=chart_cont_li[chartN][2];
                                    var rmsd_chart_div = document.getElementById(chart_cont);
                                    var chart = new google.visualization.LineChart(rmsd_chart_div);    
                                    google.visualization.events.addListener(chart, 'ready', function () {
                                        var rmsd_img_source =  chart.getImageURI(); 
                                        $("#"+chart_cont).attr("data-url",rmsd_img_source);
                                    });
                                    chart.draw(data, options);   
                                }
                                $("#"+newRMSDgraph_sel+"f").css("display","none");  
                                var rmsd_img_source_t=$("#"+newRMSDgraph_sel+"t").data("url");
                                $("#"+newRMSDgraph_sel+"t").siblings(".rmsd_settings").find(".save_img_rmsd_plot").attr("href",rmsd_img_source_t);
                                r_id+=1;
                                
                                
                                if (small_errors.length >= 1){
                                    errors_html="";
                                    for (error_msg in small_errors){
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
                            $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int").removeClass("disabled");
                        }
                    var t1= performance.now();
                    //console.log("RMSD : "+((t1 - t0)/1000));
                    },
                    error: function() {
                        $("#gotoRMSDPg").removeClass("disabled");
                        $("#wait_rmsd").remove();
                        add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>An unexpected error occurred.';
                        $("#rmsd_alert").html(add_error);  
                        if ($.active<=1){
                            $(".href_save_data_dist_plot,.href_save_data_rmsd_plot, .href_save_data_int").removeClass("disabled");
                        }
                    }
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
//-------- Buttons --------

    click_unclick(".high_pdA");
    click_unclick(".high_pdB");
    click_unclick(".high_pdC");
    click_unclick(".high_pdF");
    click_unclick(".rep_elements");
    click_unclick("#col_btn");
    click_unclick("#receptor");
    $("#btn_all").click(function(){
        $(".rep_elements").addClass("active");
        $("#receptor").addClass("active");
        $("#selectionDiv").trigger("click");
    });
    
    function removeCompBtns(){
        $(".rep_elements").removeClass("active");
        $("#receptor").removeClass("active");
    }
    
    $("#btn_clear").click(function(){
        removeCompBtns();
        $("#selectionDiv").trigger("click");
    });

    
//-------- Pass data to MDsrv --------

    function gpcr_selection(){
        if (chains_str == ""){
            receptorsel="protein";
        } else {
            var chains_s=/:(.*)$/.exec(chains_str)[1];
            var chains_l = chains_s.match(/\w+/g);
            receptorsel="protein and (";
            for (cN in chains_l){
                receptorsel+=":"+chains_l[cN]+ " , ";
            }
            receptorsel=receptorsel.slice(0,-3) +")";
        }
        return (receptorsel);
    }

    function gpcr_selection_active(){
        if ($("#receptor").hasClass("active")){
            var receptorsel=gpcr_selection();
        } else {
            var receptorsel="";
        }
        return (receptorsel);
    }

    var atomshb=[];
    var grid=[];
    var grid_shape=[];
    var grid_atoms=[];
    var all_resids=[];
    var all_resids_sb=[];
    var atomshb_inter=[];
    var atomssb=[];
    var all_resids_sasa=[];
    function obtainURLinfo(gpcr_pdb_dict){
        var layers_li =obtainTextInput();
        var dist_groups_li=displayCheckedDists();
        var int_res_li=displayIntResids();
        var int_res_li_ch = displayCheckedIntResids();
        cp = obtainCompounds();
        nonGPCR=obtainNonGPCRchains(".nonGPCR.active");// list of strings, each string contains the chains of a non-GPCR prot selected.
        if (gpcr_pdb_dict=="no"){
            high_pre = [];
        } else {
            high_pre = obtainPredefPositions();
        }
        var traj = $("#selectedTraj").data("tpath");
        var receptorsel=gpcr_selection_active();
        bs_info=obtainBS();
        return ({"cp":cp ,
                "layers_li":layers_li,
                "dist_groups_li":dist_groups_li,
                "int_res_li":int_res_li,
                "int_res_li_ch":int_res_li_ch,
                "nonGPCR":nonGPCR,
                "high_pre":high_pre,
                "traj":traj,
                "receptorsel":receptorsel,
                "bs_info" :bs_info,
                "hbondarray":atomshb,
                "sbondarray":atomssb,
                "allresidshb":all_resids,
                "allresidssb":all_resids_sb,
                "hb_inter":atomshb_inter,
                "all_resids_sasa":all_resids_sasa,
        });
    }
    

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
        var dist_of=obtainDistSel();  
        window.dist_of=dist_of;
        obtainLegend(legend_el);
    }    
    window.passInfoToIframe=passInfoToIframe;
    
    var passinfoToPlayTraj= function(){
        var bs_info=obtainBS();
        window.bs_info=bs_info;
        var dist_of=obtainDistSel();  
        window.dist_of=dist_of;
    }
    window.passinfoToPlayTraj=passinfoToPlayTraj;
    
    function join_lil(myLil){
         var myLi=[];
         for (e in myLil){
             var res_s = myLil[e].join("-");
             myLi[myLi.length]=res_s.slice(0, -1);
         }
         var my_str = myLi.join();
         return (my_str);
    }
    
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
         var all_resids=results["allresidshb"];
         var all_resids_sb=results["allresidssb"];
         var atomshb_inter=results[ "hb_inter"];

         int_res_s=join_lil(int_res_lil);
         int_res_s_ch=join_lil(int_res_lil_ch);
         var pd = "n";
         for (key in high_pre){
             if (high_pre[key].length > 0){
                 pd = "y";
                 break;
             }
        }
        var layers_li=[];
        for (layN in layers_lil){
            layer_l =layers_lil[layN];
            layer_l=layer_l.join("-,,-");
            layers_li.push(layer_l);
        }
        layers_li=layers_li.join("-;;-");
        var dist_of=obtainDistSel(); 
        var url_mdsrv=mdsrv_url+"/html/mdsrv_emb.html?struc=" + encode(struc) + "&pd=" + pd;
        var add_url_var ={"traj":encode(traj) , 
                            "ly":encode(layers_li) , 
                            "cp":encode(cp),
                            "la":encode(high_pre["A"]),
                            "lb":encode(high_pre["B"]),
                            "lc":encode(high_pre["C"]),
                            "lf":encode(high_pre["F"]), 
                            "wth":encode(dist_of) , 
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
        $(".sel_input, .dist_from, .dist_to, #rmsd_frame_1, #rmsd_frame_2, #rmsd_ref_frame, #int_thr, .seq_input, .inp_stride, .dis_res_bth").val("");
        $(".sel_within").find(".inputdist").val("");
        $(".sel_within").find(".user_sel_input").val("");
        $(".sel_within").find(".dist_sel:not(:first-child)").each(function(){
            $(this).remove();
            $(".sel_within").find(".add_btn:last").css("visibility","visible");            
        });
        var last_selWth_row=$(".sel_within").find(".dist_sel");
        inactivate_row(last_selWth_row);
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
        $("#text_input_all").find(".text_input:not(:first-child)").each(function(){
            $(this).remove();            
        });
        $("#text_input_all").find(".ti_add_btn:last").css("visibility","visible");
        $("#text_input_all").find(".input_dd_color").val("");
        $("#seq_input_all").find(".seq_input_row:not(:first-child)").each(function(){
            $(this).remove();            
        });
        $("#seq_input_all").css("display","none");
        $("#seq_input_all").find(".si_add_btn").css("visibility","hidden");
        $("#seq_input_all").find(".seq_input").val("");
        $("#seq_input_all").find(".input_dd_color").val("");
        $("#addToSel").css("display","none");
    }); 
});


