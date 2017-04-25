
$(document).ready(function(){
    $(document).on('click',"[id='id_get_data_upkb'],[id|=id_form][id$='-get_data_upkb']",function(){
        var self = $(this);
        var getdataall = $("[id='id_get_data_upkb'],[id|=id_form][id$='-get_data_upkb']");
        var uniprotkbac_isoform;
        var protform = $(this).parents("[id|=protform]");
        var uniprotkbac = protform.find("[id='id_uniprotkbac'],[id|=id_form][id$='-uniprotkbac']");
        var uniprotkbacval = uniprotkbac.val();
        var id_species = protform.find("[id='id_id_species'],[id|=id_form][id$='-id_species']");
        var species = protform.find("[id='id_id_species_autocomplete'],[id|=id_form][id$='-id_species_autocomplete']");
        var isoform = protform.find("[id='id_isoform'],[id|=id_form][id$='-isoform']");
        var pprotform = $(protform).parent();
        var addbutton = $(pprotform).children(":last-child").find("[id='id_add_protein'],[id|=id_form][id$='-add_protein']");
        var resetbuttonall = $("[id='id_reset'],[id|=id_form][id$='-reset']");
        var notuniprot = protform.find("[id='id_is_not_uniprot'],[id|=id_form][id$='-is_not_uniprot']");
        var notuniprotall = $("[id='id_is_not_uniprot'],[id|=id_form][id$='-is_not_uniprot']");
        var isoformval = isoform.val();
        var form_num_html=Number($(this).attr('id').split("-")[1])+1;
        console.log("after variables");
        if (isoformval == '') {
          uniprotkbac_isoform = uniprotkbacval;
        } else {
          uniprotkbac_isoform = uniprotkbacval + '-' + isoformval;
        }
        
        var sequence = protform.find("[id='id_sequence'],[id|=id_form][id$='-sequence']");
        var name = protform.find("[id='id_name'],[id|=id_form][id$='-name']");
        var aliases = protform.find("[id='id_other_names'],[id|=id_form][id$='-other_names']");
        
        var disablestates = [];
        getdataall.each(function() {
            if ($(this).prop("disabled")) {
                disablestates.push(true);
            } else {
                disablestates.push(false);
            }
            
        });
        getdataall.prop("disabled",true);
        
        
        addbutton.prop("disabled", true);
        resetbuttonall.prop("disabled", true);
        notuniprotall.prop("disabled", true);
        notuniprot.prop("disabled", true);
        
        uniprotkbac.prop("disabled", true);
        species.prop("disabled", true);
        isoform.prop("disabled", true);
        name.prop("disabled", true);
        aliases.prop("disabled", true);
        sequence.prop("disabled", true);
        
        uniprotkbac.prop("readonly", false);
        species.prop("readonly", false);
        isoform.prop("readonly", false);
        name.prop("readonly", false);
        aliases.prop("readonly", false);
        sequence.prop("readonly", false);
        
        uniprotkbac.set_restore_color();
        species.set_restore_color();
        isoform.set_restore_color();
        name.set_restore_color();
        aliases.set_restore_color();
        sequence.set_restore_color();
        
        name.val('Retrieving...');
        aliases.val('Retrieving...');
        species.val('Retrieving...');
        sequence.val('Retrieving...');
        console.log("before post");
        console.log("HERE"+window.location.href);
        $.post("../get_data_upkb/",
        {
            uniprotkbac:uniprotkbac_isoform
        },
        function(data){
          uniprotkbac.val(data.Entry);
          isoform.val(data.Isoform);
          name.val(data.Name);
          console.log(data);
          aliases.val(data.Aliases);
          sequence.val(data.Sequence);
          species.val(data.Organism);
          id_species.val(data.speciesid);
          self.prop("disabled", true);
          uniprotkbac.prop("readonly", true);
          isoform.prop("readonly", true);
          uniprotkbac.set_readonly_color();
          isoform.set_readonly_color();
          console.log("PPPPP "+data.GPCRmd);
          if (data.GPCRmd===true) {
              alert("Success!!!\nProtein #"+form_num_html +" information has been found in the gpcrmd database!!!\n\nIf appropriate, check the \"Is it a Mutant?\" checkbox and proceed with the Protein #"+form_num_html+" section C.\nOtherwise, either proceed with the data submission of the following protein item in your simulation (click \"+ Add Protein\" button) or submit the information in the form.");
          }else{
              alert("\nSuccess!!!\n Protein #"+form_num_html +" information has been retrieved!!!\n\nIf appropriate, check the \"Is it a Mutant?\" checkbox and proceed with the Protein #"+form_num_html+" section C.\nOtherwise, either proceed with the data submission of the following protein item in your simulation (click \"+ Add Protein\" button) or submit the information in the form.");
          }

        }, 'json')

        .fail(function(xhr,status,msg) {
           if (xhr.readyState == 4) {
                alert(status.substr(0,1).toUpperCase()+status.substr(1)+":\nStatus: " + xhr.status+". "+msg+".\n"+xhr.responseText);
           }
           else if (xhr.readyState == 0) {
                alert("Connection error");
           }
           else {
                alert("Unknown error");
           }
           name.val('');
           aliases.val('');
           sequence.val('');
           species.val('');
           id_species.val('');
           notuniprot.prop("disabled", false);
           self.prop("disabled", false);
        })
        .always(function(xhr) {
            var selfstate = self.prop("disabled");
            var selfnotuniprotstate = notuniprot.prop("disabled");
            var i = 0;
            self.prop("disabled");
            getdataall.each(function() {
                
                $(this).prop("disabled",disablestates[i]);
                
                var protform2 = $(this).parents("[id|=protform]");
                var notuniprot2 = protform2.find("[id='id_is_not_uniprot'],[id|=id_form][id$='-is_not_uniprot']");
                notuniprot2.prop("disabled",disablestates[i]);
                if (notuniprot2.prop('checked')) {
                   $(this).prop("disabled",true);
                   notuniprot2.prop("disabled",false);
                }
                i++;
            });
            self.prop("disabled",selfstate);
            notuniprot.prop("disabled",selfnotuniprotstate);
            
            addbutton.prop("disabled", false);
            resetbuttonall.prop("disabled", false);
            
            species.prop("readonly", true);
            name.prop("readonly", true);
            aliases.prop("readonly", true);
            sequence.prop("readonly", true);
            
            species.set_readonly_color();
            name.set_readonly_color();
            aliases.set_readonly_color();
            sequence.set_readonly_color();
            
            uniprotkbac.prop("disabled", false);
            species.prop("disabled", false);
            isoform.prop("disabled", false);
            name.prop("disabled", false);
            aliases.prop("disabled", false);
            sequence.prop("disabled", false);
            
            
        });
            
            

    });
});
