$(document).ready(function(){
    $.fn.exists = function () {
      return this.length !== 0;
    };

//   $.fn.protein_init_config = function(){
//      $(document).find("[id|=protform]").each(function(){
//          var protform=$(this)
//          var is_mutated= $(protform).find("[id='id_is_mutated'],[id|=id_form][id$='is_mutated']");
//          var mutations = $(protform).find("[id='id_mutations_id'],[id|=id_form][id$='mutations_id']");
//          var use_isoform= $(protform).find("[id='id_use_isoform'],[id|=id_form][id$='use_isoform']");
//          if ($(is_mutated).is(":checked")){
//              $(mutations).show();
//              console.log("f1");
//              $(mutations).find('textarea,:button').each(function(){
//                  $(this).prop('disabled',false);
//              console.log("f2");
//              });
//          }else{
//              $(mutations).hide();
//              console.log("f1");
//              $(mutations).find('textarea,:button').each(function(){
//                  $(this).prop('disabled',true);
//              console.log("f2");
//              });
//         
//          };
//  
//          if ($(use_isoform).is(":checked")){
//              console.log("f1");
//              $(protform).find("[id|=id_form][id$='isoform']").show().prop('disabled',false);
//              console.log("f2");
//          }else{
//              $(protform).find("[id|=id_form][id$='isoform']").hide().prop('disabled',true);
//          };
//        
//      });
//  };

    $.fn.clean_mutations = function() {
        var protform = $(this).parents("[id|=protform]");
        var msequence = protform.find("[id='id_msequence'],[id|=id_form][id$='-msequence']");
        var mutationtable = protform.find("[id|='id_form'][id$='mutationtable'],[id='mutationtable']");
        mutationtable.resetTableRowFromFields();
        msequence.prop("readonly",false);
        msequence.set_restore_color();
    };
    
    $.fn.resetTableRowFromFields = function() {
      var tr = $(this).find("tr:last-of-type");
      var tr_parent = $(tr).parent();
      var tr2 = tr.clone();
      $(this).find("tr").each(function () {
        if (!$(this).find("th").exists()) {
          $(this).remove();
        }
          
      });

      $(tr2).find("td").each(function () {
          $(this).find(':input').each(function () {
              var name1 = $(this).attr('name');
              var id1 = $(this).attr('id');
              var namelab1 = name1.replace(/-[0-9]+$/,"-0");
              //var namelab1 = name1.replace(/-[0-9]+$/,"-0");
              var idlab1 = id1.replace(/-[0-9]$/,"-0");
              $(this).attr({'placeholder':namelab1,'id':idlab1, 'name':namelab1});
              $(this).prop("readonly",false);
              $(this).val('');
              $(this).prop("disabled",true);
              $(this).set_restore_color();
          });
      });
      tr_parent.append(tr2);
    };
    $.fn.addTableRowFormFields = function(values,create_row=true) {
      var tr = $(this).find("tr:last-of-type");
      var tr2 = tr.clone();

      if ($(tr2).find("td :input").length != values.length) {
         alert('Error on .addTableRowFromFields: values array argument does not match the number of columns in <table>.');
         return false;
      }
      i = 0;
      $(tr2).find("td").each(function () {
          $(this).find(':input').each(function () {
              var name1 = $(this).attr('name');
              var id1 = $(this).attr('id');
              var matches = /-([0-9]+)$/.exec(id1)
              if (matches == null) {
               var id = id1 ;
               var name = name1;
               id1 = id +'-0'; 
               name1 = name1 +'-0';
               tr.find('#'+id).attr({'id':id1,'name':name1,'placeholder':id1});
               var rowid = 1;
              } else {
               var rowid = Number(matches[1]) + 1;
              }
              if (!create_row) {
                rowid--;
              }
              var namelab1 = name1.replace(/-[0-9]+$/,"-"+rowid);
              var idlab1 = id1.replace(/-[0-9]+$/,"-"+rowid);
              $(this).attr({'placeholder':idlab1,'id':idlab1, 'name':namelab1});
              $(this).val(values[i]);
              $(this).prop("disabled",false);
              $(this).prop("readonly",true);
              $(this).set_readonly_color();
              i++;
          });
      
      });
      if (create_row) {
        tr2.insertAfter(tr);
      } else {
        tr.replaceWith(tr2)
      }
      
  
    };
  
    $(document).on('change',"[id='id_alignment'],[id|=id_form][id$='-alignment'],\
    [id='id_sequence'],[id|=id_form][id$='-sequence'],[id='id_msequence'],[id|=id_form][id$='-msequence']",
    function(){
        $(this).clean_mutations();
    });
    
    $(document).on('click',"[id='id_clean_mutations'],[id|=id_form][id$='-clean_mutations']",
    function(){
        $(this).clean_mutations();
    });
    
    
    $(document).on('click',"[id='id_get_mutations'],[id|=id_form][id$='-get_mutations']",function(){
        var self = $(this);
        $(this).prop("disabled",true);
        var protform = $(this).parents("[id|=protform]");
        var ismutated = protform.find("[id='id_is_mutated'],[id|=id_form][id$='-is_mutated']");
        $(ismutated).prop("disabled",true);
        var alignmentval = protform.find("[id='id_alignment'],[id|=id_form][id$='-alignment']").val();
        var sequenceval = protform.find("[id='id_sequence'],[id|=id_form][id$='-sequence']").val();
        var msequence = protform.find("[id='id_msequence'],[id|=id_form][id$='-msequence']");
        var mutationtable = protform.find("[id|='id_form'][id$='mutationtable'],[id='mutationtable']");
        mutationtable.resetTableRowFromFields();
        
        $.post("../get_mutations/",
        {
            alignment:alignmentval,
            sequence:sequenceval
        },
        function(data){
          i = 0;
          msequence.prop("readonly",false);
          msequence.text(data.mutsequence);
          msequence.prop("readonly",true);
          msequence.prop("disabled",false);
          msequence.set_readonly_color();
          $(data.mutations).each(function(){
            if (i == 0) {
              mutationtable.addTableRowFormFields([this.resid,this.from,this.to],false);
            } else {
              mutationtable.addTableRowFormFields([this.resid,this.from,this.to]);
            }
            i++;
          });
        }, 'json')

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
            $(ismutated).prop("disabled",false);
        });
    });


// Added by Juanma!!!


//     $(document).on('click',"[id='id_is_mutated'],[id|=id_form][id$='-is_mutated']",function(){

//         if ($(document).find("[id|=id_form][id$='is_mutated']input:checked").length > 0){
//             $("#mutations_id").show();
//         } else {
//             $("#mutations_id").hide();
//         }
//         var self=$(this);
//         self.prop('disabled',true);
//         var mut_block=$(this).parents("[id|=protform]").find("[id|=id_form][id$='mutations_id']");
//         if ($(this).is(':checked')){
//             $(mut_block).show();  
//         }else{
//             $(mut_block).hide();  
//             $(mut_block).css("display","none");  
//         }
//         self.prop('disabled',false);
//     });

//     $(document).on('click',"[id='id_use_isoform'],[id|=id_form][id$='-use_isoform']",function(){

//         var self=$(this);
//         self.prop('disabled',true);
//         var mut_iso=$(this).parents("[id|=protform]").find("[id|=id_form][id$='-isoform']");
//         if ($(this).is(':checked')){
//             $(mut_iso).show();  
//         }else{
//             $(mut_iso).hide();  
//            // $(mut_iso).css("display","none");  
//         }
//         self.prop('disabled',false);
//     });



});


