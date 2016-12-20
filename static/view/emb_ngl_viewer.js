$(document).ready(function(){
    $(".sel_input, #inputdist, #dist_from, #dist_to").val("")
    $("#show_within, #show_dist").empty();
    // $("#rad_high").attr("checked",false).checkboxradio("refresh");
    // $("#rad_sel").attr("checked",true).checkboxradio("refresh");// CHECK IF WORKS, AND IF BOTH SEL AND HIGH ARE CHECKED OR ONLY SEL
  
/// AJAX

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
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');


////////

  
    function encode (sth) {return encodeURIComponent(sth).replace(/%20/g,'+');}

    function obtainInputedGPCRnum(pre_sel) {
        var gpcr = "((\\d{1,2}\\.\\d{1,2}(x\\d{2,3})?)|(\\d{1,2}x\\d{2,3}))";
        var gpcr_range = gpcr + "\\s*\\-\\s*"+gpcr;
        var re = new RegExp(gpcr_range,"g");
        var res = pre_sel.match(re); 
        return(res);
    }

    function inputText(gpcr_pdb_dict){
        var pre_sel = $(".sel_input").val();
        var gpcr_ranges=obtainInputedGPCRnum(pre_sel);
        if (gpcr_ranges == null){
            sel = pre_sel ;
        } else if (gpcr_pdb_dict=="no"){
            sel = ""
            to_add='<a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>GPCR generic residue numbering is not supported for this stricture.'
            $("#alert").attr("class","alert alert-danger row").append(to_add);
        } else {
            for (i in gpcr_ranges) {
                var gpcr_pair_str = gpcr_ranges[i];
                var gpcr_pair=gpcr_pair_str.split(new RegExp('\\s*-\\s*','g'));
                var chain_pair=[]
                var res_pair=[]
                for (n in gpcr_pair){
                    var gpcr_n=gpcr_pair[n];  
                    if(gpcr_pdb_dict[gpcr_n] != undefined) {
                        var res_chain=gpcr_pdb_dict[gpcr_n];  
                    } else if (bw_dict[gpcr_n] != undefined) {
                        var res_chain=bw_dict[gpcr_n];  
                    } else if (gpcrdb_dict[gpcr_n] != undefined){
                        var res_chain=gpcrdb_dict[gpcr_n];                   
                    } else {
                        res_chain=undefined;
                        chain_pair=false
                        to_add='<div class="alert alert-danger row" style = "margin-bottom:10px" ><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>'+gpcr_pair_str+' not found.</div>'
                        $("#alert").append(to_add);
                        break
                    }
                    res_pair[res_pair.length]=res_chain[0];
                    chain_pair[chain_pair.length]=res_chain[1];
                }
                if (chain_pair){
                    if (chains_str == "") {
                        pos_range=" "+res_pair[0] + "-" +res_pair[1]
                    } else if (chain_pair[0]==chain_pair[1]){
                        pos_range=" "+res_pair[0] + "-" +res_pair[1]+":"+chain_pair[0];
                    } else {
                        pos_range=" ("+res_pair[0] + "-:"+chain_pair[0] + " or -"+res_pair[1]+":" +chain_pair[1]+")";
                    }
                    pre_sel = pre_sel.replace(gpcr_pair_str, pos_range);
                } else {
                    pre_sel="";
                }
            sel=pre_sel;
            }
        }
        var sel_sp = sel.match(/(\s)+-(\s)+/g);
        if (sel_sp != null){ //Remove white spaces between "-" and nums
            for (i in sel_sp){
                var sp=sel_sp[i];
                sel=sel.replace(sp,"-");
            }
        }
        // alert(sel);
        sel_enc = encode(sel);
        return sel_enc
    };

    function clickRep (id, newRep, clicked) {
        if ( clicked == 1 ) {
            var index = $.inArray(newRep,rep);
            if (index == -1) {
                rep[rep.length]=newRep;
            }
            url = url_orig + ("&sel=" + sel_enc + "&rep=" + encode(rep));
            $(id).addClass("active");
            return  2;
        } else {
            var index = $.inArray(newRep,rep);
            if (index > -1) {
                rep.splice(index, 1);
            }
            url = url_orig + ("&sel=" + sel_enc + "&rep=" + encode(rep));
            $(id).removeClass("active");
            return  1;
        }
    }

    function click_unclick(class_name){
        $(class_name).click(function(){
            pos_class=$(this).attr("class");
            if(pos_class.indexOf("active") > -1){
                $(this).removeClass("active");
            } else {
                $(this).addClass("active");
            }
        });
    }

    function click_unclick_specialRec(class_name){
        $(class_name).click(function(){
            pos_class=$(this).attr("class");
            if(pos_class.indexOf("active") > -1){
                $(this).removeClass("active");
                seeReceptor="n";
            } else {
                $(this).addClass("active");
                seeReceptor="y";
            }
        });
        return seeReceptor 
    }


    function obtainCompounds(){
        var comp=[];
        $(".rep_elements.active").each(function(){
            comp[comp.length]=$(this).attr("id");
        });
        return comp;
    }


    function uniq(a) {
        var seen = {};
        return a.filter(function(item) {
            return seen.hasOwnProperty(item) ? false : (seen[item] = true);
        });
    }

///////////////
    function getSelectedPosLists(selector){
        var selPosList=[];
        $(selector).each(function(){
            range = $(this).attr("id");
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
        })

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
        return (high_pre)
    }

    $("#clear_conspos").click(function(){;
        $(".high_pd.active").each(function(){
            $(this).removeClass("active");
        });
    });    


    function obtainDicts(gpcr_pdb_dict){
        var bw_dict={};
        var gpcrdb_dict={};
        for (gen_num in gpcr_pdb_dict) {
            split=gen_num.split(new RegExp('[\.x]','g'));
            bw = split[0]+"."+ split[1];
            db = split[0]+"x"+ split[2];
            bw_dict[bw]=gpcr_pdb_dict[gen_num];
            gpcrdb_dict[db]=gpcr_pdb_dict[gen_num];
        }  
        return [bw_dict,gpcrdb_dict]
    }

 /*   var rad_option="high";
    $( "input[type=radio]" ).on( "click", function(){
        rad_option=$(this).attr("value");
    });*/

    function obtainURLinfo(gpcr_pdb_dict){
        cp = obtainCompounds();
        sel_enc =inputText(gpcr_pdb_dict);
        if (gpcr_pdb_dict=="no"){
            high_pre = [];
        } else {
            high_pre = obtainPredefPositions();
        }
        rad_option=$(".sel_high:checked").attr("value");
        var traj=obtainCheckedTrajs()
        // sel_ranges=obtainSelectedAtSeq();
        return [cp, high_pre,sel_enc,rad_option,traj] 
    }

    function disableMissingClasses(){
        $("li.cons_nav").each(function(){ 
            if ($(this).attr("id") == "False"){
                $(this).addClass("disabled")
            }
        })
        $("a.cons_nav").each(function(){ 
            if ($(this).attr("id") == "False"){
                $(this).removeAttr("data-toggle").removeAttr("href").attr("title","Class not avaliable");
            }
        })         
    }

    function obtainLegend(legend_el){
        var color_dict={"A":"<span style='margin-right:5px;color:#01C0E2'>Class A </span>","B":"<span style='margin-right:5px;color:#EF7D02'>Class B </span>","C":"<span style='margin-right:5px;color:#C7F802'>Class C </span>","F":"<span style='margin-right:5px;color:#F904CE'>Class F </span>"}
        var legend="";
        if (legend_el.length > 1){
            for (el in legend_el){
                var add=color_dict[legend_el[el]];
                legend+=add;
            }
            var legend_fin = "<span style='margin-top:5px'>" + legend + "</span>";
            $("#legend").html(legend_fin)
        } else {
            $("#legend").html("")
        }
    }


    function maxInputLength(select, maxlength){
        $(select).on('keyup blur', function() {
            // var maxlength =4;
            var val = $(this).val();
            if (val.length > maxlength) {
                $(this).val(val.slice(0, maxlength));
            }
        });
    }

    maxInputLength('#inputdist',6);
    maxInputLength('input.sel_input',100);
    maxInputLength('#rmsd_frame_1',8);
    maxInputLength('#rmsd_frame_2',8);
    maxInputLength('#rmsd_my_sel_sel',50);
    maxInputLength('#rmsd_ref_frame',8);
    disableMissingClasses();


///    Res within xA of compounf  ///

    $(".section_pan").click(function(){
        var target=$(this).attr("data-target");
        var upOrDown=$(target).attr("class");
        if(upOrDown.indexOf("in") > -1){
            $(this).children("#arrow").attr("class","glyphicon glyphicon-chevron-down");
        } else {
            $(this).children("#arrow").attr("class","glyphicon glyphicon-chevron-up");
        }
    });

    var comp_lg=[];
    var comp_sh=[];
    $(".comp").each(function(){
        var comp_l=$(this).text();
        var comp_s=$(this).attr("id");
        comp_lg[comp_lg.length]=comp_l;
        comp_sh[comp_sh.length]=comp_s;
    })

    var select="";
    for (comp_n in comp_lg){
        var option='<option value="'+comp_sh[comp_n]+'">'+comp_lg[comp_n]+'</option>';
        select += option;
    }
    var first=true;
    var i=1
    $("#add_btn").click(function(){ 
        var row='<span class="dist_sel" id=row'+i+'><br>\
                  <span id="tick" ></span>\
                  <span id="always" style="margin-left:14px">\
                    Show residues within \
                    <input class="form-control input-sm" id="inputdist" type="text" style="margin-bottom:5px;width:40px;padding-left:7px">\
                      &#8491; of\
                        <select id="comp" name="comp">' + select + '</select>\
                  </span>';
        $("#show_within").append(row);
        i+=1;
        if (first){
            $("#rm_btn").css("visibility","visible");
            first=false;
        }
    });
    
    $("#rm_btn").click(function(){ 
        $("#row"+(i-1)).remove();
        i -=1;
        if (i ==1){
            $("#rm_btn").css("visibility","hidden");
            first=true;
        }
    });


    function obtainDistSel(){
        var dist_of=[];
        $(".sel_within").find(".dist_sel").each(function(){ 
            var inp=$(this).find("input").val();
            if (inp && /^[\d.]+$/.test(inp)) {
                var comp=$(this).find("select").val();
                dist_of[dist_of.length]=inp+"-"+comp;
            }

        });       
        return (encode(dist_of))
    }


    $(".sel_within").on("blur", ".dist_sel" ,function(){
        var inp=$(this).find("input").val().replace(/\s+/g, '');
        $(this).find("input").val(inp);
        if (inp && /^[\d.]+$/.test(inp)) {
            $(this).find("#tick").attr({"class":"glyphicon glyphicon-ok", "style":"font-size:10px;color:#7acc00;padding:0;margin:0"});
            $(this).find("#always").attr("style","");
        } else {
            if ($(this).find("#tick").attr("class")=="glyphicon glyphicon-ok"){
                $(this).find("#tick").attr({"class":"","style":""});
                $(this).find("#always").attr("style","margin-left:14px");
            }
        }
    });    

///   Dist between residues  ///

    var first_dist=true;
    var i_dist=1
    $("#add_btn2").click(function(){ 
        if (i_dist < 20){
            var row_d='<span class="dist_pair" id=row2_'+i_dist+'><br>\
                  <span id="tick2" ></span>\
                  <span id="always2" style="margin-left:14px">\
                     Compute distance between \
                     <input class="form-control input-sm" id="dist_from" type="text" style="width:50px;padding-left:7px;margin-bottom:5px">\
			and\
                     <input class="form-control input-sm" id="dist_to" type="text" style="width:50px;padding-left:7px;margin-bottom:5px">\
                  </span>';
            $("#show_dist").append(row_d);
            i_dist+=1;
            if (first_dist){
                $("#rm_btn2").css("visibility","visible");
                first_dist=false;
           }
        }
    });
    
    $("#rm_btn2").click(function(){ 
        $("#row2_"+(i_dist-1)).remove();
        i_dist -=1;
        if (i_dist ==1){
            $("#rm_btn2").css("visibility","hidden");
            first_dist=true;
        }
    });



    $(".dist_btw").on("blur", ".dist_pair" ,function(){
        var d_from=$(this).find("#dist_from").val().replace(/\s+/g, '');
        var d_to=$(this).find("#dist_to").val().replace(/\s+/g, '');
        $(this).find("#dist_from").val(d_from);
        $(this).find("#dist_to").val(d_to);
        if (d_from && d_to && /^[\d]+$/.test(d_from + d_to)) {
            $(this).find("#tick2").attr({"class":"glyphicon glyphicon-ok", "style":"font-size:10px;color:#7acc00;padding:0;margin:0"});
            $(this).find("#always2").attr("style","");
            $(this).addClass("d_ok");
        } else {
            if ($(this).find("#tick2").attr("class")=="glyphicon glyphicon-ok"){
                $(this).find("#tick2").attr({"class":"","style":""});
                $(this).find("#always2").attr("style","margin-left:14px");
                $(this).removeClass("d_ok");
            }
        }
    }); 

    function obtainDistToComp(){
        var distToComp="";
        $(".dist_btw").find(".dist_pair.d_ok").each(function(){ 
            var d_from=$(this).find("#dist_from").val();
            var d_to=$(this).find("#dist_to").val();
            distToComp += d_from+"-"+d_to+"a";
        });
        if (distToComp){
            return (encode(distToComp.slice(0, -1)))
        } else {
            return ""
        }
    }

    function checkTrajUsedInDistComputatiion(res_ids){
        if (res_ids){
            var traj_id = $(".trajForDist:selected").val();
            if (traj_id){
                $("#traj_id_"+traj_id)[0].checked=true;
                return (traj_id)
            }
        }
        return (false)
    }



    $("#gotoDistPg").click(function(){ // if fistComp="" or no traj is selected do nothing
/*
        $.ajax({
            type: "POST",
            url: "/view/1/",
            dataType: "json",
            data: { "item": "Hi there"},
            success: function() {
                alert("done!");
            }
        });

*/
        var res_ids = obtainDistToComp();
        var traj_id=checkTrajUsedInDistComputatiion(res_ids);
        if (traj_id){
            var dist_url ='/view/distances/' +res_ids +"/"+struc_id+"/"+traj_id;
            newwindow=window.open(dist_url,'','width=870,height=400');
            $("#dist_alert").html("");
        } else {
            add_error_d='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>Some fields are empty or contain errors.'
            $("#dist_alert").html(add_error_d);
        }
    });

////
    function showDist(){
        if ($(".view_dist").is(":checked")){
            return ("y")
        } else {
            return ("n")
        }
    };
////
    function selectFromSeq(){
        var click_n=1;
        var seq_pos_1;
        var seq_pos_fin;
        var pos_li=[]
        $(".seq_sel").click(function(){    
            // alert("click");
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
                    // alert(typeof i);
                    while (i <= end) {
                        var mid_id="#" + String(i)
                        $(mid_id).css("background-color","#f2f2f2");
                        $(mid_id).attr("class", "seq_sel");
                        i++
                    }
                }
            } else  {
                // Finish a selection
                click_n=1;
                seq_pos_fin = Number($(this).attr("id"));
                var i = Number(seq_pos_1);
                while (i <= seq_pos_fin){
                    var mid_id="#" + String(i)
                    $(mid_id).css("background-color","#34b734");
                    $(mid_id).children().css("background-color","");
                    $(mid_id).attr("class", "seq_sel sel " + seq_pos_1+"-"+seq_pos_fin); 
                    i++
                }

            }
        })
   
        $(".seq_sel").hover(function(){
            if (click_n==2) {
                var seq_pos_2 = Number($(this).attr("id"));
                var i = Number(seq_pos_1);
                while (i <= seq_pos_2){
                    var mid_id="#" + String(i)
                    $(mid_id).children().css("background-color","#337ab7");
                    i++
                }
            }
        }, function(){
            if (click_n==2) {
                var seq_pos_2 = Number($(this).attr("id"));
                var i = Number(seq_pos_1);
                while (i <= seq_pos_2){
                    var mid_id="#" + String(i)
                    $(mid_id).children().css("background-color","");
                    i++
                }
            }
        });
    }
    selectFromSeq();

    function fromIdsToPositions(id_l, id_r){
        var pos_l=$(id_l).children("#ss_pos").text();
        var pos_r=$(id_r).children("#ss_pos").text();
        return [pos_l, pos_r]
    }

    function fromIdsToPositionsInChain(id_l, id_r){
        var pos_l=$(id_l).children("#ss_pos").text();
        var pos_r=$(id_r).children("#ss_pos").text();
        var chain_l = $(id_l).children("#ss_pos").attr("class");            
        var chain_r = $(id_r).children("#ss_pos").attr("class");
        if (chain_l==chain_r){
            var pos_chain_str=pos_l + "-" +pos_r+":"+chain_l;
        } else {
            var pos_chain_str=pos_l + "-:"+chain_l + " or -"+pos_r+":" +chain_r;
        }
        return pos_chain_str;
    }


    function joinContiguousRanges(sel_ranges){
        var sel_ranges_def=[]
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
        return sel_ranges_def
    }




    function obtainSelectedAtSeq(){
        var sel_ranges=[]
        $(".seq_sel.sel").each(function(){
            var class_str=$(this).attr("class");
            var id_range= class_str.match(/(\d)+/g);
//            var sel_range=clickSelRange($(this).attr("class"));
            sel_ranges[sel_ranges.length]=id_range[0]+"-"+id_range[1];
        });
        return(sel_ranges);
    }


    $("#addToSel").click(function(){ 
        sel_ranges=obtainSelectedAtSeq();
        if (sel_ranges.length > 0){
            sel_ranges_ok=joinContiguousRanges(sel_ranges);
            var pos_str=""
            p=0;
            while (p < (sel_ranges_ok.length -1)) {
                pos_str += sel_ranges_ok[p] + " or "
                p ++
            }
            pos_str += sel_ranges_ok[sel_ranges_ok.length-1]
            var act_val=$(".sel_input").val();
            var or=""
            if (act_val){
                or = " or "
            }
            var fin_val = act_val + or + "protein and ("+ pos_str +")";
            $(".sel_input").val(fin_val)
        }
    });    

    $("#rmds_my_sel_id").click(function(){
        if ($("#rmsd_my_sel_sel").val() == ""){
            rmsdMySel=$(".sel_input").val();
            if (rmsdMySel){
                $("#rmsd_my_sel_sel").val(rmsdMySel);
            }
        }
    });

    function removeSpacesInInput(my_selector){
        $(my_selector).blur(function(){
            my_input=$(this).val().replace(/\s+/g, '');
            $(this).val(my_input);
         });
    }

    removeSpacesInInput("#rmsd_frame_1");
    removeSpacesInInput("#rmsd_frame_2");
    removeSpacesInInput("#rmsd_ref_frame");

    function showErrorInblock(selector, error_msg){
         var sel_fr_error="<div style='color:#DC143C'>" + error_msg + "</div>";
         $(selector).html(sel_fr_error);
    }

    $("#gotoRMSDPg").click(function(){
        $("#rmsd_sel_frames_error").html("");
        $("#rmsd_ref_frames_error").html("");
        rmsdTraj=$("#rmsd_traj").val();
        rmsdFrames=$("#rmsd_sel_frames_id input[name=rmsd_sel_frames]:checked").val();
        if (rmsdFrames=="rmsd_frames_mine"){
            frameFrom=$("#rmsd_frame_1").val();
            frameTo=$("#rmsd_frame_2").val();
            if (frameFrom && frameTo) {
                if (/^[\d]+$/.test(frameFrom + frameTo)){
                    if (Number(frameFrom) >= 1){
                        if (Number(frameFrom) < Number(frameTo)){
                            rmsdFrames=encode(frameFrom + "-" + frameTo);
                        } else {
                            showErrorInblock("#rmsd_sel_frames_error", "Initial frame must be lower than final frame.");
                            rmsdFrames=false;
                        }
                    } else {
                        showErrorInblock("#rmsd_sel_frames_error", "Initial frame must be at least 1.");
                        rmsdFrames=false;
                    }
                } else {
                    showErrorInblock("#rmsd_sel_frames_error", "Input must be a number.");
                    rmsdFrames=false;
                }
            } else {
                rmsdFrames=false;
            }
        }
        rmsdRefFr=$("#rmsd_ref_frame").val();
        if (rmsdRefFr == ""){
            rmsdRefFr="1";
        } else if (! /^[\d]+$/.test(rmsdRefFr)){
            showErrorInblock("#rmsd_ref_frames_error", "Input must be a number.");
            rmsdRefFr=false;
        } else if (Number(rmsdRefFr)<1){
            showErrorInblock("#rmsd_ref_frames_error", "Frame must be at least 1.");
            rmsdRefFr=false;
        }
        rmsdRefTraj=$("#rmsd_ref_traj_id").val();
        rmsdSel=$("#rmsd_sel_id input[name=rmsd_sel]:checked").val();
        if (rmsdSel == "rmds_my_sel"){
            rmsdSel=$("#rmsd_my_sel_sel").val(); //Curate this so that mdtraj understands it            
        }
        if (! rmsdTraj || ! rmsdFrames || ! rmsdRefFr || ! rmsdRefTraj || ! rmsdSel){
            add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>Some fields are empty or contain errors.'
            $("#rmsd_alert").html(add_error);
        } else {
            $("#rmsd_alert").html("");
            $.ajax({
                type: "POST",
                url: "/view/1/",  //Change 1 for actual number
                dataType: "json",
                data: { 
                  "rmsdStr": struc,
                  "rmsdTraj": rmsdTraj,
                  "rmsdFrames": rmsdFrames,
                  "rmsdRefFr": rmsdRefFr,
                  "rmsdRefTraj": rmsdRefTraj,
                  "rmsdSel": rmsdSel
                },
                success: function() {
                    var rmsd_url ='/view/rmsd/';
                    newwindow=window.open(rmsd_url,'','width=870,height=520');
                },
                error: function() {
                    add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>An unexpected error occurred.'
                    $("#rmsd_alert").html(add_error);                
                }
            });

        }
    });

    function obtainCheckedTrajs(){
        var traj = [];
        $(".traj_element:checked").each(function(){
            traj[traj.length]=$(this).attr("value");
        }); 
        return traj;
    }
