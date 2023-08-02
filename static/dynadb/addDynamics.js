var l;
l = 0;

function addDynamics() {
	"use strict";
	l += 1;
	var ll = l - 1;
        // the first time the function works, it modifies some html attributes of the first simulation by adding indexes to the preexistent ones, in order to differently label different Simulations in the Dynamics form. Additional Simulations in the form would have the same text label but different indexes. In addition the HTML id label concerning the DOM NODE including the simulation components is modified for consistency with other js scripts 
	if (l==1) {
		var itemfirst = document.getElementById("dynform");
		var idlabnod1= "dynform-0";
		itemfirst.id = idlabnod1;
		var itemfpel = document.getElementById("pElement1-0");
		var idlabpel= "pElement1-0";
		itemfpel.id = idlabpel;
                console.log("itemfpel if " + itemfpel.id)
		//Jquery function for changing labels for all the HTML input elements
		$(itemfirst).find(':input').each(function() {
		var name1 = $(this).attr('name');
		var namelab1="form-"+ll+"-"+name1;
		var idlab1 ="id-form-"+ll+"-"+name1;
		var forlab ="id_form-"+ll+"-"+name1;
		$(this).attr({'placeholder':namelab1, 'id':idlab1, 'for':idlab1, 'name':namelab1});
		});
		l=2;
		ll=1;
	} 
	// Afterwards the DOM Node containing the Simulation fields are replicated and the corresponding labels are modifyied by increasing the index. Note that indexes for the Simulation #1 is 0 (l=1, ll=0).
        // lll variable will take the value of the index used in the last DOM Node so far (itemlast) and will be used for updating l and ll values for the additional protein DOM Node.
	var item = document.getElementById("dynform-0");
        var itemparent = document.getElementById("pdynform");
        var itemlast = itemparent.lastElementChild;
        var itemlastl = itemlast.id.split("-")[1]
        var lll=Number(itemlastl);
        ll=lll+1;
        l=ll+1;
        console.log("itemlastl " + itemlastl +" ll " + ll + " l " +l)
        
	var	protnumb = "SIMULATION  #" + l;
	var	t = item.cloneNode(true);
	var	idlabnod = "dynform-" + ll;
	t.id = idlabnod;
	t.childNodes[1].childNodes[1].childNodes[1].innerHTML = protnumb;
	document.getElementById("pdynform").appendChild(t)[ll];
        // Cambiar la etiqueta de los componentes de la dynamica para cada simulacion (necesario para script addSimcomp.js delSimcomp.js
          console.log("itemlastl " + itemlastl +" ll " + ll + " l " +l)
	// the id element of the Simulation Component DOM Node is updated according to the number of the simulation. This will allow to simultaneously add component rows in all the simulation replicates 
        var id_peln = "pElement1-"+ll;
        var pel_last = document.getElementsByTagName("tbody")[ll];
        console.log("Id before modify pElement1- list = " , pel_last.id);
        pel_last.id=id_peln;
        console.log("nuevo id pelement", pel_last.id );
	var ttt = t.childNodes[1];
        //Jquery function for changing labels for all the HTML input elements	
	$(ttt).find(':input').each(function() {
		var name1 = $(this).attr('name');
		var name= name1.replace('form-0-','');
		var namelab="form-"+ll+"-"+name;
					//alert("before change " +  name1 + "  After change >> " + name );
		var idlab ="id_form-"+ll+"-"+name;
		var forlab ="id_form-"+ll+"-"+name;
		$(this).attr({'placeholder':namelab, 'id':idlab, 'for':idlab, 'name':namelab});
	});	
}
