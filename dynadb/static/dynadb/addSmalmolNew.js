
var l = 0;

$(document).ready(function(){
    $.fn.exists = function () {
      return this.length !== 0;
    };
    
    $.fn.formrenum = function (new_form_num) {
        //Jquery function for changing labels for all the HTML input elements
        var new_form_num_1 = new_form_num + 1;
        var molnumb = "SMALL MOLECULE #" + new_form_num_1;
        var idlabnod = "molform-" + new_form_num;
        $(this).attr('id',idlabnod);
        $(this).find("#molnumb").text(molnumb);
        $(this).find(":input,:button,[id='id_upload_mol'],[id|=id_form][id$='-upload_mol'],\
        [id='id_stdform'],[id|=id_form][id$='-stdform']").each(function() {
            
            var name1 = $(this).attr('name');
            if (name1 !== "csrfmiddlewaretoken") {
                var id1 = $(this).attr('id');
                var name = name1.replace(/^form-[0-9]+-/,'');
                var id = id1.replace(/^id_/,'').replace(/^form-[0-9]+-/,'');
                var namelab="form-"+new_form_num+"-"+name;
                var idlab ="id_form-"+new_form_num+"-"+id;
                $(this).attr({'placeholder':namelab, 'id':idlab, 'name':namelab});
                var searchstr = "label[for='"+id1+"']"
                if ($(searchstr).exists()) {
                    $(searchstr).attr('for',idlab);
                }
            }
        });
        return true;
    };
    
    $(document).on('click',"[id='id_add_molecule'],[id|=id_form][id$='-add_molecule']",function(){
        var form_num = 0;
        var item = $(this).parents("[id|=molform]");
        var item_parent = $(item).parent();

        if ($(item).attr('id') === "molform") {
            $(item).formrenum(form_num);
                    

        } else {
            form_num = Number(item.attr('id').split("-")[1]);
        }
        
        var next_form_num = form_num + 1;
        
        //Clone the current molform
        var newitem = $(item).clone();

        
        $(newitem).formrenum(next_form_num);
        $(newitem).children(":first").resetMoleculeByButton();
        //Insert after last molform
        $(item_parent).append(newitem);
        
        $("#id_form-"+next_form_num+"-del_molecule").prop("disabled",false);
        //Button enabled only in the last form
        $(this).prop("disabled",true);
    });
    
    
    
    
    
});
