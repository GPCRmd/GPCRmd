$(document).ready(function(){

  //When pressing "plot selection" button, we'll run this code instead of default form submission
  function submit_form(name,form,e) {
    e.preventDefault(); // avoid to execute the actual submit of the form.

    //Hide error and show loading
    errordiv = $("#"+name+"error")
    loadingdiv = $("#"+name+"loading")
    plotdiv = $("#"+name+"plot")
    scriptdiv = $("#"+name+"script")
    downlink = $("#"+name+"down")
    plotdiv.hide()
    errordiv.hide()
    loadingdiv.show()

    //Send ajax request and get plot in return
    $.ajax({
      url: "corplot/"+name+"_plot",
      data_type: 'json',
      type: 'POST',
      data: form.serialize(),
      success: function(data) {
        data_dict = JSON.parse(data)
        plotdiv.html(data_dict['div'])
        scriptdiv.html(data_dict['script'])
        plotdiv.show();
        downlink.attr('href', 'infoplot/'+data_dict['out']+'/'+data_dict['path'])
        downlink.show();
      },
      error: function(){
        errordiv.show();            
      },
      complete: function(){
        loadingdiv.hide();
      },
      timeout: 600000
    });
  }

  //On click of the "plot selection" button
  $('#topcorform').submit(function(e) {
    submit_form('topcor',$(this),e)
  });
  $('#customform').submit(function(e) {
    submit_form('custom',$(this),e)
  });

  //Update pathway-outcome pair selection when filter by outcome or minimum n options are modified
  $("#out_fil, #min_n").on('change', function(e){
    valid_out = $("#out_fil").val()
    isall = (valid_out=='all')
    min_n = $("#min_n").val()
    //Hide and disable options with n below stablished minimum
    $(".paircor").each(function(){
      opt = $(this)
      if ((opt.attr('data-n') >= min_n) && ((opt.attr('data-out')==valid_out)||isall)){
        opt.show()
        opt.attr('disabled',false)
      }
      else {
        opt.hide()
        opt.attr('disabled',true)
        // opt.attr('selected',false)
      }
    })
    //Deselect selected option if bellow minimum
    $("#pairs").val("")
  })


  //Dropdowns
  $('.dropdown-submenu').on("click", function(e){
    $(this).next('ul').toggle();
  });

  //Avoid dropdown menu to retract at click
  $('.dropdown-menu').on("click", function(e){
      e.stopPropagation();
  });

  //Mark input radio near base Residue information buttons
  $(".sign.opt_label").click(function(){
      id_input = $(this).attr('for')
      $(".recsign").removeClass('checked')
      $("#"+id_input).addClass('checked')
  })


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