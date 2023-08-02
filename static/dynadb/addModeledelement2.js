$(document).ready(function() {
     $("#id_add_element2").click( function () {
        //var modelform = $(this).parents("#myform");
        var itemparent = $("#pElement2");
        var item = $(itemparent).find("[id|='Element2']")[0];
        
        var itemlast = $(itemparent).find("[id|='Element2']:last-child");
        var itemlastnum = Number(itemlast.attr("id").split("-")[1]);
        var itemlastnum_1 = itemlastnum+1;

        var newitem = $(item).clone();
        var idlabnod = "Element2-" + itemlastnum_1;
        $(newitem).attr("id",idlabnod);
        var resname = $(newitem).find("[id$='-resname']:input");
        var molecule = $(newitem).find("[id$='-molecule']:input");
        var numberofmol = $(newitem).find("[id$='-numberofmol']:input");
        numberofmol.val("");
        $(resname).prop("readonly",false);
        $(resname).set_restore_color();
        $(molecule).prop("readonly",false);
        $(molecule).set_restore_color();
        $(molecule).attr("type","number");
        $(molecule).attr("min",1);

        $(newitem).find(':input').each(function() {
                var name1 = $(this).attr('name');
                var name= name1.replace('formmc-0-','');
                var namelab="formmc-"+itemlastnum_1+"-"+name;
                var idlab ="id_formmc-"+itemlastnum_1+"-"+name;
                $(this).attr({'id':idlab, 'name':namelab});
        });
        console.log("PIPOL")
        $(itemparent).append($(newitem));

    });

    $("#id_del_element2").click( function () {
        var parentdin = $(this).parents("#myform");
        var itemdel = parentdin.find("[id|=Element2]:last:not(#Element2-0)");
        if (!itemdel.find("[id$='molecule']:input").prop("readonly")) {
            itemdel.remove();
        }

    });
});
