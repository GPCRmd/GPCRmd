$(document).ready(function(){
    $(document).on('click',"[id='id_del_protein'],[id|=id_form][id$='-del_protein']",function(){
        var self = $(this);
        var protform = $(this).parents("[id|=protform]");
        var pprotform = $(protform).parent();
        var addbutton = $(pprotform).children(":last-child").find("[id='id_add_protein'],[id|=id_form][id$='-add_protein']");
        addbutton.prop("disabled",true);
        $(this).prop("disabled",true);
        
        $.post("./delete/",
        {
            protein_num:($(protform).index()+1)
        },
        function(data){
            
            
            for (i = $(protform).index() + 1; i < $(pprotform).children().length; i++) {
                $(pprotform).children(":nth-child("+(i+1)+")").formrenum(i-1);
            }
            $(protform).remove();
            addbutton = $(pprotform).children(":last-child").find("[id='id_add_protein'],[id|=id_form][id$='-add_protein']");


          
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

