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
    $.ajax({
        type: "POST",
        data: {  "bigarray[]": bigarray},
        url: "/dynadb/complex_search/",
        dataType: "json",
        success: function(data) {
            $("#tablesearch").prop("disabled",false);
            if (data.message==''){
                $('#tableresults').text(data.result);
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

