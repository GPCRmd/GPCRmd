$("#tablesearch").click(function() {
    var exactboo=$('#exactmatch').prop('checked');
    var bigarray=[];
    $("#myTable tr").each(function () {
        var postarray=[];
        var counter=0;
        $('td', this).each(function () {
            if (counter==0){
                var drop=$(this).find(":selected").text();
                postarray.push(drop);
            } else {
                if (counter===3){
                    var isligrec=$(this).find('[type=checkbox]').prop('checked');
                    postarray.push(isligrec);
                }else{
                var value = $(this).text(); //var value = $(this).text();
                postarray.push(value);
                }
            }
            counter=counter+1;
        })
        bigarray.push(postarray);
    })

    var restype=$('#result_type').val();
    var ff=$('#fftype').val();
    var tstep=$('#tstep').val();
    var sof=$('#soft').val();
    var mem=$('#memtype').val();
    var method=$('#method').val();
    var sol=$('#soltype').val();
    if (restype=='model'){
        var is_apoform=$('#apoform').prop('checked');
    }
    if (restype=='dynamics'){
        var is_apoform=$('#apoform_dyn').prop('checked');
    }
    console.log(is_apoform);
    $.ajax({
        type: "POST",
        data: {  "bigarray[]": bigarray, 'exactmatch':exactboo,'restype':restype,'ff':ff,'tstep':tstep,'sol':sol,'mem':mem,'method':method,'sof':sof,'is_apo':is_apoform},
        url: "/dynadb/complex_search/",
        dataType: "json",
        success: function(data) {
            $("#tablesearch").prop("disabled",false);
            if (data.message==''){
                $('#ajaxresults').html('');
                //Results are complexes
                if (data.result.length>0 && restype=='complex'){

                    $('#ajaxresults').html('Complex Results:');
                    $('#ajaxresults').append("<ul id='complexes'></ul>");
                    var cl=data.result.split(',');
                    listc='';
                    for(i=0; i<cl.length; i++){
                        $("#complexes").append("<li> <a href=/dynadb/complex/id/"+cl[i]+">"+cl[i]+" </a> </li>");
                    }
                }//endif

                //Results are models
                if (data.model.length>0 && restype=='model'){
                    $('#ajaxresults').html('Models Results');
                    $('#ajaxresults').append("<ul id='modres'></ul>");
                    var rl=data.model
                    linkr='';
                    for(i=0; i<rl.length; i++){
                        if (is_apoform==false){
                            $("#modres").append("<li>"+ "<a href=/dynadb/model/id/"+rl[i][0]+"> Model ID:"+rl[i][0] +" contains receptor: "+rl[i][1]+" and ligand: "+rl[i][2]+" </a>" +"</li>");
                        }else{
                            $("#modres").append("<li>"+ "<a href=/dynadb/model/id/"+rl[i][0]+"> Apoform model ID:"+rl[i][0]+" with protein: "+rl[i][1]+" </a>" +"</li>");
                        }

                    }

                }//endif


                if (data.dynlist.length>0 && restype=='dynamics'){
                    $("#ajaxresults").html('Dynamics Results');
                    $("#ajaxresults").append("<ul id='dynres'></ul>");
                    var dl=data.dynlist.split(',');
                    linkd='';
                    for(i=0; i<dl.length; i++){
                        $("#dynres").append("<li>"+ "<a href=/dynadb/dynamics/id/"+dl[i]+">"+dl[i]+" </a>" +"</li>");
                    }

                } //endif



                //compound table
                if (data.compound_table.length>0){
                    var table = $('<table></table>').addClass('foo');
                    var header= $('<thead><tr><th>Complex</th><th>Compound</th><th>Molecule</th></tr></thead>');
                    table.append(header);
                    for(i=0; i<data.compound_table.length; i++){
                        var row = $('<tr><td>'+data.compound_table[i][0]+'</td><td><a href=/dynadb/compound/id/'+data.compound_table[i][1]+'>'+data.compound_table[i][1]+'</a></td><td><a href=/dynadb/molecule/id/'+data.compound_table[i][2]+'>'+data.compound_table[i][2]+'</a></td></tr>');
                        table.append(row);
                    }
                    $('#tableresults').append(table);
                } // endif

            }else{
                alert(data.message);
            }
        },

        error: function(XMLHttpRequest, textStatus, errorThrown) {
            $("#tablesearch").prop("disabled",false);
            alert("Something unexpected happen.");
        }
    });
});

function getCookie(name) {
    var cookieValue = null;
    var i = 0;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (i; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
$(document).on('click', '#deleterow', function(e){
  e.preventDefault();
  $(this).closest('tr').remove();
  $('#myTable').find('.tableselect:first').empty().append('<option selected="selected" value=""> </option><option value="not">NOT</option>');
  //$('#myTable').find('.tableselect:first').val('or');
  //$('#myTable').find('.tableselect:first').prop('disabled', 'disabled');
});

