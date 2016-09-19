
function delProtein() {
	"use strict";
        var itemparent = document.getElementById("pprotform");
        var itemdel = itemparent.lastElementChild;
        console.log("el itemdel.id es "+itemdel.id)
        var match = itemdel.id.search(/protform-/);
        var match1 = itemdel.id.search(/protform-0/);
        console.log("resultado de match "+ match +" resultado de match1 "+ match1);
        if(match == 0) {
            if(match1 == -1) {
                itemparent.removeChild(itemdel);
            }
        }
}
