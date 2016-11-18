$(document).ready(function(){
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
                    if ($("#chains").text() == "") {
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
//////////////


    // function obtainPredefPositions(){
    //     var high_pre=[];
    //     $(".high_pd.active").each(function(){
    //         range = $(this).attr("id");
    //         if (range != "None"){
    //             if (range.indexOf(",") > -1){
    //                 range_li=range.split(",");
    //                 for (num in range_li){
    //                     high_pre[high_pre.length]=" " + range_li[num];
    //                 }
    //             } else{
    //                 high_pre[high_pre.length]=" " + range;
    //             }
    //         }
    //     })
    //     high_pre.sort(function(x,y){
    //         var patt = /\d+/;
    //         var xp = Number(patt.exec(x));
    //         var yp = Number(patt.exec(y));
    //         return xp - yp });
    //     high_pre=uniq(high_pre);
    //     return (high_pre);
    // }

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

    function obtainURLinfo(gpcr_pdb_dict){
        cp = obtainCompounds();
        sel_enc =inputText(gpcr_pdb_dict);
        if (gpcr_pdb_dict=="no"){
            high_pre = [];
        } else {
            high_pre = obtainPredefPositions();
        }
        return [cp, high_pre,sel_enc] 
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

    maxInputLength('#inputdist',4);
    maxInputLength('input.sel_input',100);
    disableMissingClasses();


///    
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
                dist_of[dist_of.length]=[inp,comp];
            }

        });       
        return (encode(dist_of))
    }


    $(".sel_within").on("blur", ".dist_sel" ,function(){
        var inp=$(this).find("input").val();
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
////
    // var click_n=0;
    // var seq_pos_1
    // $(".seq_sel").click(function(){
    //     alert(click_n);
    //     if (click_n=0){
    //         $(this).css("background-color","#E8E8E8");
    //         var seq_pos_1 = $(this).attr("id");
    //         click_n=1;
    //     } else {
    //         click_n=0;
    //     }
    // })

    // $(".seq_sel").mouseenter(function(){
    //     if (click_n=1) {
    //         var seq_pos_2 = $(this).attr("id");
    //         var i = seq_pos_1;
    //         while (i <= seq_pos_2){
    //             var mid_id="#" + String(i)
    //             $(mid_id).css("background-color","#E8E8E8");
    //             i++
    //         }
    //     }
    // });





///
    var struc = $(".str_file").attr("id");
    var url_orig = "http://localhost:8081/html/embed/embed.html?struc="+encode(struc);
    var seeReceptor = "y" 
    var sel = "";
    var sel_enc = encode(sel);
    $("iframe").attr("src", url_orig + "&rc=" + seeReceptor + "&sel=" + sel_enc);
    $("#receptor").addClass("active");

    var gpcr_pdb_dict = $(".gpcr_pdb").attr("id");
    var bw_dict,gpcrdb_dict
    if (gpcr_pdb_dict !="no"){
        gpcr_pdb_dict=JSON.parse(gpcr_pdb_dict);
        dicts_result=obtainDicts(gpcr_pdb_dict); 
        bw_dict = dicts_result[0];
        gpcrdb_dict=dicts_result[1];
    }

    var rad_option="sel";
    $( "input[type=radio]" ).on( "click", function(){
        rad_option=$(this).attr("value");
    });

    click_unclick(".high_pdA");
    click_unclick(".high_pdB");
    click_unclick(".high_pdC");
    click_unclick(".high_pdF");
    click_unclick(".rep_elements");
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
        var pd = "n";
        var legend_el=[];
        for (key in high_pre){
            if (high_pre[key].length > 0){
                pd = "y"
                legend_el[legend_el.length]=key;
            }
        }
        var dist_of=obtainDistSel();  // For the dist selection
        obtainLegend(legend_el);
        url = url_orig + ("&sel=" + sel_enc + "&rc=" + seeReceptor  + "&cp=" + encode(cp) + "&sh=" + rad_option + "&pd=" + pd + "&la=" + encode(high_pre["A"])+ "&lb=" + encode(high_pre["B"])+ "&lc=" + encode(high_pre["C"])+ "&lf=" + encode(high_pre["F"]));
       $("iframe").attr("src", url);
    });

    $("#to_mdsrv").click(function(){
         var traj = [];
         $(".traj_element:checked").each(function(){
             traj[traj.length]=$(this).attr("value");
         });
        var results = obtainURLinfo(gpcr_pdb_dict);
        cp = results[0];
        high_pre=results[1];
        sel_enc=results[2];
        var pd = "n";
        for (key in high_pre){
            if (high_pre[key].length > 0){
                pd = "y"
                break
            }
        }
        // var dist_of=obtainDistSel(); // For the dist selection
        var url_mdsrv = "http://localhost:8081/html/mdsrv_emb.html?struc=" + encode(struc) + "&traj=" + encode(traj) + "&sel=" + sel_enc + "&rc=" + seeReceptor  + "&cp=" + encode(cp) + "&sh=" + rad_option + "&pd=" + pd + "&la=" + encode(high_pre["A"])+ "&lb=" + encode(high_pre["B"])+ "&lc=" + encode(high_pre["C"])+ "&lf=" + encode(high_pre["F"]);
        $(this).attr("href", url_mdsrv);
    });    

});
