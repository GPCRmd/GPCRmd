$(document).ready(function(){
    $(document).on('change',"[id='id_is_mutated'],[id|=id_form][id$='-is_mutated']",function(){
        var protform = $(this).parents("[id|=protform]");
        var align = protform.find("[id='id_alignment'],[id|=id_form][id$='-alignment']");
        var button = protform.find("[id='id_get_mutations'],[id|=id_form][id$='-get_mutations']");
        align.prop('disabled', !this.checked);
        button.prop('disabled', !this.checked);

    });
    
    
    
});