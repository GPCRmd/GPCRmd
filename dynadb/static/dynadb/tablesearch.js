$("#tablesearch").click(function() {
    var bigarray=[];
    $("#myTable tr").each(function () {
        var postarray=[];
        var counter=0;
        $('td', this).each(function () {
            if (counter>0){
                var value = $(this).text(); //var value = $(this).text();
                postarray.push(value);
            } else {  
                var drop=$(this).find(":selected").text();
                postarray.push(drop);
            }
            counter=counter+1;
        })
        bigarray.push(postarray);
    })
    var exactboo=$('#exactmatch').prop('checked');
    $.ajax({
        type: "POST",
        data: {  "bigarray[]": bigarray, 'exactmatch':exactboo},
        url: "/dynadb/complex_search/",
        dataType: "json",
        success: function(data) {
            $("#tablesearch").prop("disabled",false);
            if (data.message==''){
                $('#tableresults').text(data.result);
                $('#modelresults').text(data.model);
                if (data.compound_table.length>0){
                    var table = $('<table></table>').addClass('foo');
                    var header= $('<thead><tr><th>Complex</th><th>Compound</th><th>Molecule</th></tr></thead>');
                    table.append(header);
                    for(i=0; i<data.compound_table.length; i++){
                        var row = $('<tr><td>'+data.compound_table[i][0]+'</td><td><a href=/dynadb/compound/id/'+data.compound_table[i][1]+'>'+data.compound_table[i][1]+'</a></td><td><a href=/dynadb/molecule/id/'+data.compound_table[i][2]+'>'+data.compound_table[i][2]+'</a></td></tr>'); // $('<tr></tr>').addClass('bar').text(data.compound_table[i]);
                        table.append(row);
                    }
                    $('#tableresults').append(table);
                } // endif (data.compound_table.length>0)
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
});

