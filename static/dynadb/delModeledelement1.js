var s;
s = 0;

function delModeledelement1() {
	"use strict";
        var itemparent = document.getElementById("pElement1");
        var iii= itemparent.firstElementChild.id
        console.log("children en pElement1"+ iii)
        var itemdel = itemparent.lastElementChild;
        console.log("el itemdel.id es "+itemdel.id)
        var match = itemdel.id.search(/Element1_/);
        var match1 = itemdel.id.search(/Element1_0/);
        console.log("resultado de match "+ match +" resultado de match1 "+ match1);
        if(match == 0) {
            if(match1 == -1) {
                itemparent.removeChild(itemdel);
            }
	}
}
