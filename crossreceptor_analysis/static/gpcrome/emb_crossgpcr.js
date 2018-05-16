$(document).ready(function(){   

    $('body').on('iframeSetRef',function(){
        $('#ngl_iframe')[0].contentWindow.$('body').trigger('iframeSetRefOk');
        $('#ngl_iframe')[0].contentWindow.$('body').trigger('createNGLRef');
    });
    
})
