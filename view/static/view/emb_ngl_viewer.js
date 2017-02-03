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
            var add_or ="";
            if (num_gpcrs >1){
                add_or=" or ";
            }
            for (i in gpcr_ranges) {
                var gpcr_pair_str = gpcr_ranges[i];
                var gpcr_pair=gpcr_pair_str.split(new RegExp('\\s*-\\s*','g'));
                var pos_range_all=""
                for (gpcr_id in all_gpcr_dicts){
                    var pos_range="";
                    my_gpcr_dicts=all_gpcr_dicts[gpcr_id];
                    gpcr_comb_dict=my_gpcr_dicts["combined_num"];
                    bw_dict=my_gpcr_dicts["bw_num"];
                    gpcrdb_dict=my_gpcr_dicts["gpcrDB_num"];
                    var chain_pair=[]
                    var res_pair=[]
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
                            chain_pair=false
                            to_add='<div class="alert alert-danger row" style = "margin-bottom:10px" ><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>'+gpcr_pair_str+' not found at '+gpcr_id_name[gpcr_id]+'.</div>'
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
                            start=all_chains.indexOf(chain_pair[0]);
                            end=all_chains.indexOf(chain_pair[1]);
                            var middle_str="";
                            considered_chains=all_chains.slice(start+1,end)
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
                    pos_range_all="("+pos_range_all+")"
                }  
                pre_sel = pre_sel.replace(gpcr_pair_str, pos_range_all);
            } else {
                pre_sel="";
            }
            sel=pre_sel;
            }//END FOR GPCR RANGES
        }
        var sel_sp = sel.match(/(\s)+-(\s)+/g);
        if (sel_sp != null){ //Remove white spaces between "-" and nums
            for (i in sel_sp){
                var sp=sel_sp[i];
                sel=sel.replace(sp,"-");
            }
        }
        //alert(sel);
        sel_enc = encode(sel);
        return sel_enc
    };

    $("#gpcr_sel").change(function(){
        var gpcr_id=$(this).children(":selected").val();
        var chosen_id = "#gpcr_id_"+gpcr_id;
        $(chosen_id).css("display","inline");
        $(".gpcr_prot_show_cons:not("+chosen_id+")").css("display","none");
    })

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
        $(".comp.active").each(function(){
            comp[comp.length]=$(this).attr("id");
        });
        return comp;
    }
    
    function obtainNonGPCRchains(selector){
        nonGPCR_chains = $(selector).attr("id");
        if (nonGPCR_chains){
            var patt = new RegExp("protein and \\((.*)\\)");
            var nonGPCR_substr = patt.exec(nonGPCR_chains);
            if (nonGPCR_substr){
                nonGPCR_substr=nonGPCR_substr[1];
                nonGPCR_li = nonGPCR_substr.match(/[A-Z]/g);
                nonGPCR_str = nonGPCR_li.join();
                return nonGPCR_str;
            }
        }
        return ("");
    }


    function uniq(a) {
        var seen = {};
        return a.filter(function(item) {
            return seen.hasOwnProperty(item) ? false : (seen[item] = true);
        });
    }

