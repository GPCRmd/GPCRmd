
function delSmalmol() {
	"use strict";
        var itemparent = document.getElementById("pmolform");
        var itemdel = itemparent.lastElementChild;
        console.log("el itemdel.id es "+itemdel.id)
        var match = itemdel.id.search(/molform-/);
        var match1 = itemdel.id.search(/molform-0/);
        console.log("resultado de match "+ match +" resultado de match1 "+ match1);
        if(match == 0) {
            if(match1 == -1) {
                itemparent.removeChild(itemdel);
            }
        }
}
