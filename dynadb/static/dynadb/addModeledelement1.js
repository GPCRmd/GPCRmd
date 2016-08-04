var s;
s = 0;

function addModeledelement1() {
	"use strict";
	s += 1;
	var ss = s - 1;	 //alert(l + " l=1 primer ciclo de cambio");
	if (s==1) {
		var itemfirst = document.getElementById("Element1");
		var idlabnod1= "Element1_0";
		itemfirst.id = idlabnod1;
		$(itemfirst).find(':input').each(function() {
		var name1 = $(this).attr('name');
		var namelab1="form-"+ss+"-"+name1;
		var idlab1 ="id-form-"+0+"-"+name1;
		var forlab ="id_form-"+ss+"-"+name1;
		$(this).attr({'placeholder':namelab1, 'id':idlab1, 'for':idlab1, 'name':namelab1});
		});
		s=2;
		ss=1;
	} 
		var item = document.getElementById("Element1_0");
                var itemparent = document.getElementById("pElement1");
                var itemlast = itemparent.lastElementChild;

                console.log("itemlast " + itemlast.id);


                var itemlastl = itemlast.id.split("_")[1];
                var sss=Number(itemlastl);
                ss=sss+1;
                s=ss+1;
                console.log("itemlastl " + itemlastl +" ss " + ss + " s " +s)
		var	t = item.cloneNode(true);
		var	idlabnod = "Element1_" + ss;
		t.id = idlabnod;
//		t.childNodes[1].childNodes[1].childNodes[1].innerHTML = protnumb;
		document.getElementById("pElement1").appendChild(t)[ss];
		var ttt = t;
		$(ttt).find(':input').each(function() {
			var name1 = $(this).attr('name');
			var name= name1.replace('form-0-','');
			var namelab="form-"+ss+"-"+name;
						//alert("before change " +  name1 + "  After change >> " + name );
			var idlab ="id_form-"+ss+"-"+name;
			var forlab ="id_form-"+ss+"-"+name;
			$(this).attr({'placeholder':namelab, 'id':idlab, 'for':idlab, 'name':namelab});
		});	
//	}
   				// alert("number of children " + ttt.childElementCount);
}


