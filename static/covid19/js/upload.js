$(document).ready( function () {

    form_count_lig = $('.lig_addedfields').length; 
    form_count_memb = $('.memb_addedfields').length; 
    $("#warning_loading_time").css("display","none")
    
    //$('.has_extra_element [value=No]').attr('selected', true);
    $(".has_extra_element").each(function(){
        if ($(this).val()=="Yes"){
            var manual_errors=$(this).parents(".formfieldinfo").find(".manual_field_errors");
            manual_errors.html("<p class=text-danger>Please fill again.</p>")
            add_hide_dyn_field(this);
        }
    })

    function obtain_input_html(fields_to_add){
        var fields_html="";
        for (var i=0; i < fields_to_add.length; i++){
            var field_info=fields_to_add[i];
            var field_label=field_info["field_label"];
            var field_input=field_info["field_input"];
            var field_type=field_info["field_type"];
            var field_input_extra=field_info["field_input_extra"];
            var field_help=field_info["field_help"];
            var help_html='';
            if (field_help){
                    var help_html='<span title="'+field_help+'" class="glyphicon glyphicon-info-sign dynamictooltip" data-toggle="tooltip" >\
                    </span>';
            }
            if (field_type=="text"){
                var input_html='<input class="added_input form-control" type="text" name="'+field_input+'" '+field_input_extra+' required />'
            } else if (field_type=="choice"){
                var field_options=field_info["field_options"];
                var options_html='';
                for (var e=0;e < field_options.length; e++){
                    var option_data=field_options[e];
                    var option_val=option_data[0];
                    var option_name=option_data[1];
                    options_html+='<option value="'+option_val+'">'+option_name+'</option>';
                }
                var input_html='\
                <select class="form-control myselectform" name="'+field_input+'" '+field_input_extra+'>\
                    '+options_html+'\
                </select>\
                ';
            }
            fields_html+= '\
                    <div class="formfieldinfo">\
                      <div class="row">\
                        <div class="col-md-4 col-md-offset-2 labeltagcomp">\
                          '+field_label+"  "+help_html+' \
                        </div>\
                        <div class="col-md-4">\
                          <span class="long">\
                          '+input_html+'\
                          </span>\
                        </div>\
                      </div>\
                   </div>\
                '
        }

        return fields_html
    }

    $(".remove_field").on("click", function(){
        var sel_target=$(this).data("target");
        var last_addition=$("body").find(sel_target+":last");
        if (last_addition.length >0){
            last_addition.remove()
            if (sel_target ==".lig_addedfields"){
                form_count_lig --;
            } else if (sel_target ==".memb_addedfields"){
                form_count_memb --;
            }
        }
    })

    function add_input_row(fieldtype){  
        if (fieldtype=="ligand"){
            var fields_to_add=[
                                {"field_label": "Ligand name:", "field_input": 'ligand_name_' + form_count_lig, "field_type": "text" , "field_input_extra": 'maxlength="200"', "field_help":false},
                                {"field_label": "Ligand resname:", "field_input": 'ligand_resname_' + form_count_lig, "field_type": "text",  "field_input_extra": 'maxlength="4"', "field_help":"Resname present on the simulation topology file."},
                                {"field_label": "Ligand type:", "field_input": 'ligand_type_' + form_count_lig, "field_type": "choice", "field_options": [["orthosteric","Orthosteric"],["allosteric","Allosteric"]], "field_input_extra": '', "field_help":false}
                              ]
            var inputset_selector="lig_addedfields";
            var dynsection_selector="#ligand_fields";
            var count_name="ligand_count";
            form_count_lig ++;
            var count_new_val=form_count_lig;

        } else if (fieldtype=="membrane") {
            var fields_to_add=[
                {"field_label": "Molecule name:", "field_input": 'membmol_name_' + form_count_memb, "field_type": "text" , "field_input_extra": 'maxlength="200"', "field_help":false},
                {"field_label": "Molecule resname:", "field_input": 'membmol_resname_' + form_count_memb, "field_type": "text",  "field_input_extra": 'maxlength="4"', "field_help":"Resname present on the simulation topology file."},
            ];
            var inputset_selector="memb_addedfields";
            var dynsection_selector="#membrane_fields";
            var count_name="membrane_count";
            form_count_memb ++;
            var count_new_val=form_count_memb;
        }
        var created_fields_html = obtain_input_html(fields_to_add)
        var final_html='<div class="'+inputset_selector+'">' + created_fields_html + '</div>'
        $(dynsection_selector).append(final_html);
        // build html and append it to our container

        $("[name="+count_name+"]").val(count_new_val);
        // increment form count so our view knows to populate 
        // that many fields for validation
    }

    $(".add-another").click(function() {
        var fieldtype=$(this).data("fieldtype");
        add_input_row(fieldtype);
    })


    $("body").find('[data-toggle="tooltip"]').tooltip();    
    $('body').tooltip({
        selector: '.dynamictooltip',
        trigger:"hover",
        //container: "#view_screen"

    });  

    function add_hide_dyn_field(selector){
        var sel_id=$(selector).attr("id");
        if (sel_id=="id_has_lig"){
            var section_sel=$("#ligand_section");
            var inputset_selector=".lig_addedfields";
            var fieldtype="ligand";
        } else if (sel_id=="id_has_membrane"){
            var section_sel=$("#membrane_section");
            var inputset_selector=".memb_addedfields";
            var fieldtype="membrane";
        }
        
        var show_element=$(selector).val()
        if (show_element=="Yes"){
            section_sel.css("display","inline")
            section_sel.find('.added_input').attr("required", true);
            if ($(inputset_selector).length == 0){
                add_input_row(fieldtype)
            }
        } else {
            section_sel.find('.added_input').attr("required", false);
            section_sel.css("display","none")
        }
    }

    $(".has_extra_element").on("change" ,function(){
        add_hide_dyn_field(this)
    });    

    $(".modify_label").on("change" ,function(){
        var myval=$(this).val();
        var label_dict=$(this).data("val");
        var newlabel=label_dict[myval]
        var target=$(this).data("target");
        $("[for=id_"+target+"]").text(newlabel)
    });    

    $("#submit_btn button").on("click",function(){
        $(".manual_field_errors").html("")
        $("body").css("cursor","progress")
        $("#warning_loading_time").css("display","inline")
    })

})
