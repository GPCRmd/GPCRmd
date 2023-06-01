var stdform_global_html = '';
var retrieve_type_pubchem_default = '';
var retrieve_type_chembl_default = '';
var search_by_pubchem_default = '';
var search_by_chembl_default = '';
var similarity_chembl_default = '';




$(document).ready(function(){
    stdform_global_html = $("[id='id_stdform'],[id|=id_form][id$='-stdform']").first().clone();
    retrieve_type_pubchem_default = $("[id='id_retrieve_type_pubchem'],[id|=id_form][id$='-retrieve_type_pubchem']").first().val();
    retrieve_type_chembl_default = $("[id='id_retrieve_type_chembl'],[id|=id_form][id$='-retrieve_type_chembl']").first().val();
    search_by_pubchem_default = $("[id='id_search_by_pubchem'],[id|=id_form][id$='-search_by_pubchem']").first().val();
    search_by_chembl_default = $("[id='id_search_by_chembl'],[id|=id_form][id$='-search_by_chembl']").first().val();
    similarity_chembl_default =  $("[id='id_similarity_chembl'],[id|=id_form][id$='-similarity_chembl']").first().val();
    
    $.fn.changeSimilarityStateOnSearchByChange = function () {
        var molform = $(this).parents("[id|=molform]");
        var similarity_chembl = $(molform).find("[id='id_similarity_chembl'],[id|=id_form][id$='-similarity_chembl']");
        if ($(this).val() == 'sinchikeynoiso' || $(this).val() == 'sinchikey' ) {
            similarity_chembl.prop('disabled',true);
        } else {
            similarity_chembl.prop('disabled',false);
        }
    }
    
    $(document).on('change',"[id='id_search_by_chembl'],[id|=id_form][id$='-search_by_chembl']",function(){
        $(this).changeSimilarityStateOnSearchByChange();
    });
    

    
    function doAlways(self, pngsize, molform, stdform, stdform_html, getmolinfo, molformidx, pmolform, addbutton, 
    resetbuttonall, uploadmolbutton, inchi, inchikey, sinchikey, net_charge, 
    smiles, name, iupac_name, aliases, pubchemcid, chemblid, updatepubchem, updatechembl, 
    notindbs, notindbsall, neutralize_pubchem, retrieve_type_pubchem, search_by_pubchem, 
    neutralize_chembl, retrieve_type_chembl, search_by_chembl, similarity_chembl, disablestatesinfo, 
    disablestatespubchem, disablestateschembl, html_pngsize) {
        
        notindbs.prop("disabled", false);
//         self.prop("disabled", false);
//         var selfstate = self.prop("disabled");
        var selfnotindbsstate = notindbs.prop("disabled");
        var i = 0;
        getmolinfo.each(function() {
            
            $(this).prop("disabled",disablestatesinfo[i]);
            
            var molform2 = $(this).parents("[id|=molform]");
            var notindbs2 = molform2.find("[id='id_is_not_in_databases'],[id|=id_form][id$='-is_not_in_databases']");
            notindbs2.prop("disabled",disablestatesinfo[i]);
            if (notindbs2.prop('checked')) {
                $(this).prop("disabled",true);
                notindbs2.prop("disabled",false);
            }
            i++;
        });
        i=0;
        updatepubchem.each(function() {
            
            $(this).prop("disabled",disablestatespubchem[i]);
            
            var molform2 = $(this).parents("[id|=molform]");
            var notindbs2 = molform2.find("[id='id_is_not_in_databases'],[id|=id_form][id$='-is_not_in_databases']");
            if (notindbs2.prop('checked')) {
            $(this).prop("disabled",true);
            }
            i++;
        });
        i=0;
        updatechembl.each(function() {
            
            $(this).prop("disabled",disablestateschembl[i]);
            
            var molform2 = $(this).parents("[id|=molform]");
            var notindbs2 = molform2.find("[id='id_is_not_in_databases'],[id|=id_form][id$='-is_not_in_databases']");
            if (notindbs2.prop('checked')) {
            $(this).prop("disabled",true);
            }
            i++;
        });
//         self.prop("disabled",selfstate);
        notindbs.prop("disabled",selfnotindbsstate);
        
        addbutton.prop("disabled", false);
        resetbuttonall.prop("disabled", false);
        uploadmolbutton.prop("disabled", false);
        
        neutralize_pubchem.prop("disabled",notindbs.prop('checked'));
        retrieve_type_pubchem.prop("disabled",notindbs.prop('checked'));
        search_by_pubchem.prop("disabled",notindbs.prop('checked'));
        neutralize_chembl.prop("disabled",notindbs.prop('checked'));
        retrieve_type_chembl.prop("disabled",notindbs.prop('checked'));
        search_by_chembl.prop("disabled",notindbs.prop('checked'));
        similarity_chembl.prop("disabled",notindbs.prop('checked'));
        search_by_chembl.changeSimilarityStateOnSearchByChange();
        
        name.prop("readonly", true);
        iupac_name.prop("readonly", true);
        aliases.prop("readonly", true);

        
        name.prop("disabled", false);
        iupac_name.prop("disabled", false);
        aliases.prop("disabled", false);
        pubchemcid.prop("disabled", false);
        chemblid.prop("disabled", false);
        
        name.set_readonly_color();
        iupac_name.set_readonly_color();
        aliases.set_readonly_color();

    }
    
    function ChemblGetInfo(self, pngsize, molform, stdform, stdform_html, getmolinfo, molformidx, pmolform, addbutton, 
    resetbuttonall, uploadmolbutton, inchi, inchikey, sinchikey, net_charge, 
    smiles, name, iupac_name, aliases, pubchemcid, chemblid, updatepubchem, updatechembl, 
    notindbs, notindbsall, neutralize_pubchem, retrieve_type_pubchem, search_by_pubchem, 
    neutralize_chembl, retrieve_type_chembl, search_by_chembl, similarity_chembl, disablestatesinfo, 
    disablestatespubchem, disablestateschembl, chembl_id_only, retrieveall, html_pngsize) {
        
        var data = {
            molid:molformidx,
            pngsize:pngsize,
        };
        
        if (retrieveall) {
        
            data['search_by'] = search_by_chembl.val();
            data['retrieve_type'] = retrieve_type_chembl.val();
        
            if (neutralize_chembl.prop('checked')) {
                data['neutralize'] = '1'
            }
            if (search_by_chembl.val() == 'sinchikeynoiso') {
                data['inchi'] = inchi.val();
            } else if (search_by_chembl.val() == 'sinchikey') {
                data['sinchikey'] = sinchikey.val();
            } else if (search_by_chembl.val() == 'smiles') {
                data['smiles'] = smiles.val();
                data['similarity'] = similarity_chembl.val();
            }
        
        } else {
            data['update_from_id'] = chemblid.val(); 
        }
        

        if (!chembl_id_only) {  
            
            name.val('Retrieving...');
            aliases.val('Retrieving...');
            iupac_name.val('Retrieving...');
        
        } else {
            data['id_only'] = '1';
        }
        
        
        
        $.post("./get_compound_info_chembl/",data=data,
        function(data){

        
        if (data.chembl_id.length > 1) {  
            alert('Several PubChem CompoundIDs match this molecule.\nA pop-up will open in order to show them.');
            var urllist=window.location.href.split("/");
            console.log(urllist+" urlist");
            $.post('../open_chembl/', {cids:data.chembl_id.join()}, function (data) {
                var win=window.open('about:blank');
                win.document.open();
                win.document.write(data);
                win.document.close();
                chemblid.val('');
                
                if (!chembl_id_only) {
                    name.val('');
                    iupac_name.val('');
                    aliases.val('');
                    pubchemcid.val('');
                    var newstdform = $(stdform_html).clone()
                    $(stdform).replaceWith($(newstdform));
                    stdform = newstdform;
                    $(stdform).prop('disabled',true);
                }

            })
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
            
            });
        } else {
            if (!chembl_id_only) {
                name.val(data.name);
                iupac_name.val(data.iupac_name);
                aliases.val(data.synonyms);
                var newstdform = $("<img>")
                .attr("src",data.download_url_png+'?'+(new Date()).getTime())
                .attr("id",$(stdform).attr("id"))
                .attr("name",$(stdform).attr("name"))
                .attr("height",html_pngsize)
                .attr("width",html_pngsize);
                $(stdform).prop('disabled',false);
                $(stdform).replaceWith(newstdform);
                stdform = newstdform;
            }
            chemblid.val(data.chembl_id[0]);

            
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
        
        chemblid.val('');
        if (!chembl_id_only) {
            name.val('');
            iupac_name.val('');
            aliases.val('');
            pubchemcid.val('');
            
            var newstdform = $(stdform_html).clone()
            $(stdform).replaceWith($(newstdform));
            stdform = $(newstdform);
            $(stdform).prop('disabled',true);
        }

        })
        
        .always(function(xhr) {
            doAlways(self, pngsize, molform, stdform, stdform_html, getmolinfo, molformidx, pmolform, addbutton, 
            resetbuttonall, uploadmolbutton, inchi, inchikey, sinchikey, net_charge, 
            smiles, name, iupac_name, aliases, pubchemcid, chemblid, updatepubchem, updatechembl, 
            notindbs, notindbsall, neutralize_pubchem, retrieve_type_pubchem, search_by_pubchem, 
            neutralize_chembl, retrieve_type_chembl, search_by_chembl, similarity_chembl, disablestatesinfo, 
            disablestatespubchem, disablestateschembl);

        });
    }
    
    $(document).on('click',"[id='id_get_mol_info'],[id|=id_form][id$='-get_mol_info']\
    ,[id='id_update_from_pubchem'],[id|=id_form][id$='-update_from_pubchem']\
    ,[id='id_update_from_chembl'],[id|=id_form][id$='-update_from_chembl']",function(){
        var self = $(this);
        
        var retrieveall = false;
        var dopubchem = false;
        var dochembl = false;
        if (self.is("[id='id_get_mol_info'],[id|=id_form][id$='-get_mol_info']")) {
            retrieveall = true;
            dopubchem = true;
            dochembl = true;
        } else if (self.is("[id='id_update_from_pubchem'],[id|=id_form][id$='-update_from_pubchem']")) { 
            dopubchem = true;
        } else if (self.is("[id='id_update_from_chembl'],[id|=id_form][id$='-update_from_chembl']")) {
            dochembl = true;
        }
            
        var pngsize = 300;
        var html_pngsize = 250;
        var molform = $(this).parents("[id|=molform]");
        var stdform = $(molform).find("[id='id_stdform'],[id|=id_form][id$='-stdform']");
        var stdform_html = $(stdform_global_html).clone();
        stdform_html.attr('id',stdform.attr('id'));
        stdform_html.attr('name',stdform.attr('name'));
        var getmolinfo = $("[id='id_get_mol_info'],[id|=id_form][id$='-get_mol_info']");
        var molformidx = parseInt(molform.attr('id').split("-")[1],10);
        var pmolform = $(molform).parent();
        var addbutton = $(pmolform).children(":last-child").find("[id='id_add_molecule'],[id|=id_form][id$='-add_molecule']");
        var resetbuttonall = $("[id='id_reset'],[id|=id_form][id$='-reset']");
        var uploadmolbutton = $("[id='id_upload_button'],[id|=id_form][id$='-upload_button']");
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
        var updatepubchem = $("[id='id_update_from_pubchem'],[id|=id_form][id$='-update_from_pubchem']");
        var updatechembl = $("[id='id_update_from_chembl'],[id|=id_form][id$='-update_from_chembl']");
        var notindbs = $(molform).find("[id='id_is_not_in_databases'],[id|=id_form][id$='-is_not_in_databases']");
        var notindbsall = $("[id='id_is_not_in_databases'],[id|=id_form][id$='-is_not_in_databases']");
        var neutralize_pubchem = $(molform).find("[id='id_neutralize_pubchem'],[id|=id_form][id$='-neutralize_pubchem']");
        var retrieve_type_pubchem = $(molform).find("[id='id_retrieve_type_pubchem'],[id|=id_form][id$='-retrieve_type_pubchem']");
        var search_by_pubchem = $(molform).find("[id='id_search_by_pubchem'],[id|=id_form][id$='-search_by_pubchem']");
        var neutralize_chembl = $(molform).find("[id='id_neutralize_chembl'],[id|=id_form][id$='-neutralize_chembl']");
        var retrieve_type_chembl = $(molform).find("[id='id_retrieve_type_chembl'],[id|=id_form][id$='-retrieve_type_chembl']");
        var search_by_chembl = $(molform).find("[id='id_search_by_chembl'],[id|=id_form][id$='-search_by_chembl']");
        var similarity_chembl = $(molform).find("[id='id_similarity_chembl'],[id|=id_form][id$='-similarity_chembl']");
        
        var disablestatesinfo = [];
        getmolinfo.each(function() {
            if ($(this).prop("disabled")) {
                disablestatesinfo.push(true);
            } else {
                disablestatesinfo.push(false);
            }
            
        });
        getmolinfo.prop("disabled",true);
        
        var disablestatespubchem = [];
        updatepubchem.each(function() {
            if ($(this).prop("disabled")) {
                disablestatespubchem.push(true);
            } else {
                disablestatespubchem.push(false);
            }
            
        });
        updatepubchem.prop("disabled",true);
        
        var disablestateschembl = [];
        updatechembl.each(function() {
            if ($(this).prop("disabled")) {
                disablestateschembl.push(true);
            } else {
                disablestateschembl.push(false);
            }
            
        });
        updatechembl.prop("disabled",true);
        
        addbutton.prop("disabled", true);
        resetbuttonall.prop("disabled", true);
        notindbsall.prop("disabled", true);
        notindbs.prop("disabled", true);
        uploadmolbutton.prop("disabled", true);
        
        neutralize_pubchem.prop("disabled",true);
        retrieve_type_pubchem.prop("disabled",true);
        search_by_pubchem.prop("disabled",true);
        neutralize_chembl.prop("disabled",true);
        retrieve_type_chembl.prop("disabled",true);
        search_by_chembl.prop("disabled",true);
        similarity_chembl.prop("disabled",true);
        
        name.prop("disabled", true);
        iupac_name.prop("disabled", true);
        aliases.prop("disabled", true);
        pubchemcid.prop("disabled", true);
        chemblid.prop("disabled", true);
        
        name.prop("readonly", false);
        iupac_name.prop("readonly", false);
        aliases.prop("readonly", false);

        
        name.set_restore_color();
        iupac_name.set_restore_color();
        aliases.set_restore_color();

        
        
        name.val('Retrieving...');
        aliases.val('Retrieving...');
        iupac_name.val('Retrieving...');
        if (self.is("[id='id_get_mol_info'],[id|=id_form][id$='-get_mol_info']")) {
        pubchemcid.val('Retrieving...');
        chemblid.val('Retrieving...');
        }
        if (dopubchem) {
        
            var data = {
                molid:molformidx,
                pngsize:pngsize,
            };
            
            if (retrieveall) {
                
                data['search_by'] = search_by_pubchem.val();
                data['retrieve_type'] = retrieve_type_pubchem.val();
                
                if (neutralize_pubchem.prop('checked')) {
                    data['neutralize'] = '1'
                }
                
                if (search_by_pubchem.val() == 'sinchi' || search_by_pubchem.val() == 'sinchikeynoiso') {
                    data['inchi'] = inchi.val();
                } else if (search_by_pubchem.val() == 'sinchikey') {
                    data['sinchikey'] = sinchikey.val();
                } else if (search_by_pubchem.val() == 'smiles') {
                    data['smiles'] = smiles.val();
                }
            
            } else {
                data['update_from_id'] = pubchemcid.val(); 
            }
          
            var chembl_id_only = true;
            $.post("./get_compound_info_pubchem/",data=data,
            function(data){
            
            if (data.pubchem_cid.length > 1) {  
                alert('Several PubChem CompoundIDs match this molecule.\nA pop-up will open in order to show them.');
                $.post('../open_pubchem/', {cids:data.pubchem_cid.join()}, function (data) {
                    var win=window.open('about:blank');
                    win.document.open();
                    win.document.write(data);
                    win.document.close();
                    
                    name.val('');
                    iupac_name.val('');
                    aliases.val('');
                    pubchemcid.val('');
                    chemblid.val('');
                    var newstdform = $(stdform_html).clone()
                    $(stdform).replaceWith($(newstdform));
                    stdform = $(newstdform);
                    $(stdform).prop('disabled',true);

                })
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
                
                });
            } else {
                name.val(data.name);
                iupac_name.val(data.iupac_name);
                aliases.val(data.synonyms);
                pubchemcid.val(data.pubchem_cid[0]);
                var newstdform = $("<img>")
                .attr("src",data.download_url_png+'?'+(new Date()).getTime())
                .attr("id",$(stdform).attr("id"))
                .attr("name",$(stdform).attr("name"))
                .attr("height",html_pngsize)
                .attr("width",html_pngsize);
                $(stdform).replaceWith($(newstdform));
                stdform = newstdform;
            }
            

            }, 'json')
            .fail(function(xhr,status,msg) {
            chembl_id_only = false;
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
            iupac_name.val('');
            aliases.val('');
            pubchemcid.val('');
            chemblid.val('');
            var newstdform = $(stdform_html).clone()
            $(stdform).replaceWith($(newstdform));
            stdform = $(newstdform);
            $(stdform).prop('disabled',true);
            })
            .always(function(xhr) {
                if (dochembl) {
                    
                    if (chembl_id_only) {
                        data['id_only'] = 1;
                        alert('Starting CHEMBL ID assignment. Confirm to proceed.');
                    } else {
                        alert('PubChem download failed. Obtaining compound information from CHEMBL. Confirm to proceed.');
                    }
                    
                    ChemblGetInfo(self, pngsize, molform, stdform, stdform_html, getmolinfo, molformidx, pmolform, addbutton, 
                    resetbuttonall, uploadmolbutton, inchi, inchikey, sinchikey, net_charge, 
                    smiles, name, iupac_name, aliases, pubchemcid, chemblid, updatepubchem, updatechembl, 
                    notindbs, notindbsall, neutralize_pubchem, retrieve_type_pubchem, search_by_pubchem, 
                    neutralize_chembl, retrieve_type_chembl, search_by_chembl, similarity_chembl, disablestatesinfo, 
                    disablestatespubchem, disablestateschembl,chembl_id_only,retrieveall, html_pngsize);
                
                } else {
                    doAlways(self, pngsize, molform, stdform, stdform_html, getmolinfo, molformidx, pmolform, addbutton, 
                    resetbuttonall, uploadmolbutton, inchi, inchikey, sinchikey, net_charge, 
                    smiles, name, iupac_name, aliases, pubchemcid, chemblid, updatepubchem, updatechembl, 
                    notindbs, notindbsall, neutralize_pubchem, retrieve_type_pubchem, search_by_pubchem, 
                    neutralize_chembl, retrieve_type_chembl, search_by_chembl, similarity_chembl, disablestatesinfo, 
                    disablestatespubchem, disablestateschembl, html_pngsize);
                }
            });
            
        } else {
            if (dochembl) {
                    ChemblGetInfo(self, pngsize, molform, stdform, stdform_html, getmolinfo, molformidx, pmolform, addbutton, 
                    resetbuttonall, uploadmolbutton, inchi, inchikey, sinchikey, net_charge, 
                    smiles, name, iupac_name, aliases, pubchemcid, chemblid, updatepubchem, updatechembl, 
                    notindbs, notindbsall, neutralize_pubchem, retrieve_type_pubchem, search_by_pubchem, 
                    neutralize_chembl, retrieve_type_chembl, search_by_chembl, similarity_chembl, disablestatesinfo, 
                    disablestatespubchem, disablestateschembl,chembl_id_only,retrieveall, html_pngsize);
            }
            
        }

    });
});
