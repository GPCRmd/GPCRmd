$(document).ready(function(){
    $(document).on('click',"[id='id_del_molecule'],[id|=id_form][id$='-del_molecule']",function(){
        var self = $(this);
        var molform = $(this).parents("[id|=molform]");
        var pmolform = $(molform).parent();
        var addbutton = $(pmolform).children(":last-child").find("[id='id_add_molecule'],[id|=id_form][id$='-add_molecule']");
        addbutton.prop("disabled",true);
        $(this).prop("disabled",true);
        
        $.post("./delete/",
        {
            molecule_num:($(molform).index()+1)
        },
        function(data){
            
            
            for (i = $(molform).index() + 1; i < $(pmolform).children().length; i++) {
                $(pmolform).children(":nth-child("+(i+1)+")").formrenum(i-1);
            }
            $(molform).remove();
            addbutton = $(pmolform).children(":last-child").find("[id='id_add_molecule'],[id|=id_form][id$='-add_molecule']");


          
        })

        .fail(function(xhr,status,msg) {
           if (xhr.readyState == 4) {
                alert(status.substr(0,1).toUpperCase()+status.substr(1)+":\nStatus: " + xhr.status+". "+msg+".\n"+xhr.responseText);
           }
           else if (xhr.readyState == 0) {
                alert("Connection error");
           }
           else {
                alert("Unknown error");
           }
           $(self).prop("disabled",false);

        })
        
        .always(function(xhr,status,msg) {
            $(addbutton).prop("disabled",false);
        
        });
        
    });
    
});

