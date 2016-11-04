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
                var gpcr_pair=gpcr_pair_str.split(new RegExp('\s*\-\s*','g'));
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
    function obtainPredefPositions(){
        var high_pre=[];
        $(".high_pd.active").each(function(){
            range = $(this).attr("id");
            if (range != "None"){
                if (range.indexOf(",") > -1){
                    range_li=range.split(",");
                    for (num in range_li){
                        high_pre[high_pre.length]=" " + range_li[num];
                    }
                } else{
                    high_pre[high_pre.length]=" " + range;
                }
            }
        })
        high_pre.sort(function(x,y){
            var patt = /\d+/;
            var xp = Number(patt.exec(x));
            var yp = Number(patt.exec(y));
            return xp - yp });
        high_pre=uniq(high_pre);
        alert(high_pre)
        return (high_pre);
    }

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

    $('input:text').on('keyup blur', function() {
        var maxlength =100;
        var val = $(this).val();
        if (val.length > maxlength) {
            $(this).val(val.slice(0, maxlength));
        }
    });

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

    click_unclick(".high_pd");
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
        url = url_orig + ("&sel=" + sel_enc + "&rc=" + seeReceptor  + "&cp=" + encode(cp) + "&sh=" + rad_option + "&pd=" + encode(high_pre));
        //$("iframe").attr("src", url);
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
        var url_mdsrv = "http://localhost:8081/html/mdsrv_emb.html?struc=" + encode(struc) + "&traj=" + encode(traj) + "&sel=" + sel_enc + "&rc=" + seeReceptor  + "&cp=" + encode(cp) + "&sh=" + rad_option + "&pd=" + encode(high_pre);
        $(this).attr("href", url_mdsrv);
    });    

});
