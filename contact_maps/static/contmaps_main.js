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

  //---------Mark options selected
  var param_string, search_params, itype, clusters, ligandonly, rev, stnd;
  param_string = window.location.search; 
  search_params = new URLSearchParams(param_string)
  if (Boolean(param_string)) {
    itype = search_params.get('itype');
    clusters = search_params.get('cluster');
    ligandonly = search_params.get('prtn');
    rev = search_params.get('rev');
    stnd = search_params.get('stnd');
  }
  else {
    itype = "hb";
    clusters = "3";
    ligandonly = "prt_lg";
    rev = "norev";
    stnd = "cmpl";
  }

  $('input[value="' + itype + '"]').prop('checked', true);

  //-------Dropdowns
  $('.dropdown-submenu a.test').on("click", function(e){
    $(this).next('ul').toggle();
    e.preventDefault();
  });
  //---------Avoid dropdown menu to retract at click
  var button;
  $('.notretract').on("click", function(e){
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

  //-------- Change text and arrow in documentation title on click
  $("#show_hide_info").click(function(){
      arrow=$(this).children(".arrow");
      if ($("#more_info").attr("aria-expanded")=="true"){
          $("#show_hide_info_text").text("Show info ");
          arrow.css('transform', 'rotate(180deg)');
      } else {
          $("#show_hide_info_text").text("Hide info ");
          arrow.css('transform', 'rotate(0deg)');
      }
  });

  //If it is not the "not avalible interaction" page, but the regular one:
  if (!$("#not_avalible_text")[0]){

    //---------Remove heatmap loading icon once page is loaded
    document.getElementById("loading_div").remove();

    $(window).on('load', function(){

      //---------------When scrolling on heatmap, move the x-axis annotations along with the scrolling
      var  scrollPos = 0, container, anots, pager, pager_height, anots_height, pager_mintop, anots_mintop, top_window, new_top;
      //Elements to scroll
      container = $("#main_plot_body"); 
      anots =  $(".bk-annotation");
      pager = $("#heatmap_pager");
      pager_height = pager.offset().top;
      anots_height = anots.outerHeight();
      pager_mintop = parseInt(pager.css('top'));
      anots_mintop = parseInt(anots.css('top'));
      container.on("scroll", function() {
        top_window = container.scrollTop();
        anots.each(function(index, anot){
          new_top = scrollPos - anots_height;
          //Now move the axis annotations
          //If scroll would result in annotations going higher than original position, set them in original position again
          if (anots_mintop > new_top){
            $(anot).css('top', anots_mintop);
          }
          // if previous scrolling-position of window was down from the axis original position 
          else  {
            $(anot).css('top', new_top-45);
          }

        });
        scrollPos = top_window;
      });

      //------------ On click of dendrogram, check corresponding checkbox on the customized heatmap dropdown
      var re = /dyn\d+/, dynid, checkbox, rect;
      $(".annotation-text").click(function(){
        dynid = $(this).attr('data-unformatted').match(re)[0];
        rect = $(this).prev();
        checkbox = $("#"+dynid+"_checkbox");
        if (checkbox.is(':checked')){
          checkbox.prop('checked',false);
          rect.css('stroke-opacity', '0');
        } 
        else {
          checkbox.prop('checked',true)
          rect.css('stroke-opacity', '1');
        }
        select_simulations(itype, clusters, ligandonly, rev, stnd)
      });

      //----------- On click of checkboxes dropdown, border corresponding annotations on dendrogram
      $(".simulation_checkbox").on('change', function(){
        dynid = $(this).attr('name');
        rect = $(".annotation-text[data-unformatted*='" + dynid + "<']").prev();
        checkbox = $(this);
        if (checkbox.is(':checked')){
          rect.css('stroke-opacity', '1');
        }
        else {
          rect.css('stroke-opacity', '0');
        }
        select_simulations(itype, clusters, ligandonly, rev, stnd)
      });
    });

    //---------Uncheck all simulations button
    $("#uncheck_all_sim").click(function(){
      $('.simulation_checkbox').each(function(){
        $(this).prop('checked',false);
      });
      $('.annotation-text').prev().each(function(){
        $(this).css('stroke-opacity','0')
      });
    });

  };

});

//-------------Turn around little arrow on click of flare_title
function turn_arrow(arrowid, clicked_id) {
  var arrow, clickable;
  arrow = $("#"+arrowid);
  clicked = $("#"+clicked_id)
  if(clicked.attr("aria-expanded") == "false"){
    arrow.css('transform', 'rotate(180deg)');
  } 
  else {
    arrow.css('transform', 'rotate(0deg)');
  }; 

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

  //Check if include non-standard is selected
  stnd_value = $("#non_standard:checked").val();
  if (!Boolean(stnd_value)){
    stnd_value = "stnd";
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
    var newurl = window.origin + '/contmaps/?itype=' + check_opt + "&cluster=" + clusters + "&prtn=" + locs.join("_") + "&rev="  + rev_value + "&stnd=" + stnd_value;
    if (window.location.pathname == URL){
      location.reload()
    }
    else {
      window.open(newurl, "_self") 
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
  //Different sizes depending if it is a customized heatmap or not
}

//--------Heatmap change page system (the return false thing is for links not to redirect anywhere)
function heatmap_change(heatmap) {
    
  function set_active_page(number){
    //Hide all heatmaps and show the one selected
    $(".heatmap").hide();
    $("#heatmap"+number).css('display','inline-block');
    //Deactivate all page buttons and activate the selected one
    $("#heatmap_pager .page-item").removeClass("active");
    $("#heatmap_page_"+number).addClass("active")
  }
  var new_heatmap;
  //If the clicked option is the current one, do nothing
  if ($("#heatmap_page_"+heatmap).hasClass("active")){
    //pass
  }
  else if (heatmap=="next"){
    new_heatmap = parseInt($(".heatmap:visible").attr("data-number"))+1;
    if ($("#heatmap_page_"+new_heatmap).length){
      set_active_page(new_heatmap);
    }
  } 
  else if (heatmap=="prev"){
    new_heatmap = parseInt($(".heatmap:visible").attr("data-number"))-1;
    if ($("#heatmap_page_"+new_heatmap).length){
      set_active_page(new_heatmap);
    }
  }
  else {
    new_heatmap = heatmap;
    set_active_page(new_heatmap);
  }
  return false
}

//---------Customized selection of simulations
function select_simulations(itype, clusters, ligandonly, rev, stnd){
  
  //variables
  var simulationlist, code, URL, custombutton;

  //Get selected simulations dynIDs
  simulationlist = $(".simulation_checkbox:checked").map(function(){return $(this).attr("name");}).get();

  //(Pseudo-)Random identifier for this customized heatmap
  code = Math.random().toString(36).substring(7);

  //Open new tab with the results
  URL = window.location.origin + '/contmaps/customized/?itype=' + itype + "&cluster=" + clusters + "&prtn=" + ligandonly + "&rev="  + rev + "&stnd=" + stnd + "&code=" + code;

  //Set new attributes to the custom form, and enable it if any simulations are selected
  custombutton = $("#CustomButton");
  $("input[name='SimList']").val(simulationlist.join("&"));
  custombutton.attr('formaction',URL);
  if (simulationlist.length == 0){
    custombutton.attr('disabled',true);
  }
  else {
    custombutton.attr('disabled',false);
  }
}