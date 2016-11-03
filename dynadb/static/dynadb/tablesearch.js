$("#tablesearch").click(function() {
    $('#tableresults').html('Complex Results:');
    $('#modelresults').html('Models Results');
    var exactboo=$('#exactmatch').prop('checked');
    if (exactboo==true){
       $('#myTable').find('.tableselect').each(function() {
             $(this).val('and');
       })

    }
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
    var is_apoform=$('#apoform').prop('checked');
    $.ajax({
        type: "POST",
        data: {  "bigarray[]": bigarray, 'exactmatch':exactboo,'restype':restype,'ff':ff,'tstep':tstep,'is_apo':is_apoform},
        url: "/dynadb/complex_search/",
        dataType: "json",
        success: function(data) {
            $("#tablesearch").prop("disabled",false);
            if (data.message==''){

                //Results are complexes, which have no link
                if (data.result.length>0){
                    $('#tableresults').html('Complex Results:');
                    $('#tableresults').append("<ul id='complexes'></ul>");
                    var cl=data.result.split(',');
                    listc='';
                    for(i=0; i<cl.length; i++){
                        $("#complexes").append("<li>"+cl[i]+"</li>");
                    }
                }//endif


                //Results are models
                if (data.model.length>0){
                    $('#modelresults').html('Models Results');
                    $('#modelresults').append("<ul id='modres'></ul>");
                    var rl=data.model.split(',');
                    linkr='';
                    for(i=0; i<rl.length; i++){
                        $("#modres").append("<li>"+ "<a href=/dynadb/model/id/"+rl[i]+">"+rl[i]+" </a>" +"</li>");
                    }

                }//endif


                if (data.dynlist.length>0){
                    $('#dynresults').html('Dynamics Results');
                    $('#dynresults').append("<ul id='dynres'></ul>");
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
  $('#myTable').find('.tableselect:first').val('or');
  $('#myTable').find('.tableselect:first').prop('disabled', 'disabled');
});

