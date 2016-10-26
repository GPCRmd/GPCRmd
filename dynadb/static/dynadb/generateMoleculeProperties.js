$(document).ready(function(){
    $.fn.exists = function () {
      return this.length !== 0;
    };
    $(document).on('click',"[id='id_upload_button'],[id|=id_form][id$='-upload_button']",function(){
        var max_size = 52428800;
        var pngsize = 300;
        var stdform_html = $('<textarea rows="3" style="width:200px;" id="id_stdform" name="stdform"/></textarea>');
        var uploadmol_html = $('<textarea rows="3" style="width:200px;" id="id_upload_mol" name="upload_mol"/></textarea>');
        var self = $(this);
        $(self).prop('disabled',true);
        var mainform = $("#small_molecule");
        var molform = $(this).parents("[id|=molform]");
        var molformid = $(molform).attr('id');
        var uploadmol = $(molform).find("[id='id_upload_mol'],[id|=id_form][id$='-upload_mol']");
        var stdform = $(molform).find("[id='id_stdform'],[id|=id_form][id$='-stdform']");
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
        
        var mainformclone = $(mainform).clone();
        $(mainformclone).find("div[id|='molform']:not(#"+molformid+")").remove();
        
        var molsdf = $(molform).find("[id='id_molsdf'],[id|=id_form][id$='-molsdf']");
        if ($(molsdf).val() == "") {
             alert("No file selected.");
             return false;
        }
        
        if ($(molsdf)[0].hasOwnProperty('files') && typeof molsdf[0].files[0] !== 'undefined' && molsdf[0].files[0].hasOwnProperty('size')) {
            if (molsdf[0].files[0].size > max_size) {
                alert("Maximum size is 50 MB.");
                return false;
            }
        }
        var molsdfname = $(molsdf).attr('name');
        $(mainformclone).ajaxSubmit({
            url: "./generate_properties/",
            type: 'POST',
            data: {'molpostkey':molsdfname,'pngsize':pngsize},
            dataType:'json',
            success: function(data) {
                name.val('');
                iupac_name.val('');
                aliases.val('');
                pubchemcid.val('');
                chemblid.val('');
                
                inchi.val(data.inchi.inchi);
                inchikey.val(data.inchikey);
                sinchikey.val(data.sinchikey);
                net_charge.val(data.charge);
                smiles.val(data.smiles);
                $(stdform).replaceWith($(stdform_html));
                var newuploadmol = $("<img>")
                .attr("src",data.download_url_png+'?'+(new Date()).getTime())
                .attr("id",$(uploadmol).attr("id"))
                .attr("name",$(uploadmol).attr("name"))
                .attr("height",pngsize)
                .attr("width",pngsize)
                $(uploadmol).replaceWith($(newuploadmol));

                
            },
            error: function(xhr,status,msg){
                if (xhr.readyState == 4) {
                    alert(status.substr(0,1).toUpperCase()+status.substr(1)+":\nStatus: " + xhr.status+". "+msg+".\n"+xhr.responseText);
                }
                else if (xhr.readyState == 0) {
                    alert("Connection error. Please, try later and check that your file is not larger than 50 MB.");
                }
                else {
                    alert("Unknown error");
                }
            },
            complete: function(xhr,status,msg){
                $(self).prop('disabled',false);
            }
        });
    });
        
});