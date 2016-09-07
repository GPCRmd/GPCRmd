
$(document).ready(function(){
    $(document).on('click',"[id='id_get_data_upkb'],[id|=id_form][id$='-get_data_upkb']",function(){
        var uniprotkbac_isoform;
	var protform = $(this).parents("[id|=protform]");
        var uniprotkbac = protform.find("[id='id_uniprotkbac'],[id|=id_form][id$='-uniprotkbac']");
	var uniprotkbacval = uniprotkbac.val();
        var id_species = protform.find("[id='id_id_species'],[id|=id_form][id$='-id_species']");
        var species = protform.find("[id='id_id_species_autocomplete'],[id|=id_form][id$='-id_species_autocomplete']");
        var isoform = protform.find("[id='id_isoform'],[id|=id_form][id$='-isoform']");
	var isoformval = isoform.val();
        if (isoformval == '') {
          uniprotkbac_isoform = uniprotkbacval;
        } else {
          uniprotkbac_isoform = uniprotkbacval + '-' + isoformval;
        }
	
	var sequence = protform.find("[id='id_sequence'],[id|=id_form][id$='-sequence']");
        var name = protform.find("[id='id_name'],[id|=id_form][id$='-name']");
        var aliases = protform.find("[id='id_other_names'],[id|=id_form][id$='-other_names']");
        name.val('Retrieving...');
        aliases.text('Retrieving...');
        sequence.text('Retrieving...');
        
        $.post("get_data_upkb/",
        {
            uniprotkbac:uniprotkbac_isoform
        },
        function(data){
          uniprotkbac.val(data.Entry);
          isoform.val(data.Isoform);
	  name.val(data.Name);
          aliases.text(data.Aliases);
	  sequence.text(data.Sequence);
          species.val(data.Organism);
          id_species.val(data.speciesid);
        }, 'json')

        .fail(function(xhr) {
           alert("Error "+ "\nStatus: " + xhr.status+"\n"+xhr.responseText);
           name.val('');
           aliases.text('');
           sequence.text('');
           species.val('');
           id_species.val('');
        })

    });
});
