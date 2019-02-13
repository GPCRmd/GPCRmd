$(document).ready(function(){

  //--------Used later for some functions
  var typedict =  {
    'sb' : 'salt bridge',
    "pc" : 'pi-cation',
    "ps" : 'pi-stacking',
    'ts' : 't-stacking',
    "vdw" : 'van der waals',
    'hp' : 'hydrophobic',
    'hb' : 'hydrogen bond',
    "hbbb" : 'backbone to backbone HB',
    "hbsb" : 'sidechain to backbone HB',
    "hbss" : 'sidechain to sidechain HB',
    "hbls" : 'ligand to sidechain HB',
    "hblb" : 'ligand to backbone HB',
    "wb" : 'water bridge',
    "wb2" : 'extended water bridge',
    "hb" : 'hydrogen bonds',
    'all' : 'total frequency',
  }

  //Mark options selected
  url_pathname = window.location.pathname.split("/")
  url_variables = url_pathname[url_pathname.length-1]
  url_variables_ary = url_variables.split("&");
  var itype = url_variables_ary[url_variables_ary.length-3];
  var ligandonly = url_variables_ary[url_variables_ary.length-2];
  var rev = url_variables_ary[url_variables_ary.length-1];

  $('input[value="' + itype + '"]').prop('checked', true);
  if (ligandonly == "lg"){
    $('input[value="' + ligandonly + '"]').prop('checked', true);
  }
  else if (ligandonly == "prt"){
   $('input[value="' + ligandonly + '"]').prop('checked', true); 
  }
  else {
    $('input[name="molec"]').prop('checked', true)
  }
  if (rev == "rev"){
    $('#rev_pairs').prop('checked', true)
  }

  //-------Dropdowns
  $('.dropdown-submenu a.test').on("click", function(e){
    $(this).next('ul').toggle();
    e.stopPropagation();
    e.preventDefault();
  });
  //---------Avoid dropdown menu to retract at click
  $('.dropdown-menu').on("click", function(e){
    e.stopPropagation();
  });

  //-------change color upon clicking option
  //I know it's strange to have these two separated, but belive me, it was the only way to make it all work
  //$('.option').change(function(e){changeapplycolor()}); //In case any checkbox is clicked
  //$('#allbutton').click(function(e){changeapplycolor()}); //In cas all options button is clicked

  //-------Change active itype options depending of selected molecular intetactions 
  $('.option_location').change(function(){

    var hb_value = [];

    //Set all HB to disabled to begin wtih 
    $(".hb_option, .option").prop('disabled',true)

    //If protein contacts selected, enable all options except ligand-only HB options
    if (document.getElementById('Intraprotein contacts').checked){
      $(".hb_option, .option").prop('disabled',false)
      $( ".hb_option:not([value*='l'])" ).prop('disabled', true);
      $( ".hb_option:not([value*='l'])" ).prop('checked',false);
    }

    //If ligand contacts selected, enable ligand options
    if (document.getElementById('Protein to ligand contacts').checked) {
      $( ".hb_option[value*='l'], .option[value='vdw'], .option[value='hp'], .option[value='hb'], .option[value='wb'], .option[value='wb2'], .option[value='all']" ).prop('disabled',false);
    }

  });


  //--------Show name of selected interaction in dropdown button
  $(".option").change(function(){
    var sel_code = $(".option[type=radio]:checked").val();
    var sel_label = typedict[sel_code];
    document.getElementById("itype_button").innerHTML = sel_label + ' <span class="caret"></span>'
  });

  //-------- Clusters dropdown
  $('#cluster-dropdown .clust_opt').on('click', function(){    
    $('#cluster_button').html($(this).html() + ' clusters <span class="caret"></span>');    
  })

  //-------- Info panels
  $(".section_pan").click(function(){
      var target=$(this).attr("data-target");
      var upOrDown=$(target).attr("class");
      if(upOrDown.indexOf("in") > -1){
          var arrow=$(this).children(".arrow");
          arrow.removeClass("glyphicon-chevron-up");
          arrow.addClass("glyphicon-chevron-down");
      } else {
          var arrow=$(this).children(".arrow");
          arrow.removeClass("glyphicon-chevron-down");
          arrow.addClass("glyphicon-chevron-up");
          if (target=="#analysis_fplot"){
              if (plot){
                  setFPFrame(pg_framenum)
              }
          }
      }
  });
    
  $("#show_hide_info").click(function(){
      if ($("#more_info").attr("aria-expanded")=="true"){
          $("#show_hide_info_text").text("Show info ");
          $("#plot_col").css("height", '87%');
      } else {
          $("#show_hide_info_text").text("Hide info ");
          $("#plot_col").css("height", '50%');
      }
  });

  //--------------Setting width of the div as width of the plot image

  /* Not used any more
  //-----------Automatic deselect  or select of HB options 
  $('#allHB').change(function(e){checkoruncheckall('.hb_option',false)});
  $('#allWB').change(function(e){checkoruncheckall('.wb_option',false)});


  //If no HB or WB remain checked, uncheck main wb/HB option. And if any WB HB suboption is checked, check also the main one
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
  */
});



//---------Check all options upon clicking "check all" (currently not used) 
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

//--------Change button color of apply if any option is selected. Currently inactive since dropdown is a radio now
/*
function changeapplycolor(){
  var num_checked = $.map($('.option:checked'), function(c){return c.value; }).length;
  if (Boolean(num_checked)){
    $('#applybutton').addClass('btn-primary').removeClass('btn-danger');
  }
  else{
    $('#applybutton').addClass('btn-danger').removeClass('btn-primary');        
  }
}
*/
//------Extract checked values, create an URL with them and refresh page with new URL
function printchecked(){
  var checked_loc = []
  var locs = [];
  var checked_opts = [];
  var checked_values = [];
  var rev_value = ""
  var URL_values = "";
  var value_opt = "";

  //Check if reverse contact pairs is selected
  rev_value = $("#rev_pairs:checked").val();
  if (!Boolean(rev_value)){
    rev_value = "norev";
  }

  //Check location of the interaction options
  checked_locs = $('.option_location:checked');
  for (var i=0; i < checked_locs.length; i++){
    checked_loc = checked_locs[i].value;
    locs.push(checked_loc);
  }

  check_opt = $('.option[type = radio]:checked').val();

  //Check if selected interaction type is avalible for selected location
  if ($('.option[type = radio]:checked').attr('disabled') == "disabled"){
    window.alert("The selected interaction type is not avalible for the selected intraprotein partners. Please, select an avalible interaction type");
  }

  else if (Boolean(check_opt)){
    URL = '/contmaps/' + check_opt + "&" + locs.join("_") + "&" + rev_value;
    window.location.pathname = URL; 
  }
  else {
    window.alert("please select an interaction type and at least one interaction partner");
  }
}

function closeSideWindow() {
  //Close the side window which appears upon clicking bokeh plot
  $("#info").css({"visibility":"hidden","position":"absolute","z-index":"-1"});
  $("#first_col").attr("class","col-xs-5");
  $("#second_col").attr("class","col-xs-6");
  $("#retracting_parts").attr("class","col-xs-12");
}