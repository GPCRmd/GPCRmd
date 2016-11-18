

$(document).ready(function(){
    $.fn.exists = function () {
      return this.length !== 0;
    };
    

    
    
    $.fn.resetCompoundInfo = function (clean_ids) {
        clean_ids = typeof clean_ids !== 'undefined' ? clean_ids : true;
        
        var molform = $(this).parents("[id|=molform]");
        var notindbs = $(molform).find("[id='id_is_not_in_databases'],[id|=id_form][id$='-is_not_in_databases']");
        var stdform = $(molform).find("[id='id_stdform'],[id|=id_form][id$='-stdform']");
        var stdform_html = $(stdform_global_html).clone();
        stdform_html.attr('id',stdform.attr('id'));
        stdform_html.attr('name',stdform.attr('name'));
        var name = $(molform).find("[id='id_name'],[id|=id_form][id$='-name']");
        var iupac_name = $(molform).find("[id='id_iupac_name'],[id|=id_form][id$='-iupac_name']");
        var aliases = $(molform).find("[id='id_other_names'],[id|=id_form][id$='-other_names']");
        var pubchemcid = $(molform).find("[id='id_pubchem_cid'],[id|=id_form][id$='-pubchem_cid']");
        var chemblid = $(molform).find("[id='id_chemblid'],[id|=id_form][id$='-chemblid']");
        var neutralize_pubchem = $(molform).find("[id='id_neutralize_pubchem'],[id|=id_form][id$='-neutralize_pubchem']");
        var retrieve_type_pubchem = $(molform).find("[id='id_retrieve_type_pubchem'],[id|=id_form][id$='-retrieve_type_pubchem']");
        var search_by_pubchem = $(molform).find("[id='id_search_by_pubchem'],[id|=id_form][id$='-search_by_pubchem']");
        var neutralize_chembl = $(molform).find("[id='id_neutralize_chembl'],[id|=id_form][id$='-neutralize_chembl']");
        var retrieve_type_chembl = $(molform).find("[id='id_retrieve_type_chembl'],[id|=id_form][id$='-retrieve_type_chembl']");
        var search_by_chembl = $(molform).find("[id='id_search_by_chembl'],[id|=id_form][id$='-search_by_chembl']");
        var similarity_chembl = $(molform).find("[id='id_similarity_chembl'],[id|=id_form][id$='-similarity_chembl']");
        
        

        name.val('');
        iupac_name.val('');
        aliases.val('');
        if (clean_ids) {
            pubchemcid.val('');
            chemblid.val('');
        }
        notindbs.prop("disabled",false);
        notindbs.prop("checked",false);
        notindbs.trigger("change");
        var newstdform = $(stdform_html).clone()
        $(stdform).replaceWith($(newstdform));
        stdform = $(newstdform);
        
        neutralize_pubchem.prop("disabled",false);
        neutralize_pubchem.prop("checked",true);
        retrieve_type_pubchem.prop("disabled",false);
        search_by_pubchem.prop("disabled",false);
        retrieve_type_pubchem.val(retrieve_type_pubchem_default);
        search_by_pubchem.val(search_by_pubchem_default);
        
        neutralize_chembl.prop("disabled",false);
        neutralize_chembl.prop("checked",true);
        retrieve_type_chembl.prop("disabled",false);
        search_by_chembl.prop("disabled",false);
        retrieve_type_chembl.val(retrieve_type_chembl_default);
        search_by_chembl.val(search_by_chembl_default);
        similarity_chembl.val(similarity_chembl_default);

    };
    
    
    $(document).on('click',"[id='id_reset'],[id|=id_form][id$='-reset']",function(){
        var molform = $(this).parents("[id|=molform]");
        var uploadmol = $(molform).find("[id='id_upload_mol'],[id|=id_form][id$='-upload_mol']");
        var uploadmol_html = $(uploadmol_global_html).clone();
        uploadmol_html.attr('id',uploadmol.attr('id'));
        uploadmol_html.attr('name',uploadmol.attr('name'));
        var inchi = $(molform).find("[id='id_inchi'],[id|=id_form][id$='-inchi']");
        var inchikey = $(molform).find("[id='id_inchikey'],[id|=id_form][id$='-inchikey']");
        var sinchikey = $(molform).find("[id='id_sinchikey'],[id|=id_form][id$='-sinchikey']");
        var net_charge = $(molform).find("[id='id_net_charge'],[id|=id_form][id$='-net_charge']");
        var smiles = $(molform).find("[id='id_smiles'],[id|=id_form][id$='-smiles']");


        
        
        inchi.val('');
        inchikey.val('');
        sinchikey.val('');
        net_charge.val('');
        smiles.val('');
        
        var newuploadmol = $(uploadmol_html).clone()
        $(uploadmol).replaceWith($(newuploadmol));
        uploadmol = $(newuploadmol);

        
        
    });
    
    $(document).on('change',"[id='id_pubchem_cid'],[id|=id_form][id$='-pubchem_cid'],\
    [id='id_chemblid'],[id|=id_form][id$='-chemblid']",function(){

        $(this).resetCompoundInfo(false);

    });

});