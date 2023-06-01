$(document).ready(function() {    
    $("#id_validate_traj").click(function() {
        var self = $(this);
        
        self.prop('disabled',true);
        $.post("./check_trajectories/",{},
            function(data) {
                alert(data);
                
            },
        'text')
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

        })
        
        .always(function(xhr,status,msg) {
            $(self).prop("disabled",false);
            
        });
    
    
    
    
    });
    
    
    
});