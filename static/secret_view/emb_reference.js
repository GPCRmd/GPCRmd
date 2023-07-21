$(document).ready(function(){   
    
    $('body').on('iframeSetRef',function(){
        $('#embed_struct')[0].contentWindow.$('body').trigger('iframeSetRefOk');
        //width
        var cont_w_max=$("#info").css("width");
        var cont_w_max_num=Number(cont_w_max.match(/^\d*/g)[0]);
        var cont_w_num=cont_w_max_num - 2;
        var cont_w = cont_w_num.toString() + "px";
        var cont_w_in= (cont_w_num - 2).toString() + "px";
        //height
        var screen_h=screen.height;
        var cont_h_num=Math.round(screen_h*0.60);
        var cont_h=(cont_h_num).toString() +"px";
        var cont_h_iframe=(cont_h_num+30).toString() +"px";
        console.log("width: "+cont_w_max_num)
        console.log("height: "+cont_h)
        $("#IframeCont").css({"border" : "1px solid #F5F5F5" , "max-width": cont_w_max , "height":cont_h});
        $("#embed_struct").css("width",cont_w).attr("width",cont_w).attr("height",cont_h_iframe);
        //$("#loading").html("");
        $('#embed_struct')[0].contentWindow.$('body').trigger('createNGLRef', [ cont_w , cont_w_in , cont_h_num ]);
    });
    
})
