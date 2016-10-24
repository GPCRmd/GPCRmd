$("#ModelSearch").click(function() {
    var p=$("#cmolecule").val();
    $.ajax({
        type: "POST",
        data: { cmolecule: p},
        url: "/dynadb/model_search/",
        dataType: "json",
        success: function(data) {
            $("#ModelSearch").prop("disabled",false);
            if (data.message==''){
                //$('#resultsm').text(data.modelresult);
                res = data.modelresult.split(",");
                var linkresult='';
                for (var id in res){
                    linkresult=linkresult+'<a href=/dynadb/model/id/'+res[id]+'>'+res[id]+'</a>, ';
                }
                $('#resultsm').html(linkresult);
            }else{
                alert(data.message);
            }
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            $("#ModelSearch").prop("disabled",false);
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
