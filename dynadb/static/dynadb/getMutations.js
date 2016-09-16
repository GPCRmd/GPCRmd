$(document).ready(function(){
    $.fn.exists = function () {
      return this.length !== 0;
    };
    $.fn.resetTableRowFromFields = function() {
      var tr = $(this).find("tr:last-of-type");
      var tr2 = tr.clone();
      $(this).find("tr").each(function () {
        if (!$(this).find("th").exists()) {
          $(this).remove();
        }
          
      });
      tr = $(this).find("tr:last-of-type");

      $(tr2).find("td").each(function () {
          $(this).find(':input').each(function () {
              var name1 = $(this).attr('name');
              var id1 = this.id;
              var namelab1 = name1.replace(/-[0-9]+$/,"-0");
              var idlab1 = id1.replace(/-[0-9]$/,"-0");
              $(this).attr({'placeholder':idlab1,'id':idlab1, 'name':namelab1});
              $(this).prop("readonly",false);
              $(this).val('');
              $(this).prop("disabled",true);
              $(this).set_restore_color();
              
          });
      
      });
      tr2.insertAfter(tr);

      
  
    };
    $.fn.addTableRowFormFields = function(values,create_row=true) {
      var tr = $(this).find("tr:last-of-type");
      var tr2 = tr.clone();

      if ($(tr2).find("td :input").length != values.length) {
         alert('Error on .addTableRowFromFields: values array argument does not match the number of columns in <table>.');
         return false;
      };
      i = 0;
      $(tr2).find("td").each(function () {
          $(this).find(':input').each(function () {
              var name1 = $(this).attr('name');
              var id1 = this.id;
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
              };
              if (!create_row) {
                rowid--;
              };
              var namelab1 = name1.replace(/-[0-9]+$/,"-"+rowid);
              var idlab1 = id1.replace(/-[0-9]$/,"-"+rowid);
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
      };
      
  
    };
  
    $(document).on('change',"[id='id_alignment'],[id|=id_form][id$='-alignment'],\
    [id='id_sequence'],[id|=id_form][id$='-sequence'],[id='id_msequence'],[id|=id_form][id$='-msequence']",
                   function(){
        var protform = $(this).parents("[id|=protform]");
        protform.find("#mutationtable").resetTableRowFromFields()

    });
    
    
    $(document).on('click',"[id='id_get_mutations'],[id|=id_form][id$='-get_mutations']",function(){
        var protform = $(this).parents("[id|=protform]");
        var alignmentval = protform.find("[id='id_alignment'],[id|=id_form][id$='-alignment']").val();
        var sequenceval = protform.find("[id='id_sequence'],[id|=id_form][id$='-sequence']").val();
        var msequence = protform.find("[id='id_msequence'],[id|=id_form][id$='-msequence']");
        protform.find("#mutationtable").resetTableRowFromFields();
        
        $.post("get_mutations/",
        {
            alignment:alignmentval,
            sequence:sequenceval
        },
        function(data){
          i = 0;
          msequence.prop("readonly",false);
          msequence.val(data.mutsequence);
          msequence.prop("readonly",true);
          msequence.prop("disabled",false);
          msequence.set_readonly_color();
          $(data.mutations).each(function(){
            if (i == 0) {
              protform.find("#mutationtable").addTableRowFormFields([this.resid,this.from,this.to],false);
            } else {
              protform.find("#mutationtable").addTableRowFormFields([this.resid,this.from,this.to]);
            };
            i++;
          });
        }, 'json')

        .fail(function(xhr,status,msg) {
           alert(status.substr(0,1).toUpperCase()+status.substr(1)+":\nStatus: " + xhr.status+". "+msg+".\n"+xhr.responseText);

        })

    });
});