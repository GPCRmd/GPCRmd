var l;
l = 1;
function addProtein() {
    l += 1;
    var ll; 
    ll = l-1; 
    var protnumb= "PROTEIN  #" + l;
    var item = document.getElementById("protform");
    var t = item.cloneNode(true);
    var idlabnod= "protform" + l;
    t.id=idlabnod;
    t.childNodes[1].childNodes[1].childNodes[1].innerHTML=protnumb;
    document.getElementById("pprotform").appendChild(t)[ll];

}
