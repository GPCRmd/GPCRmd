
$(document).ready(function(){
    $.fn.exists = function () {
      return this.length !== 0;
    };

       $(document).on('change',"[id|=id_form][id$='-bulk_type'],[id|=id_form][id$='-co_type'],[id|=id_form][id$='-co-is_present'],[id|=id_form][id$='-not-is_present']",function(){
           var self=$(this);
           var cocrist_type=$(this).parents("[id|=molform]").find("[id|=id_form][id$='-co_type']");
           var ret_pubchem =  $(this).parents("[id|=molform]").find("[id|=id_form][id$='retrieve_type_pubchem']");
           var neu_pubchem =  $(this).parents("[id|=molform]").find("[id|=id_form][id$='neutralize_pubchem']");
           var ret_chembl =  $(this).parents("[id|=molform]").find("[id|=id_form][id$='retrieve_type_chembl']");
           var neu_chembl =  $(this).parents("[id|=molform]").find("[id|=id_form][id$='neutralize_chembl']");
           var charge = $(this).parents("[id|=molform]").find("[id|=id_form][id$='net_charge']");
           
           if (typeof $(charge).val() !== 'undefined'){
              if ($(charge).val()==0){
                  $(neu_pubchem).prop('checked',true);
                  $(neu_chembl).prop('checked',true);
              }else{
                  if (($(cocrist_type).val()!=0 && !$(cocrist_type).val()!=1) || $(cocrist_type).is(':disabled')) {
                      console.log("not neutralize   "+$(cocrist_type).val())
                      $(neu_pubchem).prop('checked',false);
                      $(neu_chembl).prop('checked',false);
                  } else {
                      console.log("neutralize type 0 o 1   "+$(cocrist_type).val())
                      $(neu_pubchem).prop('checked',true);
                      $(neu_chembl).prop('checked',true);
                  }
              }
            }

           console.log($(self).attr('id')+self.prop("disabled"));

           if ($(self).is("[id|=id_form][id$='-co-is_present']")) {
              var type=  $(this).parents("[id|=molform]").find("[id|=id_form][id$='-co_type']");
              //type.val(0);
           }else if ($(self).is("[id|=id_form][id$='-not-is_present']")) {
              var type=  $(this).parents("[id|=molform]").find("[id|=id_form][id$='-bulk_type']");
              //type.val(6);
 
           }else if ((($(self).is(':disabled'))&&($(self).is("[id|=id_form][id$='-bulk_type']"))) || (($(self).is(':enabled'))&&($(self).is("[id|=id_form][id$='-co_type']"))))   {
              var type=  $(this).parents("[id|=molform]").find("[id|=id_form][id$='-co_type']");
           }else if ((($(self).is(':enabled'))&&($(self).is("[id|=id_form][id$='-bulk_type']"))) || (($(self).is(':disabled'))&&($(self).is("[id|=id_form][id$='-co_type']")))){
              var type=  $(this).parents("[id|=molform]").find("[id|=id_form][id$='-bulk_type']");
           }
           console.log("print type id"+$(type).attr('id'));
           if ((type.val()==1) || (type.val()==0) || (type.val()==5) || (type.val()==9))  {
           ret_pubchem.val('parent');
           ret_chembl.val('parent');
           } else { 
           ret_pubchem.val('original');
           ret_chembl.val('original');
           }   
           console.log("type value"+$(type).val());
           
       });
});