///
    var struc_info = $(".str_file").attr("id");
    var struc_info = struc_info.split(",");
    var struc = struc_info[0];
    var struc_id = struc_info[1];
    var url_orig = "http://localhost:8081/html/embed.html?struc="+encode(struc);
    var seeReceptor = "y" 
    var sel = "";
    var sel_enc = encode(sel);
    
    var traj=obtainCheckedTrajs()
    $("iframe").attr("src", url_orig + "&rc=" + seeReceptor + "&sel="+"&traj=" + encode(traj) + sel_enc + "&sd=y" );
    $("#receptor").addClass("active");
    var chains_str = $("#chains").text();

    var gpcr_pdb_dict = $(".gpcr_pdb").attr("id");
    var bw_dict,gpcrdb_dict
    if (gpcr_pdb_dict !="no"){
        gpcr_pdb_dict=JSON.parse(gpcr_pdb_dict);
        dicts_result=obtainDicts(gpcr_pdb_dict); 
        bw_dict = dicts_result[0];
        gpcrdb_dict=dicts_result[1];
    }



    click_unclick(".high_pdA");
    click_unclick(".high_pdB");
    click_unclick(".high_pdC");
    click_unclick(".high_pdF");
    click_unclick(".rep_elements");
    click_unclick("#col_btn");
    seeReceptor=click_unclick_specialRec("#receptor");
    $("#btn_all").click(function(){
        $(".rep_elements").addClass("active");
    });
    $("#btn_clear").click(function(){
        $(".rep_elements").removeClass("active");
    });




    $("#submit").click(function(){
        var results = obtainURLinfo(gpcr_pdb_dict);
        cp = results[0];
        high_pre=results[1];
        sel_enc=results[2];
        var rad_option =results[3];
        var traj =results[4];
        var view_dist=showDist();
        var pd = "n";
        var legend_el=[];
        for (key in high_pre){
            if (high_pre[key].length > 0){
                pd = "y"
                legend_el[legend_el.length]=key;
            }
        }
        var dist_of=obtainDistSel();  // For the dist selection
        var distToComp = obtainDistToComp();
        var traj_id=checkTrajUsedInDistComputatiion(distToComp);
        obtainLegend(legend_el);
        url = url_orig + ("&sel=" + sel_enc + "&traj=" + encode(traj) + "&rc=" + seeReceptor  + "&cp=" + encode(cp) + "&sh=" + rad_option + "&pd=" + pd + "&la=" + encode(high_pre["A"])+ "&lb=" + encode(high_pre["B"])+ "&lc=" + encode(high_pre["C"])+ "&lf=" + encode(high_pre["F"]) + "&wth="+dist_of + "&sd="+view_dist + "&di="+encode(distToComp) );
       // alert(url);
       $("iframe").attr("src", url);
    });

    $("#to_mdsrv").click(function(){
         var distToComp = obtainDistToComp();
         var traj_id=checkTrajUsedInDistComputatiion(distToComp);
         var results = obtainURLinfo(gpcr_pdb_dict);
         cp = results[0];
         high_pre=results[1];
         sel_enc=results[2];
         var rad_option =results[3];
         var traj =results[4];
         var view_dist= showDist();
         var pd = "n";
         for (key in high_pre){
             if (high_pre[key].length > 0){
                 pd = "y"
                 break
             }
         }
        var dist_of=obtainDistSel(); // For the dist selection
        var url_mdsrv = "http://localhost:8081/html/mdsrv_emb.html?struc=" + encode(struc) + "&traj=" + encode(traj) + "&sel=" + sel_enc + "&rc=" + seeReceptor  + "&cp=" + encode(cp) + "&sh=" + rad_option + "&pd=" + pd + "&la=" + encode(high_pre["A"])+ "&lb=" + encode(high_pre["B"])+ "&lc=" + encode(high_pre["C"])+ "&lf=" + encode(high_pre["F"]) + "&wth="+dist_of + "&sd="+view_dist + "&di="+encode(distToComp);
        $(this).attr("href", url_mdsrv);
    });    

});

