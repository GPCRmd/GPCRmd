
var l;
l = 0;

function addProtein() {
	"use strict";
	l += 1;
	var ll = l - 1;	 
        // the first time the function works, it modifies some html attributes of the first protein by adding indexes to the preexistent ones, in order to differently label different proteins in the Protein form. Additional Proteins in the form would have the same text label but different indexes.   
	if (l==1) {
		var itemfirst = document.getElementById("protform");
		var idlabnod1= "protform-0";
		itemfirst.id = idlabnod1;
		//Jquery function for changing labels for all the HTML input elements
		$(itemfirst).find(':input,:button').each(function() {
                  var name1 = $(this).attr('name');
                  var namelab1="form-"+ll+"-"+name1;
                  var idlab1 ="id_form-"+0+"-"+name1;
                  var forlab ="id_form-"+ll+"-"+name1;
                  $(this).attr({'placeholder':namelab1, 'id':idlab1, 'for':idlab1, 'name':namelab1});
		});
		l=2;
		ll=1;
	}; 
	// Afterwards the DOM Node containing the protein fields is replicated and the corresponding labels are modifyied by increasing the index. Note that indexes for the Protein #1 is 0 (l=1, ll=0).
        // lll variable will take the value of the index used in the last DOM Node so far (itemlast) and will be used for updating l and ll values for the additional protein DOM Node.
	var item = document.getElementById("protform-0");
        var itemparent = document.getElementById("pprotform");
        var itemlast = itemparent.lastElementChild;
        var itemlastl = itemlast.id.split("-")[1];
        var lll=Number(itemlastl);
        ll=lll+1;
        l=ll+1;
	var item = document.getElementById("protform-0");
	var	protnumb = "PROTEIN  #" + l;
	var	t = item.cloneNode(true);
	var	idlabnod = "protform-" + ll;
	t.id = idlabnod;
	t.childNodes[1].childNodes[1].childNodes[1].innerHTML = protnumb;
	document.getElementById("pprotform").appendChild(t)[ll];
	var ttt = t.childNodes[1];
        
	//Jquery function for changing labels for all the HTML input elements
	$(ttt).find(':input,:button').each(function() {
		var name1 = $(this).attr('name');
		var name= name1.replace('form-0-','');
		var namelab="form-"+ll+"-"+name;
		var idlab ="id_form-"+ll+"-"+name;
		var forlab ="id_form-"+ll+"-"+name;
		$(this).attr({'placeholder':namelab, 'id':idlab, 'for':idlab, 'name':namelab});
	});

        $("#id_form-"+ll.toString()+"-id_species").combobox();
};