///////////////
    $(".high_pd").each(function(){
        if ($(this).data("pdbpos").toString() == "None"){
            $(this).attr("disabled", true);
        }
    })
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

    $(".clear_conspos").click(function(){;
        $(".high_pd.active").each(function(){
            $(this).removeClass("active");
        });
    });    


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
            all_gpcr_dicts[gpcr_id]={"combined_num":gpcr_pdb_dict[gpcr_id], "bw_num": bw_dict, "gpcrDB_num":gpcrdb_dict}
        }
        return [all_gpcr_dicts , num_gpcrs];
    }



    function obtainURLinfo(gpcr_pdb_dict){
        cp = obtainCompounds();
        nonGPCR=obtainNonGPCRchains(".nonGPCR:not(.active)");
        sel_enc =inputText(gpcr_pdb_dict);
        if (gpcr_pdb_dict=="no"){
            high_pre = [];
        } else {
            high_pre = obtainPredefPositions();
        }
        rad_option=$(".sel_high:checked").attr("value");
        var traj=obtainCheckedTrajs()
        return [cp, high_pre,sel_enc,rad_option,traj,nonGPCR] 
    }

    function disableMissingClasses(){
        $("li.cons_nav").each(function(){ 
            if ($(this).data("TF") == "False"){
                $(this).addClass("disabled");
            }
        })
        $("a.cons_nav").each(function(){ 
            if ($(this).data("TF") == "False"){
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
    maxInputLength("#int_thr", 3)
    disableMissingClasses();

    $(".section_pan").click(function(){
        var target=$(this).attr("data-target");
        var upOrDown=$(target).attr("class");
        if(upOrDown.indexOf("in") > -1){
            $(this).children("#arrow").attr("class","glyphicon glyphicon-chevron-down");
        } else {
            $(this).children("#arrow").attr("class","glyphicon glyphicon-chevron-up");
        }
    });

///    Res within xA of compounf  ///

    var comp_lg=[];
    var comp_sh=[];
    $(".comp").each(function(){
        var comp_l=$(this).text();
        var comp_s=$(this).attr("id");
        comp_lg[comp_lg.length]=comp_l;
        comp_sh[comp_sh.length]=comp_s;
    })
    
    $(".nonGPCR").each(function(){
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




function isEmptyDict(mydict){
    empty=true
    for (key in mydict){
        if (mydict[key].length >= 1){
            empty=false
            break
        }
    }
  return empty;
}

///   Freq on Interaction  ///
    function gnumFromPosChain(pos, chain){
        result="-"
        for (gpcr in all_gpcr_dicts){ //[1]["combined_num"]
            var search_dict=all_gpcr_dicts[gpcr]["combined_num"]
            for (gnum in search_dict){
                if (search_dict[gnum][0] == pos && search_dict[gnum][1] ==chain){
                    result = gnum
                }
            }
        }
        return result
    }

    var i_id=1;
    var lig_sel_str;
    $("#gotoInt").click(function(){
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
                var intof=$(".ligInt:selected").val()
                if (intof=="allLig"){
                    var all_lig_sel=[]
                    $(".unitInt").each(function(){
                        var lig_s=$(this).val();
                        all_lig_sel[all_lig_sel.length]=lig_s;        
                    });
                } else {
                    all_lig_sel=[intof]
                }
                var dist_scheme= $(".dist_scheme_opt:selected").val();
                var dist_scheme_name;
                if (dist_scheme=="closest"){
                    dist_scheme_name="All atoms";
                } else {
                    dist_scheme_name="Heavy atoms only";
                }
                $("#int_alert , #int_thr_error , #int_traj_error").html("");
                ///AJAX!!!
                $("#int_info").after("<p style='margin-left:13px;margin-top:5px;padding:5px;background-color:#e6e6ff;border-radius:3px;' id='wait_int'><span class='glyphicon glyphicon-time'></span> Computing interaction...</p>")
                if (i_id==1){
                    $("#gotoInt").addClass("disabled");
                }
                $(".href_save_data_dist_plot,.href_save_data_rmsd_plot").addClass("disabled");
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
                    },
                    success: function(int_data) {
                        if ($.active<=1){
                            $(".href_save_data_dist_plot,.href_save_data_rmsd_plot").removeClass("disabled");
                        }
                        $("#wait_int").remove();
                        if (i_id==1){
                            $("#gotoInt").removeClass("disabled");
                        }
                        var success=int_data.success;
                        if (success){  // [!]WHAT IF THERE ARE 0 INT!??
                            var int_data=int_data.result;
                            if (! isEmptyDict(int_data)){
                                var table_html='<div class="int_tbl" id=int_tbl'+i_id+' class="table-responsive" style="border:1px solid #F3F3F3;padding:10px;overflow:auto">\
                                  <table class="table table-condensed" style="font-size:12px">\
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
                                for (lig in int_data){
                                    res_int=int_data[lig];
                                    var num_res_int=res_int.length;
                                    table_html+='<tr><td rowspan='+num_res_int+'>'+lig+'</td>';
                                    var res_int_1st=res_int[0];
                                    var res_int_1st_ok=[res_int_1st[2]+res_int_1st[0].toString(),res_int_1st[1],gnumFromPosChain(res_int_1st[0].toString(), res_int_1st[1]),res_int_1st[3]+"%"]
                                    for (info in res_int_1st_ok){
                                        table_html+='<td>'+res_int_1st_ok[info]+'</td>';
                                    }
                                    table_html+='</tr>';
                                    var res_int_rest=res_int.slice(1,res_int.length);
                                    for (res_infoN in res_int_rest){
                                        var res_info=res_int_rest[res_infoN];
                                        var res_info_ok=[res_info[2]+res_info[0].toString(),res_info[1],gnumFromPosChain(res_info[0].toString(), res_info[1]),res_info[3]+"%"]
                                        table_html+='<tr>';
                                        for (infoN in res_info_ok){
                                            var info=res_info_ok[infoN];
                                            table_html+='<td>'+info+'</td>';
                                        }
                                        table_html+='</tr>';
                                    }                              
                                }
                                var patt = /[^/]*$/g;
                                var trajFile = patt.exec(traj_path);
                                table_html+="</tbody></table>\
                                 <div style='font-size:12px;' ><b>Threshold:</b> "+thr_ok+" &#8491; ("+dist_scheme_name+"), <b>Trajectory:</b> "+trajFile+"</div>\
                                    <div style='display:inline-block;margin:5px;color:#DC143C;cursor:pointer;'>\
                                        <span title='Delete' class='glyphicon glyphicon-trash delete_int_tbl'></span>\
                                    </div>\
                                </div>";
                                $("#int_info").append(table_html);
                            } else {
                                var patt = /[^/]*$/g;
                                var trajFile = patt.exec(traj_path);
                                var noInt_msg="<div class='int_tbl' id=int_tbl"+i_id+" style='border:1px solid #F3F3F3;padding:10px;'>\
                                 <div style='font-size:12px;margin-bottom:5px' ><b>Threshold:</b> "+thr_ok+" &#8491;  ("+dist_scheme_name+"), <b>Trajectory:</b> "+trajFile+"</div>\
                                        <div style='margin-bottom:5px'>No interactions found.</div>\
                                    <div style='display:inline-block;margin:5px;color:#DC143C;cursor:pointer;'>\
                                        <span title='Delete' class='glyphicon glyphicon-trash delete_int_tbl'></span>\
                                    </div>\
                                </div>"
                                $("#int_info").append(noInt_msg);
                            }
                            i_id+=1;
                        }else{
                            var int_error=int_data.e_msg;
                            add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>'+ int_error;
                            $("#int_alert").html(add_error);    
                        }
                    },
                    error: function(){
                        add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>An unexpected error occurred.';
                        $("#int_alert").html(add_error); 
                        if ($.active<=1){
                            $(".href_save_data_dist_plot,.href_save_data_rmsd_plot").removeClass("disabled");
                        }
                        $("#wait_int").remove();
                        if (i_id==1){
                            $("#gotoInt").removeClass("disabled");
                        }            
                    }
                });
            } else {
                $("#int_traj_error").text("Please select a trajectory.");
                add_error_d='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>Some fields are empty or contain errors.';
                $("#int_alert").html(add_error_d);
            }
        } else {
            $("#int_thr_error").text("Threshold must be an integer.")
            add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>Some fields are empty or contain errors.'
            $("#int_alert").html(add_error);   
        }
    });
    
    $('body').on('click','.delete_int_tbl', function(){
        var IntToRv=$(this).parents(".int_tbl").attr("id");
        $('#'+IntToRv).remove();
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

    function obtainTrajUsedInDistComputatiion(res_ids){
        if (res_ids){
            var traj_id = $(".trajForDist:selected").val();
            var traj_path = $(".trajForDist:selected").attr("name");
            if (traj_id){
                $("#traj_id_"+traj_id)[0].checked=true;
                return (traj_path)
            }
        }
        return (false)
    }

    //var distResultDict={};
    var chart_img={};
    var d_id=1;
    $("#gotoDistPg").click(function(){ // if fistComp="" or no traj is selected do nothing

        var res_ids = obtainDistToComp();
        if ($(this).attr("class").indexOf("withTrajs") > -1){
            var traj_p=obtainTrajUsedInDistComputatiion(res_ids);
            if (traj_p){                
                $("#dist_chart").after("<p style='margin-left:13px;margin-top:5px;padding:5px;background-color:#e6e6ff;border-radius:3px;' id='wait_dist'><span class='glyphicon glyphicon-time'></span> Computing distances...</p>")
                if (d_id==1){
                    $("#gotoDistPg").addClass("disabled");
                }
                $(".href_save_data_dist_plot,.href_save_data_rmsd_plot").addClass("disabled");
                $.ajax({
                    type: "POST",
                    url: "/view/"+dyn_id+"/",  //Change 1 for actual number
                    dataType: "json",
                    data: { 
                      "distStrWT": struc,
                      "distTraj": traj_p,
                      "dist_residsWT": res_ids,
                    },
                    success: function(data_dist_wt) {
                        $("#wait_dist").remove();
                        if (d_id==1){
                            $("#gotoDistPg").removeClass("disabled");
                        }
                        var success=data_dist_wt.success;
                        if (success){
                            var dist_array=data_dist_wt.result;
                            var dist_id=data_dist_wt.dist_id;
                            //distResultDict["dist_"+d_id.toString()]=dist_array;                                                    
                            function drawChart(){
                                var patt = /[^/]*$/g;
                                var trajFile = patt.exec(traj_p);
                                var data = google.visualization.arrayToDataTable(dist_array,false);
                                var options = {'title':'Residue Distance ('+trajFile+')',
                                    "height":350, "width":500, "legend":{"position":"bottom","textStyle": {"fontSize": 10}}, 
                                    "chartArea":{"right":"10","left":"40","top":"50","bottom":"60"}};
                                newgraph_sel="dist_chart_"+d_id.toString();
                                var plot_html;
                                if ($.active<=1){
                                    plot_html="<div class='dist_plot' id='all_"+newgraph_sel+"' style='border:1px solid #F3F3F3;overflow:auto;overflow-y:hidden;-ms-overflow-y: hidden;'>\
                                                    <div id="+newgraph_sel+"></div>\
                                                    <div style='margin:5px'>\
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
                                                        <div style='display:inline-block;margin:5px;color:#DC143C;cursor:pointer;'>\
                                                            <span title='Delete' class='glyphicon glyphicon-trash delete_dist_plot'></span>\
                                                        </div>\
                                                    </div>\
                                                </div>"//color:#239023
                                }else{
                                    plot_html="<div class='dist_plot' id='all_"+newgraph_sel+"' style='border:1px solid #F3F3F3;overflow:auto;overflow-y:hidden;-ms-overflow-y: hidden;'>\
                                                    <div id="+newgraph_sel+"></div>\
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
                                                        <div style='display:inline-block;margin:5px;color:#DC143C;cursor:pointer;'>\
                                                            <span title='Delete' class='glyphicon glyphicon-trash delete_dist_plot'></span>\
                                                        </div>\
                                                    </div>\
                                                </div>"                            
                                } 
                                $("#dist_chart").append(plot_html);
                                var chart_div = document.getElementById(newgraph_sel);
                                var chart = new google.visualization.LineChart(chart_div);
                                
                                /*//Wait for the chart to finish drawing before calling the getImageURI() method.
                                google.visualization.events.addListener(chart, 'ready', function () {
                                    chart_div.innerHTML = '<img src="' + chart.getImageURI() + '">';
                                    console.log(chart_div.innerHTML);
                              });*/
                                
                                google.visualization.events.addListener(chart, 'ready', function () {
                                    var img_source =  chart.getImageURI() 
                                    $(".save_img_dist_plot").attr("href",img_source)
                                });
                                
                                chart.draw(data, options);
                                d_id+=1;
                                
                            };
                            google.load("visualization", "1", {packages:["corechart"],'callback': drawChart});
                        } else {
                            var msg=data_dist_wt.msg;
                            add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>'+ msg;
                            $("#dist_alert").html(add_error);                
                        }
                        if ($.active<=1){
                            $(".href_save_data_dist_plot,.href_save_data_rmsd_plot").removeClass("disabled");
                        }
                    },
                    error: function() {
                        if (d_id==1){
                            $("#gotoDistPg").removeClass("disabled");
                        }
                        $("#wait_dist").remove();
                        if ($.active<=1){
                            $(".href_save_data_dist_plot,.href_save_data_rmsd_plot").removeClass("disabled");
                        }
                        add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>An unexpected error occurred.'
                        $("#dist_alert").html(add_error);                
                    }
                });
///////////////////////////////////////
                $("#dist_alert").html("");
            } else {
                add_error_d='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>Some fields are empty or contain errors.'
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
                            dist_result=data_dist.result
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
                add_error_d='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>Some fields are empty or contain errors.'
                $("#dist_alert").html(add_error_d);
            }
        }
    });

    $('body').on('click','.delete_dist_plot', function(){
        var plotToRv=$(this).parents(".dist_plot").attr("id");
        $('#'+plotToRv).remove();
    });


    
    function showDist(){
        if ($(".view_dist").is(":checked")){
            return ("y")
        } else {
            return ("n")
        }
    };
///////////////////////////
    function selectFromSeq(){
        var click_n=1;
        var seq_pos_1;
        var seq_pos_fin;
        var pos_li=[]
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
            start=all_chains.indexOf(chain_l);
            end=all_chains.indexOf(chain_r);
            var middle_str="";
            considered_chains=all_chains.slice(start+1,end)
            for (chain in considered_chains){
                middle_str += " or :"+ considered_chains[chain];
            }
            var pos_chain_str= pos_l + "-:"+chain_l +middle_str +" or 1-"+pos_r+":" +chain_r;
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
    removeSpacesInInput("#int_thr");

    function showErrorInblock(selector, error_msg){
         var sel_fr_error="<div style='color:#DC143C'>" + error_msg + "</div>";
         $(selector).html(sel_fr_error);
    }

    function SelectionName(traj_sel){
        var set_sel
        if (traj_sel == "bck"){
            set_sel="backbone"
        } else if (traj_sel == "noh"){
            set_sel="noh"
        } else if (traj_sel == "min"){
            set_sel="minimal"
        } else if (traj_sel == "all_atoms"){
            set_sel="all atoms"
        }
        return (set_sel)
    }
    var r_id=1;
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
                 //   if (Number(frameFrom) >= 1){
                    if (Number(frameFrom) < Number(frameTo)){
                        rmsdFrames=encode(frameFrom + "-" + frameTo);
                    } else {
                        showErrorInblock("#rmsd_sel_frames_error", "Initial frame must be lower than final frame.");
                        rmsdFrames=false;
                    }
                    //} else {
                    //    showErrorInblock("#rmsd_sel_frames_error", "Initial frame must be at least 1.");
                    //    rmsdFrames=false;
                    //}
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
            rmsdRefFr="0";
        } else if (! /^[\d]+$/.test(rmsdRefFr)){
            showErrorInblock("#rmsd_ref_frames_error", "Input must be a number.");
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
            add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>Some fields are empty or contain errors.'
            $("#rmsd_alert").html(add_error);
        } else {//class="col-md-12" style="margin-top:5px;padding-right:40px;clear:left;"
            $("#rmsd_chart").after("<div class='col-md-12'><p style='margin-left:13px;margin-top:5px;padding:5px;background-color:#e6e6ff;border-radius:3px;clear:left' id='wait_rmsd'><span class='glyphicon glyphicon-time'></span> Computing RMSD...</p></div>")        
            $("#rmsd_alert").html("");
            if (r_id==1){
                $("#gotoRMSDPg").addClass("disabled");
            }
            $(".href_save_data_dist_plot,.href_save_data_rmsd_plot").addClass("disabled"); 
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
                  "rmsdSel": rmsdSel
                },
                success: function(data_rmsd) {
                    $("#wait_rmsd").remove();
                    if (r_id==1){
                        $("#gotoRMSDPg").removeClass("disabled");
                    }
                    var success=data_rmsd.success;
                    if (success){
/////////////////////                    
                        var rmsd_array=data_rmsd.result;
                        var rmsd_id=data_rmsd.rmsd_id;                               
                        function drawChart2(){
                            var patt = /[^/]*$/g;
                            var trajFile = patt.exec(rmsdTraj);
                            var refTrajFile = patt.exec(rmsdRefTraj);
                            var rmsdSelOk=SelectionName(rmsdSel)
                            var data = google.visualization.arrayToDataTable(rmsd_array,false);
                            var options = {'title':'RMSD (traj:'+trajFile+', ref: fr '+rmsdRefFr+' of traj '+refTrajFile+', sel: '+rmsdSelOk+')',
                                "height":350, "width":500, "legend":{"position":"bottom","textStyle": {"fontSize": 10}}, 
                                "chartArea":{"right":"10","left":"40","top":"50","bottom":"60"}};
                            newRMSDgraph_sel="rmsd_chart_"+r_id.toString();
                            var RMSDplot_html;
                            if ($.active<=1){
                                RMSDplot_html="<div class='rmsd_plot' id='all_"+newRMSDgraph_sel+"' style='border:1px solid #F3F3F3;overflow:auto;overflow-y:hidden;-ms-overflow-y: hidden;'>\
                                                <div id="+newRMSDgraph_sel+"></div>\
                                                <div id='opt_"+newRMSDgraph_sel+"' style='margin:5px'>\
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
                                                        <span title='Delete' class='glyphicon glyphicon-trash delete_rmsd_plot'></span>\
                                                    </div>\
                                                </div>\
                                            </div>"//color:#239023
                            }else{
                                RMSDplot_html="<div class='rmsd_plot' id='all_"+newRMSDgraph_sel+"' style='border:1px solid #F3F3F3;overflow:auto;overflow-y:hidden;-ms-overflow-y: hidden;'>\
                                                <div id="+newRMSDgraph_sel+"></div>\
                                                <div style='margin:5px'>\
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
                                                        <span title='Delete' class='glyphicon glyphicon-trash delete_rmsd_plot'></span>\
                                                    </div>\
                                                </div>\
                                            </div>"                            
                            } 
                            $("#rmsd_chart").append(RMSDplot_html);
                            var rmsd_chart_div = document.getElementById(newRMSDgraph_sel);
                            var chart = new google.visualization.LineChart(rmsd_chart_div);
                            
                            google.visualization.events.addListener(chart, 'ready', function () {
                                var rmsd_img_source =  chart.getImageURI() 
                                $(".save_img_rmsd_plot").attr("href",rmsd_img_source)
                            });
                            
                            chart.draw(data, options);
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
                            
                        };
                        google.load("visualization", "1", {packages:["corechart"],'callback': drawChart2});
                        small_errors=data_rmsd.msg;
////////////////////
                    } else {
                        var e_msg=data_rmsd.msg;
                        add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>'+ e_msg;
                        $("#rmsd_alert").html(add_error);                              
                    }
                    if ($.active<=1){
                        $(".href_save_data_dist_plot,.href_save_data_rmsd_plot").removeClass("disabled");
                    }
                },
                error: function() {
                    if (r_id==1){
                        $("#gotoRMSDPg").removeClass("disabled");
                    }
                    $("#wait_rmsd").remove();
                    add_error='<div class="alert alert-danger"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>An unexpected error occurred.'
                    $("#rmsd_alert").html(add_error);  
                    if ($.active<=1){
                        $(".href_save_data_dist_plot,.href_save_data_rmsd_plot").removeClass("disabled");
                    }
                }
            });

        }
    });

    $('body').on('click','.delete_rmsd_plot', function(){
        var plotToRv=$(this).parents(".rmsd_plot").attr("id");
        $('#'+plotToRv).remove();
    });

    function obtainCheckedTrajs(){
        var traj = [];
        $(".traj_element:checked").each(function(){
            traj[traj.length]=$(this).attr("value");
        }); 
        return traj;
    }
