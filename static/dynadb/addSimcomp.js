$(document).ready(function() {
    $("#id_add_element").click(function () {
        var dynform = $(this).parents("#dynform");
        var itemparent = dynform.find("#pElement1");
        var item = itemparent.find("#Element1-0");
        
        var itemlast = itemparent.children("[id|='Element1']:last-child");
        var itemlastnum = Number(itemlast.attr("id").split("-")[1]);
        var itemlastnum_1 = itemlastnum+1;

        var newitem = item.clone();
        var idlabnod = "Element1-" + itemlastnum_1;
        newitem.attr("id",idlabnod);
        var resname = newitem.find("[id$='-resname']:input");
        var molecule = newitem.find("[id$='-molecule']:input");
        var numberofmol = newitem.find("[id$='-numberofmol']:input");
        numberofmol.val("");
        resname.prop("readonly",false);
        resname.set_restore_color();
        molecule.prop("readonly",false);
        molecule.set_restore_color();
        molecule.attr("type","number");
        molecule.attr("min",1);
        $(newitem).find(':input').each(function() {
                var name1 = $(this).attr('name');
                var name= name1.replace('formc-0-','');
                var namelab="formc-"+itemlastnum_1+"-"+name;
                var idlab ="id_formc-"+itemlastnum_1+"-"+name;
                $(this).attr({'id':idlab, 'name':namelab});
        });
        itemparent.append(newitem);
    });
    
    
   $("#id_del_element").click( function () {
        var parentdin = $(this).parents("#dynform");
        var itemdel = parentdin.find("[id|=Element1]:last:not(#Element1-0)");
        if (!itemdel.find("[id$='molecule']:input").prop("readonly")) {
            itemdel.remove();
        }

    });

});

