
$(document).ready(function(){
    $.fn.exists = function () {
      return this.length !== 0;
    };
    
    $.fn.formrenum = function (new_form_num) {
        //Jquery function for changing labels for all the HTML input elements
        var new_form_num_1 = new_form_num + 1;
        var molnumb = "Small Molecule #" + new_form_num_1 + " General Information";
        var mnumb = "SMOL #" + new_form_num_1;
        var idlabnod = "molform-" + new_form_num;
        $(this).attr('id',idlabnod);
        $(this).find("#molnumb").find('h4').html(molnumb);
        toto=$(this).find("[id|='id_form'][id$='-mlnumb']");
        //console.log("toto"+$(toto).attr('id'));
        $(this).find("[id|='id_form'][id$='mlnumb']").text(mnumb);
    //    $(this).find(":input,:button,[id|=small_molecule],[id|=id_form][id$='_section'],[id|=id_form][id$='-collapse_id'],[id|=id_form][id$='-is_not_in_databases'],[id|=id_form][id$='-nodb'],[id|=id_form][id$='-retrieve_id'],[id|=id_form][id$='-collapse'],[id='id_upload_mol-1'],[id|=id_form][id$='-upload_mol-1'],[id='id_upload_mol-2'],[id|=id_form][id$='-upload_mol-2'],[id='id_stdform'],[id|=id_form][id$='-imagentable'],[id|=id_form][id$='-stdform']").each(function() {
        $(this).find(":input,:button,[id|=id_form][id$='-avail'],[id|=id_form][id$='_section'],[id|=id_form][id$='-collapse_id'],[id|=id_form][id$='-is_not_in_databases'],[id|=id_form][id$='-nodb'],[id|=id_form][id$='-retrieve_id'],[id|=id_form][id$='-collapse'],[id='id_upload_mol-1'],[id|=id_form][id$='-upload_mol-1'],[id='id_upload_mol-2'],[id|=id_form][id$='-upload_mol-2'],[id='id_stdform'],[id|=id_form][id$='-imagentable'],[id|=id_form][id$='-stdform']").each(function() {
            
        //$(this).find(":input,:button,[id|='id_form'][id$='-collapse_id'],[id|='id_form'][id$='-collapse'],[id='id_upload_mol-1'],[id|=id_form][id$='-upload_mol-1'],[id='id_upload_mol-2'],[id|=id_form][id$='-upload_mol-2'],\
//        [id='id_stdform'],[id|=id_form][id$='-stdform']").each(function() {

            var name1 = $(this).attr('name');
            var id1 = $(this).attr('id');
            if (name1 !== "csrfmiddlewaretoken" ) {
                var id1 = $(this).attr('id');
                var id = id1.replace(/^id_/,'').replace(/^form-[0-9]+-/,'');
                var idlab ="id_form-"+new_form_num+"-"+id;
                if ( !$(this).is("div") || id1.startsWith('id_form') && id1.endsWith('-is_collapse') ){
                   var name = name1.replace(/^form-[0-9]+-/,'');
                   var namelab="form-"+new_form_num+"-"+name;
                   $(this).attr({'name':namelab});
                } 
                if ( !$(this).is("div") || id1.startsWith('id_form') && id1.endsWith('-collapse_id') ){
                   var name = name1.replace(/^form-[0-9]+-/,'');
                   var namelab="form-"+new_form_num+"-"+name;
                   $(this).attr({ 'name':namelab});
                } 
                if ( id1.startsWith('id_form') && id1.endsWith('-imagentable') ){
                   //console.log("TTTTppp");
                   $(this).hide();
                }
                $(this).attr('id',idlab );
                var searchstr = "label[for='"+id1+"']"
                if ($(searchstr).exists()) {
                    $(searchstr).attr('for',idlab);
                }
            //console.log(name1); 
            //if (name1.is( "[id|='form'][id$='-collapse']")){
                console.log(id1)
                if ((id1.startsWith('id_form') && id1.endsWith('_section'))) {
                   var name = name1.replace(/^form-[0-9]+-/,'');
                   var namelab="form-"+new_form_num+"-"+name;
                   $(this).attr({'name':namelab});
 
                    console.log('MIRA avail '+id1+' '+name1);
                }
                if ((id1.startsWith('id_form') && id1.endsWith('-avail'))) {
                   var name = name1.replace(/^form-[0-9]+-/,'');
                   var namelab="form-"+new_form_num+"-"+name;
                   $(this).attr({'name':namelab});
            
                    console.log('MIRA avail '+id1+' '+name1);
                }
                if (id1.startsWith('id_form') && id1.endsWith('-is_not_in_databases')){
                    $(this).attr('data-target',"#id_form-"+new_form_num+"-get_mol_info,[id|='id_form-"+new_form_num+"'][id$='nodb']");
                } 
                if (id1.startsWith('molnumb')){
                    $(this).attr('data-target',"[id|='id_form-"+new_form_num+"'][id$='_section']");
                } 
                if (id1.startsWith('id_form') && id1.endsWith('-collapse')){
                    $(this).attr('data-target',"#"+idlab+"_id");
                   var name = name1.replace(/^form-[0-9]+-/,'');
                   var namelab="form-"+new_form_num+"-"+name;
                   $(this).attr({'name':namelab});
                } 
            }
        });
        return true;
    };
    
    $(document).on('click',"[id='id_add_molecule'],[id|=id_form][id$='-add_molecule']",function(){
        var itemp = $(this).parents("[id|=pmolform]");
        var form_num = itemp.children().length - 1; // one item is substracted
        var item = $(this).parents("[id|=molform]");
        //console.log(item.attr('id')+' '+form_num));
        var item_parent = $(item).parent();
        if ($(item).attr('id') === "molform"){
            $(item).formrenum(form_num);
            //console.log('pipol');
                    

        } else {
            form_num = Number(item.attr('id').split("-")[1]);
            //console.log("aun no renum "+ form_num);
        }
        
        var next_form_num = form_num + 1;
        
        //Clone the current molform
        var newitem = $(item).clone();

        var cocrist_type=$(this).parents("[id|=molform]").find("[id|=id_form][id$='-co_type']");
        var ret_pubchem =  $(newitem).find("[id|=id_form][id$='retrieve_type_pubchem']");
        var neu_pubchem = $(newitem).find("[id|=id_form][id$='neutralize_pubchem']");
        var ret_chembl =  $(newitem).find("[id|=id_form][id$='retrieve_type_chembl']");
        var neu_chembl =  $(newitem).find("[id|=id_form][id$='neutralize_chembl']");
        var cotype= $(newitem).find("[id|=id_form][id$='co_type']");
        var nottype= $(newitem).find("[id|=id_form][id$='bulk_type']");
           nottype.val('')   
           cotype.val('')   
        $(newitem).formrenum(next_form_num);
        console.log("VALOR bulk-type "+$(newitem).find("[id|=id_form][id$='bulk_type']").val());
        console.log($(ret_pubchem)+"  "+$(ret_pubchem).val());
//        if ($(newitem).parents("[id|=molform]").find("[id|=id_form][id$='bulk_type']").value ==6 || $(newitem).parents("[id|=molform]").find("[id|=id_form][id$='co_type']").value ==4) {
        if ($(newitem).find("[id|=id_form][id$='bulk_type']").val() ==6) {
           console.log("value 6 o 4");
           $(ret_pubchem).val('original');
           $(ret_chembl).val('original');
        }
        console.log("pipolnew",next_form_num)
        //$(newitem).children(":first").resetMoleculeByButton();
        //Insert after last molform
        $(item_parent).append(newitem);
        
        $("#id_form-"+next_form_num+"-del_molecule").prop("disabled",false);
        //Button enabled only in the last form
        $(this).prop("disabled",true);
        $(newitem).find("[id='id_reset'],[id|=id_form][id$='-reset']").resetMoleculeByButton();
        $(newitem).smol_init_config();
        var checkupload = $(newitem).find("[id='id_checkupload'],[id|=id_form][id$='-checkupload']");
        $(checkupload).hide()
        var molsdf = $(newitem).find("[id='id_molsdf'],[id|=id_form][id$='-molsdf']");
        $(molsdf).val('');
    });
    
       




    $(document).on('click',"[id='id_is_not_in_databases'],[id|=id_form][id$='-is_not_in_databases']",function(){
        var self=$(this);
        self.prop("disabled",true);
        var molform = $(this).parents("[id|=molform]");
        var notdb_remove= $(molform).find("[id|=id_form][id$=-get_mol_info],[id|=id_form][id$='nodb']");
        if ($(self).is(":checked")){
            $(notdb_remove).fadeOut("200").prop('disabled',true);
        }else{
            $(notdb_remove).fadeIn("200").prop("disabled",false);
        }
        self.prop("disabled",false);
    
    
    });   
});
