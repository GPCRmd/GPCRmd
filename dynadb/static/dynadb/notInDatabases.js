
$(document).ready(function() {
    
    $.fn.set_readonly_color = function () {
        $(this).css('background-color','#FFEFD5');
        return this;
    };
    
    $.fn.set_restore_color = function () {
        $(this).css('background-color','');
        return this;
    };
    
    $("[readonly]").set_readonly_color();
    
    $.fn.OnChangeIsNotInDatabases = function () {
        var molform = $(this).parents("[id|=molform]");
        var is_not_in_databases = $(molform).find("[id='id_is_not_in_databases'],[id|=id_form][id$='-is_not_in_databases']");
        var get_mol_info = $(molform).find("[id='id_get_mol_info'],[id|=id_form][id$='-get_mol_info']");
        var name = $(molform).find("[id='id_name'],[id|=id_form][id$='-name']");
        var iupac_name = $(molform).find("[id='id_iupac_name'],[id|=id_form][id$='-iupac_name']");
        var aliases = $(molform).find("[id='id_other_names'],[id|=id_form][id$='-other_names']");
        var pubchemcid = $(molform).find("[id='id_pubchem_cid'],[id|=id_form][id$='-pubchem_cid']");
        var chemblid = $(molform).find("[id='id_chemblid'],[id|=id_form][id$='-chemblid']");
        var updatepubchem = $(molform).find("[id='id_update_from_pubchem'],[id|=id_form][id$='-update_from_pubchem']");
        var updatechembl = $(molform).find("[id='id_update_from_chembl'],[id|=id_form][id$='-update_from_chembl']");
        var neutralize = $(molform).find("[id^='id_neutralize'],[id|=id_form][id*='-neutralize']");
        var retrieve_type = $(molform).find("[id^='id_retrieve_type'],[id|=id_form][id*='-retrieve_type']");
        var search_by = $(molform).find("[id^='id_search_by'],[id|=id_form][id*='-search_by']");
        var similarity = $(molform).find("[id^='id_search_by'],[id|=id_form][id*='-search_by']");
        var lock2=  $(molform).find("[id^='id_lock2'],[id|=id_form][id*='-lock2']");
        var lock3=  $(molform).find("[id^='id_lock3'],[id|=id_form][id*='-lock3']");
       
        //if($(this).prop('checked')) {
        if($(this).is(':checked')) {
            name.set_restore_color();
            iupac_name.set_restore_color();
            aliases.set_restore_color();
            $(lock2).hide();
            $(lock3).show();
        }else{
            $(lock2).show();
            $(lock3).hide();
        }
        
        name.prop("readonly",!$(this).prop('checked'));
        iupac_name.prop("readonly",!$(this).prop('checked'));
        aliases.prop("readonly",!$(this).prop('checked'));
        
        pubchemcid.prop("disabled",$(this).prop('checked'));
        chemblid.prop("disabled",$(this).prop('checked'));
        updatepubchem.prop("disabled",$(this).prop('checked'));
        updatechembl.prop("disabled",$(this).prop('checked'));
        
        neutralize.prop("disabled",$(this).prop('checked'));
        retrieve_type.prop("disabled",$(this).prop('checked'));
        search_by.prop("disabled",$(this).prop('checked'));
        
        get_mol_info.prop("disabled",$(this).prop('checked'));

        molform.find("[readonly]").set_readonly_color();
    }
    
    $(document).on('change',"[id='id_is_not_in_databases'],[id|=id_form][id$='-is_not_in_databases']",function(){
        $(this).OnChangeIsNotInDatabases();

    });
    
    
    
});
