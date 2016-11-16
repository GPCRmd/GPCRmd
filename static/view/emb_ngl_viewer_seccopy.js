$(document).ready(function(){
    function encode (sth) {return encodeURIComponent(sth).replace(/%20/g,'+');}
    function inputText(gpcr_pdb_dict){
        var pre_sel = $(".sel_input").val();
        var nums_array = pre_sel.match(/(\d{1,2}\.\d{1,2}(x\d{2,3})?)|(\d{1,2}x\d{2,3})/g);
        if (nums_array != null){
            for (i in nums_array) {
                var gpcr_n = nums_array[i];
                if(gpcr_pdb_dict[gpcr_n] != undefined) {
                    var res_n=gpcr_pdb_dict[gpcr_n];                   
                } else if (bw_dict[gpcr_n] != undefined) {
                    res_n=bw_dict[gpcr_n];                   
                } else if (gpcrdb_dict[gpcr_n] != undefined){
                    res_n=gpcrdb_dict[gpcr_n];                   
                } else {res_n=undefined;}
                pre_sel = pre_sel.replace(gpcr_n, res_n);
                sel=pre_sel
            }
        } else {
            sel = pre_sel ;
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
            //$("iframe").attr("src", url);
            $(id).addClass("active");
            return  2;
        } else {
            var index = $.inArray(newRep,rep);
            if (index > -1) {
                rep.splice(index, 1);
            }
            url = url_orig + ("&sel=" + sel_enc + "&rep=" + encode(rep));
            //$("iframe").attr("src", url);
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
        return (high_pre);
    }

    function obtainURLinfo(gpcr_pdb_dict){
        cp = obtainCompounds();
        high_pre = obtainPredefPositions();
        sel_enc =inputText(gpcr_pdb_dict);
        return [cp, high_pre,sel_enc] 
    }
    var struc = $(".str_file").attr("id");
    var url_orig = "http://localhost:8081/html/embed/embed.html?struc="+encode(struc);
    var seeReceptor = "y" 
    var sel = "";
    var sel_enc = encode(sel);
    $("iframe").attr("src", url_orig + "&rc=" + seeReceptor + "&sel=" + sel_enc);
    $("#receptor").addClass("active");

    var gpcr_pdb_dict = $(".gpcr_pdb").attr("id");

    gpcr_pdb_dict=JSON.parse(gpcr_pdb_dict);
    var bw_dict={};
    var gpcrdb_dict={};
    for (gen_num in gpcr_pdb_dict) {
        res_num=gpcr_pdb_dict[gen_num];
        split=gen_num.split(new RegExp('[\.x]','g'));
        bw = split[0]+"."+ split[1];
        db = split[0]+"x"+ split[2];
        bw_dict[bw]=res_num;
        gpcrdb_dict[db]=res_num;
    }

    var rad_option="sel";
    $( "input[type=radio]" ).on( "click", function(){
        rad_option=$(this).attr("value");
    });

    click_unclick(".high_pd");
    click_unclick(".rep_elements");
    seeReceptor=click_unclick_specialRec("#receptor");
 
    $("#submit").click(function(){
        var results = obtainURLinfo(gpcr_pdb_dict);
        cp = results[0];
        high_pre=results[1];
        sel_enc=results[2];
        url = url_orig + ("&sel=" + sel_enc + "&rc=" + seeReceptor  + "&cp=" + encode(cp) + "&sh=" + rad_option) + "&pd=" + encode(high_pre);
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
        var url_mdsrv = "http://localhost:8081/html/mdsrv_emb.html?struc=" + encode(struc) + "&traj=" + encode(traj) + "&sel=" + sel_enc + "&rc=" + seeReceptor  + "&cp=" + encode(cp) + "&sh=" + rad_option + "&pd=" + encode(high_pre);
        $(this).attr("href", url_mdsrv);
    });    

});
