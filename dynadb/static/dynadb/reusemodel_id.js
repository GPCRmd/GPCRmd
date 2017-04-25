
$(document).ready(function() {
    $.fn.exists = function () {
        return this.length !== 0;
    };


    $(document).on('click',"[id|=id_form][id$='-is_present']",function(){
        var self=$(this);
        console.log(self);
        var item = $(this).parents("[id='PR']");
        var type1= $(item).find("#Choose_reused_model");
        var type2= $(item).find("#Choose_submission_id");
        if (self.attr('id').startsWith('id_form-1')){
           type2.hide();
           type2.val("")
           type1.show();
           
        } else {
           type1.hide();
           type1.val("")
           type2.show();
        }; 
    });


});

