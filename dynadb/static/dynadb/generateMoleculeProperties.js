var uploadmol1_global_html = '';
var uploadmol2_global_html = '';

$(document).ready(function() {
    $.fn.exists = function () {
        return this.length !== 0;
    };
    
    uploadmol1_global_html = $("[id='id_upload_mol-1'],[id|=id_form][id$='-upload_mol-1']").first().clone();
    uploadmol2_global_html = $("[id='id_upload_mol-2'],[id|=id_form][id$='-upload_mol-2']").first().clone();
    $(document).on('click',"[id='id_upload_button'],[id|=id_form][id$='-upload_button']",function(){
        var max_size = 52428800;
        var pngsize = 300;
        var molform = $(this).parents("[id|=molform]");
        var cotype= $(molform).find("[id|=id_form][id$='co_type']");
        var nottype= $(molform).find("[id|=id_form][id$='bulk_type']");
        if ($(cotype).length > 0){
            var str = $(cotype).attr('name');
            var form_num = str.split("-")[1];
            if (!cotype.attr('name').endsWith('-type') && !nottype.attr('name').endsWith('-type')){ 
                cotype.attr('name',"form-"+form_num+"-type");
            }
        } else {
            var str = $(nottype).attr('name');
            var form_num = str.split("-")[1];
            if (!nottype.attr('name').endsWith('-type')){ 
                nottype.attr('name',"form-"+form_num+"-type");
            }
        }
           
        // imagentable=== table in which the molecule to be uploaded will be shown. If changes in the DOM structure, the variable imagentable must be updated
        var imagentable=$(this).parent().parent().siblings("[id|=id_form][id$='imagentable']");
        var imagentable2=$(this).parents("[id|=id_form][id$='A_section']").siblings("[id|=id_form][id$='D_section']").find("[id|=id_form][id$='z-nodb']");
        var uploadmol1 = $(molform).find("[id='id_upload_mol-1'],[id|=id_form][id$='-upload_mol-1']");
        var uploadmol1_html = $(uploadmol1_global_html).clone();
        uploadmol1_html.attr('id',uploadmol1.attr('id'));
        uploadmol1_html.attr('name',uploadmol1.attr('name'));
        var uploadmol2 = $(molform).find("[id='id_upload_mol-2'],[id|=id_form][id$='-upload_mol-2']");
        var uploadmol2_html = $(uploadmol2_global_html).clone();
        uploadmol2_html.attr('id',uploadmol2.attr('id'));
        uploadmol2_html.attr('name',uploadmol2.attr('name'));
        var self = $(this);
        $(self).prop('disabled',true);
        var currentform = $(molform).find("[id|=small_molecule]");
        var molformid = $(molform).attr('id');
        var logfile = $(molform).find("[id='id_logfile'],[id|=id_form][id$='-logfile']");
        var inchi = $(molform).find("[id='id_inchi'],[id|=id_form][id$='-inchi']");
        var inchikey = $(molform).find("[id='id_inchikey'],[id|=id_form][id$='-inchikey']");
        var sinchikey = $(molform).find("[id='id_sinchikey'],[id|=id_form][id$='-sinchikey']");
        var net_charge = $(molform).find("[id='id_net_charge'],[id|=id_form][id$='-net_charge']");
        var smiles = $(molform).find("[id='id_smiles'],[id|=id_form][id$='-smiles']");
        
        var molsdf = $(molform).find("[id='id_molsdf'],[id|=id_form][id$='-molsdf']");
        console.log("boton pulsado");
        
        
        if ($(molsdf).val() == "") {
             $(self).prop('disabled',false);
             alert("No file selected.");
             return false;
        }
        
        var extension = $(molsdf).val().substr( ($(molsdf).val().lastIndexOf('.') +1) ).toLowerCase();
        switch(extension) {
             case "mol":
             case "sdf":
             case "sd":
             break;
             default:
                $(self).prop('disabled',false);
                alert("Invalid extension.");
                return false;
        }
        
        
        
        if ($(molsdf)[0].hasOwnProperty('files') && typeof molsdf[0].files[0] !== 'undefined' && molsdf[0].files[0].hasOwnProperty('size')) {
            if (molsdf[0].files[0].size > max_size) {
                $(self).prop('disabled',false);
                alert("Maximum size is 50 MB.");
                return false;
            }
        }
        
        inchi.val('');
        inchikey.val('');
        sinchikey.val('');
        net_charge.val('');
        smiles.val('');
        console.log("vamos a ver el self.resetCompoundInfo");
        self.resetCompoundInfo();
        
        var molsdfname = $(molsdf).attr('name');
        console.log("despues self.resetCompoundInfo "+molsdfname);
        $(currentform).ajaxSubmit({
            url: "./generate_properties/",
            type: 'POST',
            data: {'molpostkey':molsdfname,'pngsize':pngsize},
            dataType:'json',
            success: function(data) {

                
                inchi.val(data.inchi.inchi);
                inchikey.val(data.inchikey);
                sinchikey.val(data.sinchikey);
                net_charge.val(data.charge);
                smiles.val(data.smiles);
                var ret_pubchem =  $(net_charge).parents("[id|=molform]").find("[id|=id_form][id$='retrieve_type_pubchem']");
                var neu_pubchem =  $(net_charge).parents("[id|=molform]").find("[id|=id_form][id$='neutralize_pubchem']");
                var ret_chembl =  $(net_charge).parents("[id|=molform]").find("[id|=id_form][id$='retrieve_type_chembl']");
                var neu_chembl =  $(net_charge).parents("[id|=molform]").find("[id|=id_form][id$='neutralize_chembl']");
                if ($(net_charge).val()==0){
                    console.log("EEEEEEEEE"+$(net_charge).val());
                    $(neu_pubchem).prop('checked',true);
                    $(neu_chembl).prop('checked',true);
                }else{
                    $(neu_pubchem).prop('checked',false);
                    $(neu_chembl).prop('checked',false);
                }  
                console.log("complete");
                
                var newuploadmol = $("<img>")
                .attr("src",data.download_url_png+'?'+(new Date()).getTime())
                .attr("id",$(uploadmol1).attr("id"))
                .attr("name",$(uploadmol1).attr("name"))
                .attr("height",pngsize)
                .attr("width",pngsize);
                $(uploadmol1).replaceWith($(newuploadmol));
                logfile.attr("href",data.download_url_log);
                logfile.show();
                uploadmol1 = $(newuploadmol);
                newuploadmol = $("<img>")
                .attr("src",data.download_url_png+'?'+(new Date()).getTime())
                .attr("id",$(uploadmol2).attr("id"))
                .attr("name",$(uploadmol2).attr("name"))
                .attr("height",pngsize)
                .attr("width",pngsize);
                $(uploadmol2).replaceWith($(newuploadmol));
                logfile.attr("href",data.download_url_log);
                logfile.show();
                uploadmol2 = $(newuploadmol);
                imagentable.show(); //to show the table in which the image is contained 
                imagentable2.show(); //to show the table in which the image is contained 
                console.log("success");
            },
            error: function(xhr,status,msg){
                if (xhr.readyState == 4) {
                    
                    if (xhr.status==422) {
                        var data = jQuery.parseJSON(xhr.responseText);
                        if (data.download_url_log != null) {
                            logfile.attr("href",data.download_url_log);
                            logfile.show();
                        }
                        var responsetext = data.msg;
                    } else {
                        var responsetext = xhr.responseText;
                    }
                    alert(status.substr(0,1).toUpperCase()+status.substr(1)+":\nStatus: " + xhr.status+". "+msg+".\n"+responsetext);
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
                // change Search Settings default depending on the charge
         

        
});
