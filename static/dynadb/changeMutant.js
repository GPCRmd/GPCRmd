$(document).ready(function(){
    $(document).on('change',"[id='id_is_mutated'],[id|=id_form][id$='-is_mutated']",function(){
        var protform = $(this).parents("[id|=protform]");
        var msequence = protform.find("[id='id_msequence'],[id|=id_form][id$='-msequence']");
        var align = protform.find("[id='id_alignment'],[id|=id_form][id$='-alignment']");
        var getbutton = protform.find("[id='id_get_mutations'],[id|=id_form][id$='-get_mutations']");
        var algbutton = protform.find("[id='id_get_align'],[id|=id_form][id$='-get_align']");
        var clbutton = protform.find("[id='id_clean_mutations'],[id|=id_form][id$='-clean_mutations']");
        align.prop('disabled', !this.checked);
        msequence.prop('disabled', !this.checked);
        getbutton.prop('disabled', !this.checked);
        algbutton.prop('disabled', !this.checked);
        clbutton.prop('disabled', !this.checked);

    });
    
    
    
});