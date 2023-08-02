var l;
l = 0;

function delDynamics() {
	"use strict";
        var itemparent = document.getElementById("pdynform");
        var itemdel = itemparent.lastElementChild;
        console.log("el itemdel.id es "+itemdel.id)
        var match = itemdel.id.search(/dynform-/);
        var match1 = itemdel.id.search(/dynform-0/);
        console.log("resultado de match "+ match +" resultado de match1 "+ match1);
        if(match == 0) {
            if(match1 == -1) {
                itemparent.removeChild(itemdel);
            }
        }
}
