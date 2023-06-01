$(document).ready(function(){   
    /*$('body').on('iframeSet',function(){
        $('#embed_ngl')[0].contentWindow.$('body').trigger('iframeSetOk');
        var ngl_body=$('#embed_ngl')[0].contentWindow.$('body');
        console.log(ngl_body)
        metadyn_body.on('input',"#slide_input",function(){
            var trajtime=$(this).val();
            console.log("input!!",trajtime)
        })
        //$('#embed_mdsrv')[0].contentWindow.$('body').trigger('createNGL', [ cont_w , cont_w_in , cont_h_num ]);
    });*/

    var metadyn_body=false;
    $('body').on('iframeSetMV',function(){
        $('#embed_metadynview')[0].contentWindow.$('body').trigger('iframeSetOkMV');
        metadyn_body=$('#embed_metadynview')[0].contentWindow.$('body');
        metadyn_body.find("#slide_cont").css("display","none");
        metadyn_body.find(".ctrl_first_line").css("display","none");
        /*console.log(metadyn_body)
        metadyn_body.on('input',"#slide_input",function(){
            var trajtime=$(this).val();
            console.log("input!!",trajtime)
        })
        metadyn_body.on('click',"#slider",function(){
            var trajtime=metadyn_body.find("#slide_input").val();
            console.log("clicked!!",trajtime)
        })*/
        //$('#embed_mdsrv')[0].contentWindow.$('body').trigger('createNGL', [ cont_w , cont_w_in , cont_h_num ]);
    });


    updateNGL=true;
    updateMedaynView=true;
    window.metadynViewChanged = function(rat){
        //MetadynView updates NGL
        if (updateNGL){
            updateMedaynView=false;
            $('#embed_mdsrv')[0].contentWindow.updateFrameToMetadyn(rat,true);
            //console.log("MD updates NGL")            
        } else {
            //console.log("NO -- MD updates NGL")            
            updateNGL=true;
        }
    }

    window.NGLFrameChanged = function(timepoint){
        //NGL updates MetadynView 
        if (updateMedaynView){
            //updateNGL=false;
            var md_slider_input=$('#embed_metadynview')[0].contentWindow.$('body').find("#slide_input");
            md_slider_input.val(timepoint);
            md_slider_input.trigger("change");
            //console.log("NGL updates MD ",timepoint)
        } else {
            updateMedaynView=true;
        }
    }


    window.synconizeNGLMetad=true;
    $("#sync").on("click", ".syncronize_opt:not(.active)" ,function(){
        $(this).addClass("active");
        $(this).siblings(".syncronize_opt").removeClass("active");
        var sync_state=$(this).data("state");
        if (sync_state=="on"){ //Fixed metadynview
            window.synconizeNGLMetad=false;
            metadyn_body.find("#slide_cont").css("display","block");
            metadyn_body.find(".ctrl_first_line").css("display","block");
        } else { //Synced metadynview with NGL
            window.synconizeNGLMetad=true;
            var metadynstop=metadyn_body.find("#stop_ctrl");
            if (!(metadynstop.hasClass("on"))){
                //setInterval(function(){tunnel_obj.find("#loading_tun_style_clus").css("display","none");},3000);
                metadynstop.trigger("click");
                var myStopVar = setInterval(checkchange, 1000);
                function checkchange(){
                    //console.log("check change")
                    if (metadyn_body.find("#stop_ctrl").hasClass("on")){
                        metadyn_body.find("#stop_ctrl").find(".ctrl_first_line").css("display","none");
                        metadyn_body.find("#stop_ctrl").find("#slide_cont").css("display","none");
                    }
                }
            } else {
                metadynstop.trigger("click");
                metadyn_body.find(".ctrl_first_line").css("display","none");
                metadyn_body.find("#slide_cont").css("display","none");
            }
            $('#embed_mdsrv')[0].contentWindow.updateMetadyntoFrame();
        }
    });
    $("#metadyn_finalFES").on("click" ,function(){
        if (window.synconizeNGLMetad){
            //Update NGL
            var stoptraj=false;
            if ($("#syncronize_opt_off").hasClass("active")){
                stoptraj=true;
            }
            $('#embed_mdsrv')[0].contentWindow.updateFrameToMetadyn(1,stoptraj);
        } else {
            //Update MetadynView
            var md_slider_input=$('#embed_metadynview')[0].contentWindow.$('body').find("#slide_input");
            md_slider_input.val("100%");
            md_slider_input.trigger("change");
        }
    })
   





    
})
