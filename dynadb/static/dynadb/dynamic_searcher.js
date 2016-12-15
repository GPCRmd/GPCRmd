$("#DynaSearch").click(function() {
    var p=$("#cmodel").val();
    $.ajax({
        type: "POST",
        data: { cmodel: p},
        url: "/dynadb/dynamics_search/",
        dataType: "json",
        success: function(data) {
            $("#DynaSearch").prop("disabled",false);
            if (data.message==''){
                res = data.dynaresult.split(",");
                var linkresult='';
                for (var id in res){
                    linkresult=linkresult+'<a href=/dynadb/dynamics/id/'+res[id]+'>'+res[id]+'</a><br>';
                }
                $('#resultsd').html(linkresult);

            }else{
                alert(data.message);
            }
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            $("#DynaSearch").prop("disabled",false);
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
