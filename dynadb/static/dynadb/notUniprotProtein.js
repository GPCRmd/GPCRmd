





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
    
    
    
    $(document).on('change',"[id='id_is_not_uniprot'],[id|=id_form][id$='-is_not_uniprot']",function(){
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
        
        getdata.prop("disabled", this.checked);
        uniprotkbac.prop("disabled", this.checked);
        species.prop("disabled", !this.checked);
        isoform.prop("disabled", this.checked);
        name.prop("disabled", !this.checked);
        aliases.prop("disabled", !this.checked);
        sequence.prop("disabled",!this.checked);
        
        species.prop("readonly", !this.checked);
        name.prop("readonly", !this.checked);
        aliases.prop("readonly", !this.checked);
        sequence.prop("readonly",!this.checked);

        $("[readonly]").set_readonly_color();

    });
    
    
    
});