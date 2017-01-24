var timeout_update_mol_info = null; 
$(document).ready(function() {
    
    $.fn.set_readonly_color = function () {
        $(this).css('background-color','#FFEFD5');
        return this;
    }
    
    $.fn.set_restore_color = function () {
        $(this).css('background-color','');
        return this;
    }
    
    $("[readonly]").set_readonly_color();
    
    
    $.fn.update_mol_info = function () {
        var self = $(this);
        var dynform = $(this).parents("#dynform");
        var buttonadd = dynform.find("#id_add_element");
        var buttondel = dynform.find("#id_del_element");
        var element1 = $(this).parents("[id|=Element1]");
        var id_molecule = element1.find("[id='id_id_molecule'],[id|=id_formc][id$='-id_molecule']");
        var namef = element1.find("[id='id_name'],[id|=id_formc][id$='-name']");
        var typemc = element1.find("[id='id_typemc'],[id|=id_formc][id$='-typemc']");
        var type_int = element1.find("[id='id_typemc'],[id|=id_formc][id$='-type_int']");
        if (self.val() !== '') {
            $.post("./get_submission_molecule_info/",
            {
                molecule:self.val()
            },
            function(data){
                id_molecule.val(data.molecule_id);
                namef.val(data.name);
                typemc.val(data.type_text);
                type_int.val(data.type);
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
                id_molecule.val('');
                namef.val('');
                typemc.val('');
                type_int.val('');
            })
            
            .always(function(xhr,status,msg) {
                self.prop('disabled',false);
                buttonadd.prop('disabled',false);
                buttondel.prop('disabled',false);
            });
        }
    }
    
    $(document).on('change',"[id='molecule'],[id|=id_formc][id$='-molecule']",function(){
        var self = $(this);
        var dynform = $(this).parents("#dynform");
        var buttonadd = dynform.find("#id_add_element");
        var buttondel = dynform.find("#id_del_element");
        buttonadd.prop('disabled',true);
        buttondel.prop('disabled',true);
        self.prop('disabled',true);
        if (timeout_update_mol_info !== null) {
            window.clearTimeout(timeout_update_mol_info);
            timeout_update_mol_info = null;
        }
        timeout_update_mol_info = window.setTimeout(function () {
            self.update_mol_info();
            
        }
        ,3000);
        
    });
   
    $("#add_mol_new").click(function() {
        var self=$(this)
        var collapse=$(this).parents("#PRUEBA2").find("#addmoleculebutton")
        if (self.prop('checked') ===true){
            $(collapse).prop('hidden',false)
            console.log("PPP")
        } else {
            $(collapse).prop('hidden',true)
        }
      });
    
    
    $("#id_check_pdb_mol").click(function() {
        var self = $(this);
        var dynform = $(this).parents("#dynform");
        var pElement1 = dynform.find("#pElement1");
        var fields = dynform.find("#pElement1 :input:not([readonly])");
        var Element1s = dynform.find("#pElement1 [id|=Element1]");
        var buttonadd = dynform.find("#id_add_button");
        var buttondel = dynform.find("#id_del_button");
        var logfile = dynform.find("#id_logfile");
        var pdbchecker_tar_gz = dynform.find("#id_pdbchecker_tar_gz");
        var solvent_num = dynform.find("#id_solvent_num");
        var atom_num = dynform.find("#id_atom_num");
        fields.prop('readonly',true);
        
        self.prop('disabled',true);
        buttonadd.prop('disabled',true);
        buttondel.prop('disabled',true);
        var newform = $('<form method="post" id="hiddenform" action="" enctype="application/x-www-form-urlencoded"></form>');
        newform.append(pElement1.clone());
        $(newform).ajaxSubmit({
            url: "./check_pdb_molecules/",
            type: 'POST',
            dataType:'json',
            success: function(data) {
                alert(data.msg);
                Element1s.each(function () {
                    var resname = $(this).find("[id='resname'],[id|=id_formc][id$='-resname']").val().trim();
                    var numofmol = $(this).find("[id='numberofmol'],[id|=id_formc][id$='-numberofmol']");
                    numofmol.val(data.resnames[resname].num_of_mol);
                    solvent_num.val(data.num_of_solvent);
                    atom_num.val(data.atom_num);
                });
                if (data.download_url_log != null) {
                    logfile.attr("href",data.download_url_log);
                    logfile.show();
                }
                if (data.download_url_pdbchecker != null) {
                    pdbchecker_tar_gz.attr("href",data.download_url_pdbchecker);
                    pdbchecker_tar_gz.show();
                }
                
            },
            error: function(xhr,status,msg){
                if (xhr.readyState == 4) {
                    
                    if ((xhr.status==422 || xhr.status==500) &&
                    xhr.getResponseHeader("content-type") == "application/json") {
                        var data = jQuery.parseJSON(xhr.responseText);
                        if (data.download_url_log != null) {
                            logfile.attr("href",data.download_url_log);
                            logfile.show();
                        }
                        if (data.download_url_pdbchecker != null) {
                            pdbchecker_tar_gz.attr("href",data.download_url_pdbchecker);
                            pdbchecker_tar_gz.show();
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
                self.prop('disabled',false);
                fields.prop('readonly',false);
                //fields.set_restore_color();
                buttonadd.prop('disabled',false);
                buttondel.prop('disabled',false);
            }
        });
    
    
    
    
    });
    
    
    
});
