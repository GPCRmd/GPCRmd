
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
    
    
    
    $(document).on('change',"[id='id_is_not_in_databases'],[id|=id_form][id$='-is_not_in_databases']",function(){
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
        
        if($(this).prop('checked')) {
            name.set_restore_color();
            iupac_name.set_restore_color();
            aliases.set_restore_color();
        }
        
        name.prop("readonly",!$(this).prop('checked'));
        iupac_name.prop("readonly",!$(this).prop('checked'));
        aliases.prop("readonly",!$(this).prop('checked'));
        
        pubchemcid.prop("disabled",$(this).prop('checked'));
        chemblid.prop("disabled",$(this).prop('checked'));
        updatepubchem.prop("disabled",$(this).prop('checked'));
        updatechembl.prop("disabled",$(this).prop('checked'));
        
        
        get_mol_info.prop("disabled",$(this).prop('checked'));

        $("[readonly]").set_readonly_color();

    });
    
    
    
});