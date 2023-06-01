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
        var modelform = $(this).parents("form");
        var buttonadd = modelform.find("#id_add_element2");
        var buttondel = modelform.find("#id_del_element2");
        var element2 = $(this).parents("[id|=Element2]");
        var id_molecule = element2.find("[id='id_id_molecule'],[id|=id_formmc][id$='-id_molecule']");
        var namemc = element2.find("[id='id_namemc'],[id|=id_formmc][id$='-namemc']");
        var typemc = element2.find("[id='id_typemc'],[id|=id_formmc][id$='-typemc']");
//        var typ_option = typemc.find("[id='id_typemc'],[id|=id_formmc][id$='-typemc']");

//        var dict {"0":"Ions", "1":"Ligand", "2":"Lipid",  "3":"Water", "4":"Other"};
        var val_to_text_type = {0:"Ions", 1:"Ligand", 2:"Lipid", 3:"Water", 4:"Other"};
        if (self.val() !== '') {
            $.post("./get_submission_molecule_info/",
            {
                molecule:self.val()
            },
            function(data){
                id_molecule.val(data.molecule_id);
                namemc.val(data.namemc);
                $(typemc).find(":selected").val(data.type);
                $(typemc).find(":selected").html(val_to_text_type[data.type]);
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
                namemc.val('');
            })
            
            .always(function(xhr,status,msg) {
                self.prop('disabled',false);
                buttonadd.prop('disabled',false);
                buttondel.prop('disabled',false);
            });
        }
    }
    
    $(document).on('change',"[id='molecule'],[id|=id_formmc][id$='-molecule']",function(){
        var self = $(this);
        var modelform = $(this).parents("form");
        var buttonadd = modelform.find("#id_add_element2");
        var buttondel = modelform.find("#id_del_element2");
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
        } else {
            $(collapse).prop('hidden',true)
        }
      });


            
    $("#id_check_pdb_mol").click(function() {
        var self = $(this);
        var modelform = $(this).parents("#myform");
        var pElement1 = modelform.find("#pElement1");
        var pElement2 = modelform.find("#pElement2");
        var fields = modelform.find("#pElement2 :input:not([readonly])");
        var Element2s = modelform.find("#pElement2 [id|=Element2]");
        var buttonadd = modelform.find("#id_add_button");
        var buttondel = modelform.find("#id_del_button");
        var logfile = modelform.find("#id_logfile");
        var pdbchecker_tar_gz = modelform.find("#id_pdbchecker_tar_gz");
        fields.prop('readonly',true);
        //fields.set_readonly_color();
        self.prop('disabled',true);
        buttonadd.prop('disabled',true);
        buttondel.prop('disabled',true);
        var newform = $('<form method="post" id="hiddenform" action="" enctype="application/x-www-form-urlencoded"></form>');
        newform.append(pElement1.clone());
        newform.append(pElement2.clone());
        $(newform).ajaxSubmit({
            url: "./check_pdb_molecules/",
            type: 'POST',
            dataType:'json',
            success: function(data) {
                alert(data.msg);
                Element2s.each(function () {
                    var resname = $(this).find("[id='resname'],[id|=id_formmc][id$='-resname']").val().trim();
                    var numofmol = $(this).find("[id='numberofmol'],[id|=id_formmc][id$='-numberofmol']");
                    numofmol.val(data.resnames[resname].num_of_mol);
                    
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
