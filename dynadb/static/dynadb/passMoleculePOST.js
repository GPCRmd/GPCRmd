$(document).ready(function(){
    $.fn.exists = function () {
      return this.length !== 0;
    };

                                 //  , == o ; no espacio == y ; separado == uno dentro del otro 
//    $(document).on('click',"[id|='id_pass'][id$='MoleculePOST'],[id|=id_form][id$='-passMoleculePOST']",function(){

      $(document).on('click',"[id^='id_pass'][id$='MoleculePOST'],[id|=id_form][id$='-passMoleculePOST']",function(){
        
        if ( $(this).is("[id='id_passAllMoleculePOST'],[id|=id_form][id$='-passAllMoleculePOST']"))  {
            molform = $(this).parents("[id='MOLECULE_f']");
            console.log(molform.attr('class'));
        } 
        else if  ( $(this).is("[id='id_passMoleculePOST'],[id|=id_form][id$='-passMoleculePOST']") ) {
            var molform = $(this).parents("[id|=molform]");
        }
        var self = $(this);
        console.log(self.attr('name'));
        console.log($(molform).attr('class'));
        var data ={};
        var element={};
        $(molform).find(':input').each(function () {
          var self2= $(this)
          console.log($(self2).attr('name'));
          element.name=$(self2).attr('name');
          element.value=$(self2).val();
          data[element.name]=element.value;
          console.log("PIPOL  "+element.value);
}); 
        console.log(data);
        $.post("./submitpost/",
                data, 
                function(data){
                    alert("HOLA");
                },  
                "text" )
        .fail(function(xhr,status,msg) {
           if (xhr.readyState == 4) {
                alert(status.substr(0,1).toUpperCase()+status.substr(1)+":\nStatus: " + xhr.status+". "+msg+".\n"+xhr.responseText);
           }
           else if (xhr.readyState == 0) {
                alert("Connection error");
           }
           else {
                alert("Unknown error");
           }

        })
        
        .always(function(xhr,status,msg) {
            $(self).prop("disabled",false);
            
        });
});


    });
//      var ismutated = protform.find("[id='id_is_mutated'],[id|=id_form][id$='-is_mutated']");
//      $(ismutated).prop("disabled",true);
//      var alignmentval = protform.find("[id='id_alignment'],[id|=id_form][id$='-alignment']").val();
//      var sequenceval = protform.find("[id='id_sequence'],[id|=id_form][id$='-sequence']").val();
//      var msequence = protform.find("[id='id_msequence'],[id|=id_form][id$='-msequence']");
//      protform.find("#mutationtable").resetTableRowFromFields();
//      
//      $.post("../get_mutations/",
//      {
//          alignment:alignmentval,
//          sequence:sequenceval
//      },
//      function(data){
//        i = 0;
//        msequence.prop("readonly",false);
//        msequence.text(data.mutsequence);
//        msequence.prop("readonly",true);
//        msequence.prop("disabled",false);
//        msequence.set_readonly_color();
//        $(data.mutations).each(function(){
//          if (i == 0) {
//            protform.find("#mutationtable").addTableRowFormFields([this.resid,this.from,this.to],false);
//          } else {
//            protform.find("#mutationtable").addTableRowFormFields([this.resid,this.from,this.to]);
//          }
//          i++;
//        });
//      }, 'json')



    //    $(this).prop("disabled",true);
    //    var molform = $(this).parents("[id|=pmolform]");
