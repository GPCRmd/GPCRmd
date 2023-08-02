





$(document).ready(function() {
    
    $.fn.set_readonly_color = function () {
        $(this).css('background-color','#FFEFD5');
        return this;
    }
    
    $.fn.set_restore_color = function () {
        $(this).css('background-color','');
        return this;
    }
    
    $("[readonly]").set_readonly_color();
    
    $.fn.isNotUniprotChange = function () {
        var protform = $(this).parents("[id|=protform]");
        var uniprotkbac = protform.find("[id='id_uniprotkbac'],[id|=id_form][id$='-uniprotkbac']");
        var species = protform.find("[id='id_id_species_autocomplete'],[id|=id_form][id$='-id_species_autocomplete']");
        var isoform = protform.find("[id='id_isoform'],[id|=id_form][id$='-isoform']");        
        var sequence = protform.find("[id='id_sequence'],[id|=id_form][id$='-sequence']");
        var name = protform.find("[id='id_name'],[id|=id_form][id$='-name']");
        var aliases = protform.find("[id='id_other_names'],[id|=id_form][id$='-other_names']");
        var getdata = protform.find("[id='id_get_data_upkb'],[id|=id_form][id$='-get_data_upkb']");

        uniprotkbac.set_restore_color();
        species.set_restore_color();
        isoform.set_restore_color();
        name.set_restore_color();
        aliases.set_restore_color();
        sequence.set_restore_color();
     
        $(uniprotkbac).val("").removeAttr('placeholder');
        $(isoform).val("");
       
         
        
        getdata.prop("disabled", $(this).prop('checked'));
        uniprotkbac.prop("disabled", $(this).prop('checked'));
        isoform.prop("disabled", $(this).prop('checked'));

        
        species.prop("readonly", !$(this).prop('checked'));
        name.prop("readonly", !$(this).prop('checked'));
        aliases.prop("readonly", !$(this).prop('checked'));
        sequence.prop("readonly",!$(this).prop('checked'));

        protform.find("[readonly]").set_readonly_color();
    }
    
    $(document).on('change',"[id='id_is_not_uniprot'],[id|=id_form][id$='-is_not_uniprot']",function(){
        $(this).isNotUniprotChange();
        var protform = $(this).parents("[id|=protform]");
        var lock= protform.find("[id='lock'],[id|=id_form][id$='lock']");
        var mnemonics= protform.find("[id='mnemonics'],[id|=id_form][id$='mnemonics']");
        if ($(this).is(":checked")){
        $(lock).hide();
        $(mnemonics).show();
        }else{
        $(lock).show();
        $(mnemonics).hide();
        }



    });
    
    
    
});
