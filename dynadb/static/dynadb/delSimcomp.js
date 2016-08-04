
function delSimcomp() {
	"use strict";
        var parentdin =  document.getElementById("pdynform");
        
        console.log("eeeooo",parentdin.id);
        $(parentdin).find("tbody[id^='pElement1']").each(function(){
        	console.log("eeeo",parentdin.id);
     		if($(this)==null){
        		console.log("No hay nada en this")
        	}
		else{console.log("hay este id", $(this).attr("id"));
		};
        	console.log("eeeooo",$(this).attr("id"));
        	var itemdel = $(this).children(":last");
        	console.log("el itemdel.id es "+itemdel.attr("id"));
       		var match = itemdel.attr("id").search(/Element1_/);
        	var match1 = itemdel.attr("id").search(/Element1_0/);
        	console.log("resultado de match "+ match +" resultado de match1 "+ match1);
        	if(match == 0) {
            		if(match1 == -1) {
                		itemdel.remove();
        			console.log("Como match= "+ match +"y match1= "+ match1 + "eliminamos elemento");
            		}	
        	}	
            
	});
}
