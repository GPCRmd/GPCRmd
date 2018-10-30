
//Dropdowns
$(document).ready(function(){
  //Submenus
  $('.dropdown-submenu a.test').on("click", function(e){
    $(this).next('ul').toggle();
    e.stopPropagation();
    e.preventDefault();
  });
  //Avoid dropdown menu to retract at click
  $('.dropdown-menu').on("click", function(e){
    e.stopPropagation();
  });
});



//Check or uncheck all checkboxes of the selected class (Ex: .option) depending if there are, or not, checkboxes already selected.
//Disabled checkboxes are not selected  
function checkoruncheckall(checkboxclass,changename){
  var checkcomand = checkboxclass + ':checked';
  if (Boolean($(checkcomand).val())) {
    $(checkboxclass).prop('checked', false);
    if(Boolean(changename)){
      document.getElementById("allbutton").innerHTML = "Select all";
    }
  }
  else {
    $(checkboxclass + ":enabled").prop('checked', true);
    if(Boolean(changename)){
      document.getElementById("allbutton").innerHTML = "Unselect all";
    }
  }
}



$(document).ready(function(){
  //Detect if Hydrogen bond or water bridge options have been clicked, and select or deselect all its options in consequence
  $('#allHB').change(function(e){checkoruncheckall('.hb_option',false)});
  $('#allWB').change(function(e){checkoruncheckall('.wb_option',false)});
});



$(document).ready(function(){

//Change button class of apply if any checkbox is selected
  function changeapplycolor(){
    var num_checked = $.map($('.option:checked'), function(c){return c.value; }).length;
    if (Boolean(num_checked)){
      $('#applybutton').addClass('btn-primary').removeClass('btn-danger');
    }
    else{
      $('#applybutton').addClass('btn-danger').removeClass('btn-primary');        
    }
  }

  //I know it's strange to have these two separated, but belive me, it was the only way to make it all work
  $('.option').change(function(e){changeapplycolor()}); //In case any checkbox is clicked
  $('#allbutton').click(function(e){changeapplycolor()}); //In cas all options button is clicked
});    



//Disable non-ligand HB and WB types if ligand only is selected
$(document).ready(function(){
  $('.option_location').change(function(){

    var sel_value = "";

    //Set all to enabled to begin wtih 
    $(".wb_option, .hb_option, .option").prop('disabled',false)

    //If protein-only selected, disable ligand-only options
    if (document.getElementById('Intraprotein').checked){
      $( ".wb_option[value*='l'],.hb_option[value*='l']" ).prop('disabled',true).prop('checked',false);
    }

    //If ligand-only selected, disable non-ligand options
    else if (document.getElementById('Protein to ligand').checked) {
      $( ".wb_option:not([value*='l']),.hb_option:not([value*='l']),.option[value='ts'],.option[value='sb'],.option[value='ps'],.option[value='pc']" ).prop('disabled',true).prop('checked',false);
    }

    //Change dropdown text by the selected value
    sel_value = $('.option_location:checked');
    document.getElementById('loc_dropdown').innerHTML = sel_value.attr('id');
  });
});



function printchecked(){
  //Extract checked values, create an URL with them and refresh page with new URL
  var checked_loc = []
  var locs = [];
  var checked_opts = [];
  var checked_values = [];
  var URL_values = "";
  var value_opt = "";

  //Check location of the interaction options
  checked_locs = $('.option_location:checked');
  for (var i=0; i < checked_locs.length; i++){
    checked_loc = checked_locs[i].value;
    locs.push(checked_loc);
  }

  checked_opts = $('.option[type = checkbox]:checked');
  for (i=0; i < checked_opts.length; i++ ){
    value_opt = checked_opts[i].value;
    if (value_opt != "false"){
      checked_values.push(value_opt);
    }
  }
  if (Boolean(checked_values.length)){
    URL = '/contplots/' + checked_values.join("_") + "/" + locs.join("_");
    window.location.pathname = URL; 
  }
  else {
    window.alert("please select an interaction type");
  }
}



//If no HB or WB remain checked, uncheck main wb/HB option. And if any WB HB suboption is checked, check also the main one
$(document).ready(function(){
  var checkedval = "";
  
  $('.hb_option').click(function(){
    checkedval = $('.hb_option:checked').val();
    if(Boolean(checkedval)){
      $('#allHB').prop('checked', true);
    }
    else {
      $('#allHB').prop('checked', false);        
    }
  })

  $('.wb_option').click(function(){
    checkedval = $('.wb_option:checked').val();
    if(Boolean(checkedval)){
      $('#allWB').prop('checked', true);
    }
    else {
      $('#allWB').prop('checked', false);        
    }
  })
});

