
function delModeledelement2() {
	"use strict";
        var itemparent = document.getElementById("pElement2");
        var iii= itemparent.firstElementChild.id
        console.log("children en pElement2"+ iii)
        var itemdel = itemparent.lastElementChild;
        console.log("el itemdel.id es "+itemdel.id)
        var match = itemdel.id.search(/Element2_/);
        var match1 = itemdel.id.search(/Element2_0/);
        console.log("resultado de match "+ match +" resultado de match1 "+ match1);
        if(match == 0) {
            if(match1 == -1) {
                itemparent.removeChild(itemdel);
            }
	}
}

