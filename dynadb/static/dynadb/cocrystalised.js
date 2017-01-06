
$(document).ready(function(){
    $.fn.exists = function () {
      return this.length !== 0;
    };




    $(document).on('click',"[id|=id_form][id$='-is_present']",function(){
        var self=$(this);
        console.log(self);
        var item = $(this).parents("[id|=molform]");
        var cotype= $(item).find("[id|=id_form][id$='co_type']");
        var nottype= $(item).find("[id|=id_form][id$='bulk_type']");
        var str = cotype.attr('name'); 
        var form_num = str.split("-")[1];
           console.log($(this).attr('type')+" console");
        if (self.attr('id').startsWith('id_form') && self.attr('id').endsWith('-co-is_present')){
           console.log(cotype+"antes cambio propiedades ");
           nottype.attr('name',"form-"+form_num+"-bulk_type");
           nottype.prop('disabled',true);
           nottype.hide();
           cotype.attr('name',"form-"+form_num+"-type");
           cotype.show(500);
           cotype.prop('disabled',false);
          // cotype.val(0);
         //  console.log(type.attr('type')+" 3");
        } else {
           cotype.prop('disabled',true);
           //cotype.val(0);
           cotype.attr('name',"form-"+form_num+"-co_type");
           cotype.hide();
           nottype.show(500);
           //nottype.val(6);
           nottype.attr('name',"form-"+form_num+"-type");
           nottype.prop('disabled',false);
           console.log(cotype.attr('type')+" 3 pipol");
        }; 
    });


});
