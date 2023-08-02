


$(document).ready(function(){
    $.fn.exists = function () {
      return this.length !== 0;
    };
    
    $(document).on('click',"[id|=id_form][is_mutated]",function(){
       var pprotform = $(this).parents("[id='pprotform']")
       var anycheckbox= $(pprotform).children("[id|=id_form][is_mutated]")

    });



    $.fn.formrenum = function (new_form_num) {

        //Jquery function for changing labels for all the HTML input elements
        var new_form_num_1 = new_form_num + 1;
        var protnumb = "Protein  #" + new_form_num_1 + " General Infomation";
        var pnumb = "PROT  #" + new_form_num_1;
        var idlabnod = "protform-" + new_form_num;
        $(this).attr('id',idlabnod);
        $(this).find("#protlabnum").text(protnumb);
        $(this).find("#plabnum").text(pnumb);
        $(this).find(":input,:button,[id$='isoform'],[id$='not_uniprotcheck'],[id$='mutations_id']").each(function() {
            var name1 = $(this).attr('name');
            var id1 = $(this).attr('id');
            var name = name1.replace(/^form-[0-9]+-/,'');
            var id = id1.replace(/^id_/,'').replace(/^form-[0-9]+-/,'');
            var namelab="form-"+new_form_num+"-"+name;
            var idlab ="id_form-"+new_form_num+"-"+id;
            $(this).attr({'id':idlab, 'name':namelab});
            //$(this).attr({placeholder':namelab, 'id':idlab, 'name':namelab});
            var searchstr = "label[for='"+id1+"']"
            if (name1.startsWith('form') && name1.endsWith('is_mutated')){
                var tt=$(this);
                tt.prop("checked",false);
                $(this).attr('data-target',"#"+"id_form-"+new_form_num+"-mutations_id"+","+"#mutations_id");
//                $(this).attr('checked', false);
                }; 
            if (name1.startsWith('form') && name1.endsWith('mutations_id')){
                $(this).attr('class',"col-md-12 panel panel-primary collapse");
                console.log($(this).attr('class')+" "+$(this).attr('id')+" "+$(this).attr('name'));
                }; 
            if (name1.startsWith('form') && name1.endsWith('use_isoform')){
                $(this).attr('data-target',"#"+"id_form-"+new_form_num+"-isoform");
                var tt=$(this);
                tt.prop("checked",true);
                console.log(tt);
 //               $(this).attr('checked',true);
                }; 
            if (name1.startsWith('form') && name1.endsWith('isoform')){
                $(this).attr('class',"collapse in");
                }; 
            if ($(searchstr).exists()) {
                $(searchstr).attr('for',idlab);
            };
        });
        return true;
    };
    
    $(document).on('click',"[id='id_add_protein'],[id|=id_form][id$='-add_protein']",function(){
        var form_num = 0;
        var item = $(this).parents("[id|=protform]");
        var item_parent = $(item).parent();
        if ($(item).attr('id') === "protform") {
            $(item).formrenum(form_num);
                    

        } else {
            form_num = Number(item.attr('id').split("-")[1]);
        }
        
        var next_form_num = form_num + 1;
        
        //Clone the current protform
        var newitem = $(item).clone();

        
        $(newitem).formrenum(next_form_num);
        console.log($(newitem).children("[id='id_form-1-mutations_id']").attr('class'));
        $(newitem).children(":first").resetProteinByButton();
        //Insert after last protform
        $(item_parent).append(newitem);
        console.log($(newitem).children("[id='id_form-1-mutations_id']").attr('class'));
        
        $("#id_form-"+next_form_num+"-id_species").species_autocomplete();
        $("#id_form-"+next_form_num+"-del_protein").prop("disabled",false);
        var receptor = $("#id_form-"+next_form_num+"-receptor");
        receptor.prop("disabled",false);

        receptor.prop("checked",false);
        //Button enabled only in the last form
        $(this).prop("disabled",true);
    });
    
    
    
    
    
});
