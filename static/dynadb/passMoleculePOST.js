$(document).ready(function(){
    $.fn.exists = function () {
      return this.length !== 0;
    };

                                 //  , == o ; no espacio == y ; separado == uno dentro del otro 
//    $(document).on('click',"[id|='id_pass'][id$='MoleculePOST'],[id|=id_form][id$='-passMoleculePOST']",function(){

      $(document).on('click',"[id^='id_pass'][id$='MoleculePOST'],[id|=id_form][id$='-passMoleculePOST']",function(){
        
        if ( $(this).is("[id='id_passAllMoleculePOST'],[id|=id_form][id$='-passAllMoleculePOST']"))  {
            molforml = $(this).parents("[id='content']");
            var urllist=window.location.href.split("/");
            if (urllist.length ==8){ // http://localhost:8000/dynadb/moleculereuse/100/68/  --> ["http:", "", "localhost:8000", "dynadb", "moleculereuse", "100", "68", ""] 8 elements
                molform=$(molforml).find("[id='pmolform']");
            }else{
                molform=$(molforml).find("[id='MOLECULE_f']");
            }
            console.log($(molform).attr('class')+"  MENSAJE");
            var multi=true;
        } 
        else if  ( $(this).is("[id='id_passMoleculePOST'],[id|=id_form][id$='-passMoleculePOST']") ) {
            var molform = $(this).parents("[id|=molform]");
            console.log($(molform).attr('id')+"  MENSAJE");
            var multi=false;
        }
        var self = $(this);
        console.log($(self).attr('name'));
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
        data["model_id"]=$(document).find("[id='Choose_reused_model']").val();
        console.log(data);
       
        var urllist=window.location.href.split("/");
        console.log(window.location.href);
        if (urllist.length ==8){ //explanation: http://localhost:8000/dynadb/moleculereuse/100/68/  --> ["http:", "", "localhost:8000", "dynadb", "moleculereuse", "100", "68", ""] 8 elements
            var submission_id=urllist[urllist.length-3];
            var model_id=urllist[urllist.length-2];
            var url_post="../../../molecule/"+submission_id+"/";
            var url_success="../../../modelreuse/"+submission_id+"/"+model_id+"/";
        }else {
            var submission_id=urllist[urllist.length-2];
            var url_post="./";
            var url_success="../../model/"+submission_id+"/";
        }
        
        $.post(url_post,
                data, 
                function(data){
                    var urllist=window.location.href.split("/");
                    var submission_id=urllist[urllist.length-2];
                    alert("Congratulations!! "+data);
                    if (multi===true){
                        window.location.replace(url_success);
                    }else{
                        alert("Please, submit other molecules in your system.\n\nIf you submitted all the molecules in it, continue to step 3.");
                    }
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
