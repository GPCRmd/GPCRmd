var l;
l = 0;

function addModeledelement2() {
	"use strict";
	l += 1;
	var ll = l - 1;	 //alert(l + " l=1 primer ciclo de cambio");
	if (l==1) {
		var itemfirst = document.getElementById("Element2");
		var idlabnod1= "Element2_0";
		itemfirst.id = idlabnod1;
		$(itemfirst).find(':input').each(function() {
		var name1 = $(this).attr('name');
		var namelab1="formmc-"+ll+"-"+name1;
		var idlab1 ="id-formmc-"+0+"-"+name1;
		var forlab ="id_formmc-"+ll+"-"+name1;
		$(this).attr({'placeholder':namelab1, 'id':idlab1, 'for':idlab1, 'name':namelab1});
		});
		l=2;
		ll=1;
//		alert("l ="+ l + "   y ll=" +ll);
	} 
//	else {
		var item = document.getElementById("Element2_0");
                var itemparent = document.getElementById("pElement2");
                var itemlast = itemparent.lastElementChild;

                console.log("itemlast " + itemlast.id);


                var itemlastl = itemlast.id.split("_")[1];
                var lll=Number(itemlastl);
                ll=lll+1;
                l=ll+1;
//		var	protnumb = "PROTEIN  #" + l;
		//alert("Mira   "+ item.id)
		var	t = item.cloneNode(true);
		var	idlabnod = "Element2_" + ll;
		t.id = idlabnod;
//		t.childNodes[1].childNodes[1].childNodes[1].innerHTML = protnumb;
		document.getElementById("pElement2").appendChild(t)[ll];
		var ttt = t;
	
		$(ttt).find(':input').each(function() {
			var name1 = $(this).attr('name');
			var name= name1.replace('formmc-0-','');
			var namelab="formmc-"+ll+"-"+name;
						//alert("before change " +  name1 + "  After change >> " + name );
			var idlab ="id_formmc-"+ll+"-"+name;
			var forlab ="id_formmc-"+ll+"-"+name;
			$(this).attr({'placeholder':namelab, 'id':idlab, 'for':idlab, 'name':namelab});
		});	
//	}
   				// alert("number of children " + ttt.childElementCount);
}