///
    var struc = $(".str_file").data("struc_file");
    var dyn_id=$(".str_file").data("dyn_id");
    //var struc_id =$(".str_file").data("structure_file_id");
    /*var struc_info = $(".str_file").attr("id");
    var struc_info = struc_info.split(",");
    var struc = struc_info[0];
    var struc_id = struc_info[1];
    var dyn_id=struc_info[2];*/
    var mdsrv_url=$("#embed_mdsrv").data("mdsrv_url");
    var url_orig = mdsrv_url+"/html/embed.html?struc="+encode(struc);
    var seeReceptor = "y" 
    var sel = "";
    var sel_enc = encode(sel);

    
    var traj=obtainCheckedTrajs()
    $("iframe").attr("src", url_orig + "&rc=" + seeReceptor + "&sel="+"&traj=" + encode(traj) + sel_enc + "&sd=y" );
    $("#receptor").addClass("active");
    $(".nonGPCR").addClass("active");
    var chains_str = $("#chains").text();
    var all_chains = $("#chains").data("all_chains").split(",");

    var gpcr_pdb_dict = $(".gpcr_pdb").data("gpcr_pdb");
    var bw_dict,gpcrdb_dict,gpcr_id_name,all_gpcr_dicts,num_gpcrs;
    if (gpcr_pdb_dict !="no"){
        gpcr_id_name=$("#cons_pos_box_all").data("gpcr_id_name");
        //gpcr_pdb_dict=JSON.parse(gpcr_pdb_dict);
        dicts_results=obtainDicts(gpcr_pdb_dict);
        all_gpcr_dicts=dicts_results[0];
        num_gpcrs =dicts_results[1];
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
        var nonGPCR =results[5];
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
        var onlyChains="";
        if (seeReceptor=="n" && nonGPCR == ""){
            onlyChains=obtainNonGPCRchains(".nonGPCR");
        }
        obtainLegend(legend_el);
        url = url_orig + ("&sel=" + sel_enc + "&traj=" + encode(traj) + "&rc=" + seeReceptor  + "&cp=" + encode(cp) + "&sh=" + rad_option + "&pd=" + pd + "&la=" + encode(high_pre["A"])+ "&lb=" + encode(high_pre["B"])+ "&lc=" + encode(high_pre["C"])+ "&lf=" + encode(high_pre["F"]) + "&wth="+dist_of + "&sd="+view_dist + "&di="+encode(distToComp)+ "&ng="+ nonGPCR + "&och="+ onlyChains);
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
         var nonGPCR =results[5];
         var view_dist= showDist();
         var pd = "n";
         for (key in high_pre){
             if (high_pre[key].length > 0){
                 pd = "y"
                 break
             }
        }
        var onlyChains="";
        if (seeReceptor=="n" && nonGPCR == ""){
            onlyChains=obtainNonGPCRchains(".nonGPCR");
        }
        var dist_of=obtainDistSel(); // For the dist selection
        var url_mdsrv = mdsrv_url+"/html/mdsrv_emb.html?struc=" + encode(struc) + "&traj=" + encode(traj) + "&sel=" + sel_enc + "&rc=" + seeReceptor  + "&cp=" + encode(cp) + "&sh=" + rad_option + "&pd=" + pd + "&la=" + encode(high_pre["A"])+ "&lb=" + encode(high_pre["B"])+ "&lc=" + encode(high_pre["C"])+ "&lf=" + encode(high_pre["F"]) + "&wth="+dist_of + "&sd="+view_dist + "&di="+encode(distToComp)+ "&ng="+ nonGPCR + "&och="+ onlyChains;
        $(this).attr("href", url_mdsrv);
    });    

});

