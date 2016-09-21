$(document).ready(function(){
    $(document).on('click',"[id='id_del_protein'],[id|=id_form][id$='-del_protein']",function(){
        var protform = $(this).parents("[id|=protform]").remove();
       
    });
    
});

