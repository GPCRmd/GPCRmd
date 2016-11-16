$(document).ready(function(){
    $.fn.exists = function () {
      return this.length !== 0;
    };
    
    $(document).on('click',"[id='id_clear_molecule'],[id|=id_form][id$='-clear_molecule']",function(){
        var molform = $(this).parents("[id|=molform]");
        var uploadmol = $(molform).find("[id='id_upload_mol'],[id|=id_form][id$='-upload_mol']");
        var stdform = $(molform).find("[id='id_stdform'],[id|=id_form][id$='-stdform']");
        var stdform_html = $('<textarea rows="3" style="width:200px;" id="id_stdform" name="stdform"/></textarea>');
        var uploadmol_html = $('<textarea rows="3" style="width:200px;" id="id_upload_mol" name="upload_mol"/></textarea>');
        $(stdform).replaceWith($(stdform_html));
        $(uploadmol).replaceWith($(uploadmol_html));
        var inchi = $(molform).find("[id='id_inchi'],[id|=id_form][id$='-inchi']");
        var inchikey = $(molform).find("[id='id_inchikey'],[id|=id_form][id$='-inchikey']");
        var sinchikey = $(molform).find("[id='id_sinchikey'],[id|=id_form][id$='-sinchikey']");
        var net_charge = $(molform).find("[id='id_net_charge'],[id|=id_form][id$='-net_charge']");
        var smiles = $(molform).find("[id='id_smiles'],[id|=id_form][id$='-smiles']");
        var name = $(molform).find("[id='id_name'],[id|=id_form][id$='-name']");
        var iupac_name = $(molform).find("[id='id_iupac_name'],[id|=id_form][id$='-iupac_name']");
        var aliases = $(molform).find("[id='id_other_names'],[id|=id_form][id$='-other_names']");
        var pubchemcid = $(molform).find("[id='id_pubchem_cid'],[id|=id_form][id$='-pubchem_cid']");
        var chemblid = $(molform).find("[id='id_chemblid'],[id|=id_form][id$='-chemblid']");
        
        inchi.val('');
        inchikey.val('');
        sinchikey.val('');
        net_charge.val('');
        smiles.val('');
        name.val('');
        iupac_name.val('');
        aliases.val('');
        pubchemcid.val('');
        chemblid.val('');
        
        
        
    });

});
