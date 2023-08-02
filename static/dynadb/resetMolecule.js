var type_default = '';
var is_present_default = null;


$(document).ready(function(){
    $.fn.exists = function () {
      return this.length !== 0;
    };
    
    type_default = $("[id='id_type'],[id|=id_form][id$='-type']").val();
    is_present_default = $("[id='id_is_present'],[id|=id_form][id$='-is_present']").prop('checked');
    
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
        var checkupload = $(molform).find("[id='id_checkupload'],[id|=id_form][id$='-checkupload']");  
                   $(checkupload).hide()
        
        
        
        name.val('');
        iupac_name.val('');
        aliases.val('');
        if (clean_ids) {
            pubchemcid.val('');
            chemblid.val('');
        }
        notindbs.prop("disabled",false);
        notindbs.prop("checked",false);
        notindbs.OnChangeIsNotInDatabases();
        //var newstdform = $(stdform_html).clone()
       // $(stdform).replaceWith($(newstdform));
       // stdform = $(newstdform);
        $(stdform).css('opacity',0);
        $(stdform).css('filter',"alpha(opacity=0)");


        neutralize_pubchem.prop("checked",true);
        retrieve_type_pubchem.val(retrieve_type_pubchem_default);
        search_by_pubchem.val(search_by_pubchem_default);
        neutralize_chembl.prop("checked",true);
        retrieve_type_chembl.val(retrieve_type_chembl_default);
        search_by_chembl.val(search_by_chembl_default);
        similarity_chembl.val(similarity_chembl_default);
        if (!notindbs.prop("checked")) {
            search_by_chembl.changeSimilarityStateOnSearchByChange();
        }
        


    };
    
    
    $.fn.resetMoleculeByButton = function (clean_ids) {
        var molform = $(this).parents("[id|=molform]");
        var uploadmol1 = $(molform).find("[id='id_upload_mol-1'],[id|=id_form][id$='-upload_mol-1']");
        var uploadmol1_html = $(uploadmol1_global_html).clone();
        uploadmol1_html.attr('id',uploadmol1.attr('id'));
        uploadmol1_html.attr('name',uploadmol1.attr('name'));
        var uploadmol2 = $(molform).find("[id='id_upload_mol-2'],[id|=id_form][id$='-upload_mol-2']");
        var uploadmol2_html = $(uploadmol2_global_html).clone();
        uploadmol2_html.attr('id',uploadmol2.attr('id'));
        uploadmol2_html.attr('name',uploadmol2.attr('name'));
        var inchi = $(molform).find("[id='id_inchi'],[id|=id_form][id$='-inchi']");
        var inchikey = $(molform).find("[id='id_inchikey'],[id|=id_form][id$='-inchikey']");
        var sinchikey = $(molform).find("[id='id_sinchikey'],[id|=id_form][id$='-sinchikey']");
        var net_charge = $(molform).find("[id='id_net_charge'],[id|=id_form][id$='-net_charge']");
        var smiles = $(molform).find("[id='id_smiles'],[id|=id_form][id$='-smiles']");
        var mol_type = $(molform).find("[id='id_type'],[id|=id_form][id$='-type']");
        var is_present = $(molform).find("[id='id_is_present'],[id|=id_form][id$='-is_present']");
        var imagentable=$(this).parents("[id|=molform]").find("[id|=id_form][id$='imagentable']");
        var imagentable2=$(this).parents("[id|=molform]").find("[id|=id_form][id$='z-nodb']");
        
        inchi.val('');
        inchikey.val('');
        sinchikey.val('');
        net_charge.val('');
        smiles.val('');
        
        //var newuploadmol = $(uploadmol1_html).clone()
        //$(uploadmol1).replaceWith($(newuploadmol));
        //uploadmol1 = $(newuploadmol);
        //var newuploadmol = $(uploadmol2_html).clone()
        //$(uploadmol2).replaceWith($(newuploadmol));
        //uploadmol2 = $(newuploadmol);
        $(imagentable).hide();
        $(imagentable2).hide();

        
        $(mol_type).val(type_default);
        $(is_present).prop('checked',is_present_default);
        
        $(this).resetCompoundInfo(clean_ids);
    }
    $(document).on('click',"[id='id_reset'],[id|=id_form][id$='-reset']",function(){
        $(this).resetMoleculeByButton();

        var molform = $(this).parents("[id|=molform]");
        var molsdf = $(molform).find("[id='id_molsdf'],[id|=id_form][id$='-molsdf']");
        $(molsdf).val('');
        
        
    });
    
    $(document).on('change',"[id='id_pubchem_cid'],[id|=id_form][id$='-pubchem_cid'],\
    [id='id_chemblid'],[id|=id_form][id$='-chemblid']",function(){

        $(this).resetCompoundInfo(false);

    });

});
