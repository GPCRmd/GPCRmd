$(document).ready(function(){

  //Remove heatmap loading icon once page is loaded
  document.getElementById("loading_heatmap").remove();

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
  var itype, clusters, ligandonly, rev;
  url_pathname = window.location.pathname.split("/")
  url_variables = url_pathname[url_pathname.length-1]
  if (url_variables) {
    url_variables_ary = url_variables.split("&");
    itype = url_variables_ary[url_variables_ary.length-4];
    clusters = url_variables_ary[url_variables_ary.length-3];
    ligandonly = url_variables_ary[url_variables_ary.length-2];
    rev = url_variables_ary[url_variables_ary.length-1];
  }
  else {
    itype = "all";
    clusters = "3";
    ligandonly = "prt_lg";
    rev = "norev";
  }

  $('input[value="' + itype + '"]').prop('checked', true);
  $('.clusteropt[value="' + clusters + '"]').attr("selected", true)
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

  //--------Show selected number of clusters in button 
  $(".clustnum").change(function(){
    var sel_clust = $(".clustnum:checked").val();
    document.getElementById("cluster_button").innerHTML = sel_clust + ' clusters <span class="caret"></span>'
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
      } else {
          $("#show_hide_info_text").text("Hide info ");
      }
  });

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

//------Extract checked values, create an URL with them and refresh page with new URL
function printchecked(){
  var checked_loc = []
  var locs = [];
  var checked_opts = [];
  var checked_values = [];
  var rev_value = ""
  var URL_values = "";
  var value_opt = "";
  var clusters = $('#clusters_dropdown').val();

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
    URL = '/contmaps/' + check_opt + "&" + clusters + "&" + locs.join("_") + "&"  + rev_value;
    if (window.location.pathname == URL){
      location.reload()
    }
    else {
      window.location.pathname = URL; 
    }
  }
  else {
    window.alert("please select an interaction type and at least one interaction partner");
  }
}

function closeSideWindow() {
  //Close the side window which appears upon clicking bokeh plot
  $("#info").css({"visibility":"hidden","position":"absolute","z-index":"-1"});
  $("#retracting_parts").attr("class","col-xs-12");
}