$(document).ready(function(){




     $.fn.resetProteinByButton = function () {
        var protform = $(this).parents("[id|=protform]");
        var useisoform = protform.find("[id='id_use_isoform'],[id|=id_form][id$='use_isoform']");
        var mutations = protform.find("[id='id_mutations_id'],[id|=id_form][id$='mutations_id']");
        var uniprotkbac = protform.find("[id='id_uniprotkbac'],[id|=id_form][id$='-uniprotkbac']");
        var isoform = protform.find("[id='id_isoform'],[id|=id_form][id$='-isoform']");
        var notuniprot = protform.find("[id='id_is_not_uniprot'],[id|=id_form][id$='-is_not_uniprot']");
        var alignment = protform.find("[id='id_alignment'],[id|=id_form][id$='-alignment']");
        var msequence = protform.find("[id='id_msequence'],[id|=id_form][id$='-msequence']");
        var getdata = protform.find("[id='id_get_data_upkb'],[id|=id_form][id$='-get_data_upkb']");
        var is_mutated= protform.find("[id='id_is_mutated'],[id|=id_form][id$='is_mutated']");
               
        uniprotkbac.prop("readonly",false);
        uniprotkbac.set_restore_color();
        isoform.prop("readonly",false);
        isoform.set_restore_color();
        notuniprot.prop("disabled",false);
        getdata.prop("disabled",false);
        protform.find("#mutationtable").resetTableRowFromFields();
        msequence.prop("disabled",false);
        alignment.prop("disabled",false);
        msequence.prop("readonly",false);
        msequence.set_restore_color();
        
        
        
        $(protform).find(":input:not(:submit,:button)[type!='checkbox'][type!='radio']").each(function(){
            if ($(this).prop("readonly")) {
                
                $(this).prop("readonly",false);
                $(this).val("");
                $(this).prop("readonly",true);
                
            } else {

                $(this).val("");

            }
            
        });
        $(protform).find(":input[type='checkbox'][id!='id_receptor'][id!='id_form-0-receptor'],:input[type='radio']").each(function(){
            $(this).prop("checked",false);
        });
//        useisoform.prop("checked",true);
        mutations.attr("class",'col-md-12 panel panel-primary '); 
        alignment.prop("disabled",true);
        msequence.prop("disabled",true);
        notuniprot.isNotUniprotChange();
        return true;
    }
    $(document).on('click',"[id='id_reset'],[id|=id_form][id$='-reset']", function(){
        $(this).resetProteinByButton();
    });



});
