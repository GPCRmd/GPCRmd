$(document).ready(function(){
        $(document).on('click',"#selection-confirm",function(event) {
            event.preventDefault();
            if(confirm("Do you want to finish the submission? It cannot be further modified afterwards.")) {
                $.post($(this).find('a').attr('href'), {}, function (data) {
                    alert("Congratulations!!! The simulation has been successfully submitted.");
                    window.location.replace(data);
                },'text')
                
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
                
                });
            }
            
        });
    
    
});