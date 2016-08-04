var s;
s = 0;

function addSimcomp() {
console.log("Valor inicial de s = " + s)
	"use strict";
	s += 1;
        var parentdyn =  document.getElementById("pdynform");
	var ss = s - 1;	

        // the first time the function works, it modifies some html attributes of the first Simulation Element by adding indexes to the preexistent ones, in order to differently label different Components in the Simulation form. Additional Components in the form would have the same text label but different indexes.   
	if (s==1) {
        $(parentdyn).find("tr[id|='Element1']").each(function(){
	       var idlabnod1= "Element1_0";
               console.log("longitud seleccion Element1", $(this).length);
	       $(this).attr({'id':idlabnod1});
               //Jquery function for changing labels for all the HTML input elements. Note it is possible the form has previously been modified by addDynamics.js/delDynamics.js and the original labels would be previously modified by adding the "form-l" prefix.
	       $($(this)).find(':input').each(function() {
	       var name1 = $(this).attr('name')+"-"; //trick in case no '-' exists in name as'form-"l"' prefix is not added
	       var name = $(this).attr('name');
	       var spname1= name1.split("-");
	       var beg_nam1 = name1.search(/form-/);
	     		if (beg_nam1==0){ //form- is found in the name of the HTML attributes
	     		var spname1b= name1.split("-").slice(0,2).join("-");
	     		var spname1l= name1.split("-").slice(2,spname1.length-1).join("");
	     		var namelab1=spname1b+"-formc-"+ss+"-"+spname1l;
	     		var idlab1="id-"+spname1b+"-formc-"+ss+"-"+spname1l;
	     		var forlab1="id-"+spname1b+"-formc-"+ss+"-"+spname1l;
	     		} else{
	     		var namelab1="formc-"+ss+"-"+name;
	     		var idlab1="id-formc-"+ss+"-"+name;
	     		var forlab1="id_formc-"+ss+"-"+name;
	     		}
		$(this).attr({'placeholder':namelab1, 'id':idlab1, 'for':idlab1, 'name':namelab1});
		});
	});
	s=2;
	ss=1;
        }

        // Afterwards the DOM Node containing the protein fields is replicated and the corresponding labels are modifyied by increasing the index. Note that indexes for the Component #1 is 0 (s=1, ss=0).


        var toto= $(parentdyn).find("tr[id^='Element1_']").length
       	$(parentdyn).find("tr[id|='Element1_0']").each(function(){
                console.log("eoeo");
        	var itemparent =$(this).parent();
        	var itemparentid = itemparent.attr("id");
                var nsiblings=itemparent.children().length;
                var sibl=itemparent.children();
                for (i = 0; i < nsiblings; i++) { 
                console.log("sibling i = ", i, " ", sibl.eq(i).attr("id"));
                }
        	console.log("NOmbre id del Node " , $(this).attr("id") ," siblings " , nsiblings );
        	var itemlast = itemparent.children(":last");
        	var itemfirst = itemparent.children(":first");
                console.log("longitud seleccion Element1", itemparent.attr("id"),  itemparent.children().length);
                console.log("itemlastid", itemlast.attr("id"));
             	var itemlastl = itemlast.attr("id").split("_")[1];
        	var sss=Number(itemlastl);
           	ss=sss+1;
        	s=ss+1;
        	var	t = itemfirst.clone(true);
        	console.log("itemlastl " , itemlastl ," ss " , ss , " s " +s);
        	var	idlabnod = "Element1_" + ss;
        	t.attr({"id":idlabnod}) ;
//                id_t = idlabnod;
                t.appendTo(itemparent);
                var idnew=itemparent.children(":last").attr("id");
        	console.log("id del clone " + idnew + "  ss= "+ ss);
        	var ttt = t;
        	$(ttt).find(':input').each(function() {
                        var repl="formc-"+parseInt(ss)+"-"; 
        		var name1 = $(this).attr('name');
        		var name= name1.replace('formc-0-','');
        		var namelab=name1.replace('formc-0-',repl);
        		var idlab =name1.replace('formc-0-','id_formc-'+parseInt(ss)+'-');
                        console.log("namelab ", namelab, "idlab ", idlab , ss);
        		var forlab = name1.replace('formc-0-','id_formc-'+parseInt(ss)+'-');
        		$(this).attr({'placeholder':namelab, 'id':idlab, 'for':idlab, 'name':namelab});
        	});	
        });
}  
