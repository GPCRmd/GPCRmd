$(document).ready(function(){
    $(document).on('click',"[id='id_reset'],[id|=id_form][id$='-reset']", function() {
        var protform = $(this).parents("[id|=protform]");
        var uniprotkbac = protform.find("[id='id_uniprotkbac'],[id|=id_form][id$='-uniprotkbac']");
        var isoform = protform.find("[id='id_isoform'],[id|=id_form][id$='-isoform']");
        var notuniprot = protform.find("[id='id_is_not_uniprot'],[id|=id_form][id$='-is_not_uniprot']");
        var msequence = protform.find("[id='id_msequence'],[id|=id_form][id$='-msequence']");
        var getdata = protform.find("[id='id_get_data_upkb'],[id|=id_form][id$='-get_data_upkb']");
        
        uniprotkbac.prop("readonly",false);
        uniprotkbac.set_restore_color();
        isoform.prop("readonly",false);
        isoform.set_restore_color();
        notuniprot.prop("disabled",false);
        getdata.prop("disabled",false);
        protform.find("#mutationtable").resetTableRowFromFields();
        msequence.prop("disabled",true);
        msequence.prop("readonly",false);
        msequence.set_restore_color();
        
        
        
        $(protform).find(":input:not(:submit,:button)").each(function(){
            if ($(this).prop("readonly")) {
                
                $(this).prop("readonly",false);
                if ($(this).is("textarea")) {
                    $(this).text("");
                } else {
                    $(this).val("");
                }
                $(this).prop("readonly",true);
                
            } else {
                if ($(this).is("textarea")) {
                    $(this).text("");
                } else {
                    $(this).val("");
                }
            }
            
        });

    });
});