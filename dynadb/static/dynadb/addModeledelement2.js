
function addModeledelement2() {
	"use strict";


		var item = document.getElementById("Element2-0");
                var itemparent = document.getElementById("pElement2");
                var itemlast = itemparent.lastElementChild;

                console.log("itemlast antes de añadir" + itemlast.id);


                var itemlastl = itemlast.id.split("-")[1];
                var lll=Number(itemlastl);
                var ll=lll+1;
                var l=ll+1;
//		var	protnumb = "PROTEIN  #" + l;
		//alert("Mira   "+ item.id)
		var	t = item.cloneNode(true);
		var	idlabnod = "Element2-" + ll;
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
